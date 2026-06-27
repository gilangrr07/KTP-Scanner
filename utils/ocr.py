from rapidocr_onnxruntime import RapidOCR
import cv2

# ==========================================
# RapidOCR Reader (dibuat sekali)
# ==========================================

reader = RapidOCR()

# ==========================================
# OCR
# ==========================================

def extract_text(image_path):
    """
    Membaca teks dari gambar menggunakan RapidOCR
    """

    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Gagal membuka gambar OCR.")

    results, _ = reader(image)

    if not results:
        return ""

    # Urutkan berdasarkan posisi vertikal (y) lalu horizontal (x)
    # results format: [[bbox, text, confidence], ...]
    sorted_results = sorted(
        results,
        key=lambda r: (r[0][0][1], r[0][0][0])
    )

    lines = []
    prev_y = -999

    for item in sorted_results:
        bbox = item[0]
        text = item[1]
        y = bbox[0][1]

        # Jika baris baru (jarak vertikal cukup jauh)
        if abs(y - prev_y) > 10:
            lines.append(text)
        else:
            # Gabungkan ke baris sebelumnya
            if lines:
                lines[-1] += " " + text
            else:
                lines.append(text)

        prev_y = y

    raw_text = "\n".join(lines)

    return raw_text