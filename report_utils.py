import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pandas as pd
from datetime import datetime

# Path ל־Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_report_type_from_df_header_row(df: pd.DataFrame) -> str:
    """
    מזהה את סוג הדו"ח לפי אם בכותרת העמודות (שורה עליונה של DF) מופיעה המילה "שבת".
    """
    # יוצרים מחרוזת אחת מכל שמות העמודות
    header_text = " ".join(df.columns.astype(str))
    if "שבת" in header_text:
        return "A"
    return "B"


def _render_page_to_image(pdf_path: str, page_number: int = 0, zoom: float = 3.0) -> Image.Image:
    """Render a PDF page to a high-resolution PIL Image for OCR."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def preprocess_image(img: Image.Image) -> Image.Image:
    """Grayscale + thresholding to improve OCR accuracy."""
    img = img.convert("L")  # grayscale
    img = img.point(lambda x: 0 if x < 200 else 255, '1')  # threshold
    return img


def ocr_pdf_first_page_text(pdf_path: str) -> str:
    """Run OCR on the first page and return the raw text."""
    img = _render_page_to_image(pdf_path)
    img = preprocess_image(img)
    text = pytesseract.image_to_string(img, lang='heb+eng')
    return text


def extract_table_from_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Extract attendance tables from the first page of a scanned PDF.
    Returns a DataFrame with date, start, end, hours, and raw OCR line.
    """
    text = ocr_pdf_first_page_text(pdf_path)
    print("==== OCR Text ====")
    print(text)  # בדיקה חזותית

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    data = []

    date_patterns = [r"\d{4}[\-/]\d{1,2}[\-/]\d{1,2}", r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}"]
    time_pattern = r"\b\d{1,2}[:.]\d{2}\b"
    hours_pattern = r"\d+[\.,]?\d*"

    for line in lines:
        # ניקוי תווים מיוחדים
        line_clean = line.replace('\u200e', ' ').replace('\u200f', ' ')
        line_clean = line_clean.replace('|', ':').replace('․', '.').replace('，', ',')
        line_clean = re.sub(r'[^\w\d:.,/]', ' ', line_clean)

        # חיפוש תאריך
        date_match = None
        for dp in date_patterns:
            m = re.search(dp, line_clean)
            if m:
                date_match = m.group(0)
                break
        if not date_match:
            continue

        # חיפוש שעות התחלה/סיום
        times = re.findall(time_pattern, line_clean)
        start = times[0].replace('.', ':') if len(times) >= 1 else ""
        end = times[1].replace('.', ':') if len(times) >= 2 else ""

        # חיפוש שעות עבודה ישירות
        hours = None
        try:
            after = line_clean.split(times[1], 1)[1] if len(times) >= 2 else ""
            h_m = re.findall(hours_pattern, after)
            if h_m:
                hours = float(h_m[0].replace(',', '.'))
        except Exception:
            hours = None

        # חישוב שעות אם לא נמצאו
        if hours is None or hours == 0:
            if start and end:
                try:
                    fmt = '%H:%M'
                    t0 = datetime.strptime(start, fmt)
                    t1 = datetime.strptime(end, fmt)
                    delta = (t1 - t0).seconds / 3600
                    if delta <= 0:
                        delta += 24
                    hours = round(delta, 2)
                except Exception:
                    hours = 0.0
            else:
                hours = 0.0

        data.append({
            "date": date_match,
            "start": start,
            "end": end,
            "hours": hours,
            "raw_line": line_clean
        })

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    pdf_file = "input_reports/sample_type_A.pdf"  # שנה לנתיב שלך
    df = extract_table_from_pdf(pdf_file)
    print("==== DataFrame ====")
    print(df)
