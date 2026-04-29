# Scraper Toolkit

Toolkit Python untuk mengekstrak dokumentasi web menjadi Markdown dengan batas maksimal kata per file (default: 490.000 kata).

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
- `api_scraping.txt`: referensi awal script API scraping sederhana.

## Prasyarat

- Python 3.11+ (disarankan pakai venv)
- Paket Python:
  - httpx
  - beautifulsoup4
  - markdownify
  - playwright (untuk `crawler-js.py`)

## Setup Cepat

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install httpx beautifulsoup4 markdownify playwright
python -m playwright install chromium
```

## Cara Menjalankan

### 1) Crawler HTML biasa

```powershell
python crawler.py
```

### 2) Crawler Heavy-JS (Playwright)

```powershell
python crawler-js.py
```

### 3) Crawler Zendesk API

```powershell
python crawler-api.py
```

Saat dijalankan, script akan meminta input seperti root URL, locale, delay, retry, batas halaman, dan batas kata per file.

## Output

- Folder hasil dibuat otomatis dengan timestamp, contoh:
  - `crawl_example.com_YYYYMMDD_HHMMSS/`
  - `crawl_js_example.com_YYYYMMDD_HHMMSS/`
  - `crawl_api_help-center.example.com_YYYYMMDD_HHMMSS/`
- Isi utama berupa `docs_dataset_part_001.md`, `docs_dataset_part_002.md`, dst.
- Untuk `crawler-api.py` juga tersedia:
  - `raw_json/` (backup response JSON per halaman)
  - `knowledge_base_structure.json` (categories + sections)
  - `state_<domain>_<locale>.json` (checkpoint resume)

## Catatan Etika dan Kepatuhan

- Hormati Terms of Service website target.
- Gunakan rate yang wajar (delay dan concurrency rendah).
- Aktifkan penghormatan `robots.txt` bila tersedia.
- Pastikan Anda memiliki hak/izin untuk melakukan scraping data target.
