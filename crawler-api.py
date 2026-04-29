import random
import re
import time
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, cast
from urllib.parse import urljoin, urlparse

import httpx
from markdownify import markdownify as md


@dataclass
class ZendeskApiConfig:
    max_words_per_file: int = 490_000
    per_page: int = 100
    min_delay_seconds: float = 1.0
    max_delay_seconds: float = 2.5
    max_retries: int = 5
    request_timeout_seconds: float = 25.0
    max_pages: int = 0
    resume_from_checkpoint: bool = True

    def __post_init__(self) -> None:
        if self.max_words_per_file <= 0:
            raise ValueError("max_words_per_file harus lebih dari 0")
        if self.per_page <= 0 or self.per_page > 100:
            raise ValueError("per_page harus di antara 1 sampai 100")
        if self.min_delay_seconds < 0:
            raise ValueError("min_delay_seconds tidak boleh negatif")
        if self.max_delay_seconds < self.min_delay_seconds:
            raise ValueError("max_delay_seconds harus >= min_delay_seconds")
        if self.max_retries <= 0:
            raise ValueError("max_retries harus lebih dari 0")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds harus lebih dari 0")
        if self.max_pages < 0:
            raise ValueError("max_pages tidak boleh negatif")


class ZendeskApiMarkdownCrawler:
    def __init__(self, help_center_url: str, locale: str, config: Optional[ZendeskApiConfig] = None) -> None:
        if not help_center_url.strip():
            raise ValueError("help_center_url wajib diisi")
        if not locale.strip():
            raise ValueError("locale wajib diisi")

        self.config = config or ZendeskApiConfig()
        self.help_center_url = self._normalize_help_center_url(help_center_url)
        self.locale = locale.strip()

        parsed = urlparse(self.help_center_url)
        self.domain = parsed.netloc.lower()
        self.api_start_url = (
            f"{parsed.scheme}://{self.domain}/api/v2/help_center/{self.locale}/articles.json"
            f"?per_page={self.config.per_page}"
        )
        self.categories_start_url = (
            f"{parsed.scheme}://{self.domain}/api/v2/help_center/{self.locale}/categories.json?per_page=100"
        )
        self.sections_start_url = (
            f"{parsed.scheme}://{self.domain}/api/v2/help_center/{self.locale}/sections.json?per_page=100"
        )

        self.output_dir = self._build_output_dir(self.domain)
        self.raw_json_dir = self.output_dir / "raw_json"
        self.raw_json_dir.mkdir(parents=True, exist_ok=True)

        self.current_words = 0
        self.file_index = 1
        self.current_markdown_buffer: list[str] = []
        self.seen_article_ids: set[int] = set()
        self.category_map: dict[int, dict[str, Any]] = {}
        self.section_map: dict[int, dict[str, Any]] = {}

        self.current_url: Optional[str] = self.api_start_url
        self.page_index = 0
        self.processed_articles = 0

        safe_domain = re.sub(r"[^a-zA-Z0-9._-]", "_", self.domain)
        safe_locale = re.sub(r"[^a-zA-Z0-9._-]", "_", self.locale)
        self.state_file = Path(f"state_{safe_domain}_{safe_locale}.json")
        self.resumed_from_checkpoint = False

        self.user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        }

        self._load_checkpoint_if_available()

    @staticmethod
    def _build_output_dir(domain: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = re.sub(r"[^a-zA-Z0-9._-]", "_", domain)
        output_dir = Path(f"crawl_api_{safe_domain}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @staticmethod
    def _count_words(text: str) -> int:
        return len(re.findall(r"\S+", text))

    @staticmethod
    def _coerce_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _normalize_help_center_url(raw_url: str) -> str:
        candidate = raw_url.strip()
        if not urlparse(candidate).scheme:
            candidate = f"https://{candidate}"

        parsed = urlparse(candidate)
        return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"

    def _load_checkpoint_if_available(self) -> None:
        if not self.config.resume_from_checkpoint:
            return
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                loaded_state = json.load(file)
        except Exception as exc:
            print(f"[WARN] Checkpoint rusak/tidak bisa dibaca ({exc}), mulai dari awal.")
            return

        if not isinstance(loaded_state, dict):
            print("[WARN] Format checkpoint tidak valid, mulai dari awal.")
            return

        state = cast(dict[str, Any], loaded_state)

        if state.get("help_center_url") != self.help_center_url or state.get("locale") != self.locale:
            return

        output_dir_raw = state.get("output_dir")
        if isinstance(output_dir_raw, str) and output_dir_raw.strip():
            restored_output_dir = Path(output_dir_raw)
            restored_output_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir = restored_output_dir
            self.raw_json_dir = self.output_dir / "raw_json"
            self.raw_json_dir.mkdir(parents=True, exist_ok=True)

        next_page_raw = state.get("next_page_url")
        if isinstance(next_page_raw, str) and next_page_raw.strip():
            self.current_url = next_page_raw
        else:
            self.current_url = self.api_start_url

        self.page_index = self._coerce_int(state.get("page_index"), 0)
        self.processed_articles = self._coerce_int(state.get("processed_articles"), 0)
        self.file_index = self._coerce_int(state.get("file_index"), 1)
        self.current_words = self._coerce_int(state.get("current_words"), 0)

        loaded_buffer_raw = state.get("current_markdown_buffer")
        loaded_buffer: list[Any] = cast(list[Any], loaded_buffer_raw) if isinstance(loaded_buffer_raw, list) else []
        self.current_markdown_buffer = [str(part) for part in loaded_buffer]

        seen_ids_raw_value = state.get("seen_article_ids")
        seen_ids_raw: list[Any] = (
            cast(list[Any], seen_ids_raw_value) if isinstance(seen_ids_raw_value, list) else []
        )
        self.seen_article_ids = {
            item
            for item in (self._coerce_int(raw, -1) for raw in seen_ids_raw)
            if item >= 0
        }

        self.resumed_from_checkpoint = True
        print(
            f"[RESUME] Melanjutkan dari checkpoint: page={self.page_index}, "
            f"processed_articles={self.processed_articles}, next={self.current_url}"
        )

    def _save_checkpoint(self, next_page_url: Optional[str]) -> None:
        state: dict[str, Any] = {
            "help_center_url": self.help_center_url,
            "locale": self.locale,
            "next_page_url": next_page_url,
            "page_index": self.page_index,
            "processed_articles": self.processed_articles,
            "output_dir": self.output_dir.as_posix(),
            "file_index": self.file_index,
            "current_words": self.current_words,
            "current_markdown_buffer": self.current_markdown_buffer,
            "seen_article_ids": sorted(self.seen_article_ids),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        temp_file = self.state_file.with_suffix(self.state_file.suffix + ".tmp")
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

        temp_file.replace(self.state_file)

    def _clear_checkpoint(self) -> None:
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except Exception as exc:
            print(f"[WARN] Tidak bisa menghapus checkpoint ({exc}).")

    def _save_json_backup(self, prefix: str, page_number: int, payload: dict[str, Any]) -> None:
        filename = f"{prefix}_page_{page_number:06d}.json"
        file_path = self.raw_json_dir / filename
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _to_markdown_scalar(value: Any) -> str:
        if value is None:
            return "-"

        text = str(value).strip()
        if not text:
            return "-"

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return text if "\n" not in text else text.replace("\n", " ")

    def _build_structure_markdown(self, structure_payload: dict[str, Any]) -> str:
        categories_raw = structure_payload.get("categories")
        sections_raw = structure_payload.get("sections")

        categories: list[dict[str, Any]] = []
        if isinstance(categories_raw, list):
            for item in cast(list[Any], categories_raw):
                if isinstance(item, dict):
                    categories.append(cast(dict[str, Any], item))

        sections: list[dict[str, Any]] = []
        if isinstance(sections_raw, list):
            for item in cast(list[Any], sections_raw):
                if isinstance(item, dict):
                    sections.append(cast(dict[str, Any], item))

        lines: list[str] = [
            "# Knowledge Base Structure",
            "",
            f"- help_center_url: {self._to_markdown_scalar(structure_payload.get('help_center_url'))}",
            f"- locale: {self._to_markdown_scalar(structure_payload.get('locale'))}",
            f"- fetched_at: {self._to_markdown_scalar(structure_payload.get('fetched_at'))}",
            f"- category_count: {self._to_markdown_scalar(structure_payload.get('category_count'))}",
            f"- section_count: {self._to_markdown_scalar(structure_payload.get('section_count'))}",
            "",
            "## Categories",
            "",
        ]

        if not categories:
            lines.append("(Tidak ada data categories)")
            lines.append("")
        else:
            for idx, item in enumerate(categories, start=1):
                category_name = self._to_markdown_scalar(item.get("name"))
                lines.extend(
                    [
                        f"### Category {idx}: {category_name}",
                        "",
                        f"- id: {self._to_markdown_scalar(item.get('id'))}",
                        f"- name: {self._to_markdown_scalar(item.get('name'))}",
                        f"- description: {self._to_markdown_scalar(item.get('description'))}",
                        f"- html_url: {self._to_markdown_scalar(item.get('html_url'))}",
                        f"- position: {self._to_markdown_scalar(item.get('position'))}",
                        f"- created_at: {self._to_markdown_scalar(item.get('created_at'))}",
                        f"- updated_at: {self._to_markdown_scalar(item.get('updated_at'))}",
                        "",
                    ]
                )

        lines.extend(["## Sections", ""])

        if not sections:
            lines.append("(Tidak ada data sections)")
            lines.append("")
        else:
            for idx, item in enumerate(sections, start=1):
                section_name = self._to_markdown_scalar(item.get("name"))
                lines.extend(
                    [
                        f"### Section {idx}: {section_name}",
                        "",
                        f"- id: {self._to_markdown_scalar(item.get('id'))}",
                        f"- category_id: {self._to_markdown_scalar(item.get('category_id'))}",
                        f"- name: {self._to_markdown_scalar(item.get('name'))}",
                        f"- description: {self._to_markdown_scalar(item.get('description'))}",
                        f"- html_url: {self._to_markdown_scalar(item.get('html_url'))}",
                        f"- position: {self._to_markdown_scalar(item.get('position'))}",
                        f"- created_at: {self._to_markdown_scalar(item.get('created_at'))}",
                        f"- updated_at: {self._to_markdown_scalar(item.get('updated_at'))}",
                        "",
                    ]
                )

        return "\n".join(lines).strip() + "\n"

    def _save_structure_markdown_chunks(self, structure_payload: dict[str, Any]) -> None:
        markdown_text = self._build_structure_markdown(structure_payload)
        parts = self._split_text_by_words(markdown_text)

        for index, part in enumerate(parts, start=1):
            file_path = self.output_dir / f"knowledge_base_structure_part_{index:03d}.md"
            content = part.strip() + "\n"

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            print(
                f"[SAVED] {file_path.name} "
                f"(kata: {self._count_words(content):,}, lokasi: {self.output_dir.as_posix()})"
            )

    def _fetch_paginated_collection(
        self,
        client: httpx.Client,
        start_url: str,
        key: str,
        backup_prefix: str,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        url = start_url
        page_number = 1

        while url:
            page_data = self._fetch_page(client, url)
            if page_data is None:
                print(f"[WARN] Gagal mengambil koleksi '{key}' dari {url}")
                break

            self._save_json_backup(backup_prefix, page_number, page_data)

            raw_collection = page_data.get(key)
            if isinstance(raw_collection, list):
                collection_list: list[Any] = cast(list[Any], raw_collection)
                for item_raw in collection_list:
                    if isinstance(item_raw, dict):
                        items.append(cast(dict[str, Any], item_raw))

            next_page = page_data.get("next_page")
            if next_page:
                url = urljoin(self.help_center_url, next_page)
                wait_seconds = random.uniform(
                    self.config.min_delay_seconds,
                    self.config.max_delay_seconds,
                )
                time.sleep(wait_seconds)
                page_number += 1
            else:
                url = None

        return items

    def _load_structure_metadata(self, client: httpx.Client) -> None:
        categories = self._fetch_paginated_collection(
            client=client,
            start_url=self.categories_start_url,
            key="categories",
            backup_prefix="categories",
        )
        sections = self._fetch_paginated_collection(
            client=client,
            start_url=self.sections_start_url,
            key="sections",
            backup_prefix="sections",
        )

        self.category_map = {
            item_id: item
            for item in categories
            if (item_id := item.get("id")) is not None and isinstance(item_id, int)
        }
        self.section_map = {
            item_id: item
            for item in sections
            if (item_id := item.get("id")) is not None and isinstance(item_id, int)
        }

        structure_payload: dict[str, Any] = {
            "help_center_url": self.help_center_url,
            "locale": self.locale,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "category_count": len(categories),
            "section_count": len(sections),
            "categories": categories,
            "sections": sections,
        }

        structure_path = self.output_dir / "knowledge_base_structure.json"
        with open(structure_path, "w", encoding="utf-8") as file:
            json.dump(structure_payload, file, ensure_ascii=False, indent=2)

        self._save_structure_markdown_chunks(structure_payload)

        print(
            f"[INFO] Metadata dimuat: {len(categories)} categories, "
            f"{len(sections)} sections"
        )

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

            if current_blocks and current_words + block_words > max_words:
                chunks.append("\n\n".join(current_blocks))
                current_blocks = [block]
                current_words = block_words
            else:
                current_blocks.append(block)
                current_words += block_words

        if current_blocks:
            chunks.append("\n\n".join(current_blocks))

        return chunks

    def _save_file_chunk(self) -> None:
        if not self.current_markdown_buffer:
            return

        file_path = self.output_dir / f"docs_dataset_part_{self.file_index:03d}.md"
        content = "\n\n".join(self.current_markdown_buffer).strip() + "\n"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(
            f"[SAVED] {file_path.name} "
            f"(kata: {self.current_words:,}, lokasi: {self.output_dir.as_posix()})"
        )

        self.file_index += 1
        self.current_words = 0
        self.current_markdown_buffer = []

    def _process_and_chunk(
        self,
        article_url: str,
        title: str,
        markdown_content: str,
        article_id: Any,
        section_id: Any,
        section_name: str,
        category_id: Any,
        category_name: str,
    ) -> None:
        header = (
            "\n\n---\n"
            f"source: {article_url}\n"
            f"title: {title}\n"
            f"article_id: {article_id}\n"
            f"section_id: {section_id}\n"
            f"section_name: {section_name}\n"
            f"category_id: {category_id}\n"
            f"category_name: {category_name}\n"
            "---\n\n"
        )

        full_text = header + markdown_content

        for piece in self._split_text_by_words(full_text):
            piece_words = self._count_words(piece)

            if self.current_words > 0 and self.current_words + piece_words > self.config.max_words_per_file:
                self._save_file_chunk()

            self.current_markdown_buffer.append(piece)
            self.current_words += piece_words

    def _build_article_markdown(
        self, article: dict[str, Any]
    ) -> Optional[tuple[str, str, str, Any, Any, str, Any, str]]:
        title = (article.get("title") or "(tanpa judul)").strip()
        html_body = article.get("body") or ""

        if not html_body.strip():
            return None

        article_url = article.get("html_url") or ""
        if not article_url:
            slug = article.get("name") or title.lower().replace(" ", "-")
            article_id = article.get("id")
            article_url = f"{self.help_center_url}/hc/{self.locale}/articles/{article_id}-{slug}"

        article_url = article_url.strip()
        article_id = article.get("id") or "unknown"

        section_id = article.get("section_id") or "unknown"
        section_name = ""
        category_id: Any = article.get("category_id") or "unknown"
        category_name = ""

        if isinstance(section_id, int):
            section_data = self.section_map.get(section_id) or {}
            section_name = str(section_data.get("name") or "")

            resolved_category_id = section_data.get("category_id")
            if resolved_category_id is not None:
                category_id = resolved_category_id

        if isinstance(category_id, int):
            category_data = self.category_map.get(category_id) or {}
            category_name = str(category_data.get("name") or "")

        markdown_content = md(html_body, heading_style="ATX", strip=["img"])
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content).strip()

        if not markdown_content:
            return None

        return (
            article_url,
            title,
            markdown_content,
            article_id,
            section_id,
            section_name,
            category_id,
            category_name,
        )

    @staticmethod
    def _get_retry_delay(response: Optional[httpx.Response], attempt: int) -> float:
        if response is not None:
            retry_after_raw = response.headers.get("Retry-After")
            if retry_after_raw:
                try:
                    retry_after = float(retry_after_raw)
                    if retry_after > 0:
                        return min(120.0, retry_after)
                except ValueError:
                    pass

        return min(60.0, (2 ** attempt) + random.uniform(0.5, 1.5))

    @staticmethod
    def _create_http_client(timeout_seconds: float) -> httpx.Client:
        try:
            return httpx.Client(http2=True, timeout=timeout_seconds, follow_redirects=True)
        except ImportError:
            print("[WARN] Paket 'h2' belum terpasang, fallback ke HTTP/1.1.")
            return httpx.Client(http2=False, timeout=timeout_seconds, follow_redirects=True)

    def _fetch_page(self, client: httpx.Client, url: str) -> Optional[dict[str, Any]]:
        retryable_statuses = {429, 500, 502, 503, 504}

        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = client.get(url, headers=self.headers)

                if response.status_code in retryable_statuses:
                    wait_seconds = self._get_retry_delay(response, attempt)
                    print(
                        f"[RETRY] Status {response.status_code} untuk {url} "
                        f"(attempt {attempt}/{self.config.max_retries}), tunggu {wait_seconds:.1f}s"
                    )
                    time.sleep(wait_seconds)
                    continue

                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "application/json" not in content_type:
                    print(f"[SKIP] Konten bukan JSON untuk {url}")
                    return None

                return response.json()

            except httpx.HTTPStatusError as exc:
                print(f"[ERROR] HTTP {exc.response.status_code} saat akses {url}")
                return None
            except (httpx.RequestError, ValueError) as exc:
                if attempt == self.config.max_retries:
                    print(f"[ERROR] Gagal akses {url}: {exc}")
                    return None

                wait_seconds = self._get_retry_delay(None, attempt)
                print(
                    f"[RETRY] Error jaringan/parsing untuk {url} "
                    f"(attempt {attempt}/{self.config.max_retries}), tunggu {wait_seconds:.1f}s"
                )
                time.sleep(wait_seconds)

        return None

    def run(self) -> None:
        print(f"[START] Mulai scraping API Zendesk: {self.api_start_url}")
        print(f"[INFO] Output folder: {self.output_dir.as_posix()}")

        pages_processed_this_run = 0

        try:
            with self._create_http_client(self.config.request_timeout_seconds) as client:
                self._load_structure_metadata(client)

                while self.current_url:
                    if self.config.max_pages > 0 and pages_processed_this_run >= self.config.max_pages:
                        print(f"[INFO] Batas max_pages={self.config.max_pages} tercapai.")
                        self._save_checkpoint(self.current_url)
                        break

                    page_data = self._fetch_page(client, self.current_url)
                    if page_data is None:
                        self._save_checkpoint(self.current_url)
                        break

                    self._save_json_backup("articles", self.page_index + 1, page_data)

                    raw_articles = page_data.get("articles")
                    articles: list[dict[str, Any]] = []
                    if isinstance(raw_articles, list):
                        raw_articles_list: list[Any] = cast(list[Any], raw_articles)
                        for item_raw in raw_articles_list:
                            if isinstance(item_raw, dict):
                                articles.append(cast(dict[str, Any], item_raw))

                    print(
                        f"[PAGE] Halaman ke-{self.page_index + 1}: "
                        f"{len(articles)} artikel, total-terproses={self.processed_articles}"
                    )

                    for article in articles:
                        article_id = article.get("id")
                        if isinstance(article_id, int) and article_id in self.seen_article_ids:
                            continue

                        built = self._build_article_markdown(article)
                        if not built:
                            continue

                        (
                            article_url,
                            title,
                            markdown_content,
                            article_id,
                            section_id,
                            section_name,
                            category_id,
                            category_name,
                        ) = built
                        self._process_and_chunk(
                            article_url,
                            title,
                            markdown_content,
                            article_id,
                            section_id,
                            section_name,
                            category_id,
                            category_name,
                        )

                        if isinstance(article_id, int):
                            self.seen_article_ids.add(article_id)

                        self.processed_articles += 1

                    self.page_index += 1
                    pages_processed_this_run += 1

                    next_page = page_data.get("next_page")
                    if next_page:
                        self.current_url = urljoin(self.help_center_url, next_page)
                        self._save_checkpoint(self.current_url)
                        wait_seconds = random.uniform(
                            self.config.min_delay_seconds,
                            self.config.max_delay_seconds,
                        )
                        time.sleep(wait_seconds)
                    else:
                        self.current_url = None
                        self._save_checkpoint(self.current_url)

        except KeyboardInterrupt:
            print("\n[STOP] Dihentikan pengguna. Menyimpan buffer terakhir...")
            self._save_checkpoint(self.current_url)
        finally:
            self._save_file_chunk()

        if self.current_url is None:
            self._clear_checkpoint()
        else:
            # Sinkronkan state setelah flush terakhir agar resume tidak menulis ulang part yang sama.
            self._save_checkpoint(self.current_url)

        print(
            f"[DONE] Selesai. Artikel diproses: {self.processed_articles}, "
            f"file markdown di: {self.output_dir.as_posix()}"
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


def _prompt_settings() -> tuple[str, str, ZendeskApiConfig]:
    print("=== Zendesk API Markdown Crawler ===")

    help_center_url = ""
    while not help_center_url:
        help_center_url = input("Masukkan domain help center (contoh: https://help-center.talenta.co): ").strip()
        if not help_center_url:
            print("Domain help center tidak boleh kosong.")

    locale = input("Masukkan locale (contoh: id, en-us) [id]: ").strip() or "id"

    max_words = _prompt_int("Maksimal kata per file", 490000, 1000)
    per_page = _prompt_int("Jumlah artikel per halaman API (maks 100)", 100, 1)
    per_page = min(per_page, 100)
    min_delay = _prompt_float("Delay minimum antar halaman (detik)", 1.0, 0.0)
    max_delay = _prompt_float("Delay maksimum antar halaman (detik)", 2.5, min_delay)
    max_retries = _prompt_int("Maksimal retry per request", 5, 1)
    max_pages = _prompt_int("Batas halaman (0 = tanpa batas)", 0, 0)
    resume_checkpoint = _prompt_bool("Lanjutkan dari checkpoint jika tersedia?", True)

    config = ZendeskApiConfig(
        max_words_per_file=max_words,
        per_page=per_page,
        min_delay_seconds=min_delay,
        max_delay_seconds=max_delay,
        max_retries=max_retries,
        max_pages=max_pages,
        resume_from_checkpoint=resume_checkpoint,
    )

    return help_center_url, locale, config


def main() -> None:
    help_center_url, locale, config = _prompt_settings()
    crawler = ZendeskApiMarkdownCrawler(help_center_url=help_center_url, locale=locale, config=config)
    crawler.run()


if __name__ == "__main__":
    main()
