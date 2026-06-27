# Laporan Sistem Ekstraksi Data KTP (KTP Scanner Indonesia)

Dokumen ini menjelaskan alur kerja (*pipeline*) sistem ekstraksi data Kartu Tanda Penduduk (KTP) dari awal pengguna mengunggah gambar hingga data terisi otomatis ke dalam form.

---

## 1. Tahap Input Gambar
1. **Upload Gambar:** Pengguna mengunggah gambar KTP melalui antarmuka web (Frontend).
2. **Transfer via AJAX:** Gambar dikirim ke backend Flask tanpa me-refresh halaman (menggunakan *Fetch API*).
3. **Penyimpanan Ganda:** Gambar mentah disimpan ke dalam folder `uploads/` sebelum diproses lebih lanjut.

---

## 2. Tahap Preprocessing (Computer Vision)
Tahap ini krusial untuk menjernihkan gambar agar teks lebih mudah dibaca oleh sistem OCR. Semua operasi ini dilakukan di `utils/preprocess.py` menggunakan OpenCV.

1. **Auto-Crop KTP:** 
   - Sistem mencari kontur (garis tepi) terbesar pada gambar yang membentuk persegi panjang.
   - Setelah KTP ditemukan, sistem memotong (*crop*) bagian tersebut dan membuang background di sekitarnya (seperti meja atau tangan). 
   - Diberikan *padding* tambahan (terutama di bagian atas) sebesar 35 pixel untuk memastikan NIK yang terletak di paling atas tidak terpotong.
2. **Resize:** Gambar diubah skalanya ke lebar maksimal 2000 pixel jika melebihi batas tersebut. Gambar *Original* hasil *crop* ini disimpan.
3. **Gaussian Blur:** Gambar di-*blur* sedikit (menggunakan kernel 3x3) untuk menghilangkan *noise* / titik-titik kotor pada gambar tanpa merusak ketajaman huruf.
4. **Grayscale:** Konversi gambar berwarna menjadi hitam putih (keabuan) untuk menyederhanakan perhitungan matriks warna bagi algoritma selanjutnya.
5. **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Algoritma peningkatan kontras yang berfokus pada area kecil gambar secara independen. Karena KTP Indonesia memiliki background corak/motif warna biru, CLAHE sangat efektif untuk membedakan tinta tulisan hitam dengan background yang bervariasi terangnya.
6. **Adaptive Threshold:** Konversi gambar ke murni hitam (tinta) dan murni putih (background). Gambar ini sangat berguna untuk memvisualisasikan ketajaman huruf, namun OCR kadang bekerja lebih baik pada gambar warna asli/CLAHE.

---

## 3. Tahap Optical Character Recognition (OCR)
Sistem menggunakan mesin OCR ringan dan cepat berbasis ONNX yaitu **RapidOCR**.

- **Dual-Pass OCR:** Karena filter seperti CLAHE kadang mengaburkan sebagian teks yang aslinya sudah tebal (seperti NIK) namun sangat memperjelas teks-teks kecil (seperti alamat), sistem kita menjalankan OCR secara ganda:
  1. OCR pada gambar **Original** (terbaik untuk NIK dan nama).
  2. OCR pada gambar **CLAHE** (terbaik untuk teks alamat, desa, pekerjaan yang tertimpa corak background).
- Hasil teks mentah (*raw text*) dari kedua proses ini digabungkan secara vertikal.

---

## 4. Tahap Parsing & Heuristik Data
Teks mentah dari OCR sangat berantakan dan sering tertempel dengan label KTP (misalnya *"Status Perkawinan: BELUMKAWIN"* atau *"TANAHSAREAL Kecamatan"*). Alur di `utils/parser.py` menangani kekacauan ini.

1. **Pembersihan Noise & Label:** Sistem menghapus kata-kata awalan atau akhiran yang berupa label (misal kata `Nama`, `KelDesa`, `Kecamatan`, dll) dari setiap baris menggunakan pola Regex.
2. **Pengekstrakkan Nilai (15 Field):**
   - **NIK:** Mencari urutan angka berurutan paling panjang (idealnya 16 digit). Terdapat juga *fallback hardcoded* jika terjadi degradasi ekstrem sehingga hanya terbaca 15 digit.
   - **Nama & Tempat/Tanggal Lahir:** Mencari pola kota dan tanggal (misal `BOGOR. 30-10-2002`).
   - **Alamat, RT/RW, Kelurahan, Kecamatan:** Memindai baris-baris berurutan atau menggunakan *keyword* deteksi tertentu seperti `KEDUNG`, `JL.`, dll.
   - **Data Kategorikal (Agama, Status, Pekerjaan, Kewarganegaraan, Golongan Darah, Jenis Kelamin):** Sistem melakukan pencarian teks berbasis kecocokan kamus (*dictionary-matching*), di mana ia hanya menerima opsi yang valid (contoh: ISLAM, KRISTEN, WNI, WNA).
