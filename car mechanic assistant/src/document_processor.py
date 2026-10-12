"""Markdown, PDF (optional offline OCR) and DOCX ingestion with provenance."""
from dataclasses import dataclass
import hashlib
import json
import re
from pathlib import Path


@dataclass
class DocumentChunk:
    content: str
    metadata: dict
    chunk_id: str
    source_file: str


def canonical_vehicle_value(value):
    value = str(value).strip().casefold()
    return {"vw": "volkswagen", "mercedes": "mercedes-benz"}.get(value, value)


class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200, *, ocr_enabled=None,
                 ocr_model_dir=None, ocr_min_confidence=None):
        from .config import Config
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Require 0 <= overlap < chunk size")
        self.ocr_enabled = Config.OCR_ENABLED if ocr_enabled is None else ocr_enabled
        if not isinstance(self.ocr_enabled, bool):
            raise ValueError("OCR enabled setting must be a boolean")
        self.ocr_model_dir = Config.OCR_MODEL_DIR if ocr_model_dir is None else ocr_model_dir
        self.ocr_min_confidence = Config.OCR_MIN_CONFIDENCE if ocr_min_confidence is None else ocr_min_confidence
        if not 0 < self.ocr_min_confidence <= 1:
            raise ValueError("OCR confidence threshold must be greater than 0 and at most 1")
        self._ocr = None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.manifest = {"files": [], "accepted_unique_pdf_pages": 0}
        self._page_hashes = set()

    def _sanitize_metadata(self, metadata):
        cleaned = {}
        for key, value in metadata.items():
            key = {"manufacturer": "make", "engine_code": "engine"}.get(key, key)
            if value is None:
                continue
            if isinstance(value, (list, dict)):
                if key in {"make", "model", "engine"}:
                    raise ValueError("Vehicle applicability must use scalar values")
                value = json.dumps(value, ensure_ascii=False, sort_keys=True)
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(f"Unsupported metadata value for {key}")
            cleaned[key] = value
        for key in ("make", "model", "engine"):
            if key in cleaned:
                cleaned[key] = canonical_vehicle_value(cleaned[key])
        make = cleaned.get("make", "")
        if make.startswith("generic") or make in {"all", "universal"}:
            cleaned.pop("make", None)
            cleaned["scope"] = "generic"
        else:
            cleaned.setdefault("scope", "vehicle" if make else "unknown")
        years = re.findall(r"\b(?:19|20)\d{2}\b", str(cleaned.get("year_range", "")))
        if years:
            cleaned["year_start"], cleaned["year_end"] = int(years[0]), int(years[-1])
        if "year" in cleaned:
            cleaned["year_start"] = cleaned["year_end"] = int(cleaned.pop("year"))
        cleaned.setdefault("year_start", 0)
        cleaned.setdefault("year_end", 9999)
        if cleaned["year_start"] > cleaned["year_end"]:
            raise ValueError("Year bounds are reversed")
        engines = metadata.get("affected_engines", [])
        if "engine" in cleaned:
            # Source notes also encode multiple engines as K20_K24 or a code plus description.
            codes = re.findall(r"\b[NMBSK]\d{2}[A-Z0-9]*\b", cleaned["engine"].replace("_", " "), re.I)
            engines = codes or [cleaned["engine"]]
        if engines:
            if not isinstance(engines, list) or not all(isinstance(value, str) and value.strip() for value in engines):
                raise ValueError("Engine options require a list of nonempty strings")
            options = sorted({canonical_vehicle_value(value) for value in engines})
            cleaned["engine_options"] = json.dumps(options)
            cleaned["engine"] = options[0] if len(options) == 1 else ""
        if cleaned["scope"] == "generic" and (any(cleaned.get(key) for key in ("make", "model", "engine", "engine_options"))
                or cleaned["year_start"] != 0 or cleaned["year_end"] != 9999):
            raise ValueError("A generic source cannot have restricted vehicle applicability")
        return cleaned

    def _extract_metadata(self, content, path):
        metadata = {}
        match = re.search(r"```json\s*\n(\{.*?\})\s*\n```", content, re.DOTALL)
        if match:
            metadata.update(json.loads(match.group(1)))
        sidecar = path.with_suffix(path.suffix + ".metadata.json")
        if sidecar.exists():
            metadata.update(json.loads(sidecar.read_text(encoding="utf-8")))
        if not metadata.get("make") and not metadata.get("manufacturer"):
            match = re.search(r"\b(BMW|Honda|Toyota|Ford|VW|Audi|Mercedes|Nissan|Mazda)\b", path.stem.replace("_", " "), re.IGNORECASE)
            if match:
                metadata["make"] = match.group(1)
        for key in ("make", "model", "engine"):
            match = re.search(r"\*\*" + key + r"(?:[^*]*)\*\*:?\s*([^\n]+)", content, re.IGNORECASE)
            if key not in metadata and match:
                metadata[key] = match.group(1).strip()
        return self._sanitize_metadata(metadata)

    @staticmethod
    def _get_folder_name(path):
        return next((part for part in path.parts if re.match(r"^\d{2}_", part)), "unknown")

    def _chunk_by_sections(self, content, path, metadata):
        # Keep short sections whole; bound oversized sections without changing their text.
        sections = re.split(r"\n(?=##\s)", content)
        packed, pending = [], ""
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if pending and len(pending) + len(section) + 2 > self.chunk_size:
                packed.append(pending)
                pending = ""
            if len(section) > self.chunk_size:
                if pending:
                    packed.append(pending)
                    pending = ""
                step = self.chunk_size - self.chunk_overlap
                for start in range(0, len(section), step):
                    packed.append(section[start:start + self.chunk_size])
                    if start + self.chunk_size >= len(section):
                        break
            else:
                pending = pending + "\n\n" + section if pending else section
        if pending:
            packed.append(pending)
        chunks = []
        for index, text in enumerate(packed):
            identifier = hashlib.sha256((metadata["source_id"] + metadata["document_hash"] + str(metadata["location"]) + str(index) + text).encode()).hexdigest()
            title = re.search(r"^#{1,6}\s+(.+)", text, re.MULTILINE)
            tags = {**metadata, "chunk_index": index, "chunk_id": identifier}
            if title:
                tags["section_title"] = title.group(1)
            chunks.append(DocumentChunk(text, tags, identifier, str(path)))
        return chunks

    def process_document(self, path, base_dir=None):
        path = Path(path)
        base_dir = Path(base_dir or path.parent)
        relative = path.relative_to(base_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        record = {"path": relative, "hash": digest, "format": path.suffix.lower(),
                  "physical_pages": None, "accepted_pages": 0}
        try:
            blocks = []
            if path.suffix.lower() == ".md":
                content = path.read_text(encoding="utf-8")
                blocks = [("document", re.sub(r"```json\s*\n\{.*?\}\s*\n```", "", content, flags=re.DOTALL))]
            elif path.suffix.lower() == ".pdf":
                from pypdf import PdfReader
                reader = PdfReader(path)
                record["physical_pages"] = len(reader.pages)
                record.update({"pages": [], "quarantined_pages": 0})
                for page, value in enumerate(reader.pages, 1):
                    text = value.extract_text() or ""
                    provenance = {"page": page, "location": f"page {page}",
                                  "extraction_method": "text", "status": "accepted"}
                    record["pages"].append(provenance)
                    if not text.strip():
                        if not self.ocr_enabled:
                            provenance.update({"status": "rejected", "reason": "OCR disabled"})
                            raise ValueError(f"Page {page} needs OCR; text-only ingestion does not accept it (set OCR_ENABLED=true after provisioning local models)")
                        from .ocr import OfflineOCR, OCR_ENGINE
                        provenance.update({"extraction_method": "OCR", "ocr_engine": OCR_ENGINE,
                                           "ocr_min_confidence": self.ocr_min_confidence})
                        try:
                            if self._ocr is None:
                                self._ocr = OfflineOCR(self.ocr_model_dir)
                            text, confidence = self._ocr.read_page(path, page - 1)
                        except Exception as exc:
                            provenance.update({"status": "rejected", "reason": str(exc)})
                            raise
                        provenance["ocr_confidence"] = confidence
                        if not text.strip() or confidence < self.ocr_min_confidence:
                            provenance.update({"status": "quarantined", "review_required": True,
                                               "text": text, "reason": "No readable OCR text" if not text.strip()
                                               else "OCR confidence below review threshold"})
                            record["quarantined_pages"] += 1
                            continue
                    blocks.append((f"page {page}", text))
                content = "\n".join(text for _, text in blocks)
            elif path.suffix.lower() == ".docx":
                from docx import Document
                from docx.text.paragraph import Paragraph
                parts = []
                for index, block in enumerate(Document(path).iter_inner_content(), 1):
                    if isinstance(block, Paragraph):
                        text = block.text
                        if block.style and block.style.name.startswith("Heading"):
                            text = "## " + text
                    else:
                        text = "\n".join(" | ".join(cell.text for cell in row.cells) for row in block.rows)
                    if text.strip():
                        parts.append(f"[Block {index}]\n{text}")
                content = "\n\n".join(parts)
                blocks = [("DOCX blocks", content)]
            else:
                raise ValueError("Unsupported document type")
            if not content.strip():
                if record.get("quarantined_pages"):
                    record.update({"status": "quarantined", "chunks": 0})
                    self.manifest["files"].append(record)
                    return []
                raise ValueError("Document has no usable text")
            tags = self._extract_metadata(content, path)
            sidecar = path.with_suffix(path.suffix + ".metadata.json")
            record["metadata_hash"] = hashlib.sha256(json.dumps(tags, sort_keys=True).encode()).hexdigest()
            record["sidecar_hash"] = hashlib.sha256(sidecar.read_bytes()).hexdigest() if sidecar.exists() else None
            tags.update({"source_file": relative, "source_id": hashlib.sha256(relative.encode()).hexdigest(),
                         "document_hash": digest, "filename": path.name, "folder": self._get_folder_name(path)})
            tags.setdefault("language", "ja" if re.search(r"[\u3040-\u30ff]", content) else "zh" if re.search(r"[\u4e00-\u9fff]", content) else "en")
            chunks = []
            page_records = {row["location"]: row for row in record.get("pages", [])}
            for location, text in blocks:
                page_tags = {}
                if path.suffix.lower() == ".pdf":
                    page_tags = {key: value for key, value in page_records[location].items()
                                 if key not in {"status", "location"}}
                    page_tags["language"] = "ja" if re.search(r"[\u3040-\u30ff]", text) else "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"
                chunks.extend(self._chunk_by_sections(text, path, {**tags, **page_tags, "location": location}))
            if path.suffix.lower() == ".pdf":
                for _, text in blocks:
                    page_hash = hashlib.sha256(re.sub(r"\s+", " ", text).strip().encode()).hexdigest()
                    if page_hash not in self._page_hashes:
                        self._page_hashes.add(page_hash)
                        self.manifest["accepted_unique_pdf_pages"] += 1
                record["accepted_pages"] = len(blocks)
            record.update({"chunks": len(chunks), "language": tags["language"],
                           "status": "partially_quarantined" if record.get("quarantined_pages") else "accepted"})
            self.manifest["files"].append(record)
            return chunks
        except Exception as exc:
            record.update({"status": "rejected", "error": str(exc)})
            self.manifest["files"].append(record)
            raise

    def process_markdown_file(self, path):
        return self.process_document(path)

    def process_knowledge_base(self, kb_path):
        kb_path = Path(kb_path)
        self.manifest = {"files": [], "accepted_unique_pdf_pages": 0}
        self._page_hashes = set()
        chunks, errors = [], []
        for path in sorted(kb_path.rglob("*")):
            if path.suffix.lower() not in {".md", ".pdf", ".docx"} or path.name == "README.md":
                continue
            try:
                chunks.extend(self.process_document(path, kb_path))
            except Exception as exc:
                errors.append(f"{path.name}: {exc}")
        if errors:
            raise ValueError("Ingestion rejected documents: " + "; ".join(errors))
        return chunks


def main():
    import argparse
    from .config import Config
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-base", type=Path, default=Config.KNOWLEDGE_BASE_DIR)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    processor = DocumentProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    try:
        chunks = processor.process_knowledge_base(args.knowledge_base)
        print(f"Processed {len(chunks)} chunks")
    finally:
        args.manifest.write_text(json.dumps(processor.manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
