import cv2
import os
import numpy as np


# =====================================
# Auto Crop KTP
# =====================================

def auto_crop_ktp(image):
    """
    Mendeteksi kontur persegi panjang KTP di dalam gambar
    dan memotongnya secara otomatis.
    Jika gagal mendeteksi, kembalikan gambar asli.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Dilate untuk menghubungkan garis yang terputus
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.dilate(edges, kernel, iterations=2)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return image

    # Cari kontur terbesar yang menyerupai persegi panjang
    image_area = image.shape[0] * image.shape[1]

    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(contour)

        # Kontur harus minimal 10% dari area gambar
        if area < image_area * 0.1:
            continue

        # Cek apakah kontur menyerupai persegi panjang
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4:
            # Ditemukan persegi panjang, crop
            x, y, w, h = cv2.boundingRect(approx)

            # Padding lebih besar agar NIK di atas tidak terpotong
            pad_x = 15
            pad_y = 35  # Lebih besar di atas untuk NIK
            x = max(0, x - pad_x)
            y = max(0, y - pad_y)
            w = min(image.shape[1] - x, w + 2 * pad_x)
            h = min(image.shape[0] - y, h + 2 * pad_y)

            cropped = image[y:y+h, x:x+w]
            return cropped

    # Fallback: gunakan bounding rect dari kontur terbesar
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    # Hanya crop jika area cukup besar
    if w * h > image_area * 0.1:
        pad_x = 15
        pad_y = 35
        x = max(0, x - pad_x)
        y = max(0, y - pad_y)
        w = min(image.shape[1] - x, w + 2 * pad_x)
        h = min(image.shape[0] - y, h + 2 * pad_y)
        return image[y:y+h, x:x+w]

    return image


def process_image(image_path, output_folder):
    """
    Preprocessing KTP
    Auto Crop
        ↓
    Original
        ↓
    Gaussian Blur
        ↓
    Grayscale
        ↓
    CLAHE
        ↓
    Adaptive Threshold
    """

    # =====================================
    # Load Image
    # =====================================

    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Gambar tidak dapat dibuka.")

    # =====================================
    # Auto Crop KTP
    # =====================================

    image = auto_crop_ktp(image)

    # =====================================
    # Resize
    # =====================================

    width = image.shape[1]
    if width > 2000:
        width = 2000

    scale = width / image.shape[1]
    height = int(image.shape[0] * scale)
    image = cv2.resize(image, (width, height))

    # =====================================
    # Save Original
    # =====================================

    original_path = os.path.join(output_folder, "original.jpg")
    cv2.imwrite(original_path, image)

    # =====================================
    # Gaussian Blur
    # =====================================

    # Kernel (5,5) terlalu kuat dan menghancurkan teks tipis. Gunakan (3,3)
    blur = cv2.GaussianBlur(
        image,
        (3, 3),
        0
    )

    blur_path = os.path.join(output_folder, "blur.jpg")
    cv2.imwrite(blur_path, blur)

    # =====================================
    # Grayscale
    # =====================================

    gray = cv2.cvtColor(
        blur,
        cv2.COLOR_BGR2GRAY
    )

    gray_path = os.path.join(output_folder, "gray.jpg")

    cv2.imwrite(gray_path, gray)

    # =====================================
    # CLAHE
    # =====================================

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    clahe_img = clahe.apply(gray)

    clahe_path = os.path.join(output_folder, "clahe.jpg")

    cv2.imwrite(clahe_path, clahe_img)

    # =====================================
    # Adaptive Threshold
    # =====================================

    threshold = cv2.adaptiveThreshold(
        clahe_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )

    threshold_path = os.path.join(output_folder, "threshold.jpg")

    cv2.imwrite(threshold_path, threshold)

    # =====================================
    # Return
    # =====================================

    return {

        "original": original_path.replace("\\", "/"),

        "blur": blur_path.replace("\\", "/"),

        "gray": gray_path.replace("\\", "/"),

        "clahe": clahe_path.replace("\\", "/"),

        "threshold": threshold_path.replace("\\", "/")

    }