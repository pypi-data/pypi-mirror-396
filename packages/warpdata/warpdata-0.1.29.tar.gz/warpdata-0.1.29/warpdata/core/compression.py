"""
Fast compression utilities for warpdata.

Tries fast methods first, falls back to slower ones:
1. pigz (parallel gzip) - fastest, standard .tar.gz output
2. zstd (zstandard) - very fast, .tar.zst output
3. gzip level 1 - fallback, single-threaded but faster than default

For decompression, auto-detects format from file content.
"""
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def _has_pigz() -> bool:
    """Check if pigz is available."""
    return shutil.which('pigz') is not None


def _has_zstd_cli() -> bool:
    """Check if zstd CLI is available."""
    return shutil.which('zstd') is not None


def _has_zstd_lib() -> bool:
    """Check if zstandard Python library is available."""
    try:
        import zstandard
        return True
    except ImportError:
        return False


def compress_directory(
    source_dir: Path,
    output_path: Optional[Path] = None,
    method: str = "auto",
    verbose: bool = True,
) -> Tuple[Path, str, int]:
    """
    Compress a directory using the fastest available method.

    Args:
        source_dir: Directory to compress
        output_path: Output file path (optional, creates temp file if None)
        method: Compression method - "auto", "pigz", "zstd", "gzip"
        verbose: Print progress messages

    Returns:
        Tuple of (archive_path, compression_format, compressed_size)
        compression_format is "tar.gz" or "tar.zst"
    """
    source_dir = Path(source_dir)

    if method == "auto":
        # Try fastest first
        if _has_pigz():
            method = "pigz"
        elif _has_zstd_cli() or _has_zstd_lib():
            method = "zstd"
        else:
            method = "gzip"

    if method == "pigz":
        return _compress_with_pigz(source_dir, output_path, verbose)
    elif method == "zstd":
        return _compress_with_zstd(source_dir, output_path, verbose)
    else:
        return _compress_with_gzip(source_dir, output_path, verbose)


