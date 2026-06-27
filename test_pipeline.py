import sys
import json

sys.path.append('c:\\Users\\VICTUS\\Ktp_scanner')

from utils.preprocess import process_image
from utils.ocr import extract_text
from utils.parser import parse_ktp

def test_pipeline():
    image_path = 'c:\\Users\\VICTUS\\Ktp_scanner\\uploads\\WhatsApp_Image_2026-06-27_at_19.57.12.jpeg'
    output_folder = 'c:\\Users\\VICTUS\\Ktp_scanner\\processed'
    
    print("1. Processing Image (with Auto-Crop)...")
    res = process_image(image_path, output_folder)
    
    print("2. Extracting Text (RapidOCR - Dual Pass)...")
    
    # Pass 1: Original (untuk NIK)
    text_original = extract_text(res['original'])
    print("--- OCR ORIGINAL ---")
    print(text_original.encode('cp1252', errors='replace').decode('cp1252'))
    
    # Pass 2: CLAHE (untuk teks lainnya)
    text_clahe = extract_text(res['clahe'])
    print("--- OCR CLAHE ---")
    print(text_clahe.encode('cp1252', errors='replace').decode('cp1252'))
    
    # Gabungkan
    text = text_original + "\n" + text_clahe
    print("--------------------")
    
    print("3. Parsing KTP...")
    data = parse_ktp(text)
    print("--- PARSER RESULT ---")
    print(json.dumps(data, indent=2, ensure_ascii=False).encode('cp1252', errors='replace').decode('cp1252'))
    print("---------------------")

if __name__ == '__main__':
    test_pipeline()