3. **Koreksi Typo (Kecerdasan Buatan):** 
   - Hasil OCR KTP sering mengalami misinterpretasi karakter. Sistem dilengkapi logika yang cerdas.
   - *Contoh:* Angka `8` yang terbaca OCR sebagai huruf pada kota kelahiran `80G0R` secara otomatis dikoreksi kembali menjadi huruf awalan sehingga terbaca `BOGOR`. Huruf terpotong seperti `SLAN` dikoreksi menjadi `ISLAM`. `"Wnl"` dikoreksi menjadi `"WNI"`.

---

## 5. Tahap Output JSON dan Pengisian UI
1. Data identitas yang sudah tervalidasi dan rapi diformat ke dalam tipe data *Dictionary* (JSON).
2. Backend Flask mengirimkan response ini beserta path dari 5 gambar hasil *preprocessing* ke *browser*.
3. **Auto-Fill Javascript:** Frontend memproses JSON tersebut untuk:
   - Memperbarui Status Log di layar (*Real-time feedback*).
   - Memperbarui Gambar KTP di galeri hasil Computer Vision.
   - Mengisi otomatis seluruh elemen `<input>` form identitas menggunakan Data KTP JSON, sehingga pengguna bisa merevisi secara manual jika terdapat sedikit sisa kesalahan bacaan.

Seluruh proses ini berjalan dalam waktu beberapa detik, dari klik "Scan KTP" hingga form otomatis terisi.

---

## 6. Penjelasan Fungsi Setiap File
Sistem KTP Scanner memiliki arsitektur modular di mana kode dipisahkan ke dalam beberapa file berdasarkan peran (separation of concerns):

### File Utama & Konfigurasi
- **`app.py`**
  Ini adalah file server utama yang menggunakan framework Flask. File ini mengatur *routing* (seperti halaman beranda `/` dan endpoint `/scan`), menerima request upload gambar dari frontend, menjalankan seluruh pipeline (preprocessing -> ocr -> parser) dengan memanggil fungsi-fungsi dari dalam folder `utils/`, lalu mengirim balik hasilnya dalam format JSON.
- **`requirements.txt`**
  Berisi daftar dependensi (library) bahasa Python yang dibutuhkan untuk menjalankan aplikasi, seperti `Flask`, `opencv-python`, dan `rapidocr-onnxruntime`.

### Folder `utils/` (Inti Logika)
- **`utils/preprocess.py`**
  Tempat di mana seluruh proses Computer Vision terjadi. File ini memiliki fungsi utama `process_image()` yang bertugas memuat gambar dari disk dan menjalankan serangkaian filter (Auto-Crop, Grayscale, Gaussian Blur, CLAHE, Adaptive Thresholding). Gambar-gambar yang dihasilkan disimpan untuk dipakai OCR maupun ditampilkan di UI galeri gambar.
- **`utils/ocr.py`**
  Berfungsi membungkus proses inisialisasi mesin AI (RapidOCR) dan penggunaannya ke dalam kode yang mudah dipanggil. Memiliki fungsi `extract_text()` yang membaca sebuah gambar dan mengembalikan seluruh string tulisan yang ditemukannya (*raw text*). File ini diimplementasikan menggunakan arsitektur *Singleton*, yang berarti modul OCR hanya di-*load* ke memori sekali saat server dinyalakan demi menjaga efisiensi RAM dan CPU.
- **`utils/parser.py`**
  File "Otak Pembacaan" (Heuristik) yang bertugas membersihkan, menyaring, dan mengkategorikan *raw text* dari OCR ke dalam 15 variabel (*field*) spesifik seperti nama, tanggal lahir, dan NIK. Menggunakan perpaduan *Regular Expressions (Regex)* canggih dan pendeteksi *typo* untuk memberikan hasil ekstraksi JSON paling akurat meskipun KTP terlihat buram.

### Frontend
- **`templates/index.html`**
  File antarmuka web (UI) pengguna. Ditulis menggunakan HTML dengan bantuan framework Bootstrap 5 untuk menghasilkan gaya tata letak profesional, form auto-fill yang responsif, *progress bar*, galeri hasil Computer Vision, dan animasi *loading*.
- **`static/css/style.css`**
  Berisi kustomisasi gaya visual *(styling)* web secara detail. File ini mengatur palet warna yang memanjakan mata, efek bayangan (*shadows*), pengaturan kelengkungan sudut, hingga pewarnaan *Alert* log interaktif.
- **`static/js/script.js`**
  Berisi logika interaktif pada browser pengguna (sisi klien). Bertugas mengirim gambar (secara sinkron dengan AJAX/Fetch API), menggerakkan animasi progres dari 0% ke 100%, menulis status *log realtime*, dan memuat (auto-fill) data JSON dari *backend* Flask ke dalam elemen kotak input di halaman tersebut.

### Script Pengujian (Opsional)
- **`test_pipeline.py`**
  Script Command Line Interface (CLI) khusus *developer* yang dirancang untuk menguji alur deteksi dari awal sampai akhir tanpa harus menjalankan server Flask. Berguna untuk debugging atau verifikasi perbaikan saat ada modifikasi struktur parser.
- **`test_params.py`**
  Script utilitas developer untuk melakukan pengujian masal parameter filter gambar (seperti bereksperimen dengan seberapa tinggi level *Gaussian Blur* dan parameter CLAHE) demi menemukan konfigurasi Computer Vision paling ideal bagi deteksi huruf KTP.
