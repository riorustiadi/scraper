from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


DEFAULT_HASH_ALGORITHM = "sha256"
DEFAULT_CHUNK_SIZE_MB = 16.0


@dataclass(frozen=True)
class DuplicateEntry:
    original_path: Path
    duplicate_path: Path
    file_hash: str
    size_bytes: int


def iter_files(target_path: Path, follow_symlinks: bool = False) -> Iterable[Path]:
    for root, dirs, files in os.walk(target_path, followlinks=follow_symlinks):
        root_path = Path(root)

        if not follow_symlinks:
            dirs[:] = [dirname for dirname in dirs if not (root_path / dirname).is_symlink()]

        for filename in files:
            file_path = root_path / filename
            if file_path.is_symlink() and not follow_symlinks:
                continue
            yield file_path


def get_file_hash(file_path: Path, algorithm: str, chunk_size_bytes: int) -> str | None:
    hasher = hashlib.new(algorithm)
    try:
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size_bytes)
                if not chunk:
                    break
                hasher.update(chunk)
    except (PermissionError, OSError):
        return None
    return hasher.hexdigest()


def find_duplicates(
    target_path: Path,
    algorithm: str,
    chunk_size_bytes: int,
    follow_symlinks: bool,
    verbose: bool,
) -> tuple[list[DuplicateEntry], list[str], int]:
    size_buckets: dict[int, list[Path]] = defaultdict(list)
    warnings: list[str] = []
    scanned_files = 0

    for file_path in iter_files(target_path, follow_symlinks=follow_symlinks):
        try:
            stat_info = file_path.stat(follow_symlinks=follow_symlinks)
        except (PermissionError, OSError) as exc:
            warnings.append(f"[WARN] Gagal baca metadata: {file_path} ({exc})")
            continue

        if not file_path.is_file():
            continue

        scanned_files += 1
        size_buckets[stat_info.st_size].append(file_path)

    duplicates: list[DuplicateEntry] = []

    for size_bytes, paths in size_buckets.items():
        if len(paths) < 2:
            continue

        hash_to_original: dict[str, Path] = {}
        for file_path in paths:
            file_hash = get_file_hash(file_path, algorithm=algorithm, chunk_size_bytes=chunk_size_bytes)
            if not file_hash:
                warnings.append(f"[WARN] Gagal hashing: {file_path}")
                continue

            original = hash_to_original.get(file_hash)
            if original is None:
                hash_to_original[file_hash] = file_path
                continue

            duplicates.append(
                DuplicateEntry(
                    original_path=original,
                    duplicate_path=file_path,
                    file_hash=file_hash,
                    size_bytes=size_bytes,
                )
            )

            if verbose:
                print(f"[FOUND] Duplikat: {file_path} | Original: {original}")

    return duplicates, warnings, scanned_files


def create_duplicate_output_dir(parent_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = parent_dir / f"duplicates-{timestamp}"

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=False)
        return output_dir

    # Sangat jarang terjadi, tapi dijaga bila eksekusi di detik yang sama.
    suffix = 2
    while True:
        candidate = parent_dir / f"duplicates-{timestamp}_{suffix}"
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        suffix += 1


def ensure_unique_destination(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = path.with_name(f"{stem}__dupe_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def move_duplicates_to_dir(
    duplicates: list[DuplicateEntry],
    target_path: Path,
    destination_root: Path,
    verbose: bool,
) -> tuple[int, list[str]]:
    moved_count = 0
    warnings: list[str] = []

    for entry in duplicates:
        try:
            relative_path = entry.duplicate_path.relative_to(target_path)
        except ValueError:
            relative_path = Path(entry.duplicate_path.name)

        destination_path = destination_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path = ensure_unique_destination(destination_path)

        try:
            shutil.move(str(entry.duplicate_path), str(destination_path))
            moved_count += 1
            if verbose:
                print(f"[MOVE] {entry.duplicate_path} -> {destination_path}")
        except FileNotFoundError:
            warnings.append(f"[WARN] File sudah tidak ada saat dipindahkan: {entry.duplicate_path}")
        except (PermissionError, OSError, shutil.Error) as exc:
            warnings.append(f"[WARN] Gagal memindahkan: {entry.duplicate_path} ({exc})")

    return moved_count, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Deteksi file duplikat berdasarkan ukuran+hash dalam folder target, "
            "lalu pindahkan file duplikat ke folder baru di parent target."
        )
    )
    parser.add_argument("target_path", nargs="?", help="Path folder yang ingin dipindai")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Tampilkan detail file duplikat yang ditemukan/dipindahkan",
    )
    return parser.parse_args()


