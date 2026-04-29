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
class JSCrawlConfig:
    max_words_per_file: int = 490_000
    max_concurrent_pages: int = 1
    min_delay_seconds: float = 1.5
    max_delay_seconds: float = 3.5
    max_retries: int = 3
    navigation_timeout_seconds: float = 45.0
    wait_after_load_seconds: float = 1.0
    max_scroll_rounds: int = 10
    expand_click_rounds: int = 2
    respect_robots_txt: bool = True
    headless: bool = True

    def __post_init__(self) -> None:
        if self.max_words_per_file <= 0:
            raise ValueError("max_words_per_file harus lebih dari 0")
        if self.max_concurrent_pages <= 0:
            raise ValueError("max_concurrent_pages harus lebih dari 0")
        if self.min_delay_seconds < 0:
            raise ValueError("min_delay_seconds tidak boleh negatif")
        if self.max_delay_seconds < self.min_delay_seconds:
            raise ValueError("max_delay_seconds harus lebih besar atau sama dengan min_delay_seconds")
        if self.max_retries <= 0:
            raise ValueError("max_retries harus lebih dari 0")
        if self.navigation_timeout_seconds <= 0:
            raise ValueError("navigation_timeout_seconds harus lebih dari 0")
        if self.wait_after_load_seconds < 0:
            raise ValueError("wait_after_load_seconds tidak boleh negatif")
        if self.max_scroll_rounds <= 0:
            raise ValueError("max_scroll_rounds harus lebih dari 0")
        if self.expand_click_rounds < 0:
            raise ValueError("expand_click_rounds tidak boleh negatif")


