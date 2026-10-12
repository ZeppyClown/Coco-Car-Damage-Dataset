"""Offline OCR checks against authored FICTIONAL raster manuals only."""
import json
import os
from pathlib import Path
import socket
import sys
from types import SimpleNamespace

import pytest

ASSISTANT = Path(__file__).resolve().parents[2] / "car mechanic assistant"
sys.path.insert(0, str(ASSISTANT))
from src.config import Config
from src.document_processor import DocumentProcessor

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "ocr"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("OCR tests must never access the network")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(Config, "OCR_ENABLED", False)


def stub_ocr(monkeypatch, results):
    from src.ocr import OfflineOCR
    calls = []
    def read(self, path, page_index):
        calls.append(page_index)
        return results[page_index]
    monkeypatch.setattr(OfflineOCR, "read_page", read)
    return calls


def test_ocr_off_by_default_and_records_rejection(monkeypatch):
    from src.ocr import OfflineOCR
    monkeypatch.setattr(OfflineOCR, "read_page", lambda *args: pytest.fail("OCR is disabled"))
    processor = DocumentProcessor()
    with pytest.raises(ValueError, match="needs OCR"):
        processor.process_document(FIXTURES / "fictional_en.pdf")
    assert processor.manifest["files"][0]["status"] == "rejected"
    assert processor.manifest["accepted_unique_pdf_pages"] == 0


def test_config_enables_existing_callers(monkeypatch):
    monkeypatch.setattr(Config, "OCR_ENABLED", True)
    monkeypatch.setattr(Config, "OCR_MIN_CONFIDENCE", 0.95)
    calls = stub_ocr(monkeypatch, {0: ("Torque: 42.5 Nm; K24; P0300", 0.96)})
    chunks = DocumentProcessor().process_document(FIXTURES / "fictional_en.pdf")
    assert calls == [0] and chunks[0].metadata["extraction_method"] == "OCR"


def test_mixed_pages_quarantine_and_preserve_exact_technical_text(monkeypatch):
    raw = "FICTIONAL\nTorque: 42.5\u00a0N·m; range 40–45 Nm\nK24 P0300 FX-1234"
    calls = stub_ocr(monkeypatch, {1: (raw, 0.97), 2: ("Unclear: 4?.5 Nm P03?0", 0.4)})
    processor = DocumentProcessor(ocr_enabled=True)
    chunks = processor.process_document(FIXTURES / "fictional_mixed.pdf")
    assert calls == [1, 2] and len(chunks) == 2 and chunks[1].content == raw
    assert chunks[0].metadata["extraction_method"] == "text"
    assert chunks[1].metadata["extraction_method"] == "OCR"
    assert chunks[1].metadata["ocr_confidence"] == 0.97
    assert chunks[1].metadata["location"] == "page 2"
    assert chunks[1].metadata["document_hash"]
    record = processor.manifest["files"][0]
    assert record["status"] == "partially_quarantined"
    assert record["physical_pages"] == 3 and record["accepted_pages"] == 2
    assert record["quarantined_pages"] == 1
    page = record["pages"][2]
    assert page["status"] == "quarantined" and page["review_required"]
    assert page["ocr_confidence"] == 0.4 and "4?.5" in page["text"]
    assert page["extraction_method"] == "OCR"
    assert processor.manifest["accepted_unique_pdf_pages"] == 2
    json.dumps(processor.manifest, allow_nan=False)


def test_entirely_quarantined_document_returns_no_chunks(monkeypatch):
    stub_ocr(monkeypatch, {0: ("", 0.0)})
    processor = DocumentProcessor(ocr_enabled=True)
    assert processor.process_document(FIXTURES / "fictional_unreadable.pdf") == []
    record = processor.manifest["files"][0]
    assert record["status"] == "quarantined" and record["accepted_pages"] == 0
    assert record["quarantined_pages"] == 1
    assert processor.manifest["accepted_unique_pdf_pages"] == 0


