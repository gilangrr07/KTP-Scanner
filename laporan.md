# Laporan Sistem Ekstraksi Data KTP (OpenCV + RapidOCR + Flask)

## 1. Alur Sistem

Sistem ini memproses gambar KTP yang diunggah pengguna untuk mengekstrak informasi teks secara otomatis dan mengisi formulir. Alur sistem secara keseluruhan adalah sebagai berikut:

```text
Input Gambar KTP
        │
        ▼
Image Acquisition (Mengambil gambar dari pengguna)
        │
        ▼
Image Preprocessing (OpenCV)
        │
        ├── Gaussian Blur
        ├── Grayscale
        ├── CLAHE
        └── Adaptive Threshold
        │
        ▼
RapidOCR
        │
        ├── Text Detection
        ├── Angle Classification
        └── Text Recognition
        │
        ▼
Parser
        │
        ▼
Auto Fill Form
```

---

## 2. Metode Pengolahan Citra (Image Preprocessing)

Pengolahan citra dilakukan sebelum gambar masuk ke tahap OCR. Tujuannya adalah untuk meningkatkan kualitas gambar agar OCR dapat membaca teks dengan tingkat akurasi yang lebih tinggi. Pengolahan citra pada dasarnya adalah proses matematika yang dilakukan pada matriks piksel.

Berikut adalah tahapan, metode pengolahan citra, beserta contoh perhitungannya:

### A. Grayscale
* **Tujuan**: Menyederhanakan citra dari tiga kanal warna (RGB) menjadi satu kanal intensitas (keabuan) agar proses komputasi lebih ringan.
* **Contoh Perhitungan**:
  Misalkan ada satu piksel berwarna dengan nilai:
  ```text
  R = 120
  G = 180
  B = 240
  ```
  Grayscale dihitung menggunakan rumus: `Gray = 0.299(R) + 0.587(G) + 0.114(B)`
  Substitusi angkanya:
  ```text
  Gray = 0.299(120) + 0.587(180) + 0.114(240)
       = 35.88 + 105.66 + 27.36
       = 168.9
  ```
  Dibulatkan menjadi **169**. 
  Artinya piksel RGB `(120, 180, 240)` berubah menjadi intensitas tunggal `169`. Gambar kini tidak memiliki warna lagi.

### B. Gaussian Blur
* **Tujuan**: Mengurangi noise atau gangguan pada gambar yang biasanya berasal dari sensor kamera, pencahayaan, atau kompresi gambar.
* **Contoh Perhitungan**:
  Gaussian Blur bekerja menggunakan kernel (matriks bobot). Misalnya menggunakan kernel 3x3:
  ```text
  1  2  1
  2  4  2
  1  2  1
  ```
  Jumlah seluruh bobot angka = 16.
  Misalkan intensitas piksel pada gambar di area tersebut adalah:
  ```text
  120  125  130
  124  150  128
  121  126  129
  ```
  Perhitungan rata-rata berbobotnya:
  ```text
  (120×1) + (125×2) + (130×1) +
  (124×2) + (150×4) + (128×2) +
  (121×1) + (126×2) + (129×1) = 2108
  ```
  Karena total bobot kernel adalah 16, maka: `2108 ÷ 16 = 131.75` (dibulatkan menjadi **132**).
  Artinya, piksel tengah yang tadinya **150** berubah menjadi **132**. Hasilnya gambar menjadi lebih halus dan *noise* berkurang.

### C. CLAHE (Contrast Limited Adaptive Histogram Equalization)
* **Tujuan**: Meningkatkan kontras gambar secara lokal agar tulisan yang redup menjadi lebih jelas tanpa membuat area terang menjadi terlalu *overexposed*.
* **Cara Kerja & Contoh Logika**:
  Misalnya terdapat sekumpulan piksel gelap di sebuah blok gambar dengan intensitas: `50, 52, 53, 55, 56, 57, 58, 59`.
  Histogram awalnya menumpuk di area gelap:
  ```text
  50 ███
  51 
  52 ███
  53 ██
  54 
  55 ███
  56 ██
  ```
  CLAHE akan menyebarkan rentang histogram ini (menjadi misal `20, 60, 100, 140, 180, 220`), sehingga rentang intensitas melebar dan tulisan menjadi jauh lebih kontras.
  Berbeda dengan Histogram Equalization biasa, CLAHE membagi gambar menjadi beberapa blok kecil (*tile*), meningkatkan kontras pada tiap blok, lalu membatasi peningkatan tersebut agar *noise* tidak diperkuat secara berlebihan (*Contrast Limited*).

