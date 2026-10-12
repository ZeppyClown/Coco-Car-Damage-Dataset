"""Author FICTIONAL raster PDFs; requires reportlab/Pillow and a local CJK font.

Run: CJK_FONT=/path/to/CJK-font.ttf python tests/fixtures/ocr/generate.py
No company documents or downloaded catalogues are used.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab import rl_config
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).parent
TEXT = {
    "en": ["FICTIONAL TEST MANUAL", "Torque: 42.5 Nm", "Engine: K24", "Fault: P0300", "Part: FX-1234"],
    "zh_s": ["FICTIONAL TEST MANUAL", "虚构维修测试", "扭矩: 42.5 Nm", "发动机: K24", "故障码: P0300", "零件: FX-1234"],
    "zh_t": ["FICTIONAL TEST MANUAL", "虛構維修測試", "扭矩: 42.5 Nm", "發動機: K24", "故障碼: P0300", "零件: FX-1234"],
    "ja": ["FICTIONAL TEST MANUAL", "架空の整備テスト", "トルク: 42.5 Nm", "エンジン: K24", "故障コード: P0300", "部品: FX-1234"],
}


def scan(lines, font):
    image = Image.new("RGB", (1400, 850), "white")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((80, 70 + 100 * i), line, fill="black", font=font)
    return image


def raster_page(canvas, image):
    canvas.drawImage(ImageReader(image), 0, 0, width=504, height=306)
    canvas.showPage()


def main():
    rl_config.useA85 = False
    font = ImageFont.truetype(os.environ["CJK_FONT"], 48)
    for language, lines in TEXT.items():
        canvas = Canvas(str(ROOT / f"fictional_{language}.pdf"), pagesize=(504, 306), invariant=1)
        raster_page(canvas, scan(lines, font))
        canvas.save()
    canvas = Canvas(str(ROOT / "fictional_mixed.pdf"), pagesize=(504, 306), invariant=1)
    canvas.setFont("Helvetica", 14)
    canvas.drawString(25, 260, "FICTIONAL text page: Torque 12 Nm; Engine K20; Fault P0420")
    canvas.showPage()
    raster_page(canvas, scan(TEXT["en"], font))
    # Destroy all glyph detail, leaving an intentionally unreadable image-only page.
    unreadable = scan(TEXT["en"], font).resize((14, 8)).resize((1400, 850))
    raster_page(canvas, unreadable)
    canvas.save()
    canvas = Canvas(str(ROOT / "fictional_unreadable.pdf"), pagesize=(504, 306), invariant=1)
    raster_page(canvas, unreadable)
    canvas.save()
    image = scan(["FICTIONAL LAYOUT TEST", "Torque range: 40-45 Nm", "Fault: P0300", "* Cold engine only"], font)
    draw = ImageDraw.Draw(image)
    draw.text((810, 270), "K24", font=font, fill="black")
    draw.text((810, 370), "FX-1234", font=font, fill="black")
    draw.rectangle((55, 250, 1320, 450), outline="black", width=3)
    draw.line((770, 250, 770, 450), fill="black", width=3)
    canvas = Canvas(str(ROOT / "fictional_layout.pdf"), pagesize=(504, 306), invariant=1)
    raster_page(canvas, image)
    canvas.save()
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    writer.add_page(PdfReader(ROOT / "fictional_en.pdf").pages[0].rotate(90))
    with (ROOT / "fictional_rotated.pdf").open("wb") as file:
        writer.write(file)


if __name__ == "__main__":
    main()