def test_quarantine_cannot_reach_embeddings(tmp_path, monkeypatch):
    from src.vector_store import VectorStore
    class TestEmbeddings:
        model = "fictional-ocr-test"
        dimensions = 3
        def embed_batch(self, texts, **kwargs):
            assert all("Unclear" not in text for text in texts)
            return [[1., 0., 0.] for _ in texts]
    stub_ocr(monkeypatch, {1: ("FICTIONAL Torque: 42.5 Nm K24 P0300", 0.98),
                           2: ("Unclear torque", 0.2)})
    chunks = DocumentProcessor(ocr_enabled=True).process_document(FIXTURES / "fictional_mixed.pdf")
    store = VectorStore(tmp_path / "index", embeddings=TestEmbeddings())
    store.add_documents(chunks)
    assert store.collection.count() == 2
    assert {row["extraction_method"] for row in store.collection.get()["metadatas"]} == {"text", "OCR"}


@pytest.mark.parametrize("value", [-1, 0, 1.1, float("nan"), float("inf")])
def test_invalid_confidence_threshold(value):
    with pytest.raises(ValueError, match="confidence"):
        DocumentProcessor(ocr_enabled=True, ocr_min_confidence=value)


def test_missing_dependency_is_friendly_and_never_skips_pages(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "rapidocr", None)
    processor = DocumentProcessor(ocr_enabled=True, ocr_model_dir=tmp_path)
    with pytest.raises(ValueError, match="install.*requirements"):
        processor.process_document(FIXTURES / "fictional_en.pdf")
    record = processor.manifest["files"][0]
    assert record["status"] == "rejected" and record["accepted_pages"] == 0
    assert record["pages"][0]["status"] == "rejected"


def test_missing_models_is_friendly_and_offline(tmp_path):
    processor = DocumentProcessor(ocr_enabled=True, ocr_model_dir=tmp_path)
    with pytest.raises(ValueError, match="OCR_MODEL_DIR"):
        processor.process_document(FIXTURES / "fictional_en.pdf")


def test_model_checksum_mismatch_is_rejected(tmp_path):
    from src.ocr import MODEL_HASHES, OfflineOCR
    for name in MODEL_HASHES:
        (tmp_path / name).write_bytes(b"fictional invalid model")
    with pytest.raises(ValueError, match="checksum"):
        OfflineOCR(tmp_path).read_page(FIXTURES / "fictional_en.pdf", 0)


def test_minimum_line_score_includes_weak_specifications():
    from src.ocr import page_result
    assert page_result(SimpleNamespace(txts=("Heading", "42.5 Nm"), scores=(0.99, 0.3))) == ("Heading\n42.5 Nm", 0.3)
    assert page_result(SimpleNamespace(txts=None, scores=None)) == ("", 0.0)
    with pytest.raises(ValueError, match="confidence"):
        page_result(SimpleNamespace(txts=("42.5 Nm",), scores=(float("nan"),)))
    with pytest.raises(ValueError, match="result"):
        page_result(SimpleNamespace(txts=("42.5 Nm",), scores=()))


@pytest.fixture(scope="module")
def real_ocr():
    pytest.importorskip("rapidocr", reason="Offline OCR integration requires rapidocr")
    pytest.importorskip("pypdfium2", reason="Offline OCR integration requires pypdfium2")
    from src.ocr import MODEL_HASHES, OfflineOCR
    directory = os.getenv("OCR_TEST_MODEL_DIR")
    if not directory or not all((Path(directory) / name).is_file() for name in MODEL_HASHES):
        pytest.skip("Offline OCR models unavailable: provision verified PP-OCRv6 small models and set OCR_TEST_MODEL_DIR; no downloads during tests")
    return OfflineOCR(directory)


@pytest.mark.parametrize("language,expected", [("en", "Torque"), ("zh_s", "发动机"), ("zh_t", "發動機"), ("ja", "エンジン")])
def test_real_multilingual_raster_pdf(real_ocr, language, expected):
    processor = DocumentProcessor(ocr_enabled=True)
    processor._ocr = real_ocr
    chunks = processor.process_document(FIXTURES / f"fictional_{language}.pdf")
    content = "\n".join(chunk.content for chunk in chunks)
    assert expected in content
    assert "42.5 Nm" in content and "K24" in content and "P0300" in content and "FX-1234" in content
    assert "FICTIONAL" in content
    assert chunks[0].metadata["extraction_method"] == "OCR"
    assert chunks[0].metadata["ocr_confidence"] >= 0.90
    page = processor.manifest["files"][0]["pages"][0]
    assert page["extraction_method"] == "OCR" and page["status"] == "accepted"
    assert page["ocr_confidence"] == chunks[0].metadata["ocr_confidence"]
    assert chunks[0].metadata["language"] == ("zh" if language.startswith("zh") else language)


