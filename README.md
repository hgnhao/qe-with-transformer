# Sistem Temu Kembali Informasi dengan Perluasan Kueri (Transformer)

Sistem Temu Kembali Informasi (TKI) berbasis Model Ruang Vektor (VSM) yang dilengkapi mekanisme **Perluasan Kueri berbasis Transformer** untuk meningkatkan kualitas hasil pencarian. Dibangun dengan backend FastAPI dan frontend Vue 3.

---

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Fitur](#fitur)
- [Arsitektur](#arsitektur)
- [Teknologi](#teknologi)
- [Prasyarat](#prasyarat)
- [Instalasi dan Menjalankan](#instalasi-dan-menjalankan)
  - [Backend](#setup-backend)
  - [Frontend](#setup-frontend)
- [Referensi API](#referensi-api)
- [Cara Kerja](#cara-kerja)
  - [Perluasan Kueri dengan Transformer](#perluasan-kueri-dengan-transformer)
  - [Skema Pembobotan](#skema-pembobotan)
  - [Evaluasi MAP](#evaluasi-map)
- [Dataset](#dataset)
- [Struktur Proyek](#struktur-proyek)
- [Tim](#tim)

---

## Gambaran Umum

Proyek ini mengimplementasikan sistem TKI lengkap untuk evaluasi akademik pada korpus **CISI**. Pengguna dapat mengirimkan kueri lewat antarmuka web, mengatur parameter preprocessing dan pembobotan, lalu membandingkan hasil pencarian antara **kueri asli** dan **kueri yang sudah diperluas** secara berdampingan. Sistem ini juga mendukung **pemrosesan kueri batch** dengan skor MAP untuk evaluasi eksperimen penuh.

---

## Fitur

| Ketentuan Tugas | Implementasi |
|---|---|
| Pilihan stemming | NLTK PorterStemmer, dapat diaktifkan/dinonaktifkan |
| Pilihan eliminasi stopword | Daftar stopword bahasa Inggris NLTK, dapat dikonfigurasi |
| Varian TF | Raw, Logarithmic, Binary, Augmented |
| Skema pembobotan | TF saja, IDF saja, TF-IDF, TF-IDF + Normalisasi Cosine |
| Jumlah kata perluasan | Parameter top_k (1-N) atau semua kata di atas threshold |
| Mode kueri interaktif | Pencarian satu kueri secara real-time lewat antarmuka web |
| Mode batch | Upload file kueri format CISI, hasilkan laporan MAP |
| Inspeksi inverted index | Lihat isi indeks per dokumen berdasarkan ID dokumen |
| Hasil kueri asli vs diperluas | Perbandingan ranking berdampingan dengan skor similarity dan AP/MAP |
| Bobot kata perluasan | Ditampilkan bersama setiap kata perluasan pada hasil |

---

## Arsitektur

```
+----------------------------------------------------+
|               Browser (Vue 3 SPA)                  |
|  +-------------+ +------------------+ +---------+  |
|  | ConfigPanel | | InteractiveSearch| |  Batch  |  |
|  | (preprocessing| | (asli vs        | |Processing| |
|  |  pembobotan) | |  diperluas)      | |(laporan)| |
|  +-------------+ +------------------+ +---------+  |
+---------------------+---------+--------------------+
                       |  HTTP (Axios)
+---------------------v------------------------------+
|                 FastAPI Backend                     |
|  +----------+  +----------+  +------------------+  |
|  | /config  |  | /search  |  | /index/{doc_id}  |  |
|  +----------+  +-----+----+  +------------------+  |
|                      |                              |
|  +-------------------v--------------------------+  |
|  |               Core Engine                    |  |
|  | preprocess -> ir_engine -> vsm -> expansion  |  |
|  |              evaluation (MAP/AP/P@k/R@k)     |  |
|  +----------------------------------------------+  |
+----------------------------------------------------+
```

---

## Teknologi

**Backend**
- Python 3.13+
- FastAPI + Uvicorn
- SentenceTransformers - model all-MiniLM-L6-v2
- NLTK - tokenisasi, stemming, stopword
- scikit-learn - cosine similarity
- Pydantic v2

**Frontend**
- Vue 3 (Composition API)
- Vite 8
- Tailwind CSS v4
- Axios

---

## Prasyarat

- **Python** versi 3.13 ke atas (cek dengan `python --version`)
- **Node.js** versi 18 ke atas (cek dengan `node --version`)
- **uv** (disarankan) atau `pip` untuk manajemen paket Python
  - Install uv: `pip install uv`

---

## Instalasi dan Menjalankan

### Setup Backend

```bash
# 1. Masuk ke direktori backend
cd backend

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan virtual environment
#    Windows PowerShell:
.\.venv\Scripts\Activate.ps1
#    macOS / Linux:
source .venv/bin/activate

# 4. Install dependensi
#    Menggunakan uv (disarankan):
uv sync
#    Atau menggunakan pip:
pip install fastapi uvicorn sentence-transformers nltk scikit-learn pydantic python-multipart

# 5. Download data NLTK (sekali saja, jalankan di Python REPL)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# 6. Letakkan file dataset CISI di folder test/ di root repo
#    File yang dibutuhkan: cisi.all, query.text, qrels.text

# 7. Jalankan server
fastapi dev main.py
```

API tersedia di **http://localhost:8000**.
Dokumentasi Swagger UI tersedia di **http://localhost:8000/docs**.

---

### Setup Frontend

```bash
# 1. Masuk ke direktori frontend
cd frontend

# 2. Install dependensi Node.js
npm install

# 3. Jalankan dev server
npm run dev
```

Antarmuka web tersedia di **http://localhost:5173** (atau port yang ditampilkan di terminal).

Pastikan backend sudah berjalan sebelum menggunakan antarmuka web.

---

## Referensi API

### `GET /config`
Mengambil konfigurasi preprocessing saat ini.

**Respons:**
```json
{
  "apply_stemming": true,
  "remove_stopwords": true,
  "dataset_loaded": true
}
```

---

### `POST /config`
Memperbarui pengaturan preprocessing. Memicu pembangunan ulang indeks.

**Body:**
```json
{
  "apply_stemming": true,
  "remove_stopwords": false
}
```

---

### `POST /search/interactive`
Pencarian satu kueri dengan hasil asli dan diperluas.

**Body:**
```json
{
  "query": "information retrieval systems",
  "query_id": 1,
  "weight_scheme": "tf-idf-cosine",
  "tf_variant": "logarithmic",
  "top_k_expansion": 5,
  "all_expansion_terms": false
}
```

| Field | Pilihan | Default |
|---|---|---|
| `weight_scheme` | `tf`, `idf`, `tf-idf`, `tf-idf-cosine` | `tf` |
| `tf_variant` | `raw`, `logarithmic`, `binary`, `augmented` | `raw` |
| `top_k_expansion` | bilangan bulat >= 1 | `5` |
| `all_expansion_terms` | `true` / `false` | `false` |
| `query_id` | ID kueri CISI, opsional, mengaktifkan skor AP | `null` |

**Respons:**
```json
{
  "original": {
    "query": ["information", "retrieval", "system"],
    "results": [{"doc_id": 1, "score": 0.87, "title": "..."}],
    "map": 0.423
  },
  "expanded": {
    "query": ["information", "retrieval", "system", "database", "indexing"],
    "expansion_weights": {"database": 0.82, "indexing": 0.79},
    "results": [{"doc_id": 1, "score": 0.91, "title": "..."}],
    "map": 0.531
  }
}
```

---

### `POST /search/batch`
Memproses file kueri multi-kueri dan mengembalikan laporan MAP.

**Form data:**
- `file` - file kueri format CISI (.text)
- `weight_scheme` - sama seperti mode interaktif
- `tf_variant` - sama seperti mode interaktif
- `top_k_expansion` - bilangan bulat
- `all_expansion_terms` - boolean

**Respons:**
```json
{
  "result_text": "Batch Processing Results\n...OVERALL ORIGINAL MAP: 0.3142\nOVERALL EXPANDED MAP: 0.3897"
}
```

---

### `GET /index/{doc_id}`
Mengembalikan entri inverted index untuk ID dokumen tertentu.

**Respons:**
```json
{
  "doc_id": 5,
  "inverted_file": [
    {"term": "retrieval", "frequency": 3, "total_doc_frequency": 120},
    {"term": "system", "frequency": 1, "total_doc_frequency": 450}
  ]
}
```

---

## Cara Kerja

### Perluasan Kueri dengan Transformer

Perluasan kueri menambahkan kata-kata yang secara semantis berkaitan dengan kueri asli sebelum proses perankingan, sehingga dokumen relevan yang tidak secara persis memakai kata yang sama dengan kueri tetap bisa ditemukan.

1. Kueri asli diproses terlebih dahulu (tokenisasi, opsional stemming dan penghapusan stopword).
2. Setiap kata kueri dienkode menggunakan model SentenceTransformer **all-MiniLM-L6-v2**.
3. Model menghitung cosine similarity antara embedding kata kueri dan semua kata dalam kosakata korpus.
4. Kata-kata paling mirip secara semantis yang belum ada di kueri dipilih sebagai kata perluasan, masing-masing diberi bobot berdasarkan skor similarity-nya.
5. Kueri diperluas berupa gabungan kata asli (bobot = 1.0) dan kata perluasan (bobot = skor cosine similarity).
6. Kueri asli dan kueri diperluas diranking secara terpisah agar hasilnya bisa dibandingkan langsung.

Permintaan pencarian pertama akan memuat model dan mengenkode seluruh kosakata, yang bisa memakan waktu 10-30 detik. Permintaan selanjutnya akan jauh lebih cepat.

---

### Skema Pembobotan

VSM meranking dokumen dengan menghitung dot product antara vektor kueri dan vektor setiap dokumen.

**Varian TF:**

| Varian | Rumus |
|---|---|
| `raw` | tf(t, d) |
| `logarithmic` | 1 + log10(tf) jika tf > 0, jika tidak maka 0 |
| `binary` | 1 jika tf > 0, jika tidak maka 0 |
| `augmented` | 0.5 + 0.5 x (tf / tf_maks_dalam_dokumen) |

**Skema Bobot:**

| Skema | Rumus |
|---|---|
| `tf` | Varian TF saja |
| `idf` | log10(N / df) |
| `tf-idf` | Varian TF x IDF |
| `tf-idf-cosine` | (TF x IDF) dinormalisasi dengan panjang vektor dokumen |

---

### Evaluasi MAP

**Average Precision (AP)** untuk satu kueri mengukur seberapa baik daftar ranking menemukan dokumen relevan di setiap posisi:

```
AP = (1 / |R|) x jumlah P(k) x rel(k)
```

Di mana |R| adalah total dokumen relevan, P(k) adalah presisi pada peringkat k, dan rel(k) bernilai 1 jika dokumen pada peringkat k relevan.

**Mean Average Precision (MAP)** adalah rata-rata skor AP dari semua kueri dalam pengujian batch.

**Precision@k** dan **Recall@k** juga tersedia pada modul evaluasi untuk analisis lebih lanjut per posisi peringkat.

---

## Dataset

Sistem ini dirancang untuk korpus **CISI (Computer and Information Science Index)**, tolok ukur evaluasi TKI standar akademik.

Letakkan file berikut di dalam direktori `test/` pada root repositori:

| File | Keterangan |
|---|---|
| `cisi.all` | 1.460 abstrak dokumen dalam format CISI |
| `query.text` | 112 kueri dalam format CISI |
| `qrels.text` | Penilaian relevansi (ID kueri ke ID dokumen relevan) |

---

## Struktur Proyek

```
qe-with-transformer/
+-- backend/
|   +-- main.py              # Entry point aplikasi FastAPI
|   +-- state.py             # State in-memory (indeks, VSM, expander)
|   +-- schemas.py           # Model Pydantic untuk request/response
|   +-- pyproject.toml       # Dependensi Python
|   +-- core/
|   |   +-- ir_engine.py     # Pembangunan inverted index dan parsing dokumen
|   |   +-- vsm.py           # Model Ruang Vektor dan perankingan
|   |   +-- expansion.py     # Perluasan kueri berbasis Transformer
|   |   +-- preprocess.py    # Tokenisasi, stemming, penghapusan stopword
|   |   +-- parser.py        # Parser format dokumen/kueri/qrels CISI
|   |   +-- evaluation.py    # Perhitungan metrik AP, MAP, P@k, R@k
|   +-- routers/
|       +-- config.py        # GET/POST /config
|       +-- search.py        # POST /search/interactive, POST /search/batch
|       +-- index.py         # GET /index/{doc_id}
+-- frontend/
|   +-- src/
|   |   +-- App.vue                   # Komponen root dengan navigasi tab
|   |   +-- store.js                  # State reaktif dan klien Axios
|   |   +-- components/
|   |       +-- ConfigPanel.vue       # Sidebar pengaturan preprocessing dan pembobotan
|   |       +-- InteractiveSearch.vue # UI pencarian, perbandingan hasil berdampingan
|   |       +-- BatchProcessing.vue   # Upload batch dan tampilan laporan MAP
|   |       +-- IndexInspector.vue    # Penampil inverted index per ID dokumen
|   +-- index.html
|   +-- vite.config.js
|   +-- package.json
+-- test/
    +-- cisi.all
    +-- query.text
    +-- qrels.text
```

---

## Tim

### Ahsan Malik Al Farisi - 13523074

Menyiapkan peladen API backend yang asinkron menggunakan FastAPI dan Python (direktori backend).

Mengimplementasikan logika utama sistem temu kembali informasi pada core/, mencakup komputasi Model Ruang Vektor (vsm.py), pengelolaan teks dasar seperti tokenisasi, stemming, stopwords (preprocess.py, parser.py), dan pembuatan Inverted Index (ir_engine.py).

Membangun semua titik akhir rute lalu-lintas data web (router /search, /index, dan /config) lalu menggabungkannya agar dapat dipanggil oleh antarmuka web.

---

### Kefas Kurnia Jonathan - 13523113

Merancang dan membangun seluruh antarmuka pengguna berbasis web menggunakan Vue.js, Vite, dan TailwindCSS (direktori frontend).

Mengembangkan komponen reaktif seperti kotak pencarian (InteractiveSearch.vue), panel konfigurasi (ConfigPanel.vue), fitur inspeksi indeks, dan modul antarmuka pengujian (BatchProcessing.vue).

Membangun State Management (store.js) untuk menjaga sinkronisasi data sisi klien (status kueri, parameter preprocessing, sistem pembobotan, dan skor dokumen).

Mengintegrasikan halaman frontend dengan API HTTP menggunakan Axios.

---

### Farrel Athalla Putra - 13523118

Mengimplementasikan dan mengoptimasi model Transformer (pustaka SentenceTransformer) ke dalam logika perluasan kueri (expansion.py), mengurus komputasi Cosine Similarity pada ruang vektor leksikon, serta mengatur nilai threshold dan top-K.

Melakukan pengujian fungsionalitas dan metrik kualitas evaluasi mesin (evaluation.py) menggunakan dataset CISI (cisi.all, query.text, qrels.text).

Mengumpulkan catatan metrik kualitas dari pengujian dan membuat rangkuman laporan tertulis mencakup User Guide, arsitektur, dan laporan deliverable akhir.
