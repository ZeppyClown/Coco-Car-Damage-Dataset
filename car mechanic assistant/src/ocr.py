"""Offline RapidOCR / PP-OCRv6 small extraction for EN, ZH and JA scans."""
import hashlib
import math
from contextlib import closing
from pathlib import Path


MODEL_HASHES = {
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
    "ch_ppocr_mobile_v2.0_cls_mobile.onnx": "e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c",
}
OCR_ENGINE = "rapidocr-3.10.0/PP-OCRv6-small"


def page_result(result):
    texts = result.txts if result.txts is not None else ()
    scores = result.scores if result.scores is not None else ()
    if len(texts) != len(scores):
        raise ValueError("OCR returned an incomplete text/confidence result")
    if any(not isinstance(text, str) for text in texts):
        raise ValueError("OCR returned an invalid text result")
    if any(not math.isfinite(score) or not 0 <= score <= 1 for score in scores):
        raise ValueError("OCR returned an invalid confidence value")
    # One weak specification must not disappear inside a high page average.
    # shortcut: OCR emits lines, add layout extraction before claiming complex table relationships.
    return "\n".join(texts), float(min(scores)) if len(scores) else 0.0


class OfflineOCR:
    def __init__(self, model_dir):
        self.model_dir = Path(model_dir) if model_dir else None
        self.engine = None

    def _load_engine(self):
        try:
            from rapidocr import RapidOCR
            import onnxruntime
            import pypdfium2
        except ImportError as exc:
            raise ValueError(
                "Scanned PDF OCR needs optional Python packages; install the assistant requirements.txt in your virtualenv."
            ) from exc
        if self.model_dir is None:
            raise ValueError("OCR models are unavailable; set OCR_MODEL_DIR to the verified local models (see handoff/mechanic-ocr.md).")
        for name, digest in MODEL_HASHES.items():
            path = self.model_dir / name
            if not path.is_file():
                raise ValueError(f"OCR model {name} is unavailable in OCR_MODEL_DIR; provision models before running offline ingestion.")
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"OCR model checksum mismatch: {name}; restore the documented model.")
        # Verify the embedded vocabulary before RapidOCR can attempt a dictionary download.
        rec_path = self.model_dir / "PP-OCRv6_rec_small.onnx"
        session = onnxruntime.InferenceSession(str(rec_path), providers=["CPUExecutionProvider"])
        if "character" not in session.get_modelmeta().custom_metadata_map:
            raise ValueError("OCR recognition model has no embedded vocabulary; restore the documented model.")
        del session
        self.engine = RapidOCR(params={
            "Det.model_path": str(self.model_dir / "PP-OCRv6_det_small.onnx"),
            "Rec.model_path": str(rec_path),
            "Cls.model_path": str(self.model_dir / "ch_ppocr_mobile_v2.0_cls_mobile.onnx"),
            "Global.text_score": 0.0,
            "Global.log_level": "error",
        })

    def read_page(self, path, page_index):
        try:
            if self.engine is None:
                self._load_engine()
            import pypdfium2 as pdfium
            with pdfium.PdfDocument(path) as document:
                with closing(document[page_index]) as page:
                    width, height = page.get_size()
                    if width * height * (300 / 72) ** 2 > 20_000_000:
                        raise ValueError("OCR page exceeds the 20 megapixel rendering limit")
                    bitmap = page.render(scale=300 / 72)
                    try:
                        image = bitmap.to_pil().convert("RGB")
                    finally:
                        bitmap.close()
            try:
                return page_result(self.engine(image))
            finally:
                image.close()
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Could not read scanned PDF page {page_index + 1} with offline OCR: {exc}") from exc
