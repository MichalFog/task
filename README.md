
# Attendance Variation Example

## איך להריץ
1. התקנת דרישות (מומלץ ליצור virtualenv):

```bash
pip install -r requirements.txt
```

2. ודאו ש-Tesseract OCR מותקן על המערכת ושמוספת ל-PATH. על Windows התקינו מה:
https://github.com/tesseract-ocr/tesseract

3. הרצת הקוד:

```bash
python main.py
```

4. קובץ התוצאה יווצר ב- `output_reports/sample_type_A_variation.pdf` (או נתיב שתעבירו ל-main)

הערות:

- הקוד משתמש ב-PyMuPDF + pytesseract כדי לתמוך בקבצי PDF סרוקים ולטקסטים.
- אם הדוחות בעברית התקינו גם את שפת Hebrew (heb) ל-Tesseract לקבלת תוצאות טובות יותר.