def test_real_mixed_and_unreadable_pages(real_ocr):
    processor = DocumentProcessor(ocr_enabled=True)
    processor._ocr = real_ocr
    chunks = processor.process_document(FIXTURES / "fictional_mixed.pdf")
    assert len(chunks) == 2
    assert "12 Nm" in chunks[0].content and "42.5 Nm" in chunks[1].content
    assert [c.metadata["location"] for c in chunks] == ["page 1", "page 2"]
    page = processor.manifest["files"][0]["pages"][2]
    assert page["status"] == "quarantined" and page["ocr_confidence"] < 0.90
    assert processor.process_document(FIXTURES / "fictional_unreadable.pdf") == []


@pytest.mark.parametrize("name,expected", [("rotated", "42.5 Nm"), ("layout", "40-45 Nm")])
def test_real_rotated_and_table_layout(real_ocr, name, expected):
    processor = DocumentProcessor(ocr_enabled=True)
    processor._ocr = real_ocr
    chunks = processor.process_document(FIXTURES / f"fictional_{name}.pdf")
    content = "\n".join(c.content for c in chunks)
    assert expected in content and "P0300" in content and "FX-1234" in content


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.pdf")), ids=lambda path: path.name)
def test_fixtures_really_are_image_only(path):
    from pypdf import PdfReader
    pages = PdfReader(path).pages
    scans = pages[1:] if path.name == "fictional_mixed.pdf" else pages
    assert all(not (page.extract_text() or "").strip() for page in scans)
    assert all(page.images for page in scans)


def test_threshold_boundary_and_duplicate_page_accounting(monkeypatch):
    stub_ocr(monkeypatch, {0: ("FICTIONAL 42.5 Nm K24 P0300", 0.90)})
    processor = DocumentProcessor(ocr_enabled=True)
    for _ in range(2):
        chunks = processor.process_document(FIXTURES / "fictional_en.pdf")
        assert len(chunks) == 1 and chunks[0].metadata["ocr_min_confidence"] == 0.90
    assert processor.manifest["accepted_unique_pdf_pages"] == 1


def test_enable_setting_requires_boolean():
    with pytest.raises(ValueError, match="boolean"):
        DocumentProcessor(ocr_enabled="false")


def test_ocr_engine_errors_do_not_skip_pages(monkeypatch):
    from src.ocr import OfflineOCR
    def failed(*args):
        raise RuntimeError("fictional engine failure")
    monkeypatch.setattr(OfflineOCR, "read_page", failed)
    processor = DocumentProcessor(ocr_enabled=True)
    with pytest.raises(RuntimeError, match="fictional engine failure"):
        processor.process_document(FIXTURES / "fictional_mixed.pdf")
    assert processor.manifest["files"][0]["status"] == "rejected"
    assert processor.manifest["files"][0]["pages"][1]["status"] == "rejected"
    assert processor.manifest["accepted_unique_pdf_pages"] == 0


def test_render_limit_fails_before_allocating_bitmap(monkeypatch):
    from src.ocr import OfflineOCR
    class OversizePage:
        def get_size(self):
            return 100_000, 100_000
        def close(self):
            pass
        def render(self, **kwargs):
            pytest.fail("Oversize page must fail before rendering")
    class Document:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def __getitem__(self, index):
            return OversizePage()
    import pypdfium2
    monkeypatch.setattr(pypdfium2, "PdfDocument", lambda path: Document())
    ocr = OfflineOCR(None)
    ocr.engine = lambda image: pytest.fail("Oversize page must fail before OCR")
    with pytest.raises(ValueError, match="rendering limit"):
        ocr.read_page(FIXTURES / "fictional_en.pdf", 0)
