import sys
import cv2
import re

sys.path.append('c:\\Users\\VICTUS\\Ktp_scanner')
from utils.ocr import extract_text

def clean_nik(text):
    t = text.upper()
    t = t.replace('O', '0').replace('L', '1').replace('I', '1').replace('S', '5').replace('Z', '2').replace('B', '8')
    return re.sub(r'\D', '', t)

def test_preprocessing(image_path):
    orig = cv2.imread(image_path)
    
    # Try different widths and blurs
    for width in [1000, 1500, 2000, orig.shape[1]]:
        scale = width / orig.shape[1]
        height = int(orig.shape[0] * scale)
        img_resized = cv2.resize(orig, (width, height), interpolation=cv2.INTER_CUBIC)
        
        for blur_k in [None, (3,3), (5,5)]:
            if blur_k:
                blur = cv2.GaussianBlur(img_resized, blur_k, 0)
            else:
                blur = img_resized
                
            gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            clahe_img = clahe.apply(gray)
            
            # Save temporary file for easyocr
            tmp_path = 'c:\\Users\\VICTUS\\Ktp_scanner\\processed\\tmp_test.jpg'
            cv2.imwrite(tmp_path, clahe_img)
            
            text = extract_text(tmp_path)
            
            # Find NIK and Name heuristically
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            nik = ""
            name = ""
            for i, line in enumerate(lines):
                if len(clean_nik(line)) >= 16:
                    nik = clean_nik(line)[:16]
                    if i + 1 < len(lines):
                        name = lines[i+1]
                    break
            
            print(f"W={width}, Blur={blur_k} => NIK: {nik}, Nama: {name}")

if __name__ == '__main__':
    test_preprocessing('c:\\Users\\VICTUS\\Ktp_scanner\\uploads\\Screenshot_2026-06-27_103256.png')