### D. Adaptive Threshold
* **Tujuan**: Mengubah gambar grayscale menjadi gambar biner (hanya hitam atau putih), sehingga teks terpisah dari latar belakang (*background*).
* **Contoh Perhitungan**:
  Misalkan terdapat sederet piksel: `120, 122, 118, 119, 123`.
  Pada area tersebut, rata-rata lingkungan adalah `120`. Nilai Threshold (ambang batas) dihitung dari rata-rata lingkungan dikurangi sebuah konstanta (misal 5):
  `Threshold = 120 - 5 = 115`.
  Maka, setiap piksel dievaluasi:
  * `120 > 115` → Putih (255)
  * `90 < 115` → Hitam (0)
  
  Hasil akhirnya, kumpulan piksel `[128, 120, 132, 100, 110]` bisa berubah menjadi `[255, 255, 255, 0, 0]`. Teks menjadi hitam sempurna di atas warna putih, sangat ideal untuk proses pembacaan OCR.

---

## 3. Implementasi Sistem dalam Kode

Kalau dosen bertanya: *"Tunjukkan di mana metode pengolahan citra diterapkan di kode,"* berikut adalah pemetaan alur dan letak kodenya:

### 1. `app.py`
Ini adalah **controller** yang mengatur seluruh alur aplikasi.
* **Bagian Upload**: Sistem menerima gambar KTP yang diupload oleh pengguna. Gambar kemudian disimpan ke folder `uploads` agar dapat diproses lebih lanjut.
  ```python
  file = request.files["image"]
  file.save(upload_path)
  ```
* **Bagian Image Processing**: Sistem memanggil fungsi `process_image()` yang berada pada file `utils/preprocess.py`. Di sinilah seluruh proses pengolahan citra dilakukan.
  ```python
  process_result = process_image(
      upload_path,
      app.config["PROCESSED_FOLDER"]
  )
  ```
* **OCR**: Setelah kualitas gambar ditingkatkan, gambar hasil preprocessing dikirim ke RapidOCR melalui fungsi `extract_text()`.
  ```python
  raw_text = extract_text(
      process_result["threshold"]
  )
  ```
* **Parser**: Hasil OCR diproses menggunakan parser untuk mengambil informasi penting seperti NIK, Nama, dan Alamat.
  ```python
  data = parse_ktp(raw_text)
  ```

### 2. `utils/preprocess.py`
Di sinilah letak **inti pengolahan citra**. Semua perhitungan matematis dilakukan menggunakan *library* OpenCV.
* **Membaca Gambar**: OpenCV membaca gambar KTP menjadi matriks piksel (misal `640 x 480 x 3` RGB).
  ```python
  image = cv2.imread(image_path)
  ```
* **Gaussian Blur**: Mengurangi noise sebelum masuk ke OCR.
  ```python
  blur = cv2.GaussianBlur(image, (5,5), 0)
  ```
* **Grayscale**: Mengubah RGB menjadi grayscale.
  ```python
  gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
  ```
* **CLAHE**: Meningkatkan kontras lokal.
  ```python
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
  ```
* **Adaptive Threshold**: Mengubah gambar grayscale menjadi hitam-putih.
  ```python
  threshold = cv2.adaptiveThreshold(...)
  ```
Setiap tahapan disimpan (misal menggunakan `cv2.imwrite(...)`) sehingga di website bisa memunculkan visualisasi progres (Original, Blur, Gray, CLAHE, Threshold).

### 3. `utils/ocr.py`
Di sini **RapidOCR** dijalankan.
```python
engine(...) # atau ocr(...)
```
RapidOCR tidak menggunakan rumus sederhana seperti Gaussian Blur, melainkan **model Deep Learning** yang sudah dilatih (CNN + LSTM). Tahapannya:
1. *Text Detection*
2. *Angle Classification*
3. *Text Recognition*
Outputnya berupa **Raw Text** (misal: `NIK 3274100101010001`).

### 4. `utils/parser.py`
Parser mengubah **Raw Text** menjadi **Dictionary**.
Misalnya `NIK 327410...` diubah menjadi:
```python
{
    "nik": "3274100101010001",
    "nama": "Budi"
}
```
Parser menggunakan **Regular Expression (Regex)** dan **Keyword Matching** untuk mencari informasi penting tersebut.

### 5. `static/js/script.js`
Ini adalah *frontend* yang terhubung dengan *backend* Flask.
* **Upload**: Mengirim gambar ke server via URL endpoint.
  ```javascript
  fetch("/scan")
  ```
* **Progress**: Menampilkan animasi tahapan proses agar interaktif.
  ```javascript
  setProgress()
  ```
* **Auto Fill**: Mengisi seluruh elemen form secara otomatis menggunakan data hasil parser sehingga pengguna tidak perlu mengetik ulang data KTP.
  ```javascript
  fillForm(result.data)
  ```
