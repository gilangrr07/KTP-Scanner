# 💳 KTP Scanner Indonesia

Sebuah aplikasi berbasis Web (Flask) pintar yang dirancang untuk mengekstrak data dari Kartu Tanda Penduduk (KTP) Indonesia secara otomatis menggunakan gabungan **Computer Vision (OpenCV)** dan **Optical Character Recognition (RapidOCR)**.

Sistem secara otomatis mendeteksi pindaian foto KTP, membersihkan distorsi gambar, membaca teks, merapikan hasil ejaan *(parser & typo heuristic)*, lalu menampilkannya sebagai *form identitas* *(Auto-fill JSON)* langsung di layar Anda.

---

## 🌟 Fitur Utama
- **⚡ Real-Time Auto-Fill:** Upload gambar KTP, dan semua data (NIK, Nama, Alamat, Gol. Darah, dll) akan terisi otomatis dalam hitungan detik secara *seamless* tanpa *refresh* (AJAX).
- **✂️ Auto-Crop KTP:** Mesin pemotong cerdas (berbasis kontur) otomatis mendeteksi ujung KTP dan membuang latar belakang (seperti meja/tangan) yang tak perlu sebelum diproses.
- **👁️ Dual-Pass OCR:** Membaca gambar menggunakan RapidOCR **dua kali** — satu pada citra asli (untuk resolusi optimal NIK) dan satu lagi pada citra yang sudah terfilter *CLAHE* (untuk kejelasan tulisan alamat kecil yang tertimpa *background* KTP).
- **🧠 Smart Parser:** Tidak sekadar mengekstrak huruf mati; aplikasi dilengkapi logika Heuristik Regex yang cerdas (contoh: otomatis meluruskan typo *"80G0R"* -> *"BOGOR"*, atau *"INM"* -> *"WNI"*).
- **🎨 Modern UI Dashboard:** Antarmuka estetik yang di-*support* dengan gaya animasi memukau, palet cantik Bootstrap 5, galeri pratinjau *Computer Vision Pipeline*, serta animasi transisi *loading*.

---

## 🛠️ Tech Stack
- **Bahasa Utama:** Python 3.11+
- **Backend Framework:** Flask
- **Computer Vision:** OpenCV (`opencv-python`)
- **Optical Character Recognition:** RapidOCR (`rapidocr-onnxruntime`)
- **Frontend:** HTML5, Vanilla JS (Fetch API), CSS3, Bootstrap 5

---

## ⚙️ Instalasi dan Cara Penggunaan

1. **Clone repository ini** (atau ekstrak ke dalam sebuah folder):
   ```bash
   git clone https://github.com/username/ktp-scanner.git
   cd ktp-scanner
   ```

2. **Install Dependensi:**
   Sangat direkomendasikan untuk menggunakan *virtual environment*.
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi:**
   ```bash
   python app.py
   ```

4. **Akses Dashboard Web:**
   Buka browser Anda dan navigasikan ke:
   ```
   http://127.0.0.1:5000
   ```

5. **Lakukan Pemindaian:**
   Klik tombol `Choose File` lalu pilih file foto KTP yang ingin di-*scan*. Klik `Scan KTP` dan saksikan form identitas terisi otomatis!

---

## 📁 Struktur Direktori
```text
Ktp_scanner/
│
├── app.py                  # Entry point (Backend Flask)
├── requirements.txt        # Daftar librari dependensi project
├── README.md               # Dokumentasi project (File ini)
├── laporan.md              # Laporan alur kerja rinci untuk developer
├── PROJECT_RULES.md        # Aturan kaku proyek dan guideline struktur kode
├── CLAUDE.md               # Ringkasan stack, arsitektur, dan visi proyek
│
├── static/                 # Folder aset statis
│   ├── css/style.css       # Kustomisasi UI Modern
│   └── js/script.js        # Logika AJAX dan interaktif Frontend
│
├── templates/
│   └── index.html          # Halaman UI Web
│
├── utils/                  # Core Business Logic & Algoritma
│   ├── preprocess.py       # Algoritma Computer Vision (OpenCV)
│   ├── ocr.py              # Wrapper RapidOCR Model
│   └── parser.py           # Otak heuristik Regex KTP
│
└── uploads/ & processed/   # Folder tembolok (otomatis dibuat sistem)
```

---

## 🧪 Pengujian Skrip (CLI)
Jika Anda hanya ingin mengeksekusi pipeline atau menguji seberapa kebal logika *parser* tanpa harus membuka *server* web, Anda bisa memanfaatkan skrip pengujian berbasis *terminal* yang kami sediakan:

```bash
python test_pipeline.py
```
*(Jangan lupa untuk mengubah path gambar di dalam file tersebut sesuai foto KTP lokal yang Anda tes).*

---

## 🤝 Lisensi
Project ini dibuat sebagai purwarupa (demo) implementasi e-KYC OCR di lingkungan Python. Dapat dipelajari, digunakan, dan dimodifikasi secara bebas untuk kebutuhan edukasi maupun pengembangan tahap mahir.

*— Built for accuracy, designed for speed.*