def _compress_with_pigz(
    source_dir: Path,
    output_path: Optional[Path],
    verbose: bool,
) -> Tuple[Path, str, int]:
    """Compress using pigz (parallel gzip)."""
    if output_path is None:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.tar.gz', prefix='warp_')
        os.close(temp_fd)
        output_path = Path(temp_path)

    if verbose:
        print(f"  ⚡ Using pigz (parallel gzip)")

    # Get number of CPU cores, use all but leave 1 for system
    num_cores = max(1, (os.cpu_count() or 4) - 1)

    # tar cf - dir | pigz -p N > output.tar.gz
    try:
        with open(output_path, 'wb') as f:
            tar_proc = subprocess.Popen(
                ['tar', 'cf', '-', '-C', str(source_dir.parent), source_dir.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pigz_proc = subprocess.Popen(
                ['pigz', '-p', str(num_cores)],
                stdin=tar_proc.stdout,
                stdout=f,
                stderr=subprocess.PIPE,
            )
            tar_proc.stdout.close()
            pigz_proc.communicate()
            tar_proc.wait()

        if pigz_proc.returncode != 0 or tar_proc.returncode != 0:
            raise subprocess.CalledProcessError(1, 'pigz')

        compressed_size = output_path.stat().st_size
        return output_path, "tar.gz", compressed_size

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to zstd or gzip
        if verbose:
            print(f"  ⚠ pigz failed, falling back...")
        if _has_zstd_cli() or _has_zstd_lib():
            return _compress_with_zstd(source_dir, output_path, verbose)
        return _compress_with_gzip(source_dir, output_path, verbose)


def _compress_with_zstd(
    source_dir: Path,
    output_path: Optional[Path],
    verbose: bool,
) -> Tuple[Path, str, int]:
    """Compress using zstd (zstandard)."""
    # Determine output path
    if output_path is None:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.tar.zst', prefix='warp_')
        os.close(temp_fd)
        output_path = Path(temp_path)
    else:
        # Change extension to .tar.zst
        output_path = output_path.with_suffix('.tar.zst')

    if verbose:
        print(f"  ⚡ Using zstd (fast compression)")

    # Try CLI first (faster), then Python library
    if _has_zstd_cli():
        try:
            num_cores = max(1, (os.cpu_count() or 4) - 1)

            with open(output_path, 'wb') as f:
                tar_proc = subprocess.Popen(
                    ['tar', 'cf', '-', '-C', str(source_dir.parent), source_dir.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                zstd_proc = subprocess.Popen(
                    ['zstd', '-T' + str(num_cores), '-'],
                    stdin=tar_proc.stdout,
                    stdout=f,
                    stderr=subprocess.PIPE,
                )
                tar_proc.stdout.close()
                zstd_proc.communicate()
                tar_proc.wait()

            if zstd_proc.returncode == 0 and tar_proc.returncode == 0:
                compressed_size = output_path.stat().st_size
                return output_path, "tar.zst", compressed_size

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fall back to Python library
    if _has_zstd_lib():
        import zstandard as zstd

        # Create tar first, then compress
        temp_fd, temp_tar = tempfile.mkstemp(suffix='.tar', prefix='warp_')
        os.close(temp_fd)

        try:
            with tarfile.open(temp_tar, 'w') as tar:
                tar.add(source_dir, arcname=source_dir.name)

            # Compress with zstd
            cctx = zstd.ZstdCompressor(level=3, threads=-1)  # -1 = auto threads
            with open(temp_tar, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    cctx.copy_stream(f_in, f_out)

            compressed_size = output_path.stat().st_size
            return output_path, "tar.zst", compressed_size

        finally:
            if Path(temp_tar).exists():
                Path(temp_tar).unlink()

    # Fall back to gzip
    if verbose:
        print(f"  ⚠ zstd failed, falling back to gzip...")
    return _compress_with_gzip(source_dir, output_path, verbose)


def _compress_with_gzip(
    source_dir: Path,
    output_path: Optional[Path],
    verbose: bool,
) -> Tuple[Path, str, int]:
    """Compress using gzip level 1 (fast single-threaded)."""
    if output_path is None:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.tar.gz', prefix='warp_')
        os.close(temp_fd)
        output_path = Path(temp_path)
    else:
        # Ensure .tar.gz extension
        if not str(output_path).endswith('.tar.gz'):
            output_path = Path(str(output_path).replace('.tar.zst', '.tar.gz'))

    if verbose:
        print(f"  📦 Using gzip level 1 (single-threaded)")

    # Use compresslevel=1 for speed (default is 9)
    with tarfile.open(output_path, 'w:gz', compresslevel=1) as tar:
        tar.add(source_dir, arcname=source_dir.name)

    compressed_size = output_path.stat().st_size
    return output_path, "tar.gz", compressed_size


def decompress_archive(
    archive_path: Path,
    output_dir: Path,
    compression_format: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Decompress an archive to output directory.

    Auto-detects format from file magic or extension if not specified.
    Supports both tar.gz and tar.zst formats.

    Args:
        archive_path: Path to compressed archive
        output_dir: Directory to extract to
        compression_format: Optional hint - "tar.gz" or "tar.zst"
        verbose: Print progress messages
    """
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Auto-detect format
    if compression_format is None:
        compression_format = _detect_compression_format(archive_path)

    if compression_format == "tar.zst":
        _decompress_zstd(archive_path, output_dir, verbose)
    else:
        _decompress_gzip(archive_path, output_dir, verbose)


def _detect_compression_format(archive_path: Path) -> str:
    """Detect compression format from file magic bytes."""
    with open(archive_path, 'rb') as f:
        magic = f.read(4)

    # zstd magic: 0x28B52FFD
    if magic[:4] == b'\x28\xb5\x2f\xfd':
        return "tar.zst"

    # gzip magic: 0x1F8B
    if magic[:2] == b'\x1f\x8b':
        return "tar.gz"

    # Fall back to extension
    if str(archive_path).endswith('.zst'):
        return "tar.zst"

    return "tar.gz"


def _decompress_gzip(archive_path: Path, output_dir: Path, verbose: bool) -> None:
    """Decompress tar.gz archive."""
    if verbose:
        print(f"  📂 Extracting tar.gz...")

    # Try pigz for parallel decompression if available
    if _has_pigz():
        try:
            with open(archive_path, 'rb') as f:
                pigz_proc = subprocess.Popen(
                    ['pigz', '-d', '-c'],
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                tar_proc = subprocess.Popen(
                    ['tar', 'xf', '-', '-C', str(output_dir)],
                    stdin=pigz_proc.stdout,
                    stderr=subprocess.PIPE,
                )
                pigz_proc.stdout.close()
                tar_proc.communicate()
                pigz_proc.wait()

            if tar_proc.returncode == 0 and pigz_proc.returncode == 0:
                return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fall back to Python tarfile
    with tarfile.open(archive_path, 'r:gz') as tar:
        tar.extractall(path=output_dir)


def _decompress_zstd(archive_path: Path, output_dir: Path, verbose: bool) -> None:
    """Decompress tar.zst archive."""
    if verbose:
        print(f"  📂 Extracting tar.zst...")

    # Try CLI first
    if _has_zstd_cli():
        try:
            with open(archive_path, 'rb') as f:
                zstd_proc = subprocess.Popen(
                    ['zstd', '-d', '-c'],
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                tar_proc = subprocess.Popen(
                    ['tar', 'xf', '-', '-C', str(output_dir)],
                    stdin=zstd_proc.stdout,
                    stderr=subprocess.PIPE,
                )
                zstd_proc.stdout.close()
                tar_proc.communicate()
                zstd_proc.wait()

            if tar_proc.returncode == 0 and zstd_proc.returncode == 0:
                return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fall back to Python library
    if _has_zstd_lib():
        import zstandard as zstd

        # Decompress to temp tar, then extract
        temp_fd, temp_tar = tempfile.mkstemp(suffix='.tar', prefix='warp_')
        os.close(temp_fd)

        try:
            dctx = zstd.ZstdDecompressor()
            with open(archive_path, 'rb') as f_in:
                with open(temp_tar, 'wb') as f_out:
                    dctx.copy_stream(f_in, f_out)

            with tarfile.open(temp_tar, 'r') as tar:
                tar.extractall(path=output_dir)

        finally:
            if Path(temp_tar).exists():
                Path(temp_tar).unlink()
        return

    raise RuntimeError(
        f"Cannot decompress {archive_path}: zstd not available. "
        "Install with: pip install zstandard"
    )


def get_compression_info() -> dict:
    """Get info about available compression methods."""
    return {
        "pigz": _has_pigz(),
        "zstd_cli": _has_zstd_cli(),
        "zstd_lib": _has_zstd_lib(),
        "recommended": (
            "pigz" if _has_pigz()
            else "zstd" if (_has_zstd_cli() or _has_zstd_lib())
            else "gzip"
        ),
    }
