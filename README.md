# Scraper Toolkit

Toolkit Python untuk mengekstrak dokumentasi web menjadi Markdown dengan batas maksimal kata per file (default: 490.000 kata).

## Kompatibilitas Runtime

- Direkomendasikan: Python 3.14.4
- Sudah kompatibel: Python 3.13+
- OS target: Ubuntu (server/desktop) dan Windows

## Fitur Utama

- Crawler HTTP biasa untuk situs static/semi-dynamic.
- Crawler Playwright untuk halaman heavy-JS.
- Crawler Zendesk API tanpa browser (lebih cepat untuk Help Center berbasis Zendesk).
- Output Markdown terpecah otomatis per file berdasarkan batas kata.
- Delay, retry, backoff, dan mode aman untuk mengurangi risiko rate-limit.

## Struktur Script

- `crawler.py`: crawler HTTP/HTML parser (BeautifulSoup + markdownify).
- `crawler-js.py`: crawler JS-rendered page (Playwright).
- `crawler-api.py`: crawler Zendesk Help Center API langsung.
- `requirements.txt`: dependency utama proyek.
- `api_scraping.txt`: referensi awal script API scraping sederhana.

## Setup Ubuntu (Python 3.14.4)

Jika Python 3.14.4 sudah terpasang, jalankan:

```bash
python3.14 --version
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

Catatan:

- Opsi `--with-deps` akan memasang dependency sistem yang dibutuhkan browser Playwright di Ubuntu.
- Jika command default Anda adalah `python`, pastikan menunjuk ke env `.venv` (bukan global).

## Setup Windows (Opsional)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Cara Menjalankan

### 1) Crawler HTML biasa

```bash
python crawler.py
```

### 2) Crawler Heavy-JS (Playwright)

```bash
python crawler-js.py
```

### 3) Crawler Zendesk API

```bash
python crawler-api.py
```

Saat dijalankan, script akan meminta input seperti root URL, locale, delay, retry, batas halaman, dan batas kata per file.

Khusus `crawler-api.py`, akan ada prompt:

- `Mulai fresh download (abaikan checkpoint lama)?` pilih `y` untuk selalu mulai dari awal.
- Jika memilih fresh mode, crawler tidak akan melanjutkan checkpoint lama.

## Output

- Folder hasil dibuat otomatis dengan timestamp, contoh:
  - `crawl_example.com_YYYYMMDD_HHMMSS/`
  - `crawl_js_example.com_YYYYMMDD_HHMMSS/`
  - `crawl_api_help-center.example.com_YYYYMMDD_HHMMSS/`
- Isi utama berupa `docs_dataset_part_001.md`, `docs_dataset_part_002.md`, dst.
- Untuk `crawler-api.py` juga tersedia:
  - `raw_json/` (backup response JSON per halaman)
  - `knowledge_base_structure.json` (categories + sections)
  - `knowledge_base_structure_part_001.md`, dst. (konversi markdown dari structure JSON, auto-split max 490000 kata/file)
  - `state_<domain>_<locale>.json` (checkpoint resume)

Catatan:

- Jika total konten artikel belum melebihi `max_words_per_file`, maka `docs_dataset` memang bisa hanya 1 file `.md`.

## Catatan Etika dan Kepatuhan

- Hormati Terms of Service website target.
- Gunakan rate yang wajar (delay dan concurrency rendah).
- Aktifkan penghormatan `robots.txt` bila tersedia.
- Pastikan Anda memiliki hak/izin untuk melakukan scraping data target.
