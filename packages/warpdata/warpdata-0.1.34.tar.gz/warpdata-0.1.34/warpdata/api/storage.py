"""
Storage API for warpdata.

Provides high-level functions for:
- Getting dataset provenance (raw data sources)
- Backing up datasets to cloud storage
- Restoring datasets from cloud storage
- Syncing datasets to cloud storage
"""
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

import fsspec

from ..core.uris import parse_uri, require_warpdata_id
from ..core.registry import get_registry, get_registry_readonly
from ..core.config import get_config
from ..core.utils import ensure_dir
from ..core.storage import get_storage_backend
from ..core.storage.bucket_utils import normalize_bucket_name
from ..core.manifest import normalize_resources, resource_uris, build_cloud_manifest

# Default S3 bucket for warpdata
DEFAULT_BUCKET = "warp"

# Cache for S3 object listings to avoid repeated scans
_s3_objects_cache: Dict[str, list] = {}
_s3_datasets_cache: Dict[str, List[Dict]] = {}


def get_raw_data_sources(dataset_id: str) -> List[Dict[str, Any]]:
    """
    Get raw data sources for a dataset.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://arxiv/papers')

    Returns:
        List of raw data source dictionaries

    Examples:
        >>> import warpdata as wd
        >>> sources = wd.get_raw_data_sources("warpdata://arxiv/papers")
        >>> for source in sources:
        ...     print(f"{source['source_type']}: {source['source_path']} ({source['size']} bytes)")
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(workspace, name, version)

    if not dataset_ver:
        raise ValueError(f"Dataset not found: {dataset_id}")

    version_hash = dataset_ver["version_hash"]
    return registry.list_raw_data_sources(workspace, name, version_hash)


def backup_dataset(
    dataset_id: str,
    backend: str = "s3",
    bucket: Optional[str] = None,
    include_raw: bool = True,
    progress: bool = True,
) -> Dict[str, Any]:
    """
    Backup dataset to cloud storage.

    Args:
        dataset_id: Dataset ID
        backend: Storage backend ('s3')
        bucket: S3 bucket name (required for S3)
        include_raw: Whether to backup raw data sources

    Returns:
        Dictionary with backup info (files uploaded, total size, etc.)

    Examples:
        >>> import warpdata as wd
        >>> info = wd.backup_dataset(
        ...     "warpdata://arxiv/papers",
        ...     backend="s3",
        ...     bucket="my-warp-backup",
        ...     include_raw=True
        ... )
        >>> print(f"Backed up {info['total_files']} files ({info['total_size']} bytes)")
    """
    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get dataset version (read-only - backup only reads registry)
    registry = get_registry_readonly()
    dataset_ver = registry.get_dataset_version(workspace, name, version)
    if not dataset_ver:
        raise ValueError(f"Dataset not found: {dataset_id}")

    version_hash = dataset_ver["version_hash"]
    manifest = registry.get_manifest(workspace, name, version_hash)
    if not manifest:
        raise ValueError(f"Manifest not found for {dataset_id}")

    # Initialize storage backend
    storage_config = {}
    if backend == "s3":
        if not bucket:
            raise ValueError("S3 backend requires 'bucket' parameter")
        # Normalize bucket name (add warpbucket- prefix if needed)
        bucket = normalize_bucket_name(bucket)
        storage_config["bucket"] = bucket
        storage_config["prefix"] = "warp"  # Use warp/objects/ path

    storage = get_storage_backend(backend, **storage_config)

    uploaded_files = []
    total_size = 0

    # Backup dataset resources
    from ..core.cache import get_cache
    from tqdm import tqdm
    cache = get_cache()

    resources = normalize_resources(manifest.get("resources"))
    for resource in tqdm(resources, desc=f"  Uploading {workspace}/{name}", unit="file", disable=not progress):
        resource_uri = resource["uri"]
        local_path = cache.get(resource_uri)

        # Get file extension from local path for format detection
        extension = local_path.suffix.lstrip('.') if local_path.suffix else 'parquet'

        content_hash = storage.put(
            local_path,
            metadata={
                "type": "dataset_resource",
                "dataset": f"{workspace}/{name}",
                "version": version_hash,
                "extension": extension,
            },
            overwrite=False,
            show_progress=True,
        )

        uploaded_files.append({
            "type": "resource",
            "uri": resource_uri,
            "hash": content_hash,
            "size": local_path.stat().st_size,
        })
        total_size += local_path.stat().st_size

    # Backup embedding spaces (vectors/index files)
    try:
        spaces = get_registry_readonly().list_embedding_spaces(workspace, name, version_hash)
    except Exception:
        spaces = []

    from ..core.cache import get_cache as _get_cache
    _cache = _get_cache()

    for space in spaces or []:
        storage_path = Path(space.get("storage_path", ""))
        if not storage_path:
            continue
        # Upload known files if present
        for fname in ("vectors.parquet", "index.faiss"):
            fpath = storage_path / fname
            if not fpath.exists():
                continue
            content_hash = storage.put(
                fpath,
                metadata={
                    "type": "embedding",
                    "dataset": f"{workspace}/{name}",
                    "version": version_hash,
                    "space": space.get("space_name"),
                    "provider": space.get("provider"),
                    "model": space.get("model"),
                    "dimension": str(space.get("dimension", "")),
                    "distance": space.get("distance_metric", "cosine"),
                    "filename": fname,
                },
                overwrite=False,
            )
            uploaded_files.append({
                "type": "embedding",
                "space": space.get("space_name"),
                "file": fname,
                "hash": content_hash,
                "size": fpath.stat().st_size,
            })
            total_size += fpath.stat().st_size

    # Backup raw data if requested
    if include_raw:
        raw_sources = registry.list_raw_data_sources(workspace, name, version_hash)

        for source in raw_sources:
            source_path = Path(source["source_path"])

            if not source_path.exists():
                print(f"Warning: Raw data source not found, skipping: {source_path}")
                continue

            if source_path.is_file():
                content_hash = storage.put(
                    source_path,
                    metadata={
                        "type": "raw_data",
                        "dataset": f"{workspace}/{name}",
                        "version": version_hash,
                        "source_type": source["source_type"],
                    },
                    overwrite=False,
                )

                uploaded_files.append({
                    "type": "raw_data",
                    "path": str(source_path),
                    "hash": content_hash,
                    "size": source_path.stat().st_size,
                })
                total_size += source_path.stat().st_size

            elif source_path.is_dir():
                # Check if already uploaded (has content_hash in registry)
                existing_hash = source.get('content_hash')
                if existing_hash:
                    try:
                        if storage.exists(existing_hash):
                            print(f"  ✓ Raw directory already in cloud: {source_path.name}")
                            continue
                    except Exception:
                        pass  # Fall through to upload

                # Compress directory and upload
                from ..core.compression import compress_directory

                # Calculate directory size
                dir_size = 0
                for sub in source_path.rglob('*'):
                    try:
                        if sub.is_file():
                            dir_size += sub.stat().st_size
                    except Exception:
                        continue

                print(f"  📂 Compressing directory: {source_path.name} ({dir_size / 1e6:.1f} MB)")

                temp_archive = None
                try:
                    # Compress using fastest available method (pigz > zstd > gzip)
                    temp_archive, compression_format, compressed_size = compress_directory(
                        source_path, verbose=True
                    )

                    compression_ratio = compressed_size / dir_size * 100 if dir_size > 0 else 100
                    print(f"  ✓ Compressed: {compressed_size / 1e6:.1f} MB ({compression_ratio:.1f}% of original)")

                    # Upload compressed archive
                    content_hash = storage.put(
                        Path(temp_archive),
                        metadata={
                            "type": "raw_data_directory_compressed",
                            "dataset": f"{workspace}/{name}",
                            "version": version_hash,
                            "source_dir": source_path.name,
                            "compression": compression_format,
                            "original_size": str(dir_size),
                        },
                        overwrite=False,
                    )

                    print(f"  ✓ Uploaded compressed directory: {source_path.name}")

                    uploaded_files.append({
                        "type": "raw_data_directory",
                        "path": str(source_path),
                        "hash": content_hash,
                        "size": dir_size,
                        "compressed_size": compressed_size,
                        "compression_format": compression_format,
                    })
                    total_size += compressed_size

                finally:
                    # Clean up temp file
                    if temp_archive and Path(temp_archive).exists():
                        Path(temp_archive).unlink()

    # Build and upload cloud manifest
    if backend == "s3":
        # Collect manifest resources
        manifest_resources = []
        manifest_embeddings = []
        manifest_raw_data = []

        for f in uploaded_files:
            if f["type"] == "resource":
                # Build S3 URI from hash
                h = f["hash"]
                s3_uri = f"s3://{bucket}/warp/objects/{h[:2]}/{h[2:4]}/{h}"
                manifest_resources.append({
                    "content_hash": h,
                    "uri": s3_uri,
                    "size": f["size"],
                    "extension": Path(f.get("uri", "")).suffix.lstrip('.') or "parquet",
                })
            elif f["type"] == "embedding":
                # Group embeddings by space
                space_name = f.get("space", "default")
                h = f["hash"]
                s3_uri = f"s3://{bucket}/warp/objects/{h[:2]}/{h[2:4]}/{h}"
                # Find or create embedding entry
                existing = next((e for e in manifest_embeddings if e["space_name"] == space_name), None)
                if not existing:
                    existing = {"space_name": space_name, "files": []}
                    manifest_embeddings.append(existing)
                existing["files"].append({
                    "name": f.get("file", "vectors.parquet"),
                    "content_hash": h,
                    "size": f["size"],
                    "uri": s3_uri,
                })
            elif f["type"] in ("raw_data", "raw_data_directory"):
                h = f["hash"]
                s3_uri = f"s3://{bucket}/warp/objects/{h[:2]}/{h[2:4]}/{h}"
                manifest_raw_data.append({
                    "source_path": f.get("path", ""),
                    "source_type": "directory" if f["type"] == "raw_data_directory" else "file",
                    "content_hash": h,
                    "size": f["size"],
                    "compressed": f.get("compressed_size") is not None,
                    "compression_format": f.get("compression_format") if f.get("compressed_size") else None,
                    "uri": s3_uri,
                })

        # Get schema from manifest if available
        schema_dict = manifest.get("schema", {}) if manifest else {}

        # Build cloud manifest
        cloud_manifest = build_cloud_manifest(
            workspace=workspace,
            name=name,
            version_hash=version_hash,
            resources=manifest_resources,
            schema=schema_dict,
            row_count=manifest.get("row_count") if manifest else None,
            embeddings=manifest_embeddings,
            raw_data=manifest_raw_data,
            metadata=manifest.get("metadata") if manifest else None,
        )

        # Upload manifest
        try:
            manifest_key = storage.put_manifest(
                workspace=workspace,
                name=name,
                version_hash=version_hash,
                manifest_data=cloud_manifest,
                update_latest=True,
            )
            print(f"  ✓ Uploaded manifest: {manifest_key}")
        except Exception as e:
            print(f"  ⚠️  Failed to upload manifest: {e}")

    return {
        "dataset_id": dataset_id,
        "version_hash": version_hash,
        "backend": backend,
        "total_files": len(uploaded_files),
        "total_size": total_size,
        "files": uploaded_files,
    }


def restore_dataset(
    dataset_id: str,
    backend: str = "s3",
    bucket: Optional[str] = None,
    include_raw: bool = True,
    include_embeddings: bool = False,
    output_dir: Optional[str] = None,
    max_raw_size: Optional[int] = None,
    progress: bool = True,
    max_bytes: Optional[int] = None,
    max_files: Optional[int] = None,
    workers: int = 1,
) -> Dict[str, Any]:
    """
    Restore dataset from cloud storage.

    Args:
        dataset_id: Dataset ID
        backend: Storage backend ('s3')
        bucket: S3 bucket name (default: 'warp')
        include_raw: Whether to restore raw data sources
        include_embeddings: Whether to restore embeddings (slow - scans all objects)
        output_dir: Output directory (defaults to cache)
        max_raw_size: Maximum size of raw data to restore
        progress: Show progress bar
        max_bytes: Maximum total bytes to download (for sampling)
        max_files: Maximum number of files to download (for sampling)
        workers: Number of parallel download workers (default: 1 for sequential)

    Returns:
        Dictionary with restore info

    Examples:
        >>> import warpdata as wd
        >>> info = wd.restore_dataset(
        ...     "warpdata://arxiv/papers",
        ...     backend="s3",
        ...     bucket="my-warp-backup",
        ...     include_raw=True,
        ...     output_dir="./restored"
        ... )
        >>> print(f"Restored {info['total_files']} files to {info['output_dir']}")
    """
    from tqdm import tqdm

    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    workspace = uri.workspace
    name = uri.name
    version = uri.version or "latest"

    # Get dataset version
    registry = get_registry()
    dataset_ver = registry.get_dataset_version(workspace, name, version)
    if not dataset_ver:
        raise ValueError(f"Dataset not found: {dataset_id}")

    version_hash = dataset_ver["version_hash"]

    # Initialize storage backend
    storage_config = {}
    if backend == "s3":
        if not bucket:
            bucket = DEFAULT_BUCKET
        bucket = normalize_bucket_name(bucket)
        storage_config["bucket"] = bucket

    storage = get_storage_backend(backend, **storage_config)

    # Setup output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        from ..core.cache import get_cache
        output_path = get_cache().datasets_dir / workspace / name / version_hash

    downloaded_files = []
    total_size = 0

    # Restore dataset resources (parquet/arrow files)
    manifest = registry.get_manifest(workspace, name, version_hash)
    if manifest:
        from ..core.cache import get_cache
        cache = get_cache()

        resources = normalize_resources(manifest.get("resources"))

        # Apply sampling limits if specified
        original_count = len(resources)
        if max_files and len(resources) > max_files:
            resources = resources[:max_files]
            print(f"  📊 Sampling: {len(resources)}/{original_count} files (max_files={max_files})")

        if max_bytes:
            cumulative = 0
            selected = []
            for r in resources:
                r_size = r.get('size') or 0
                if cumulative + r_size > max_bytes:
                    break
                selected.append(r)
                cumulative += r_size
            if len(selected) < len(resources):
                print(f"  📊 Sampling: {len(selected)}/{len(resources)} files (max_bytes={max_bytes / 1e6:.1f}MB)")
                resources = selected

        # Calculate total size for better progress display
        total_bytes = sum(r.get('size') or 0 for r in resources)
        total_mb = total_bytes / 1e6

        # Helper function to download a single resource
        def download_single_resource(resource):
            """Download a single resource and return result dict."""
            resource_uri = resource["uri"]

            if not resource_uri.startswith("s3://"):
                return None

            # Extract content hash from S3 key
            parts = resource_uri.split("/")
            if 'objects' not in parts or len(parts) == 0:
                return None
            content_hash = parts[-1]
            expected_size = resource.get('size')

            try:
                cache_path = cache.get(resource_uri)

                # Verify size if we have expected size
                if expected_size is not None:
                    actual_size = cache_path.stat().st_size
                    if actual_size != expected_size:
                        # Force re-download
                        cache_path.unlink()
                        cache_path = cache.get(resource_uri, force_refresh=True)
                        file_size = cache_path.stat().st_size
                        if file_size != expected_size:
                            cache_path.unlink()
                            return {"error": f"Size mismatch for {content_hash[:16]}"}
                        return {"type": "dataset_resource", "hash": content_hash, "path": str(cache_path), "size": file_size, "redownloaded": True}
                    else:
                        return {"type": "dataset_resource", "hash": content_hash, "path": str(cache_path), "size": actual_size}
                else:
                    file_size = cache_path.stat().st_size
                    return {"type": "dataset_resource", "hash": content_hash, "path": str(cache_path), "size": file_size}
            except Exception as e:
                return {"error": str(e)}

        downloaded_bytes = 0

        if workers > 1:
            # Parallel download with ThreadPoolExecutor
            from concurrent.futures import ThreadPoolExecutor, as_completed

            pbar = tqdm(
                total=len(resources),
                desc=f"  Downloading {workspace}/{name} ({total_mb:.0f} MB) [{workers} workers]",
                unit="file",
                disable=not progress
            )

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(download_single_resource, r): r for r in resources}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        if "error" in result:
                            print(f"      ✗ {result['error']}")
                        else:
                            downloaded_files.append(result)
                            total_size += result.get("size", 0)
                            downloaded_bytes += result.get("size", 0)
                    pbar.update(1)
                    pbar.set_postfix_str(f"{downloaded_bytes/1e6:.0f}/{total_mb:.0f} MB")

            pbar.close()
        else:
            # Sequential download (original behavior)
            pbar = tqdm(
                resources,
                desc=f"  Downloading {workspace}/{name} ({total_mb:.0f} MB)",
                unit="file",
                disable=not progress
            )
            for resource in pbar:
                result = download_single_resource(resource)
                if result:
                    if "error" in result:
                        print(f"      ✗ {result['error']}")
                    else:
                        if result.get("redownloaded"):
                            print(f"    ✓ Re-downloaded: {result['hash'][:16]}")
                        downloaded_files.append(result)
                        total_size += result.get("size", 0)
                        downloaded_bytes += result.get("size", 0)
                pbar.set_postfix_str(f"{downloaded_bytes/1e6:.0f}/{total_mb:.0f} MB")

    # Restore embeddings (if present in remote) - best effort, non-fatal
    # This is slow because it scans all objects in the bucket, so it's opt-in
    if include_embeddings and backend == "s3" and bucket:
        try:
            import boto3
            s3 = boto3.client('s3')
            from ..core.cache import get_cache as _get_cache
            _cache = _get_cache()
            dataset_cache_dir = _cache.get_dataset_cache_dir(workspace, name, version_hash)
            embeddings_root = dataset_cache_dir / 'embeddings'
            paginator = s3.get_paginator('list_objects_v2')
            spaces_meta: dict[str, dict] = {}
            objects: list[dict] = []
            for page in paginator.paginate(Bucket=bucket, Prefix='warp/objects/'):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    try:
                        meta = s3.head_object(Bucket=bucket, Key=key)
                    except Exception:
                        continue
                    md = meta.get('Metadata', {})
                    if md.get('type') != 'embedding':
                        continue
                    if md.get('dataset') != f"{workspace}/{name}" or md.get('version') != version_hash:
                        continue
                    # Derive content hash from key (last segment)
                    parts = key.split('/')
                    content_hash = parts[-1] if parts else None
                    if not content_hash:
                        continue
                    space_name = md.get('space') or 'default'
                    filename = md.get('filename') or 'vectors.parquet'
                    provider = md.get('provider') or 'sentence-transformers'
                    model = md.get('model') or 'unknown'
                    try:
                        dimension = int(md.get('dimension') or 0)
                    except Exception:
                        dimension = 0
                    distance = md.get('distance') or 'cosine'

                    # Ensure local dir
                    space_dir = embeddings_root / space_name
                    space_dir.mkdir(parents=True, exist_ok=True)

                    # Download to target path
                    target = space_dir / filename
                    try:
                        storage.get(content_hash, target)
                        size_bytes = target.stat().st_size
                        downloaded_files.append({
                            'type': 'embedding', 'space': space_name, 'file': filename,
                            'hash': content_hash, 'path': str(target), 'size': size_bytes,
                        })
                        total_size += size_bytes
                        spaces_meta[space_name] = {
                            'space_name': space_name,
                            'provider': provider,
                            'model': model,
                            'dimension': dimension,
                            'distance_metric': distance,
                            'storage_path': str(space_dir),
                        }
                    except Exception as e:
                        # Continue best-effort
                        pass

            # Register spaces discovered
            if spaces_meta:
                for sn, sm in spaces_meta.items():
                    try:
                        get_registry().register_embedding_space(
                            workspace=workspace,
                            name=name,
                            version_hash=version_hash,
                            space_name=sm['space_name'],
                            provider=sm['provider'],
                            model=sm['model'],
                            dimension=sm['dimension'] or 0,
                            distance_metric=sm['distance_metric'],
                            storage_path=sm['storage_path'],
                        )
                    except Exception:
                        # ignore if already registered or errors
                        pass
        except Exception as e:
            # Embeddings restore is optional, don't fail the whole operation
            print(f"  ⚠️  Skipping embeddings restore: {e}")

    # Restore raw data if requested
    if include_raw:
        raw_sources = registry.list_raw_data_sources(workspace, name, version_hash)

        # Calculate total raw data size
        total_raw_size = sum(source.get('size', 0) for source in raw_sources)

        # Check if raw data exceeds max_raw_size
        if max_raw_size and total_raw_size > max_raw_size:
            print(f"  ⚠️  Skipping raw data ({total_raw_size / 1e9:.2f} GB > {max_raw_size / 1e9:.2f} GB limit)")
        else:
            for source in raw_sources:
                if not source.get("content_hash"):
                    continue

                content_hash = source["content_hash"]
                source_path = Path(source["source_path"])

                # Check if this source is compressed
                source_metadata = source.get("metadata") or {}
                is_compressed = source_metadata.get("compressed", False)
                compression_format = source_metadata.get("compression_format", "tar.gz")

                # Restore to original path or output_dir
                if output_dir:
                    restore_path = output_path / "raw_data" / source_path.name
                else:
                    restore_path = source_path

                restore_path.parent.mkdir(parents=True, exist_ok=True)

                # Get expected size from source metadata
                expected_size = source.get('size')

                # Check if file/directory exists and verify
                needs_download = False
                if not restore_path.exists():
                    needs_download = True
                elif is_compressed and restore_path.is_dir():
                    # For compressed sources, we restore as directory, so check if directory has content
                    if not any(restore_path.iterdir()):
                        needs_download = True
                elif expected_size is not None and restore_path.is_file():
                    actual_size = restore_path.stat().st_size
                    if actual_size != expected_size:
                        print(f"  ⚠️  Raw data size mismatch: {restore_path.name} ({actual_size} != {expected_size}), re-downloading...")
                        needs_download = True

                if needs_download:
                    if is_compressed:
                        # Download compressed file to temp location and extract
                        from ..core.compression import decompress_archive
                        import tempfile
                        import os

                        print(f"  📥 Downloading compressed: {source_path.name}")

                        # Download to temp file (extension doesn't matter, format is auto-detected)
                        suffix = '.tar.zst' if compression_format == 'tar.zst' else '.tar.gz'
                        temp_fd, temp_archive = tempfile.mkstemp(suffix=suffix, prefix='warp_dl_')
                        os.close(temp_fd)

                        try:
                            storage.get(content_hash, Path(temp_archive))

                            # Extract using auto-detecting decompressor (handles tar.gz and tar.zst)
                            decompress_archive(
                                Path(temp_archive),
                                restore_path.parent,
                                compression_format=compression_format,
                                verbose=True,
                            )

                            print(f"  ✓ Restored compressed directory: {source_path.name}")

                            downloaded_files.append({
                                "type": "raw_data_directory",
                                "hash": content_hash,
                                "path": str(restore_path),
                                "size": source.get('size', 0),
                                "compressed": True,
                            })
                            total_size += source.get('size', 0)

                        finally:
                            # Clean up temp file
                            if Path(temp_archive).exists():
                                Path(temp_archive).unlink()
                    else:
                        # Regular file download
                        storage.get(content_hash, restore_path)

                        # Verify downloaded size (warning only, don't fail)
                        file_size = restore_path.stat().st_size
                        if expected_size is not None and file_size != expected_size:
                            print(f"  ⚠️  Raw data size mismatch: {file_size} != {expected_size} (continuing anyway)")

                        downloaded_files.append({
                            "type": "raw_data",
                            "hash": content_hash,
                            "path": str(restore_path),
                            "size": file_size,
                        })
                        total_size += file_size
                else:
                    # Already exists
                    if restore_path.is_file():
                        total_size += restore_path.stat().st_size
                    elif restore_path.is_dir():
                        total_size += source.get('size', 0)

    return {
        "dataset_id": dataset_id,
        "version_hash": version_hash,
        "output_dir": str(output_path),
        "total_files": len(downloaded_files),
        "total_size": total_size,
        "files": downloaded_files,
    }


def list_remote_datasets(
    backend: str = "s3",
    bucket: Optional[str] = None,
    progress: bool = True,
    workers: int = 32,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """
    List datasets available in cloud storage.

    Uses cloud manifests for O(1) discovery (no HEAD requests needed).
    For buckets without manifests, run: warp manifest generate --bucket <bucket>

    Args:
        backend: Storage backend ('s3')
        bucket: S3 bucket name (default: 'warp')
        progress: Show progress bar
        workers: Number of parallel workers (for fetching manifest details)
        use_cache: Use cached results if available

    Returns:
        List of dataset info dictionaries

    Examples:
        >>> datasets = wd.list_remote_datasets(backend='s3', bucket='mydata')
        >>> for ds in datasets:
        ...     print(f"{ds['dataset']} - {ds['size'] / 1e6:.1f} MB")
    """
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import json

    if backend != "s3":
        raise ValueError(f"Backend '{backend}' not supported")

    if not bucket:
        bucket = DEFAULT_BUCKET

    bucket = normalize_bucket_name(bucket)

    # Check cache
    cache_key = f"{backend}:{bucket}"
    if use_cache and cache_key in _s3_datasets_cache:
        return _s3_datasets_cache[cache_key]

    import boto3
    s3 = boto3.client('s3')

    # Fast path: List manifests (O(1) per dataset, no HEAD requests)
    manifest_keys = []
    paginator = s3.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=bucket, Prefix='warp/manifests/'):
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Skip latest.json pointers, only process versioned manifests
            if key.endswith('.json') and not key.endswith('/latest.json'):
                manifest_keys.append(key)

    if not manifest_keys:
        # No manifests found - strict mode, require migration
        # Check if there are objects in warp/objects/ to give a helpful error
        has_objects = False
        for page in paginator.paginate(Bucket=bucket, Prefix='warp/objects/', MaxKeys=1):
            if page.get('Contents'):
                has_objects = True
                break

        if has_objects:
            raise ValueError(
                f"Bucket '{bucket}' has data but no manifests. "
                f"Run 'warp manifest generate --bucket {bucket}' to create manifests."
            )
        return []

    # Parse manifest paths to get dataset info
    # Format: warp/manifests/<workspace>/<name>/<version_hash>.json
    datasets_map = {}

    def fetch_manifest_info(key: str):
        """Fetch manifest and extract summary info."""
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            manifest = json.loads(response['Body'].read().decode('utf-8'))

            # Extract info
            dataset = manifest.get('dataset', '')
            version = manifest.get('version_hash', '')
            resources = manifest.get('resources', [])
            total_size = sum(r.get('size', 0) for r in resources)
            row_count = manifest.get('row_count')

            return {
                'dataset': dataset,
                'version': version,
                'size': total_size,
                'files': len(resources),
                'row_count': row_count,
                '_manifest': manifest,  # Store full manifest for later use
            }
        except Exception as e:
            # Parse from key if manifest fetch fails
            parts = key.split('/')
            if len(parts) >= 5:
                ws, nm, vf = parts[2], parts[3], parts[4]
                return {
                    'dataset': f"{ws}/{nm}",
                    'version': vf.replace('.json', ''),
                    'size': 0,
                    'files': 0,
                    'row_count': None,
                    '_manifest': None,
                }
            return None

    # Parallel manifest fetching for details
    with ThreadPoolExecutor(max_workers=min(workers, len(manifest_keys))) as executor:
        futures = {executor.submit(fetch_manifest_info, key): key for key in manifest_keys}
        for future in tqdm(as_completed(futures), total=len(manifest_keys),
                          desc="  Loading manifests", unit="manifest", leave=False, disable=not progress):
            info = future.result()
            if info:
                ds_key = f"{info['dataset']}:{info['version']}"
                # Keep most recent if duplicates
                if ds_key not in datasets_map:
                    datasets_map[ds_key] = info

    result = list(datasets_map.values())
    _s3_datasets_cache[cache_key] = result
    return result


def register_remote_dataset(
    dataset_id: str,
    backend: str = "s3",
    bucket: Optional[str] = None,
    version: Optional[str] = None,
) -> str:
    """
    Register a dataset into the local registry using cloud manifest.

    Uses cloud manifests for fast registration (no HEAD requests needed).

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://arc/arcagi')
        backend: Storage backend ('s3')
        bucket: Remote bucket name (default: 'warp')
        version: Version hash to register (if None, uses latest)

    Returns:
        Version hash registered locally
    """
    if backend != "s3":
        raise ValueError(f"Backend '{backend}' not supported")
    if not bucket:
        bucket = DEFAULT_BUCKET

    bucket = normalize_bucket_name(bucket)

    from ..api.management import register_dataset as _register

    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    # Get remote datasets (uses manifests)
    remote = list_remote_datasets(backend=backend, bucket=bucket)
    target_dataset = f"{uri.workspace}/{uri.name}"
    candidates = [ds for ds in remote if ds.get('dataset') == target_dataset]

    if not candidates:
        raise ValueError(f"Dataset not found in remote: {target_dataset}")

    # If version not provided, pick the one with most files (or first if same)
    if version is None:
        candidates.sort(key=lambda d: (d.get('files', 0), d.get('size', 0)), reverse=True)
        version = candidates[0]['version']

    # Find the matching dataset entry
    matching = [ds for ds in candidates if ds.get('version') == version]
    if not matching:
        raise ValueError(f"Version {version} not found for {target_dataset}")

    dataset_entry = matching[0]
    manifest = dataset_entry.get('_manifest')

    if not manifest:
        raise ValueError(
            f"Manifest not loaded for {target_dataset}. "
            f"Run 'warp manifest generate --bucket {bucket}' to create manifests."
        )

    # Extract resources from manifest
    resources = manifest.get('resources', [])
    if not resources:
        raise ValueError(f"No resources in manifest for {uri.workspace}/{uri.name}:{version}")

    # Build resource URIs list with sizes
    resource_uris = []
    resource_sizes = {}
    for r in resources:
        s3_uri = r.get('uri')
        if s3_uri:
            resource_uris.append(s3_uri)
            resource_sizes[s3_uri] = r.get('size', 0)

    print(f"  ✓ Found {len(resource_uris)} resources for {target_dataset} (from manifest)")

    # Try to get schema from manifest first
    manifest_schema = manifest.get('schema', {})
    schema_columns = manifest_schema.get('columns', [])

    if schema_columns:
        # Convert manifest schema format to dict
        schema = {col['name']: col['type'] for col in schema_columns}
        file_format = resources[0].get('extension', 'parquet') if resources else 'parquet'
        print(f"  ✓ Schema from manifest ({len(schema)} columns)")
    else:
        # Infer schema from first resource using DuckDB
        from ..engine.duck import get_engine

        engine = get_engine()
        first_uri = resource_uris[0]
        ext = resources[0].get('extension', 'parquet') if resources else 'parquet'

        print(f"  📊 Reading schema from remote (format: {ext})...")
        try:
            schema = engine.conn.sql(f"DESCRIBE SELECT * FROM read_parquet('{first_uri}')").fetchall()
            schema = {row[0]: row[1] for row in schema}
            file_format = ext
            print(f"  ✓ Schema inferred ({len(schema)} columns)")
        except Exception as e:
            print(f"  ⚠️  Direct read failed ({e}), downloading sample file...")
            from ..core.cache import get_cache
            import tempfile
            import shutil

            cache = get_cache()
            first_file = cache.get(first_uri)
            print(f"  ✓ Downloaded {first_file.stat().st_size / 1e6:.1f} MB")

            with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as tmp:
                tmp_path = Path(tmp.name)
            shutil.copy2(first_file, tmp_path)
            try:
                schema = engine.get_schema(tmp_path)
                file_format = engine._detect_format(tmp_path)
            finally:
                tmp_path.unlink()

    # Register with S3 URIs and schema
    version_hash = _register(dataset_id, resources=resource_uris, schema=schema, file_format=file_format, metadata={
        "registered_from": f"s3://{bucket}",
        "remote_version": version,
        "row_count": manifest.get('row_count'),
    })

    # Register raw_data sources from manifest (for restore on destination machines)
    # BUT don't overwrite existing raw_data sources that have content_hashes
    # (those are from the source machine and have correct original paths)
    raw_data = manifest.get('raw_data', [])
    if raw_data:
        registry = get_registry()
        from pathlib import Path

        # Check if raw_data_sources already exist with content_hashes
        existing_raw = registry.list_raw_data_sources(uri.workspace, uri.name, version_hash)
        if existing_raw and any(r.get('content_hash') for r in existing_raw):
            # Already have synced raw data sources - don't overwrite paths
            print(f"  ℹ️  Keeping {len(existing_raw)} existing raw data source paths")
        else:
            # No existing raw data - register with pull destination paths
            raw_base = Path.home() / ".warpdata" / "raw" / uri.workspace / uri.name

            for rd in raw_data:
                # rd has: uri, source_path, source_type, size, content_hash
                source_path = rd.get('source_path', '')
                content_hash = rd.get('content_hash')
                size = rd.get('size')
                source_type = rd.get('source_type', 'file')

                if not content_hash:
                    continue

                # Rewrite source_path to point to local raw data directory
                filename = Path(source_path).name
                local_path = str(raw_base / filename)

                registry.add_raw_data_source(
                    workspace=uri.workspace,
                    name=uri.name,
                    version_hash=version_hash,
                    source_type=source_type,
                    source_path=local_path,  # Local path where we'll restore
                    size=size,
                    content_hash=content_hash,
                    metadata=rd.get('metadata'),
                )

            print(f"  ✓ Registered {len(raw_data)} raw data sources")

    return version_hash


def pull_dataset(
    dataset_id: str,
    backend: str = "s3",
    bucket: Optional[str] = None,
    dry_run: bool = False,
    include_raw: bool = True,
    max_raw_size: Optional[int] = None,
    mode: str = "full",
    max_bytes: Optional[int] = None,
    max_files: Optional[int] = None,
    workers: int = 1,
) -> Dict[str, Any]:
    """
    Pull (download) a specific dataset from cloud storage.

    Supports multiple pull modes for flexible data access:
    - "full": Download all resources (default)
    - "register-only": Register dataset locally but download nothing
    - "metadata": Download only parquet footer for schema inspection

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://workspace/name')
        backend: Storage backend ('s3')
        bucket: S3 bucket name (default: 'warp')
        dry_run: If True, only show what would be downloaded
        include_raw: Whether to download raw data sources
        max_raw_size: Maximum size for raw data per dataset
        mode: Pull mode - "full", "register-only", or "metadata"
        max_bytes: Maximum total bytes to download (for sampling)
        max_files: Maximum number of files to download (for sampling)
        workers: Number of parallel download workers (default: 1)

    Returns:
        Dictionary with download info (total_files, total_size, etc.)

    Examples:
        >>> # Quick catalog - just register without downloading
        >>> wd.pull_dataset("nlp/imdb", bucket="mydata", mode="register-only")

        >>> # Sample first 100MB
        >>> wd.pull_dataset("nlp/imdb", bucket="mydata", max_bytes=100*1024*1024)
    """
    if not bucket:
        bucket = DEFAULT_BUCKET

    # Validate mode
    valid_modes = ("full", "register-only", "metadata")
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    # Resolve dataset ID (must be warpdata://, not a file)
    dataset_id = require_warpdata_id(dataset_id)
    uri = parse_uri(dataset_id)

    # Check if dataset exists in local registry
    registry = get_registry()
    dataset_ver = registry.get_dataset_version(uri.workspace, uri.name, uri.version or "latest")

    # Check if dataset has S3 resources or local resources
    needs_registration = False
    if not dataset_ver:
        needs_registration = True
    else:
        # Check if resources are S3 URIs or local files
        manifest = registry.get_manifest(uri.workspace, uri.name, dataset_ver["version_hash"])
        if manifest and manifest.get("resources"):
            resources = normalize_resources(manifest.get("resources"))
            first_resource = resources[0]["uri"] if resources else None
            # If it's a local file, check if it actually exists
            # Only re-register from S3 if the local file is MISSING
            if first_resource and not first_resource.startswith("s3://"):
                local_path = Path(first_resource) if not first_resource.startswith("file://") else Path(first_resource[7:])
                if not local_path.exists():
                    print(f"  📝 Dataset has local resources but file missing, re-registering from S3...")
                    needs_registration = True
                # else: local file exists, no need to re-register

    if needs_registration:
        if dataset_ver:
            print(f"  📝 Re-registering dataset from S3...")
        else:
            print(f"  📝 Dataset not in local registry, registering from S3...")
        try:
            version_hash = register_remote_dataset(
                dataset_id=dataset_id,
                backend=backend,
                bucket=bucket,
                version=None  # Auto-detect latest version
            )
            print(f"  ✓ Registered {dataset_id} (version: {version_hash[:16]}...)")
        except Exception as e:
            print(f"  ✗ Failed to register dataset: {e}")
            raise

    # Handle register-only mode
    if mode == "register-only":
        print(f"  ✓ Dataset registered (mode=register-only, no files downloaded)")
        return {
            'dataset_id': dataset_id,
            'mode': 'register-only',
            'registered': True,
            'total_files': 0,
            'total_size': 0,
        }

    # Handle metadata mode - just get schema from parquet footer
    if mode == "metadata":
        from ..engine.duck import get_engine

        # Get first resource URI
        dataset_ver = registry.get_dataset_version(uri.workspace, uri.name, uri.version or "latest")
        manifest = registry.get_manifest(uri.workspace, uri.name, dataset_ver["version_hash"])
        resources = normalize_resources(manifest.get("resources", []))

        if not resources:
            return {
                'dataset_id': dataset_id,
                'mode': 'metadata',
                'schema': {},
                'row_count': None,
            }

        first_uri = resources[0]["uri"]
        engine = get_engine()

        try:
            # DuckDB reads parquet footer directly from S3 (a few KB)
            schema = engine.conn.sql(f"DESCRIBE SELECT * FROM read_parquet('{first_uri}')").fetchall()
            schema_dict = {row[0]: row[1] for row in schema}

            # Try to get row count from parquet metadata
            try:
                count_result = engine.conn.sql(f"SELECT COUNT(*) FROM read_parquet('{first_uri}')").fetchone()
                row_count = count_result[0] if count_result else None
            except Exception:
                row_count = None

            print(f"  ✓ Schema retrieved (mode=metadata, {len(schema_dict)} columns)")
            return {
                'dataset_id': dataset_id,
                'mode': 'metadata',
                'schema': schema_dict,
                'row_count': row_count,
                'total_files': 0,
                'total_size': 0,
            }
        except Exception as e:
            print(f"  ⚠️  Failed to read metadata: {e}")
            return {
                'dataset_id': dataset_id,
                'mode': 'metadata',
                'schema': {},
                'error': str(e),
            }

    # Now restore/download the dataset files
    if dry_run:
        # For dry-run, just report what would be downloaded from S3
        datasets = list_remote_datasets(backend=backend, bucket=bucket)
        dataset_key = f"{uri.workspace}/{uri.name}"

        matching = [ds for ds in datasets if ds['dataset'] == dataset_key]
        if matching:
            ds = matching[0]
            return {
                'dataset_id': dataset_id,
                'total_files': ds['files'],
                'total_size': ds['size'],
            }
        else:
            return {
                'dataset_id': dataset_id,
                'total_files': 0,
                'total_size': 0,
            }

    return restore_dataset(
        dataset_id=dataset_id,
        backend=backend,
        bucket=bucket,
        include_raw=include_raw,
        output_dir=None,
        max_raw_size=max_raw_size,
        max_bytes=max_bytes,
        max_files=max_files,
        workers=workers,
    )


def bulk_pull(
    dataset_ids: List[str],
    backend: str = "s3",
    bucket: Optional[str] = None,
    workers: int = 8,
    include_raw: bool = False,
    max_raw_size: Optional[int] = None,
    progress: bool = True,
) -> Dict[str, Any]:
    """
    Pull multiple datasets in parallel for maximum efficiency.

    This is much faster than calling pull_dataset() repeatedly because:
    1. S3 object listing is done once and cached
    2. Dataset registrations are batched
    3. File downloads happen in parallel across datasets

    Args:
        dataset_ids: List of dataset IDs (e.g., ['warpdata://nlp/imdb', 'warpdata://math/gsm8k'])
        backend: Storage backend ('s3')
        bucket: S3 bucket name (default: 'warp')
        workers: Number of parallel download workers (default: 8)
        include_raw: Whether to download raw data (default: False for speed)
        max_raw_size: Maximum size of raw data to download
        progress: Show progress bar

    Returns:
        Dictionary with download summary

    Examples:
        >>> import warpdata as wd
        >>> datasets = ['nlp/imdb', 'nlp/ag-news', 'math/gsm8k', 'eval/mmlu']
        >>> result = wd.bulk_pull(datasets, workers=8)
        >>> print(f"Downloaded {result['successful']} datasets")
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm

    if not bucket:
        bucket = DEFAULT_BUCKET
    bucket = normalize_bucket_name(bucket)

    # Normalize dataset IDs
    normalized_ids = []
    for ds_id in dataset_ids:
        if not ds_id.startswith('warpdata://'):
            ds_id = f'warpdata://{ds_id}'
        normalized_ids.append(ds_id)

    # Pre-warm the S3 objects cache with a single scan
    print(f"📋 Scanning {backend}://{bucket} for datasets...")
    _ = list_remote_datasets(backend=backend, bucket=bucket, progress=progress)
    print(f"  ✓ Cache warmed")

    results = {
        'successful': [],
        'failed': [],
        'total_files': 0,
        'total_size': 0,
    }

    def pull_one(dataset_id: str) -> Dict:
        try:
            result = pull_dataset(
                dataset_id=dataset_id,
                backend=backend,
                bucket=bucket,
                include_raw=include_raw,
                max_raw_size=max_raw_size,
            )
            return {'dataset_id': dataset_id, 'success': True, 'result': result}
        except Exception as e:
            return {'dataset_id': dataset_id, 'success': False, 'error': str(e)}

    # Download in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(pull_one, ds_id): ds_id for ds_id in normalized_ids}
        pbar = tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Downloading datasets",
            unit="dataset",
            disable=not progress,
        )
        for future in pbar:
            res = future.result()
            ds_id = res['dataset_id']
            if res['success']:
                results['successful'].append(ds_id)
                results['total_files'] += res['result'].get('total_files', 0)
                results['total_size'] += res['result'].get('total_size', 0)
                pbar.set_postfix_str(f"✓ {ds_id.split('/')[-1]}")
            else:
                results['failed'].append({'dataset_id': ds_id, 'error': res['error']})
                pbar.set_postfix_str(f"✗ {ds_id.split('/')[-1]}")

    # Summary
    print(f"\n{'=' * 60}")
    print("Bulk Pull Summary")
    print(f"{'=' * 60}")
    print(f"  Requested: {len(normalized_ids)}")
    print(f"  Successful: {len(results['successful'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Total size: {results['total_size'] / 1e9:.2f} GB")

    if results['failed']:
        print(f"\nFailed datasets:")
        for f in results['failed']:
            print(f"  - {f['dataset_id']}: {f['error']}")

    return results


