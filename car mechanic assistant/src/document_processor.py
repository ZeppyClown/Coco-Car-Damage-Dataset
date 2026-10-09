"""Markdown, text PDF and DOCX ingestion with source provenance."""
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
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Require 0 <= overlap < chunk size")
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
                for page, value in enumerate(reader.pages, 1):
                    text = value.extract_text() or ""
                    if not text.strip():
                        raise ValueError(f"Page {page} needs OCR; text-only ingestion does not accept it")
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
                raise ValueError("Document has no usable text")
            tags = self._extract_metadata(content, path)
            tags.update({"source_file": relative, "source_id": hashlib.sha256(relative.encode()).hexdigest(),
                         "document_hash": digest, "filename": path.name, "folder": self._get_folder_name(path)})
            tags.setdefault("language", "ja" if re.search(r"[\u3040-\u30ff]", content) else "zh" if re.search(r"[\u4e00-\u9fff]", content) else "en")
            chunks = []
            for location, text in blocks:
                chunks.extend(self._chunk_by_sections(text, path, {**tags, "location": location}))
            if path.suffix.lower() == ".pdf":
                for _, text in blocks:
                    page_hash = hashlib.sha256(re.sub(r"\s+", " ", text).strip().encode()).hexdigest()
                    if page_hash not in self._page_hashes:
                        self._page_hashes.add(page_hash)
                        self.manifest["accepted_unique_pdf_pages"] += 1
                record["accepted_pages"] = len(blocks)
            record.update({"chunks": len(chunks), "language": tags["language"], "status": "accepted"})
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
