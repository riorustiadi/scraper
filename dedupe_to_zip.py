from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DuplicateEntry:
    original_path: Path
    duplicate_path: Path
    file_hash: str
    size_bytes: int


def sanitize_name(raw_name: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", raw_name).strip("._")
    return safe or "target"


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


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


def build_manifest_csv(duplicates: list[DuplicateEntry], target_path: Path) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "hash",
            "size_bytes",
            "original_path",
            "duplicate_path",
            "duplicate_relative_path",
        ]
    )

    for index, entry in enumerate(duplicates, start=1):
        try:
            duplicate_relative = entry.duplicate_path.relative_to(target_path).as_posix()
        except ValueError:
            duplicate_relative = entry.duplicate_path.as_posix()

        writer.writerow(
            [
                index,
                entry.file_hash,
                entry.size_bytes,
                str(entry.original_path),
                str(entry.duplicate_path),
                duplicate_relative,
            ]
        )

    return buffer.getvalue()


def unique_arcname(base_arcname: str, used_names: set[str]) -> str:
    if base_arcname not in used_names:
        used_names.add(base_arcname)
        return base_arcname

    stem, suffix = os.path.splitext(base_arcname)
    counter = 2
    while True:
        candidate = f"{stem}__dupe_{counter}{suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        counter += 1


def create_zip_archive(
    duplicates: list[DuplicateEntry],
    target_path: Path,
    output_zip_path: Path,
    manifest_csv: str,
    overwrite: bool,
) -> Path:
    temp_zip_path = output_zip_path.with_suffix(output_zip_path.suffix + ".part")

    if output_zip_path.exists() and not overwrite:
        raise FileExistsError(
            f"File ZIP sudah ada: {output_zip_path}. Gunakan --overwrite jika ingin menimpa."
        )

    if temp_zip_path.exists():
        temp_zip_path.unlink()

    used_names: set[str] = set()

    with zipfile.ZipFile(
        temp_zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=True,
    ) as zipf:
        for entry in duplicates:
            try:
                rel_path = entry.duplicate_path.relative_to(target_path).as_posix()
            except ValueError:
                rel_path = entry.duplicate_path.name

            arcname = unique_arcname(f"duplicates/{rel_path}", used_names)
            zipf.write(entry.duplicate_path, arcname=arcname)

        zipf.writestr("manifest_duplikat.csv", manifest_csv)

    with zipfile.ZipFile(temp_zip_path, mode="r") as zipf:
        bad_file = zipf.testzip()
        if bad_file is not None:
            raise RuntimeError(f"ZIP gagal verifikasi CRC, entry rusak: {bad_file}")

    if output_zip_path.exists() and overwrite:
        output_zip_path.unlink()

    temp_zip_path.replace(output_zip_path)
    return output_zip_path


def remove_duplicates(duplicates: list[DuplicateEntry]) -> tuple[int, list[str]]:
    removed_count = 0
    warnings: list[str] = []

    for entry in duplicates:
        try:
            entry.duplicate_path.unlink()
            removed_count += 1
        except FileNotFoundError:
            warnings.append(f"[WARN] File sudah tidak ada saat dihapus: {entry.duplicate_path}")
        except (PermissionError, OSError) as exc:
            warnings.append(f"[WARN] Gagal hapus: {entry.duplicate_path} ({exc})")

    return removed_count, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Deteksi file duplikat berdasarkan ukuran+hash dalam folder target, "
            "arsipkan duplikat ke ZIP di parent/output folder, lalu hapus file duplikat dari target."
        )
    )
    parser.add_argument("target_path", help="Path folder yang ingin dipindai")
    parser.add_argument(
        "--output-dir",
        help="Folder output ZIP dan manifest (default: parent dari target_path)",
    )
    parser.add_argument(
        "--zip-name",
        help="Nama file ZIP output (default otomatis: duplicates_<folder>_<timestamp>.zip)",
    )
    parser.add_argument(
        "--algorithm",
        default="sha256",
        choices=("sha256", "sha1", "md5"),
        help="Algoritma hashing (default: sha256)",
    )
    parser.add_argument(
        "--chunk-size-mb",
        type=float,
        default=4.0,
        help="Ukuran blok baca saat hashing dalam MB (default: 4.0)",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Ikuti symbolic link saat scan (default: tidak)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Hanya scan dan laporan, tanpa bikin ZIP atau hapus file",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Timpa file ZIP output jika sudah ada",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Tampilkan detail setiap file duplikat yang ditemukan",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    target_path = Path(args.target_path).expanduser().resolve()
    if not target_path.exists() or not target_path.is_dir():
        print(f"[ERROR] target_path tidak valid: {target_path}")
        return 1

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else target_path.parent.resolve()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    if is_relative_to(output_dir, target_path):
        print(
            "[ERROR] output_dir berada di dalam target_path. "
            "Pilih output di luar folder target untuk mencegah konflik scan."
        )
        return 1

    chunk_size_bytes = int(args.chunk_size_mb * 1024 * 1024)
    if chunk_size_bytes <= 0:
        print("[ERROR] --chunk-size-mb harus lebih besar dari 0")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_zip_name = f"duplicates_{sanitize_name(target_path.name)}_{timestamp}.zip"
    zip_name = args.zip_name or default_zip_name
    if not zip_name.lower().endswith(".zip"):
        zip_name = f"{zip_name}.zip"

    output_zip_path = output_dir / zip_name
    manifest_path = output_dir / f"{output_zip_path.stem}_manifest_duplikat.csv"

    print(f"[*] Mulai scan folder: {target_path}")
    print(f"[*] Algoritma hash: {args.algorithm} | Chunk size: {args.chunk_size_mb:.2f} MB")

    duplicates, scan_warnings, scanned_files = find_duplicates(
        target_path=target_path,
        algorithm=args.algorithm,
        chunk_size_bytes=chunk_size_bytes,
        follow_symlinks=args.follow_symlinks,
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

    manifest_csv = build_manifest_csv(duplicates, target_path=target_path)
    manifest_path.write_text(manifest_csv, encoding="utf-8")
    print(f"[*] Manifest disimpan: {manifest_path}")

    if args.dry_run:
        print("[DRY-RUN] Selesai. Tidak membuat ZIP dan tidak menghapus file.")
        return 0

    try:
        archived_zip = create_zip_archive(
            duplicates=duplicates,
            target_path=target_path,
            output_zip_path=output_zip_path,
            manifest_csv=manifest_csv,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"[ERROR] Gagal membuat ZIP: {exc}")
        return 1

    removed_count, remove_warnings = remove_duplicates(duplicates)
    print(f"[OK] ZIP berhasil dibuat: {archived_zip}")
    print(f"[OK] File duplikat terhapus: {removed_count}/{len(duplicates)}")

    if remove_warnings:
        print(f"[*] Warning saat hapus file: {len(remove_warnings)}")
        for warning in remove_warnings[:20]:
            print(warning)
        if len(remove_warnings) > 20:
            print(f"[INFO] {len(remove_warnings) - 20} warning tambahan tidak ditampilkan")

    if removed_count != len(duplicates):
        print(
            "[INFO] Sebagian file duplikat gagal dihapus. "
            "Cek warning, tapi ZIP cadangan sudah tersedia."
        )

    print("[DONE] Proses deduplikasi selesai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())