def pull_all_datasets(
    backend: str = "s3",
    bucket: Optional[str] = None,
    dry_run: bool = False,
    include_raw: bool = True,
    max_raw_size: Optional[int] = None,
    workers: int = 1,
) -> Dict[str, Any]:
    """
    Pull (download) all datasets from cloud storage.

    Discovers all datasets in the remote bucket, registers them locally,
    and downloads their files.

    Args:
        backend: Storage backend ('s3')
        bucket: S3 bucket name
        dry_run: If True, only show what would be downloaded
        include_raw: Whether to download raw data
        max_raw_size: Maximum size of raw data to download
        workers: Number of parallel workers (default: 1 for sequential)

    Returns:
        Dictionary with download summary (total_datasets, total_files, total_size)
    """
    # Normalize bucket name
    bucket = normalize_bucket_name(bucket)

    # List all datasets in the remote bucket
    print(f"📋 Scanning {backend}://{bucket} for datasets...")
    datasets = list_remote_datasets(backend=backend, bucket=bucket)

    if not datasets:
        print("  No datasets found in bucket")
        return {
            'total_datasets': 0,
            'total_files': 0,
            'total_size': 0
        }

    print(f"  Found {len(datasets)} datasets")
    print()

    # Use bulk_pull for parallel downloads
    if workers > 1 and not dry_run:
        dataset_ids = [f"warpdata://{ds['dataset']}" for ds in datasets]
        return bulk_pull(
            dataset_ids=dataset_ids,
            backend=backend,
            bucket=bucket,
            workers=workers,
            include_raw=include_raw,
            max_raw_size=max_raw_size,
        )

    # Sequential mode (original behavior)
    total_files = 0
    total_size = 0
    errors = []

    for i, ds in enumerate(datasets, 1):
        dataset_id = f"warpdata://{ds['dataset']}"
        print(f"[{i}/{len(datasets)}] {dataset_id}")

        try:
            result = pull_dataset(
                dataset_id=dataset_id,
                backend=backend,
                bucket=bucket,
                dry_run=dry_run,
                include_raw=include_raw,
                max_raw_size=max_raw_size
            )
            total_files += result.get('total_files', 0)
            total_size += result.get('total_size', 0)

            if dry_run:
                print(f"  Would download: {result.get('total_files', 0)} files ({result.get('total_size', 0) / 1e6:.1f} MB)")
            else:
                print(f"  ✓ Downloaded: {result.get('total_files', 0)} files ({result.get('total_size', 0) / 1e6:.1f} MB)")

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            errors.append({'dataset': dataset_id, 'error': str(e)})

        print()

    # Print summary
    print("=" * 60)
    print("Pull Summary")
    print("=" * 60)
    print(f"  Total datasets: {len(datasets)}")
    print(f"  Successful: {len(datasets) - len(errors)}")
    print(f"  Failed: {len(errors)}")
    if not dry_run:
        print(f"  Downloaded: {total_files} files ({total_size / 1e9:.2f} GB)")
    else:
        print(f"  Would download: {total_files} files ({total_size / 1e9:.2f} GB)")

    return {
        'total_datasets': len(datasets),
        'total_files': total_files,
        'total_size': total_size,
        'errors': errors,
    }