class JSMarkdownCrawler:
    def __init__(self, root_url: str, config: Optional[JSCrawlConfig] = None) -> None:
        if not root_url:
            raise ValueError("root_url wajib diisi")

        self.config = config or JSCrawlConfig()
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
        self.output_dir = Path(f"crawl_js_{safe_domain}_{timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Polite request pacing
        self.request_lock = asyncio.Lock()
        self.last_request_at = 0.0

        # robots.txt info
        self.robot_parser: Optional[robotparser.RobotFileParser] = None
        self.robots_crawl_delay: Optional[float] = None
        self.robot_user_agent = "*"

        # Browser fingerprint basics (not bypassing anti-bot, just stable browser-like defaults)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

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

    async def _load_robots(self) -> None:
        if not self.config.respect_robots_txt:
            return

        robots_url = f"{urlparse(self.root_url).scheme}://{self.domain}/robots.txt"
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/plain,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        }

        try:
            async with httpx.AsyncClient(http2=True) as client:
                response = await client.get(robots_url, headers=headers, timeout=12.0)

            if response.status_code >= 400:
                print("[INFO] robots.txt tidak ditemukan, lanjut dengan mode hati-hati.")
                return

            parser.parse(response.text.splitlines())
            self.robot_parser = parser

            crawl_delay = parser.crawl_delay(self.robot_user_agent)
            if crawl_delay is not None and crawl_delay > 0:
                self.robots_crawl_delay = float(crawl_delay)
                print(f"[INFO] robots crawl-delay terdeteksi: {self.robots_crawl_delay} detik")

        except ImportError:
            async with httpx.AsyncClient(http2=False) as client:
                response = await client.get(robots_url, headers=headers, timeout=12.0)

            if response.status_code >= 400:
                print("[INFO] robots.txt tidak ditemukan, lanjut dengan mode hati-hati.")
                return

            parser.parse(response.text.splitlines())
            self.robot_parser = parser
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

    async def _scroll_to_bottom(self, page) -> None:
        last_height = 0
        stable_rounds = 0

        for _ in range(self.config.max_scroll_rounds):
            await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(random.uniform(0.25, 0.7))

            current_height = await page.evaluate("() => document.body.scrollHeight")
            if current_height <= last_height + 10:
                stable_rounds += 1
            else:
                stable_rounds = 0

            last_height = current_height
            if stable_rounds >= 2:
                break

    async def _expand_common_interactions(self, page) -> None:
        selectors = [
            "button[aria-expanded='false']",
            "[role='button'][aria-expanded='false']",
            "details:not([open]) > summary",
            "button:has-text('Show more')",
            "button:has-text('Load more')",
            "button:has-text('Read more')",
            "button:has-text('Lihat selengkapnya')",
            "button:has-text('Muat lebih banyak')",
        ]

        total_clicked = 0

        for _ in range(self.config.expand_click_rounds):
            clicked_this_round = 0

            for selector in selectors:
                locator = page.locator(selector)
                count = await locator.count()

                for idx in range(min(count, 15)):
                    target = locator.nth(idx)

                    try:
                        if not await target.is_visible():
                            continue
                        if not await target.is_enabled():
                            continue

                        await target.click(timeout=1200)
                        clicked_this_round += 1
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                    except Exception:
                        continue

            total_clicked += clicked_this_round
            if clicked_this_round == 0:
                break

            await asyncio.sleep(random.uniform(0.2, 0.5))

        if total_clicked > 0:
            print(f"[INFO] Interaksi expand/load-more dieksekusi: {total_clicked} klik")

    async def _render_page(self, page, url: str) -> tuple[Optional[str], Optional[str]]:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        retryable_statuses = {429, 500, 502, 503, 504}

        for attempt in range(1, self.config.max_retries + 1):
            await self._polite_wait()

            try:
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=int(self.config.navigation_timeout_seconds * 1000),
                )

                if response is not None:
                    status_code = response.status
                    if status_code in retryable_statuses:
                        backoff = min(30.0, (2 ** attempt) + random.uniform(0.5, 1.5))
                        print(
                            f"[RETRY] Status {status_code} untuk {url} "
                            f"(attempt {attempt}/{self.config.max_retries}), tunggu {backoff:.1f}s"
                        )
                        await asyncio.sleep(backoff)
                        continue

                    if status_code >= 400:
                        print(f"[SKIP] HTTP status {status_code} untuk {url}")
                        return None, None

                    content_type = response.headers.get("content-type", "").lower()
                    if content_type and "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        return None, None

                try:
                    await page.wait_for_load_state("networkidle", timeout=8_000)
                except PlaywrightTimeoutError:
                    # Sebagian situs terus memuat polling request; lanjut dengan konten yang sudah ada.
                    pass

                await asyncio.sleep(self.config.wait_after_load_seconds + random.uniform(0.0, 0.6))

                await self._scroll_to_bottom(page)
                await self._expand_common_interactions(page)
                await self._scroll_to_bottom(page)

                html = await page.content()
                final_url = self._canonicalize_url(page.url)
                return html, final_url

            except PlaywrightTimeoutError as exc:
                if attempt == self.config.max_retries:
                    print(f"[ERROR] Timeout render {url}: {exc}")
                    return None, None

                backoff = min(30.0, (2 ** attempt) + random.uniform(0.5, 1.5))
                print(
                    f"[RETRY] Timeout render untuk {url} "
                    f"(attempt {attempt}/{self.config.max_retries}), tunggu {backoff:.1f}s"
                )
                await asyncio.sleep(backoff)

            except Exception as exc:
                if attempt == self.config.max_retries:
                    print(f"[ERROR] Gagal render {url}: {exc}")
                    return None, None

                backoff = min(30.0, (2 ** attempt) + random.uniform(0.5, 1.5))
                print(
                    f"[RETRY] Error render untuk {url} "
                    f"(attempt {attempt}/{self.config.max_retries}), tunggu {backoff:.1f}s"
                )
                await asyncio.sleep(backoff)

        return None, None

    def extract_content_and_links(self, html: str, current_url: str) -> tuple[str, str, list[str]]:
        soup = BeautifulSoup(html, "html.parser")

        title = (soup.title.string or "").strip() if soup.title else "(tanpa judul)"

        # Ekstrak link dari DOM yang sudah dirender JavaScript.
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

        md_text = md(str(main_content), heading_style="ATX", strip=["img"])
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

    async def _crawl_one(self, context, url: str) -> tuple[str, str, list[str]]:
        print(f"[CRAWL] ({len(self.visited)} visited | {len(self.queue)} in queue) -> {url}")

        page = await context.new_page()
        try:
            html, final_url = await self._render_page(page, url)
            if not html or not final_url:
                return "", "", []

            if not self._is_url_in_scope(final_url):
                print(f"[SKIP] Redirect keluar scope: {final_url}")
                return "", "", []

            return self.extract_content_and_links(html, final_url)
        finally:
            await page.close()

    async def run_pipeline(self) -> None:
        print(f"[START] Mulai JS crawling dari: {self.root_url}")
        print(f"[INFO] Output folder: {self.output_dir.as_posix()}")

        await self._load_robots()

        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright belum terpasang. Jalankan: pip install playwright lalu "
                "python -m playwright install chromium"
            ) from exc

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=self.config.headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=self.user_agent,
                locale="id-ID",
                timezone_id="Asia/Jakarta",
                viewport={"width": 1366, "height": 768},
            )

            try:
                while self.queue:
                    batch: list[str] = []

                    while self.queue and len(batch) < self.config.max_concurrent_pages:
                        current_url = self.queue.popleft()
                        if current_url in self.visited:
                            continue
                        self.visited.add(current_url)
                        batch.append(current_url)

                    if not batch:
                        continue

                    results = await asyncio.gather(
                        *(self._crawl_one(context, url) for url in batch),
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

            finally:
                await context.close()
                await browser.close()

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


def _prompt_bool(message: str, default: bool) -> bool:
    default_label = "Y/n" if default else "y/N"

    while True:
        raw = input(f"{message} [{default_label}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes", "1", "true", "t"}:
            return True
        if raw in {"n", "no", "0", "false", "f"}:
            return False
        print("Masukkan y atau n.")


def _prompt_settings() -> tuple[str, JSCrawlConfig]:
    print("=== JS Markdown Crawler (Playwright) ===")

    root_address = ""
    while not root_address:
        root_address = input("Masukkan root web address: ").strip()
        if not root_address:
            print("Root web address tidak boleh kosong.")

    max_words = _prompt_int("Maksimal kata per file", 490000, 1000)
    max_concurrent_pages = _prompt_int("Jumlah halaman bersamaan (aman: 1-2)", 1, 1)
    min_delay = _prompt_float("Delay minimum antar halaman (detik)", 1.5, 0.1)
    max_delay = _prompt_float("Delay maksimum antar halaman (detik)", 3.5, min_delay)
    expand_click_rounds = _prompt_int("Putaran klik expand/load-more", 2, 0)
    headless = _prompt_bool("Jalankan browser tanpa UI (headless)?", True)
    respect_robots = _prompt_bool("Hormati robots.txt?", True)

    config = JSCrawlConfig(
        max_words_per_file=max_words,
        max_concurrent_pages=max_concurrent_pages,
        min_delay_seconds=min_delay,
        max_delay_seconds=max_delay,
        expand_click_rounds=expand_click_rounds,
        headless=headless,
        respect_robots_txt=respect_robots,
    )

    return root_address, config


async def _main() -> None:
    root_address, config = _prompt_settings()
    crawler = JSMarkdownCrawler(root_url=root_address, config=config)
    await crawler.run_pipeline()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\n[STOP] Dihentikan oleh pengguna.")
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