def resolve_target_path(arg_target_path: str | None) -> Path | None:
    if arg_target_path:
        raw_value = arg_target_path.strip()
    else:
        raw_value = input("Masukkan path folder target: ").strip()

    if not raw_value:
        return None

    return Path(raw_value).expanduser().resolve()


def main() -> int:
    args = parse_args()

    target_path = resolve_target_path(args.target_path)
    if target_path is None:
        print("[ERROR] Path folder target wajib diisi.")
        return 1

    if not target_path.exists() or not target_path.is_dir():
        print(f"[ERROR] target_path tidak valid: {target_path}")
        return 1

    chunk_size_bytes = int(DEFAULT_CHUNK_SIZE_MB * 1024 * 1024)
    if chunk_size_bytes <= 0:
        print("[ERROR] Konfigurasi chunk size tidak valid")
        return 1

    print(f"[*] Mulai scan folder: {target_path}")
    print(
        f"[*] Algoritma hash: {DEFAULT_HASH_ALGORITHM} | "
        f"Chunk size: {DEFAULT_CHUNK_SIZE_MB:.2f} MB | Scan rekursif subfolder: aktif"
    )

    duplicates, scan_warnings, scanned_files = find_duplicates(
        target_path=target_path,
        algorithm=DEFAULT_HASH_ALGORITHM,
        chunk_size_bytes=chunk_size_bytes,
        follow_symlinks=False,
        verbose=args.verbose,
    )

    total_duplicate_bytes = sum(item.size_bytes for item in duplicates)
    unique_hashes = len({item.file_hash for item in duplicates})

    print(f"[*] Total file dipindai: {scanned_files}")
    print(f"[*] Total file duplikat: {len(duplicates)}")
    print(f"[*] Total grup hash duplikat: {unique_hashes}")
    print(f"[*] Total ukuran duplikat: {total_duplicate_bytes:,} bytes")

    if scan_warnings:
        print(f"[*] Warning selama scan: {len(scan_warnings)}")
        for warning in scan_warnings[:20]:
            print(warning)
        if len(scan_warnings) > 20:
            print(f"[INFO] {len(scan_warnings) - 20} warning tambahan tidak ditampilkan")

    if not duplicates:
        print("[OK] Tidak ada duplikat. Tidak ada file yang diubah.")
        return 0

    destination_root = create_duplicate_output_dir(target_path.parent.resolve())
    moved_count, move_warnings = move_duplicates_to_dir(
        duplicates=duplicates,
        target_path=target_path,
        destination_root=destination_root,
        verbose=args.verbose,
    )

    print(f"[OK] Folder duplikat dibuat: {destination_root}")
    print(f"[OK] File duplikat berhasil dipindahkan: {moved_count}/{len(duplicates)}")

    if move_warnings:
        print(f"[*] Warning saat memindahkan file: {len(move_warnings)}")
        for warning in move_warnings[:20]:
            print(warning)
        if len(move_warnings) > 20:
            print(f"[INFO] {len(move_warnings) - 20} warning tambahan tidak ditampilkan")

    if moved_count != len(duplicates):
        print(
            "[INFO] Sebagian file duplikat gagal dipindahkan. "
            "Cek warning untuk detailnya."
        )

    print("[DONE] Proses deduplikasi selesai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())