def _upload_sync_manifest(
    storage,
    bucket: str,
    workspace: str,
    name: str,
    version_hash: str,
    resource_hashes: list,  # List of (content_hash, size, extension)
    local_manifest: dict,
    raw_data_entries: Optional[list] = None,  # List of dicts with raw_data info
) -> None:
    """
    Helper to build and upload a cloud manifest during sync.

    Args:
        storage: S3 storage backend
        bucket: S3 bucket name
        workspace: Dataset workspace
        name: Dataset name
        version_hash: Version hash
        resource_hashes: List of (content_hash, size, extension) tuples
        local_manifest: Local registry manifest dict
        raw_data_entries: List of raw data dicts with content_hash, source_path, etc.
    """
    # Build manifest resources
    manifest_resources = []
    for content_hash, size, extension in resource_hashes:
        s3_uri = f"s3://{bucket}/warp/objects/{content_hash[:2]}/{content_hash[2:4]}/{content_hash}"
        manifest_resources.append({
            "content_hash": content_hash,
            "uri": s3_uri,
            "size": size,
            "extension": extension,
        })

    # Build raw_data entries for manifest
    manifest_raw_data = []
    if raw_data_entries:
        for rd in raw_data_entries:
            h = rd["content_hash"]
            s3_uri = f"s3://{bucket}/warp/objects/{h[:2]}/{h[2:4]}/{h}"
            manifest_raw_data.append({
                "source_path": rd.get("source_path", ""),
                "source_type": rd.get("source_type", "file"),
                "content_hash": h,
                "size": rd.get("size", 0),
                "compressed": rd.get("compressed", False),
                "compression_format": rd.get("compression_format"),
                "original_size": rd.get("original_size"),
                "uri": s3_uri,
            })

    # Get schema from local manifest if available
    schema_dict = local_manifest.get("schema", {}) if local_manifest else {}

    # Build cloud manifest
    cloud_manifest = build_cloud_manifest(
        workspace=workspace,
        name=name,
        version_hash=version_hash,
        resources=manifest_resources,
        schema=schema_dict,
        row_count=local_manifest.get("row_count") if local_manifest else None,
        embeddings=[],  # TODO: track embeddings in sync
        raw_data=manifest_raw_data,
        metadata=local_manifest.get("metadata") if local_manifest else None,
    )

    # Upload manifest
    try:
        manifest_key = storage.put_manifest(
            workspace=workspace,
            name=name,
            version_hash=version_hash,
            manifest_data=cloud_manifest,
            update_latest=True,
        )
        print(f"  ✓ Uploaded manifest: {manifest_key}")
    except Exception as e:
        print(f"  ⚠️  Failed to upload manifest: {e}")


