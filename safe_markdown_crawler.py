import asyncio
import random
import re
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib import robotparser
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "mkt_tok",
    "ref",
    "source",
}


@dataclass
class CrawlConfig:
    max_words_per_file: int = 490_000
    max_concurrent: int = 3
    min_delay_seconds: float = 1.0
    max_delay_seconds: float = 2.5
    max_retries: int = 4
    request_timeout_seconds: float = 20.0
    respect_robots_txt: bool = True

    def __post_init__(self) -> None:
        if self.max_words_per_file <= 0:
            raise ValueError("max_words_per_file harus lebih dari 0")
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent harus lebih dari 0")
        if self.min_delay_seconds < 0:
            raise ValueError("min_delay_seconds tidak boleh negatif")
        if self.max_delay_seconds < self.min_delay_seconds:
            raise ValueError("max_delay_seconds harus lebih besar atau sama dengan min_delay_seconds")
        if self.max_retries <= 0:
            raise ValueError("max_retries harus lebih dari 0")


class SafeMarkdownPipeline:
    def __init__(self, root_url: str, config: Optional[CrawlConfig] = None) -> None:
        if not root_url:
            raise ValueError("root_url wajib diisi")

        self.config = config or CrawlConfig()
        self.root_url = self._normalize_input_url(root_url)
        parsed_root = urlparse(self.root_url)

        self.domain = parsed_root.netloc.lower()
        self.root_path = self._normalize_path(parsed_root.path)

        # State management
        self.visited: set[str] = set()
        self.enqueued: set[str] = {self.root_url}
        self.queue: deque[str] = deque([self.root_url])

        # Markdown chunking
        self.current_words = 0
        self.file_index = 1
        self.current_markdown_buffer: list[str] = []

        # Output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = re.sub(r"[^a-zA-Z0-9._-]", "_", self.domain)
        self.output_dir = Path(f"crawl_{safe_domain}_{timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Polite request pacing
        self.request_lock = asyncio.Lock()
        self.last_request_at = 0.0

        # robots.txt info
        self.robot_parser: Optional[robotparser.RobotFileParser] = None
        self.robots_crawl_delay: Optional[float] = None
        self.robot_user_agent = "*"

        # Request headers
        self.headers = {
            "User-Agent": "SafeMarkdownCrawler/1.0 (+https://example.local)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Connection": "keep-alive",
        }

    @staticmethod
    def _count_words(text: str) -> int:
        return len(re.findall(r"\S+", text))

    @staticmethod
    def _normalize_path(path: str) -> str:
        normalized = re.sub(r"/{2,}", "/", path or "/")
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        if normalized != "/" and normalized.endswith("/"):
            normalized = normalized.rstrip("/")
        return normalized

    def _normalize_input_url(self, raw_url: str) -> str:
        candidate = raw_url.strip()
        if not urlparse(candidate).scheme:
            candidate = f"https://{candidate}"
        return self._canonicalize_url(candidate)

    @staticmethod
    def _sanitize_query(query: str) -> str:
        if not query:
            return ""

        clean_params = []
        for key, value in parse_qsl(query, keep_blank_values=True):
            lowered = key.lower()
            if lowered.startswith("utm_") or lowered in TRACKING_QUERY_KEYS:
                continue
            clean_params.append((key, value))

        return urlencode(clean_params, doseq=True)

    def _canonicalize_url(self, raw_url: str) -> str:
        parsed = urlparse(raw_url)

        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        path = self._normalize_path(parsed.path)
        query = self._sanitize_query(parsed.query)

        return urlunparse((scheme, netloc, path, "", query, ""))

    async def _load_robots(self, client: httpx.AsyncClient) -> None:
        if not self.config.respect_robots_txt:
            return

        robots_url = f"{urlparse(self.root_url).scheme}://{self.domain}/robots.txt"
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = await client.get(robots_url, timeout=10.0, headers=self.headers)
            if response.status_code >= 400:
                print("[INFO] robots.txt tidak ditemukan, lanjut dengan mode hati-hati.")
                return

            parser.parse(response.text.splitlines())
            self.robot_parser = parser

            crawl_delay = parser.crawl_delay(self.robot_user_agent)
            if crawl_delay is not None and crawl_delay > 0:
                self.robots_crawl_delay = float(crawl_delay)
                print(f"[INFO] robots crawl-delay terdeteksi: {self.robots_crawl_delay} detik")

        except Exception as exc:
            print(f"[WARN] Gagal memproses robots.txt ({exc}), lanjut dengan mode hati-hati.")

    def _is_url_in_scope(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.netloc.lower() != self.domain:
            return False

        path = self._normalize_path(parsed.path)
        if self.root_path == "/":
            in_scope = True
        else:
            in_scope = path == self.root_path or path.startswith(self.root_path + "/")

        if not in_scope:
            return False

        if self.robot_parser is not None and self.config.respect_robots_txt:
            try:
                if not self.robot_parser.can_fetch(self.robot_user_agent, url):
                    return False
            except Exception:
                return False

        return True

    async def _polite_wait(self) -> None:
        min_delay = max(self.config.min_delay_seconds, self.robots_crawl_delay or 0.0)
        extra_jitter = max(self.config.max_delay_seconds - min_delay, 0.0)
        target_delay = min_delay + random.uniform(0.0, extra_jitter)

        async with self.request_lock:
            now = time.monotonic()
            wait_for = self.last_request_at + target_delay - now
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            self.last_request_at = time.monotonic()

    async def fetch(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        retryable_statuses = {429, 500, 502, 503, 504}

        for attempt in range(1, self.config.max_retries + 1):
            await self._polite_wait()

            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=self.config.request_timeout_seconds,
                    follow_redirects=True,
                )

                if response.status_code in retryable_statuses:
                    backoff = min(30.0, (2 ** attempt) + random.uniform(0.5, 1.5))
                    print(
                        f"[RETRY] Status {response.status_code} untuk {url} "
                        f"(attempt {attempt}/{self.config.max_retries}), tunggu {backoff:.1f}s"
                    )
                    await asyncio.sleep(backoff)
                    continue

                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    return None

                return response.text

            except httpx.HTTPStatusError as exc:
                print(f"[SKIP] HTTP error {exc.response.status_code} untuk {url}")
                return None
            except httpx.RequestError as exc:
                if attempt == self.config.max_retries:
                    print(f"[ERROR] Gagal akses {url}: {exc}")
                    return None

                backoff = min(30.0, (2 ** attempt) + random.uniform(0.5, 1.5))
                print(
                    f"[RETRY] Request error untuk {url} "
                    f"(attempt {attempt}/{self.config.max_retries}), tunggu {backoff:.1f}s"
                )
                await asyncio.sleep(backoff)

        return None

    def extract_content_and_links(self, html: str, current_url: str) -> tuple[str, str, list[str]]:
        soup = BeautifulSoup(html, "html.parser")

        title = (soup.title.string or "").strip() if soup.title else "(tanpa judul)"

        # Ekstrak link dulu sebelum elemen non-konten dihapus.
        new_urls: list[str] = []
        local_seen: set[str] = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue

            full_url = self._canonicalize_url(urljoin(current_url, href))
            if full_url in local_seen:
                continue
            if self._is_url_in_scope(full_url):
                local_seen.add(full_url)
                new_urls.append(full_url)

        # Hilangkan bagian noisy yang biasanya bukan isi utama.
        for element in soup(["nav", "footer", "header", "script", "style", "aside", "svg", "noscript"]):
            element.decompose()

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.find("body")
        )

        if not main_content:
            return "", title, new_urls

        md_text = md(str(main_content), heading_style="ATX", strip=["img"])  # Keep text links
        md_text = re.sub(r"\n{3,}", "\n\n", md_text).strip()

        return md_text, title, new_urls

    def _split_text_by_words(self, text: str) -> list[str]:
        max_words = self.config.max_words_per_file
        if self._count_words(text) <= max_words:
            return [text]

        chunks: list[str] = []
        current_blocks: list[str] = []
        current_words = 0

        for block in text.split("\n\n"):
            block = block.strip()
            if not block:
                continue

            block_words = self._count_words(block)

            if block_words > max_words:
                if current_blocks:
                    chunks.append("\n\n".join(current_blocks))
                    current_blocks = []
                    current_words = 0

                words = block.split()
                for start in range(0, len(words), max_words):
                    chunks.append(" ".join(words[start : start + max_words]))
                continue

            if current_blocks and (current_words + block_words > max_words):
                chunks.append("\n\n".join(current_blocks))
                current_blocks = [block]
                current_words = block_words
            else:
                current_blocks.append(block)
                current_words += block_words

        if current_blocks:
            chunks.append("\n\n".join(current_blocks))

        return chunks if chunks else [text]

    def save_file_chunk(self) -> None:
        if not self.current_markdown_buffer:
            return

        filename = self.output_dir / f"docs_dataset_part_{self.file_index:03d}.md"
        content = "\n\n".join(self.current_markdown_buffer).strip() + "\n"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        print(
            f"[SAVED] {filename.name} "
            f"(kata: {self.current_words:,}, lokasi: {self.output_dir.as_posix()})"
        )

        self.file_index += 1
        self.current_words = 0
        self.current_markdown_buffer = []

    def process_and_chunk(self, url: str, title: str, md_text: str) -> None:
        header = f"\n\n---\nsource: {url}\ntitle: {title}\n---\n\n"
        full_text = header + md_text

        for piece in self._split_text_by_words(full_text):
            piece_words = self._count_words(piece)
            if self.current_words > 0 and (self.current_words + piece_words > self.config.max_words_per_file):
                self.save_file_chunk()

            self.current_markdown_buffer.append(piece)
            self.current_words += piece_words

    async def _crawl_one(self, client: httpx.AsyncClient, url: str) -> tuple[str, str, list[str]]:
        print(f"[CRAWL] ({len(self.visited)} visited | {len(self.queue)} in queue) -> {url}")

        html = await self.fetch(client, url)
        if not html:
            return "", "", []

        return self.extract_content_and_links(html, url)

    @staticmethod
    def _create_http_client(limits: httpx.Limits) -> httpx.AsyncClient:
        try:
            return httpx.AsyncClient(http2=True, limits=limits)
        except ImportError:
            print("[WARN] Paket 'h2' belum terpasang, fallback ke HTTP/1.1.")
            return httpx.AsyncClient(http2=False, limits=limits)

    async def run_pipeline(self) -> None:
        print(f"[START] Mulai crawling dari: {self.root_url}")
        print(f"[INFO] Output folder: {self.output_dir.as_posix()}")

        limits = httpx.Limits(
            max_connections=self.config.max_concurrent,
            max_keepalive_connections=self.config.max_concurrent,
        )

        async with self._create_http_client(limits) as client:
            await self._load_robots(client)

            while self.queue:
                batch: list[str] = []

                while self.queue and len(batch) < self.config.max_concurrent:
                    current_url = self.queue.popleft()
                    if current_url in self.visited:
                        continue
                    self.visited.add(current_url)
                    batch.append(current_url)

                if not batch:
                    continue

                results = await asyncio.gather(
                    *(self._crawl_one(client, url) for url in batch),
                    return_exceptions=True,
                )

                for source_url, result in zip(batch, results):
                    if isinstance(result, Exception):
                        print(f"[ERROR] Gagal memproses {source_url}: {result}")
                        continue

                    md_text, title, new_links = result

                    if md_text:
                        self.process_and_chunk(source_url, title, md_text)

                    for link in new_links:
                        if link not in self.visited and link not in self.enqueued:
                            self.queue.append(link)
                            self.enqueued.add(link)

        self.save_file_chunk()
        print(
            f"[DONE] Selesai. Total halaman dikunjungi: {len(self.visited)}. "
            f"File markdown dibuat di: {self.output_dir.as_posix()}"
        )


def _prompt_int(message: str, default: int, min_value: int) -> int:
    while True:
        raw = input(f"{message} [{default}]: ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
            if value < min_value:
                raise ValueError
            return value
        except ValueError:
            print(f"Masukkan angka >= {min_value}.")


def _prompt_float(message: str, default: float, min_value: float) -> float:
    while True:
        raw = input(f"{message} [{default}]: ").strip()
        if not raw:
            return default
        try:
            value = float(raw)
            if value < min_value:
                raise ValueError
            return value
        except ValueError:
            print(f"Masukkan angka >= {min_value}.")


def _prompt_settings() -> tuple[str, CrawlConfig]:
    print("=== Safe Markdown Crawler ===")

    root_address = ""
    while not root_address:
        root_address = input("Masukkan root web address: ").strip()
        if not root_address:
            print("Root web address tidak boleh kosong.")

    max_words = _prompt_int("Maksimal kata per file", 490000, 1000)
    max_concurrent = _prompt_int("Jumlah koneksi bersamaan (aman: 2-3)", 3, 1)
    min_delay = _prompt_float("Delay minimum antar request (detik)", 1.0, 0.1)
    max_delay = _prompt_float("Delay maksimum antar request (detik)", 2.5, min_delay)

    config = CrawlConfig(
        max_words_per_file=max_words,
        max_concurrent=max_concurrent,
        min_delay_seconds=min_delay,
        max_delay_seconds=max_delay,
    )

    return root_address, config


async def _main() -> None:
    root_address, config = _prompt_settings()
    pipeline = SafeMarkdownPipeline(root_url=root_address, config=config)
    await pipeline.run_pipeline()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\n[STOP] Dihentikan oleh pengguna.")
