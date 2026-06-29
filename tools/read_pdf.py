"""
read_pdf.py — PDF 預處理腳本，輸出 Markdown 純文字到 stdout
用法：python read_pdf.py <PDF路徑> [--mode auto|ocr|text] [--pages 1-5]
"""
import sys
import argparse
import io
import re

TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def find_tesseract():
    import os
    for p in TESSERACT_PATHS:
        if os.path.exists(p):
            return p
    return None


def extract_text_pdfplumber(path, page_range=None):
    import pdfplumber
    parts = []
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        if page_range:
            start, end = page_range
            pages = pdf.pages[start - 1:end]
        for i, page in enumerate(pages, 1):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            if tables:
                for table in tables:
                    md_rows = []
                    for j, row in enumerate(table):
                        cells = [str(c or "").replace("\n", " ") for c in row]
                        md_rows.append("| " + " | ".join(cells) + " |")
                        if j == 0:
                            md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
                    text += "\n\n" + "\n".join(md_rows)
            if text.strip():
                parts.append(f"<!-- Page {i} -->\n{text.strip()}")
    return "\n\n".join(parts)


def is_text_based(path, sample_pages=3):
    """用 PyMuPDF 快速偵測 PDF 是否含有可提取文字"""
    import fitz
    doc = fitz.open(path)
    total_chars = 0
    for i, page in enumerate(doc):
        if i >= sample_pages:
            break
        total_chars += len(page.get_text().strip())
    doc.close()
    return total_chars > 100


def extract_via_ocr(path, page_range=None, lang="chi_tra+eng"):
    """用 PyMuPDF 渲染頁面成圖片，再交給 Tesseract OCR"""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "[錯誤] 需要安裝 pytesseract 和 Pillow：pip install pytesseract Pillow"

    tess = find_tesseract()
    if not tess:
        return (
            "[錯誤] 未偵測到 Tesseract OCR。\n"
            "請至 https://github.com/UB-Mannheim/tesseract/wiki 下載安裝，\n"
            f"安裝後確認路徑為：{TESSERACT_PATHS[0]}"
        )
    pytesseract.pytesseract.tesseract_cmd = tess

    import fitz
    doc = fitz.open(path)
    pages = list(range(len(doc)))
    if page_range:
        start, end = page_range
        pages = list(range(start - 1, min(end, len(doc))))

    parts = []
    for i in pages:
        page = doc[i]
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang)
        if text.strip():
            parts.append(f"<!-- Page {i + 1} -->\n{text.strip()}")
    doc.close()
    return "\n\n".join(parts)


def clean_output(text):
    """移除頁碼雜訊、合併過多空行"""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def parse_pages(pages_str):
    if not pages_str:
        return None
    if "-" in pages_str:
        parts = pages_str.split("-")
        return int(parts[0]), int(parts[1])
    n = int(pages_str)
    return n, n


def main():
    parser = argparse.ArgumentParser(description="PDF 預處理：輸出 Markdown 文字")
    parser.add_argument("path", help="PDF 檔案路徑")
    parser.add_argument("--mode", choices=["auto", "text", "ocr"], default="auto",
                        help="auto=自動偵測, text=強制文字模式, ocr=強制 OCR 模式")
    parser.add_argument("--pages", help="頁碼範圍，例如 1-5 或 3")
    parser.add_argument("--lang", default="chi_tra+eng", help="OCR 語言（預設 chi_tra+eng）")
    args = parser.parse_args()

    page_range = parse_pages(args.pages)

    if args.mode == "ocr":
        result = extract_via_ocr(args.path, page_range, args.lang)
    elif args.mode == "text":
        result = extract_text_pdfplumber(args.path, page_range)
    else:
        if is_text_based(args.path):
            result = extract_text_pdfplumber(args.path, page_range)
        else:
            result = extract_via_ocr(args.path, page_range, args.lang)

    try:
        sys.stdout.buffer.write(clean_output(result).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except (BrokenPipeError, OSError):
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