def sync_to_cloud(
    backend: str = "s3",
    bucket: Optional[str] = None,
    include_raw: bool = True,
    dry_run: bool = False,
    max_raw_size: Optional[int] = None,
    force: bool = False,
    verify: bool = False,
    workspaces: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync all local datasets to cloud storage (upload only new/changed datasets).

    Like 'git push' for datasets - compares local datasets with remote and
    uploads only what's missing or changed.

    Args:
        backend: Storage backend ('s3')
        bucket: S3 bucket name (required for S3)
        include_raw: Whether to sync raw data sources
        dry_run: If True, only show what would be synced without uploading
        max_raw_size: Maximum size in bytes for raw data to sync. Datasets with
                     raw data larger than this will skip raw data upload.
                     Example: 10*1024**3 for 10GB
        force: If True, re-upload all files even if they exist in storage
        verify: If True, verify files exist in storage after upload
        workspaces: Optional list of workspaces to sync (syncs all if not specified)

    Returns:
        Dictionary with sync summary (uploaded, skipped, errors)

    Examples:
        >>> import warpdata as wd
        >>>
        >>> # Dry run - see what would be synced
        >>> result = wd.sync_to_cloud(
        ...     backend="s3",
        ...     bucket="my-warp-backup",
        ...     dry_run=True
        ... )
        >>> print(f"Would upload {result['to_upload']} datasets")
        >>>
        >>> # Sync with max 10GB raw data per dataset
        >>> result = wd.sync_to_cloud(
        ...     backend="s3",
        ...     bucket="my-warp-backup",
        ...     include_raw=True,
        ...     max_raw_size=10*1024**3  # 10GB
        ... )
        >>> print(f"Uploaded {result['uploaded']}, skipped {result['skipped']}")
    """
    # Initialize storage backend
    storage_config = {}
    if backend == "s3":
        if not bucket:
            raise ValueError("S3 backend requires 'bucket' parameter")

        # Normalize bucket name (add warpbucket- prefix if needed)
        normalized_bucket = normalize_bucket_name(bucket)
        if normalized_bucket != bucket:
            print(f"📦 Using warp bucket: {normalized_bucket}")
        bucket = normalized_bucket

        storage_config["bucket"] = bucket
        storage_config["prefix"] = "warp"  # Use warp/objects/ path

        # Auto-create bucket if it doesn't exist
        try:
            import boto3
            import os
            s3_client = boto3.client('s3')

            # Check if bucket exists and is accessible
            bucket_exists = False
            try:
                s3_client.head_bucket(Bucket=bucket)
                bucket_exists = True
            except:
                pass

            if not bucket_exists:
                # Bucket doesn't exist or not accessible, try to create it
                print(f"Creating S3 bucket: {bucket}")
                try:
                    # Get region from environment or boto3 session
                    region = os.environ.get('AWS_DEFAULT_REGION') or s3_client.meta.region_name or 'us-east-1'

                    # us-east-1 doesn't need LocationConstraint
                    if region == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    print(f"✓ Created bucket: s3://{bucket} in {region}")
                except Exception as e:
                    error_msg = str(e)
                    if 'IllegalLocationConstraintException' in error_msg or 'BucketAlreadyExists' in error_msg:
                        # Suggest unique bucket name based on AWS account ID
                        try:
                            sts = boto3.client('sts')
                            identity = sts.get_caller_identity()
                            account_id = identity['Account']
                            suggested_bucket = f"{bucket}-{account_id}"
                            print(f"")
                            print(f"❌ Bucket '{bucket}' is not available (S3 bucket names are globally unique)")
                            print(f"")
                            print(f"💡 Suggested bucket name: {suggested_bucket}")
                            print(f"   Run: warp sync --bucket {suggested_bucket} --backend s3")
                            raise ValueError(f"Bucket '{bucket}' already exists. Use a unique name like '{suggested_bucket}'")
                        except:
                            print(f"")
                            print(f"❌ Bucket '{bucket}' is not available (S3 bucket names are globally unique)")
                            print(f"   Try adding a suffix: {bucket}-<yourname> or {bucket}-<random>")
                            raise ValueError(f"Bucket '{bucket}' already exists. Use a unique bucket name.")
                    else:
                        print(f"Warning: Could not create bucket: {e}")
                        raise
        except ImportError:
            pass  # boto3 not available, will fail later if needed

    storage = get_storage_backend(backend, **storage_config)

    # Get all local datasets
    registry = get_registry()
    datasets = registry.list_datasets()

    # Filter by workspaces if specified
    if workspaces:
        datasets = [d for d in datasets if d["workspace"] in workspaces]
        print(f"Filtering to workspaces: {', '.join(workspaces)}")

    from tqdm import tqdm
    from ..core.cache import get_cache

    # Sort datasets by size (lightest first)
    def get_dataset_size(ds):
        try:
            manifest = registry.get_manifest(ds["workspace"], ds["name"], ds["latest_version"])
            if not manifest:
                return 0
            cache = get_cache()
            total = 0
            for resource in normalize_resources(manifest.get("resources", [])):
                try:
                    local_path = cache.get(resource["uri"])
                    if local_path and local_path.exists():
                        total += local_path.stat().st_size
                except:
                    pass
            return total
        except:
            return 0

    print("Calculating dataset sizes...")
    datasets_with_size = [(ds, get_dataset_size(ds)) for ds in tqdm(datasets, desc="Sizing", unit="dataset", leave=False)]
    datasets_with_size.sort(key=lambda x: x[1])
    datasets = [ds for ds, _ in datasets_with_size]
    print(f"Sorted {len(datasets)} datasets by size (lightest first)")

    uploaded_datasets = []
    skipped_datasets = []
    errors = []
    total_uploaded_size = 0
    total_existing_size = 0

    print(f"Syncing {len(datasets)} datasets to {backend}://{bucket}...")
    print("=" * 60)

    for dataset in tqdm(datasets, desc="Syncing datasets", unit="dataset"):
        workspace = dataset["workspace"]
        name = dataset["name"]
        version_hash = dataset["latest_version"]  # Use latest_version from list_datasets
        dataset_id = f"warpdata://{workspace}/{name}"

        print(f"\n[{workspace}/{name}]")

        # Get manifest
        manifest = registry.get_manifest(workspace, name, version_hash)
        if not manifest:
            print(f"  ⚠️  No manifest found, skipping")
            errors.append({"dataset": dataset_id, "error": "No manifest"})
            continue

        # Check if dataset resources exist in storage
        from ..core.cache import get_cache
        cache = get_cache()

        dataset_files = []
        dataset_upload_size = 0
        dataset_total_size = 0
        needs_upload = False

        # Track ALL resources for manifest (not just those needing upload)
        all_resource_hashes = []  # List of (content_hash, size, extension) for manifest
        all_raw_data_entries = []  # List of raw_data dicts for manifest

        # Check dataset resources
        for resource in normalize_resources(manifest.get("resources")):
            resource_uri = resource["uri"]

            try:
                local_path = cache.get(resource_uri)
            except Exception as e:
                print(f"  ⚠️  Failed to get resource: {resource_uri}: {e}")
                continue

            if not local_path or not local_path.exists():
                print(f"  ⚠️  Resource not found: {resource_uri}")
                continue

            file_size = local_path.stat().st_size
            dataset_total_size += file_size

            # Compute hash
            from ..core.storage import compute_content_hash
            content_hash = compute_content_hash(local_path)

            # Track for manifest (all resources, not just those needing upload)
            extension = local_path.suffix.lstrip('.') if local_path.suffix else 'parquet'
            all_resource_hashes.append((content_hash, file_size, extension))

            # Check if exists in storage
            exists_in_storage = False
            if not force:
                try:
                    exists_in_storage = storage.exists(content_hash)
                except Exception as e:
                    print(f"  ⚠️  Error checking storage for {local_path.name}: {e}")
                    # Assume doesn't exist to trigger upload
                    exists_in_storage = False

            if force or not exists_in_storage:
                needs_upload = True
                dataset_files.append({
                    "type": "resource",
                    "path": local_path,
                    "hash": content_hash,
                    "size": file_size,
                })
                dataset_upload_size += file_size

        # Check raw data if requested
        if include_raw:
            raw_sources = registry.list_raw_data_sources(workspace, name, version_hash)

            # Calculate total raw data size for this dataset
            total_raw_size = 0
            for source in raw_sources:
                if source_path := Path(source["source_path"]):
                    if source_path.exists():
                        if source_path.is_file():
                            total_raw_size += source_path.stat().st_size
                        elif source_path.is_dir():
                            total_raw_size += source.get('size', 0)

            # Check if raw data exceeds max_raw_size
            skip_raw = False
            if max_raw_size and total_raw_size > max_raw_size:
                skip_raw = True
                print(f"  ⚠️  Skipping raw data ({total_raw_size / 1e9:.2f} GB > {max_raw_size / 1e9:.2f} GB limit)")

            if not skip_raw:
                for source in raw_sources:
                    source_path = Path(source["source_path"])

                    if not source_path.exists():
                        continue

                    # Handle both files and directories
                    # Note: For large directories, we track the total size but don't enumerate individual files
                    # to avoid performance issues. In dry-run mode, we just assume all raw data needs upload.
                    if source_path.is_file():
                        file_size = source_path.stat().st_size
                        dataset_total_size += file_size

                        # Only compute hash and check existence if not dry-run
                        if not dry_run:
                            from ..core.storage import compute_content_hash
                            content_hash = compute_content_hash(source_path)

                            exists_in_storage = False
                            if not force:
                                try:
                                    exists_in_storage = storage.exists(content_hash)
                                except Exception as e:
                                    print(f"  ⚠️  Error checking storage for raw file {source_path.name}: {e}")
                                    exists_in_storage = False

                            if force or not exists_in_storage:
                                needs_upload = True
                                dataset_files.append({
                                    "type": "raw_data",
                                    "path": source_path,
                                    "hash": content_hash,
                                    "size": file_size,
                                })
                                dataset_upload_size += file_size
                            else:
                                # Raw file already in storage - track for manifest
                                all_raw_data_entries.append({
                                    "content_hash": content_hash,
                                    "source_path": str(source_path),
                                    "source_type": "file",
                                    "size": file_size,
                                    "compressed": False,
                                })
                        else:
                            # Dry-run: assume all raw data needs upload
                            needs_upload = True
                            dataset_files.append({
                                "type": "raw_data",
                                "path": source_path,
                                "hash": None,
                                "size": file_size,
                            })
                            dataset_upload_size += file_size

                    elif source_path.is_dir():
                        # For directories, use the size from the registry
                        # (computed when the raw data was registered)
                        dir_size = source.get('size', 0)
                        dataset_total_size += dir_size

                        # If we have a previously uploaded compressed archive for this
                        # directory (content_hash recorded in registry) and it still
                        # exists in storage, skip re-upload to avoid redundant traffic.
                        existing_hash = source.get('content_hash')
                        if (not force) and existing_hash:
                            try:
                                # If directory size matches recorded size and the
                                # previously uploaded archive exists in storage,
                                # assume no changes and skip re-upload.
                                def _dir_size(p: Path) -> int:
                                    total = 0
                                    for sub in p.rglob('*'):
                                        try:
                                            if sub.is_file():
                                                total += sub.stat().st_size
                                        except Exception:
                                            continue
                                    return total

                                current_size = _dir_size(source_path)
                                recorded_size = int(dir_size or 0)

                                if current_size == recorded_size and storage.exists(existing_hash):
                                    # Already uploaded; skip scheduling upload for this dir
                                    # but still count its size toward total_existing_size
                                    print(f"  ✓ Raw dir already in cloud: {source_path.name}")
                                    # Track for manifest even though already uploaded
                                    all_raw_data_entries.append({
                                        "content_hash": existing_hash,
                                        "source_path": str(source_path),
                                        "source_type": "directory",
                                        "size": source.get('metadata', {}).get('compressed_size', recorded_size),
                                        "compressed": True,
                                        "compression_format": source.get('metadata', {}).get('compression_format', 'tar.gz'),
                                        "original_size": recorded_size,
                                    })
                                    continue
                            except Exception:
                                # If storage check fails, fall back to uploading
                                pass

                        # Schedule directory for compression + upload
                        if dry_run:
                            needs_upload = True
                            dataset_files.append({
                                "type": "raw_data_directory",
                                "path": source_path,
                                "hash": None,
                                "size": dir_size,
                            })
                            dataset_upload_size += dir_size
                        else:
                            needs_upload = True
                            dataset_files.append({
                                "type": "raw_data_directory",
                                "path": source_path,
                                "hash": None,
                                "size": dir_size,
                            })
                            dataset_upload_size += dir_size

        # Upload or skip
        if needs_upload:
            print(f"  📤 Needs upload: {len(dataset_files)} files ({dataset_upload_size / 1e6:.1f} MB)")

            if dry_run:
                print(f"  [DRY RUN] Would upload {len(dataset_files)} files")
            else:
                # Upload files
                for file_info in dataset_files:
                    file_path = file_info["path"]
                    file_type = file_info["type"]

                    # Handle directories by compressing first, then uploading
                    if file_type == "raw_data_directory":
                        print(f"  📂 Compressing directory: {file_path.name} ({file_info['size'] / 1e6:.1f} MB)")

                        from ..core.compression import compress_directory

                        # Create temporary compressed archive
                        temp_archive = None
                        try:
                            # Compress using fastest available method (pigz > zstd > gzip)
                            temp_archive, compression_format, compressed_size = compress_directory(
                                file_path, verbose=True
                            )

                            compression_ratio = compressed_size / file_info['size'] * 100 if file_info['size'] > 0 else 100
                            print(f"  ✓ Compressed: {compressed_size / 1e6:.1f} MB ({compression_ratio:.1f}% of original)")

                            # Upload compressed archive
                            metadata = {
                                "type": "raw_data_directory_compressed",
                                "dataset": f"{workspace}/{name}",
                                "version": version_hash,
                                "source_dir": file_path.name,
                                "compression": compression_format,
                                "original_size": str(file_info['size']),
                            }

                            content_hash = storage.put(Path(temp_archive), metadata=metadata, show_progress=True)
                            print(f"  ✓ Uploaded compressed directory: {file_path.name}")

                            # Track for manifest (do this first before registry update which might fail)
                            all_raw_data_entries.append({
                                "content_hash": content_hash,
                                "source_path": str(file_path),
                                "source_type": "directory",
                                "size": compressed_size,
                                "compressed": True,
                                "compression_format": compression_format,
                                "original_size": file_info['size'],
                            })

                            # Update registry to mark this directory as compressed
                            try:
                                registry.update_raw_data_source(
                                    workspace=workspace,
                                    name=name,
                                    version_hash=version_hash,
                                    source_path=str(file_path),
                                    content_hash=content_hash,
                                )
                            except Exception as reg_err:
                                print(f"  ⚠️  Could not update registry: {reg_err}")

                        except Exception as e:
                            print(f"  ✗ Failed to compress/upload directory: {e}")
                            errors.append({
                                "dataset": dataset_id,
                                "file": str(file_path),
                                "error": str(e)
                            })

                        finally:
                            # Clean up temp file
                            if temp_archive and Path(temp_archive).exists():
                                Path(temp_archive).unlink()

                        continue

                    # Get file extension for format detection
                    extension = file_path.suffix.lstrip('.') if file_path.suffix else ''

                    metadata = {
                        "type": file_type,
                        "dataset": f"{workspace}/{name}",
                        "version": version_hash,
                    }

                    # Add extension for dataset resources
                    if file_type in ('resource', 'dataset_resource') and extension:
                        metadata["extension"] = extension

                    try:
                        content_hash = storage.put(file_path, metadata=metadata, overwrite=force, show_progress=True)
                        print(f"  ✓ Uploaded: {file_path.name}")

                        # Track raw_data files for manifest
                        if file_type == "raw_data":
                            all_raw_data_entries.append({
                                "content_hash": content_hash,
                                "source_path": str(file_path),
                                "source_type": "file",
                                "size": file_path.stat().st_size,
                                "compressed": False,
                            })

                        # Verify upload if requested
                        if verify:
                            if storage.exists(content_hash):
                                print(f"    ✓ Verified in storage")
                            else:
                                print(f"    ⚠️  Verification failed - file not found in storage!")
                                errors.append({
                                    "dataset": dataset_id,
                                    "file": str(file_path),
                                    "error": "Verification failed after upload"
                                })
                    except Exception as e:
                        print(f"  ✗ Failed: {file_path.name}: {e}")
                        errors.append({
                            "dataset": dataset_id,
                            "file": str(file_path),
                            "error": str(e)
                        })

            uploaded_datasets.append({
                "dataset": dataset_id,
                "files": len(dataset_files),
                "size": dataset_upload_size,
            })
            total_uploaded_size += dataset_upload_size

            # Upload cloud manifest after data files
            if backend == "s3" and all_resource_hashes:
                _upload_sync_manifest(
                    storage, bucket, workspace, name, version_hash,
                    all_resource_hashes, manifest, all_raw_data_entries
                )
        else:
            print(f"  ✓ Already synced ({dataset_total_size / 1e6:.1f} MB)")
            skipped_datasets.append({
                "dataset": dataset_id,
                "size": dataset_total_size,
            })
            total_existing_size += dataset_total_size

            # Also upload manifest for already-synced datasets (if manifest doesn't exist)
            if backend == "s3" and all_resource_hashes:
                if not storage.manifest_exists(workspace, name, version_hash):
                    _upload_sync_manifest(
                        storage, bucket, workspace, name, version_hash,
                        all_resource_hashes, manifest, all_raw_data_entries
                    )

    # Calculate total storage
    total_storage_gb = (total_uploaded_size + total_existing_size) / 1e9

    # Summary
    print(f"\n{'=' * 60}")
    print("Sync Summary")
    print(f"{'=' * 60}")
    print(f"  Total datasets: {len(datasets)}")
    print(f"  Uploaded: {len(uploaded_datasets)}")
    print(f"  Already synced: {len(skipped_datasets)}")
    print(f"  Errors: {len(errors)}")

    if uploaded_datasets:
        action = "Would upload" if dry_run else "Uploaded"
        print(f"\n  {action}: {total_uploaded_size / 1e9:.2f} GB")

    if skipped_datasets:
        print(f"  Already in cloud: {total_existing_size / 1e9:.2f} GB")

    # Storage usage and cost estimates
    print(f"\n{'=' * 60}")
    print("Storage Usage & Cost Estimates")
    print(f"{'=' * 60}")
    print(f"  Total storage: {total_storage_gb:.2f} GB")

    # S3 cost estimates (monthly)
    s3_standard = total_storage_gb * 0.023
    s3_ia = total_storage_gb * 0.0125
    s3_glacier_instant = total_storage_gb * 0.004
    s3_glacier_flex = total_storage_gb * 0.0036

    print(f"\n  Monthly costs (estimated):")
    print(f"    S3 Standard:           ${s3_standard:>7.2f}/month ($0.023/GB)")
    print(f"    S3 Infrequent Access:  ${s3_ia:>7.2f}/month ($0.0125/GB)")
    print(f"    S3 Glacier Instant:    ${s3_glacier_instant:>7.2f}/month ($0.004/GB) ⭐ Recommended")
    print(f"    S3 Glacier Flexible:   ${s3_glacier_flex:>7.2f}/month ($0.0036/GB)")

    print(f"\n  Annual cost (Glacier Instant): ${s3_glacier_instant * 12:.2f}/year")

    if dry_run:
        print(f"\n  💡 Run without --dry-run to actually upload")

    return {
        "backend": backend,
        "bucket": bucket,
        "dry_run": dry_run,
        "total_datasets": len(datasets),
        "uploaded": uploaded_datasets if not dry_run else [],
        "to_upload": uploaded_datasets if dry_run else [],
        "skipped": skipped_datasets,
        "errors": errors,
        "total_uploaded_size": total_uploaded_size,
        "total_existing_size": total_existing_size,
        "total_storage_gb": total_storage_gb,
    }


def _ensure_parent(fs, path: str):
    """Best-effort creation of parent directory for fsspec-backed paths."""
    if "/" not in path:
        return
    parent = path.rsplit("/", 1)[0]
    try:
        fs.makedirs(parent, exist_ok=True)
    except Exception:
        # Parent creation isn't critical for object stores
        pass


def export_registry(destination: str, overwrite: bool = False) -> str:
    """
    Export the local registry.duckdb to a path or URL (e.g., s3://.../registry.duckdb).

    Args:
        destination: Target path/URL for the registry file.
        overwrite: Overwrite the destination if it already exists.

    Returns:
        Destination string used for the export.
    """
    # Registry uses .duckdb extension, not .db
    registry_path = get_config().registry_db.with_suffix(".duckdb")
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found at {registry_path}")

    fs, fs_path = fsspec.core.url_to_fs(destination)

    if fs.exists(fs_path) and not overwrite:
        raise FileExistsError(f"Destination already exists: {destination} (use --overwrite to replace)")

    _ensure_parent(fs, fs_path)

    with fs.open(fs_path, "wb") as dest_f, open(registry_path, "rb") as src_f:
        shutil.copyfileobj(src_f, dest_f)

    return destination


def import_registry(source: str, overwrite: bool = True) -> Path:
    """
    Import a registry.duckdb from a path or URL into the local warpdata home.

    Args:
        source: Source path/URL for the registry file (e.g., s3://.../registry.duckdb).
        overwrite: Overwrite existing local registry.

    Returns:
        Path to the local registry after import.
    """
    # Registry uses .duckdb extension, not .db
    registry_path = get_config().registry_db.with_suffix(".duckdb")
    ensure_dir(registry_path.parent)

    if registry_path.exists() and not overwrite:
        raise FileExistsError(f"Local registry already exists at {registry_path} (use --overwrite to replace)")

    fs, fs_path = fsspec.core.url_to_fs(source)
    if not fs.exists(fs_path):
        raise FileNotFoundError(f"Source not found: {source}")

    with fs.open(fs_path, "rb") as src_f, open(registry_path, "wb") as dest_f:
        shutil.copyfileobj(src_f, dest_f)

    return registry_path


def upload_registry_to_cloud(
    bucket: str,
    backend: str = "s3",
) -> str:
    """
    Upload the local registry.duckdb to cloud storage.

    The registry is stored at: warp/registry/registry.duckdb

    Args:
        bucket: S3 bucket name
        backend: Storage backend ('s3')

    Returns:
        S3 key where registry was uploaded

    Examples:
        >>> import warpdata as wd
        >>> key = wd.upload_registry_to_cloud(bucket="mydata")
        >>> print(f"Registry uploaded to s3://{bucket}/{key}")
    """
    if backend != "s3":
        raise ValueError(f"Backend '{backend}' not supported")

    bucket = normalize_bucket_name(bucket)

    registry_path = get_config().registry_db.with_suffix(".duckdb")
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found at {registry_path}")

    import boto3
    s3 = boto3.client('s3')

    registry_key = "warp/registry/registry.duckdb"

    print(f"  Uploading registry ({registry_path.stat().st_size / 1e6:.1f} MB)...")
    s3.upload_file(str(registry_path), bucket, registry_key)
    print(f"  ✓ Uploaded to s3://{bucket}/{registry_key}")

    return registry_key


def download_registry_from_cloud(
    bucket: str,
    backend: str = "s3",
    overwrite: bool = True,
) -> Path:
    """
    Download registry.duckdb from cloud storage.

    The registry is downloaded from: warp/registry/registry.duckdb

    Args:
        bucket: S3 bucket name
        backend: Storage backend ('s3')
        overwrite: Overwrite existing local registry

    Returns:
        Path to local registry file

    Examples:
        >>> import warpdata as wd
        >>> path = wd.download_registry_from_cloud(bucket="mydata")
        >>> print(f"Registry downloaded to {path}")
    """
    if backend != "s3":
        raise ValueError(f"Backend '{backend}' not supported")

    bucket = normalize_bucket_name(bucket)

    registry_path = get_config().registry_db.with_suffix(".duckdb")
    ensure_dir(registry_path.parent)

    if registry_path.exists() and not overwrite:
        raise FileExistsError(
            f"Local registry already exists at {registry_path}. "
            "Use overwrite=True to replace."
        )

    import boto3
    s3 = boto3.client('s3')

    registry_key = "warp/registry/registry.duckdb"

    # Check if registry exists in cloud
    try:
        s3.head_object(Bucket=bucket, Key=registry_key)
    except Exception:
        raise FileNotFoundError(
            f"Registry not found at s3://{bucket}/{registry_key}. "
            "Run 'warp sync --upload-registry' first."
        )

    print(f"  Downloading registry from s3://{bucket}/{registry_key}...")
    s3.download_file(bucket, registry_key, str(registry_path))
    print(f"  ✓ Downloaded to {registry_path} ({registry_path.stat().st_size / 1e6:.1f} MB)")

    return registry_path


def generate_manifests_for_bucket(
    bucket: str,
    backend: str = "s3",
    progress: bool = True,
    workers: int = 32,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Generate cloud manifests for all datasets in a legacy bucket.

    This scans all objects in the bucket (using HEAD requests to read metadata),
    groups them by dataset/version, and creates manifests for each.

    Use this to migrate buckets that were created before manifest support was added.

    Args:
        bucket: S3 bucket name
        backend: Storage backend ('s3')
        progress: Show progress bar
        workers: Number of parallel workers for S3 HEAD requests
        dry_run: If True, only show what would be generated

    Returns:
        Dictionary with migration summary

    Examples:
        >>> import warpdata as wd
        >>> result = wd.generate_manifests_for_bucket("my-warp-backup")
        >>> print(f"Generated {result['manifests_created']} manifests")
    """
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if backend != "s3":
        raise ValueError(f"Backend '{backend}' not supported")

    bucket = normalize_bucket_name(bucket)

    print(f"Scanning bucket: {bucket}")
    print("=" * 60)

    import boto3
    s3 = boto3.client('s3')

    # Step 1: List all objects
    print("  Listing objects...")
    all_objects = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix='warp/objects/'):
        all_objects.extend(page.get('Contents', []))

    if not all_objects:
        print("  No objects found in bucket")
        return {"manifests_created": 0, "datasets_found": 0}

    print(f"  Found {len(all_objects)} objects")

    # Step 2: Check which datasets already have manifests
    print("  Checking existing manifests...")
    existing_manifests = set()
    for page in paginator.paginate(Bucket=bucket, Prefix='warp/manifests/'):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('.json') and not key.endswith('/latest.json'):
                # Parse: warp/manifests/workspace/name/version.json
                parts = key.split('/')
                if len(parts) >= 5:
                    ws, nm, vf = parts[2], parts[3], parts[4]
                    vh = vf.replace('.json', '')
                    existing_manifests.add(f"{ws}/{nm}:{vh}")

    print(f"  Found {len(existing_manifests)} existing manifests")

    # Step 3: Scan objects to get metadata (parallel HEAD requests)
    print("  Scanning object metadata...")

    datasets_map = {}

    def get_metadata(obj):
        try:
            meta = s3.head_object(Bucket=bucket, Key=obj['Key'])
            md = meta.get('Metadata', {})
            dataset = md.get('dataset')
            version = md.get('version')
            obj_type = md.get('type', 'resource')
            extension = md.get('extension', 'parquet')

            if not dataset or not version:
                return None

            return {
                'dataset': dataset,
                'version': version,
                'key': obj['Key'],
                'size': obj['Size'],
                'type': obj_type,
                'extension': extension,
                'metadata': md,
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(get_metadata, obj): obj for obj in all_objects}
        for future in tqdm(as_completed(futures), total=len(all_objects),
                          desc="  Scanning", unit="obj", leave=False, disable=not progress):
            result = future.result()
            if result:
                dataset = result['dataset']
                version = result['version']
                ds_key = f"{dataset}:{version}"

                if ds_key not in datasets_map:
                    datasets_map[ds_key] = {
                        'dataset': dataset,
                        'version': version,
                        'resources': [],
                        'embeddings': [],
                        'raw_data': [],
                    }

                obj_type = result['type']
                if obj_type in ('resource', 'dataset_resource'):
                    # Extract content hash from key
                    parts = result['key'].split('/')
                    content_hash = parts[-1] if parts else None

                    datasets_map[ds_key]['resources'].append({
                        'content_hash': content_hash,
                        'uri': f"s3://{bucket}/{result['key']}",
                        'size': result['size'],
                        'extension': result['extension'],
                    })
                elif obj_type == 'embedding':
                    datasets_map[ds_key]['embeddings'].append(result)
                elif obj_type in ('raw_data', 'raw_data_directory_compressed'):
                    datasets_map[ds_key]['raw_data'].append(result)

    # Step 4: Generate manifests for datasets that don't have them
    print(f"\n  Found {len(datasets_map)} dataset versions")

    # Filter to only those needing manifests
    need_manifests = {
        k: v for k, v in datasets_map.items()
        if k not in existing_manifests
    }

    print(f"  Need manifests: {len(need_manifests)}")

    if dry_run:
        print("\n  [DRY RUN] Would generate manifests for:")
        for ds_key in need_manifests:
            print(f"    - {ds_key}")
        return {
            "manifests_created": 0,
            "would_create": len(need_manifests),
            "datasets_found": len(datasets_map),
            "already_have_manifest": len(existing_manifests),
        }

    # Step 5: Generate and upload manifests
    storage = get_storage_backend(backend, bucket=bucket)
    manifests_created = 0
    errors = []

    print("\n  Generating manifests...")
    for ds_key, ds_info in tqdm(need_manifests.items(), desc="  Generating", disable=not progress):
        dataset = ds_info['dataset']
        version = ds_info['version']

        # Parse workspace/name
        if '/' in dataset:
            workspace, name = dataset.split('/', 1)
        else:
            workspace = 'default'
            name = dataset

        # Build cloud manifest
        cloud_manifest = build_cloud_manifest(
            workspace=workspace,
            name=name,
            version_hash=version,
            resources=ds_info['resources'],
            schema={},  # Can't infer schema without reading files
            row_count=None,
            embeddings=[],  # TODO: process embeddings
            raw_data=[],    # TODO: process raw data
            metadata={
                "generated_from": "legacy_migration",
            },
        )

        try:
            manifest_key = storage.put_manifest(
                workspace=workspace,
                name=name,
                version_hash=version,
                manifest_data=cloud_manifest,
                update_latest=True,
            )
            manifests_created += 1
        except Exception as e:
            errors.append({"dataset": ds_key, "error": str(e)})

    # Summary
    print(f"\n{'=' * 60}")
    print("Migration Summary")
    print(f"{'=' * 60}")
    print(f"  Total objects scanned: {len(all_objects)}")
    print(f"  Dataset versions found: {len(datasets_map)}")
    print(f"  Already had manifests: {len(existing_manifests)}")
    print(f"  Manifests created: {manifests_created}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for err in errors[:5]:
            print(f"    - {err['dataset']}: {err['error']}")

    return {
        "manifests_created": manifests_created,
        "datasets_found": len(datasets_map),
        "already_have_manifest": len(existing_manifests),
        "errors": errors,
    }
