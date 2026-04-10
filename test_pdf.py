import pdfplumber

def read_pdf_sample(pdf_path):
    print(f"--- Reading {pdf_path} ---")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                print("PAGE 1 TEXT:")
                print(pdf.pages[0].extract_text())
                if len(pdf.pages) > 1:
                    print("PAGE 2 TEXT:")
                    print(pdf.pages[1].extract_text()[:1000])
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

if __name__ == "__main__":
    read_pdf_sample("data/raw/2368.pdf")
    read_pdf_sample("data/raw/confuseddrugnames(02.2015).pdf")
