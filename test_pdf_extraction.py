import pdfplumber

pdf_path = "First Mathematics Challenge 2023 Paper.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"--- Page {page_number + 1} ---")
        print(text)
        print("\n" + "="*50 + "\n")
