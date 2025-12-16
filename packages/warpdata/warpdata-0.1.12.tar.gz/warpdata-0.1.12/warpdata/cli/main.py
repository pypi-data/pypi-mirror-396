#!/usr/bin/env python3
"""
warpdata - Fast data loading and versioning for ML/AI

Quick Start (Python):
    import warpdata as wd

    # Load dataset as DuckDB relation (lazy, memory-efficient)
    rel = wd.load("crypto/coingecko/hourly")
    df = rel.limit(1000).df()  # Slice first, then convert to pandas

    # Works with S3, local files, HTTP
    rel = wd.load("s3://bucket/*.parquet")
    df = wd.load("data.csv", as_format="pandas")  # Small files: pandas OK

Common Commands:
    warp list                           List all local datasets
    warp info <dataset>                 Show dataset details and resources
    warp load <dataset> --limit 5       Preview rows (local)
    warp scaffold <dataset>             Generate Python loader boilerplate
    warp pull --bucket warp -j 8        Bulk download datasets (parallel)

Full help: warp help
Help topics: warp help <topic>  (topics: load, stream, embeddings, cloud, config)
"""
import argparse
import json
import pandas as pd
import sys
from typing import Optional
from pathlib import Path

import warpdata as wd
from warpdata.core.utils import safe_filename


# Topic-based help system
HELP_TOPICS = {
    "overview": """
===============================================================================
WARPDATA - DATA LOADING AND VERSIONING FOR ML/AI
===============================================================================

Install: pip install warpdata[all]
Import:  import warpdata as wd

Dataset IDs
  - Use workspace/name or full warpdata://workspace/name
  - Files/URLs work directly (CSV/Parquet/HTTP/S3/globs)
  - Tip: export WARPDATA_DEFAULT_WORKSPACE=crypto to enable name-only

Core Python API (import warpdata as wd)
  wd.load(source)              Load dataset as DuckDB relation (lazy)
  wd.schema(source)            Get column names and types
  wd.head(source, n=5)         Preview first n rows
  wd.list_datasets()           List all local datasets
  wd.dataset_info(source)      Get dataset metadata
  wd.register_dataset(path)    Register a local dataset
  wd.load_images(source)       Load image dataset with PIL decoding
  wd.is_image_dataset(source)  Check if dataset has image columns
""",

    "load": """
===============================================================================
LOADING DATA (Python + CLI)
===============================================================================

Python: Load / Schema / Head
    rel = wd.load("vision/coco")                      # DuckDB relation (default, lazy)
    df = rel.limit(100).df()                          # Slice then convert to pandas
    df = wd.load("small.csv", as_format="pandas")     # Small files: pandas OK
    schema = wd.schema("vision/coco")
    head = wd.head("vision/coco", n=5)

Python: Efficient Slicing (use DuckDB for large datasets!)
    # Load as DuckDB relation for lazy evaluation
    rel = wd.load("text/gutenberg-en-50k", as_format="duckdb")

    # Slice efficiently - only reads needed rows from disk
    subset = rel.limit(1000)                    # First 1000 rows
    subset = rel.offset(500).limit(1000)        # Rows 500-1500
    subset = rel.filter("year > 2020")          # Filter condition
    subset = rel.project("id", "text", "label") # Select columns

    # Then convert to pandas/numpy
    df = subset.df()  # or .to_df() for pandas

Python: Row IDs for Embeddings Workflow
    # Use include_rid=True to get 0-based row IDs for embeddings
    rel = wd.load("text/corpus", include_rid=True)
    df = rel.limit(1000).df()
    rids = df['rid'].tolist()

    # Load embeddings for just those rows
    from warpdata.api.embeddings import load_embeddings
    X = load_embeddings("text/corpus", space="minilm", rids=rids)

CLI: Preview
    warp list                                   # All local datasets
    warp info vision/coco                       # Schema + resources
    warp load vision/coco --limit 5             # Preview rows
    warp load vision/coco --include-rid         # Include rid column

Best Practices
  - Use as_format='duckdb' (default) for lazy evaluation
  - Use .limit()/.offset()/.filter() BEFORE converting to pandas
  - Use include_rid=True when you need row IDs for embeddings
  - Project needed columns only: rel.project("col1", "col2")
  - Don't load 10GB+ datasets with as_format='pandas'
""",

    "stream": """
===============================================================================
STREAMING DATA (for huge datasets, 10GB+ / billions of rows)
===============================================================================

Python: Zero-Copy Streaming
    from warpdata.api.streaming import stream, stream_batch_dicts

    # Option 1: Raw Arrow batches (fastest, zero-copy)
    for batch in stream("text/wikipedia-main", batch_size=50000):
        # batch is pyarrow.RecordBatch (zero-copy)
        texts = batch['text'].to_pylist()
        # Or convert to pandas: df = batch.to_pandas()
        process(texts)

    # Option 2: Dict batches (compatible with collators)
    for batch in stream_batch_dicts("text/fineweb2-mix", batch_size=10000):
        # batch is {'text': [...], 'url': [...]}
        train_step(batch)

    # Option 3: Multi-worker with file sharding (distributed training)
    for batch in stream("text/wikipedia-main",
                        batch_size=50000,
                        shard=(worker_rank, world_size)):
        # Each worker reads different files (no duplicates!)
        train_step(batch)

Best Practices
  - Use streaming for datasets >10GB to prevent OOM
  - Use shard=(rank, world_size) for multi-worker training
  - Don't have multiple workers read the same files
""",

    "embeddings": """
===============================================================================
EMBEDDINGS (compute, search, load)
===============================================================================

Python: Embeddings API
    from warpdata.api.embeddings import (
        add_embeddings, search_embeddings, load_embeddings,
        list_embeddings, join_results
    )

    # Add embeddings to a dataset
    add_embeddings("vision/coco-train", space="captions",
                   provider="sentence-transformers",
                   model="sentence-transformers/all-MiniLM-L6-v2",
                   source={"columns": ["first_caption"]})

    # Search embeddings
    results = search_embeddings("vision/coco-train", space="captions",
                                query="a dog", top_k=5)
    rids = [r["rid"] for r in results]

    # Join search results with original data
    df_top = join_results("vision/coco-train", rids=rids)

    # Load embeddings as numpy array
    X = load_embeddings("vision/celeba-attrs", space="clip")  # np.ndarray [N, dim]

    # Load only specific rows (efficient!)
    X_subset = load_embeddings("vision/celeba-attrs", space="clip", rids=rids)

    # List available embeddings
    spaces = list_embeddings("vision/coco-train")

CLI: Embeddings
    warp embeddings add vision/coco-train --space captions \\
        --provider sentence-transformers \\
        --model sentence-transformers/all-MiniLM-L6-v2 \\
        --column first_caption
    warp embeddings list vision/coco-train
    warp embeddings search vision/coco-train --space captions --query "a dog" --top-k 5
    warp embeddings run vision/celeba-attrs --space clip

Best Practices
  - Load embeddings with rids parameter to subset efficiently
  - Don't load all embeddings when you only need a subset
""",

    "images": """
===============================================================================
IMAGE DATASETS
===============================================================================

warpdata auto-detects image datasets and provides utilities for working with
embedded images (stored as BLOB columns in parquet/duckdb).

Python: Check if Dataset Has Images
    import warpdata as wd

    wd.is_image_dataset("vision/coco-embedded")    # True
    wd.is_image_dataset("nlp/imdb")                # False
    wd.get_image_columns("vision/coco-embedded")   # ['image']

Python: Load Images with Auto-Decoding
    # Load with automatic PIL decoding (recommended)
    df = wd.load_images("vision/coco-embedded", limit=10)
    df['image'].iloc[0].show()          # Display first image (PIL Image)
    df['image'].iloc[0].size            # (width, height)

    # Load specific columns (image columns auto-included)
    df = wd.load_images("vision/coco-embedded",
                        columns=["file_name", "first_caption"],
                        limit=100)

Python: Manual Decoding
    # Load raw bytes
    df = wd.load("vision/coco-embedded", limit=1, as_format="pandas")

    # Decode single image
    img = wd.decode_image(df['image'].iloc[0])              # PIL Image
    img_np = wd.decode_image(df['image'].iloc[0], format="numpy")  # numpy array

    # Decode entire column
    df = wd.decode_images_column(df, "image")               # Modifies column in-place

Python: Get Image Dataset Info
    info = wd.image_dataset_info("vision/coco-embedded")
    # {'is_image_dataset': True, 'image_columns': ['image'], 'all_columns': [...]}

Available Image Datasets
    vision/coco-embedded     163k images with captions (25GB, chunked parquet)
    vision/mnist             60k handwritten digits
    vision/fashion_mnist     60k fashion items
    vision/cifar10           60k small images (10 classes)
    vision/celeba-attrs      200k celebrity faces with attributes
    vision/imagenet-1k       ImageNet validation set

Best Practices
  - Use load_images() for convenient auto-decoding to PIL
  - Use limit= to avoid loading too many images at once
  - For large-scale processing, use wd.load() and decode in batches
  - Image datasets use chunked parquet (5GB chunks) for memory safety
""",

    "cloud": """
===============================================================================
CLOUD SYNC & PULL
===============================================================================

CLI: Cloud Operations
    warp pull --bucket warp --list                    # List remote datasets
    warp pull nlp/imdb --bucket warp                  # Pull single dataset
    warp pull --bucket warp                           # Pull all (sequential)
    warp pull --bucket warp -j 8                      # Pull all (8 parallel workers)
    warp pull --bucket warp --mode register-only      # Register without downloading
    warp pull --bucket warp --mode metadata           # Download parquet footers only
    warp sync --bucket mybucket                       # Sync local datasets to S3
    warp sync --bucket mybucket --upload-registry     # Also upload registry

Python: Cloud Operations
    from warpdata.api.storage import (
        pull_dataset, sync_to_cloud, list_remote_datasets,
        bulk_pull, pull_all_datasets,
        upload_registry_to_cloud, download_registry_from_cloud
    )

    # List remote datasets
    datasets = list_remote_datasets(bucket='warp')

    # Pull single dataset
    pull_dataset("nlp/imdb", bucket='warp')

    # Pull with lazy modes
    pull_dataset("nlp/imdb", bucket='warp', mode='register-only')  # No download
    pull_dataset("nlp/imdb", bucket='warp', max_bytes=10_000_000)  # Limit size

    # Bulk download (parallel)
    result = bulk_pull(['nlp/imdb', 'nlp/ag-news'], workers=8)

    # Pull all datasets from bucket
    pull_all_datasets(bucket='warp', workers=8)

    # Sync to cloud
    sync_to_cloud(bucket='mybucket')

    # Registry sync
    upload_registry_to_cloud(bucket='mybucket')
    download_registry_from_cloud(bucket='mybucket')

Manifest-Based Discovery
  Cloud operations use manifests for O(1) dataset discovery.
  For legacy buckets without manifests:
    warp manifest generate --bucket mybucket
""",

    "config": """
===============================================================================
CONFIGURATION
===============================================================================

Environment Variables
  WARPDATA_DEFAULT_WORKSPACE    Enable name-only loads (e.g., "crypto")
  WARPDATA_CACHE_DIR            Relocate cache directory
  WARPDATA_REGISTRY_PATH        Custom registry location (default: ~/.warpdata/registry.duckdb)

Cache Management (CLI)
    warp cache stats                    # Show local disk usage
    warp cache stats --verbose          # Show per-dataset sizes
    warp cache clear                    # Clear entire cache

Generate Python Loaders (smart, dataset-aware)
    warp scaffold vision/vesuvius-scrolls         # -> vision_vesuvius-scrolls_loader.py
    warp scaffold crypto/binance-klines-um-1h     # -> crypto_binance-klines-um-1h_loader.py
    warp scaffold vision/coco-embedded -o my.py   # -> my.py

Registry
  The registry is stored as a DuckDB database at ~/.warpdata/registry.duckdb.
  Export/import for backup:
    # Python
    from warpdata.core.registry import get_registry
    reg = get_registry()
    # Registry methods available for inspection

Best Practices
  - Use warpdata://workspace/name IDs consistently
  - Resolve paths once, operate on local paths in hot loops
  - Don't trigger network/sync/pull in automated agents
""",
}

# For backward compatibility
EXTENDED_HELP = HELP_TOPICS["overview"] + HELP_TOPICS["load"] + HELP_TOPICS["images"] + HELP_TOPICS["stream"] + HELP_TOPICS["embeddings"] + HELP_TOPICS["cloud"] + HELP_TOPICS["config"]


def cmd_load(args):
    """Load and display dataset."""
    try:
        # Default to 100 rows for CLI to prevent OOM on large datasets
        limit = args.limit if hasattr(args, 'limit') and args.limit is not None else 100
        include_rid = getattr(args, 'include_rid', False)

        # Load as DuckDB first for efficient limiting, then convert to pandas
        rel = wd.load(args.source, as_format="duckdb", include_rid=include_rid)
        if limit is not None:
            rel = rel.limit(limit)
        df = rel.df()
        # Show schema alongside the preview
        try:
            schema = wd.schema(args.source)
        except Exception:
            schema = None

        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        if schema:
            print("\nSchema:")
            for col, dtype in schema.items():
                print(f"  {col}: {dtype}")

        # Print preview without pandas truncation of columns or cell contents
        n_head = args.head if hasattr(args, 'head') else 5
        print("\nFirst rows:")
        with pd.option_context(
            'display.max_columns', None,
            'display.max_colwidth', None,
            'display.width', None,
            'display.expand_frame_repr', False,
        ):
            print(df.head(n_head))
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_schema(args):
    """Show dataset schema."""
    try:
        schema = wd.schema(args.source)
        print(f"Schema for {args.source}:")
        for col, dtype in schema.items():
            print(f"  {col}: {dtype}")
    except Exception as e:
        print(f"Error getting schema: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List datasets (local or remote)."""
    try:
        if getattr(args, 'remote', False):
            # Remote listing (e.g., S3 bucket)
            backend = getattr(args, 'backend', 's3')
            bucket = getattr(args, 'bucket', None)
            if not bucket:
                print("Error: --bucket is required for remote listing", file=sys.stderr)
                sys.exit(2)
            remote = wd.list_remote_datasets(backend=backend, bucket=bucket)
            if not remote:
                print(f"No remote datasets found in {backend}://{bucket}")
                return
            print(f"🌐 Remote datasets in {backend}://{bucket} ({len(remote)} versions):\n")
            for item in sorted(remote, key=lambda x: x['dataset']):
                ds = item['dataset']
                ver = item['version'][:8]
                size_display = _format_size_gb_mb(item.get('size'))
                print(f"  {ds:40s} v:{ver} {size_display:>10s}")
            print("\n💡 Use 'warp pull --list --bucket <name>' to explore and download")
            return

        # Local listing (default)
        datasets = wd.list_datasets(workspace=args.workspace if hasattr(args, 'workspace') else None)
        if not datasets:
            print("No datasets found")
            return

        # Precompute dataset sizes from cache for quick lookup
        from warpdata.core.cache import get_cache

        cache = get_cache()
        datasets_root = cache.datasets_dir
        dataset_sizes = {}
        for ds in datasets:
            workspace = ds.get('workspace')
            name = ds.get('name')
            if not workspace or not name:
                continue
            ds_dir = datasets_root / workspace / Path(name)
            try:
                if ds_dir.exists():
                    dataset_sizes[(workspace, name)] = _dir_size(ds_dir)
            except Exception:
                continue

        # Check if verbose mode
        verbose = hasattr(args, 'verbose') and args.verbose

        if verbose:
            # Verbose output with embedding summary
            print(f"Found {len(datasets)} datasets:\n")
            for ds in datasets:
                workspace = ds.get('workspace', 'unknown')
                name = ds.get('name', 'unknown')
                version = ds.get('latest_version', 'none')
                dataset_id = f"warpdata://{workspace}/{name}"
                print(f"  {dataset_id}")
                print(f"    Latest version: {version[:16]}...")
                size_display = _format_size_gb_mb(dataset_sizes.get((workspace, name)))
                print(f"    Size: {size_display}")
                # Show embeddings if available
                try:
                    spaces = wd.list_embeddings(dataset_id)
                except Exception:
                    spaces = []
                if spaces:
                    present = []
                    missing = []
                    for s in spaces:
                        if isinstance(s, dict):
                            nm = s.get('space_name', '')
                            sp = s.get('storage_path')
                        else:
                            nm = str(s)
                            sp = None
                        ok = False
                        if sp:
                            vec = Path(sp) / 'vectors.parquet'
                            ok = vec.exists()
                        present.append(nm) if ok else missing.append(nm)
                    if present:
                        print(f"    Embeddings (present): |- {', '.join(present)}")
                    if missing:
                        print(f"    Embeddings (missing on disk): |- {', '.join(missing)}")
        else:
            # Compact table output grouped by workspace, with embeddings summary
            from collections import defaultdict

            # Group by workspace
            by_workspace = defaultdict(list)
            for ds in datasets:
                workspace = ds.get('workspace', 'unknown')
                name = ds.get('name', 'unknown')
                version = ds.get('latest_version', 'none')[:8]
                by_workspace[workspace].append((name, version))

            # Print header
            print(f"📊 {len(datasets)} datasets across {len(by_workspace)} workspaces")
            print()

            # Print by workspace
            for workspace in sorted(by_workspace.keys()):
                datasets_in_workspace = by_workspace[workspace]
                print(f"  {workspace}/ ({len(datasets_in_workspace)} datasets)")
                for name, version in sorted(datasets_in_workspace):
                    dataset_id = f"warpdata://{workspace}/{name}"
                    size_display = _format_size_gb_mb(dataset_sizes.get((workspace, name)))
                    line = f"    • {name:35s} v:{version}  size:{size_display}"
                    # Append compact embeddings summary if present
                    try:
                        spaces = wd.list_embeddings(dataset_id)
                    except Exception:
                        spaces = []
                    if spaces:
                        present = []
                        missing = []
                        for s in spaces:
                            if isinstance(s, dict):
                                nm = s.get('space_name', '')
                                sp = s.get('storage_path')
                            else:
                                nm = str(s)
                                sp = None
                            ok = False
                            if sp:
                                vec = Path(sp) / 'vectors.parquet'
                                ok = vec.exists()
                            if ok:
                                present.append(nm)
                            else:
                                missing.append(nm)
                        if present:
                            line += "  |- " + ", ".join(present)
                        elif missing:
                            line += "  |- (missing on disk)"
                    print(line)
                print()

            print("💡 Use --verbose for full version hashes and embedding details")
            print("💡 Use --workspace <name> to filter by workspace")
            print("💡 Use --remote --bucket <name> to list remote datasets")
    except Exception as e:
        print(f"Error listing datasets: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_module(args):
    """Module commands: schema, fetch (materialize)."""
    from warpdata.modules import get_module

    if args.module_cmd == 'schema':
        try:
            mod = get_module(args.id)
            schema = mod.get_schema()
            if getattr(args, 'json', False):
                print(json.dumps(schema, indent=2, sort_keys=True))
            else:
                print(f"Schema for module {args.id}:")
                cols = schema.get('columns') if isinstance(schema, dict) else None
                if isinstance(cols, dict):
                    for k, v in cols.items():
                        print(f"  {k}: {v}")
                elif isinstance(cols, list):
                    for c in cols:
                        name = c.get('name') if isinstance(c, dict) else str(c)
                        dtype = c.get('dtype') if isinstance(c, dict) else 'UNKNOWN'
                        print(f"  {name}: {dtype}")
                else:
                    for k, v in (schema or {}).items():
                        print(f"  {k}: {v}")
        except Exception as e:
            print(f"Error loading module schema: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.module_cmd == 'fetch':
        try:
            mod = get_module(args.id)
            cache_dir = Path(args.cache_dir).resolve() if getattr(args, 'cache_dir', None) else None
            out_dir = mod.prepare(split=args.split or '', cache_dir=cache_dir, force=getattr(args, 'force', False))
            print(f"✅ Fetched module {args.id}")
            print(f"   Output directory: {out_dir}")
            p = out_dir / 'materialized.parquet'
            if p.exists():
                print(f"   File: {p} ({p.stat().st_size/1e6:.2f} MB)")
        except Exception as e:
            print(f"Error fetching module data: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_info(args):
    """Show dataset information."""
    try:
        info = wd.dataset_info(args.dataset_id)
        print(f"Dataset: {args.dataset_id}")
        print(f"Workspace: {info.get('workspace')}")
        print(f"Name: {info.get('name')}")
        print(f"Version: {info.get('version_hash', 'unknown')[:16]}...")

        # Show schema
        try:
            schema = wd.schema(args.dataset_id)
            if schema:
                print(f"\nSchema ({len(schema)} columns):")
                for col_name, col_type in schema.items():
                    print(f"  {col_name}: {col_type}")
        except Exception:
            pass

        # Show row count
        try:
            rel = wd.load(args.dataset_id)
            count = rel.count("*").fetchone()[0]
            print(f"\nRows: {count:,}")
        except Exception:
            pass

        # Show embeddings if available
        try:
            embeddings = wd.list_embeddings(args.dataset_id)
            if embeddings:
                print(f"\nEmbedding Spaces ({len(embeddings)}):")
                for emb in embeddings:
                    sp = emb.get('storage_path')
                    ok = Path(sp).joinpath('vectors.parquet').exists() if sp else False
                    status = "OK" if ok else "missing"
                    print(f"  - {emb['space_name']} [{status}]")
                    print(f"    Model: {emb['model']} ({emb['dimension']}-dim, {emb['distance_metric']})")
        except Exception:
            pass

        print(f"\nManifest:")
        print(json.dumps(info.get('manifest', {}), indent=2, default=str))
    except Exception as e:
        print(f"Error getting dataset info: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_detect_frames(args):
    """Detect likely frames column in a dataset or a logical table."""
    try:
        # If a table is specified, derive schema by loading a small sample
        if getattr(args, 'table', None):
            rel = wd.load_table(args.dataset_id, table=args.table, as_format='duckdb')
            schema = {c: str(t) for c, t in zip(rel.columns, rel.types)}
        else:
            schema = wd.schema(args.dataset_id)
        name_candidates = ["frames", "voxels", "bold", "signals", "vector", "embedding"]
        type_candidates = {"LIST", "LIST<FLOAT>", "LIST<FLOAT32>", "FLOAT[]", "DOUBLE[]"}

        matches = []
        for col, dtype in (schema or {}).items():
            c = col.lower()
            if any(k in c for k in name_candidates):
                matches.append((col, dtype, "name"))
            elif str(dtype).upper() in type_candidates:
                matches.append((col, dtype, "type"))

        if not matches:
            print("No likely frames column detected.")
            print("Hint: common names are: frames, voxels, bold, signals")
            sys.exit(2)

        print("Likely frames columns:")
        for (col, dtype, how) in matches:
            print(f"  - {col} (type: {dtype}, detected: {how})")

        print(f"\nBest guess: --frame-col {matches[0][0]}")
    except Exception as e:
        print(f"Error detecting frames: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_register(args):
    """Register a new dataset."""
    try:
        version = wd.register_dataset(
            args.dataset_id,
            resources=args.resources,
            metadata=json.loads(args.metadata) if hasattr(args, 'metadata') and args.metadata else None
        )
        print(f"✅ Registered {args.dataset_id}")
        print(f"   Version: {version}")
    except Exception as e:
        print(f"Error registering dataset: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_materialize(args):
    """Materialize dataset with row IDs."""
    try:
        path = wd.materialize(
            args.dataset_id,
            force=args.force if hasattr(args, 'force') else False,
            update_registry=getattr(args, 'update_registry', False)
        )
        print(f"✅ Materialized to: {path}")
    except Exception as e:
        print(f"Error materializing dataset: {e}", file=sys.stderr)
        sys.exit(1)


def _human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024 or u == units[-1]:
            return f"{size:.1f} {u}"
        size /= 1024


def _format_size_gb_mb(num_bytes: Optional[int]) -> str:
    """
    Format bytes as GB (preferred) or MB if below 1GB.
    """
    if num_bytes is None:
        return "--"
    gb = num_bytes / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.1f} GB"
    mb = num_bytes / (1024 ** 2)
    return f"{mb:.1f} MB"


def _dir_size(path: Path) -> int:
    total = 0
    for p in path.rglob('*'):
        try:
            if p.is_file():
                total += p.stat().st_size
        except Exception:
            pass
    return total


def cmd_cache(args):
    """Cache utilities (prune, stats, etc.)."""
    from warpdata.core.cache import get_cache
    from warpdata.core.uris import parse_uri

    cache = get_cache()
    datasets_root = cache.datasets_dir
    from warpdata.core.registry import get_registry
    registry = get_registry()

    if args.cache_cmd == 'stats':
        # Show cache statistics
        workspace_filter = getattr(args, 'workspace', None)
        verbose = getattr(args, 'verbose', False)

        # Collect dataset sizes
        from collections import defaultdict
        workspace_sizes = defaultdict(int)
        workspace_counts = defaultdict(int)
        dataset_sizes = []

        datasets = registry.list_datasets(workspace_filter) if workspace_filter else registry.list_datasets()

        for ds in datasets:
            ws = ds.get('workspace')
            name = ds.get('name')
            if not ws or not name:
                continue

            ds_dir = datasets_root / ws / Path(name)
            if ds_dir.exists():
                size = _dir_size(ds_dir)
                workspace_sizes[ws] += size
                workspace_counts[ws] += 1
                dataset_sizes.append((f"{ws}/{name}", size))

        # Calculate totals
        total_size = sum(workspace_sizes.values())
        total_datasets = sum(workspace_counts.values())

        print("📊 Cache Statistics")
        print("="*70)
        print(f"Cache directory: {datasets_root}")
        print(f"Total size: {_human_size(total_size)}")
        print(f"Total datasets: {total_datasets}")

        if workspace_filter:
            print(f"Filtered to workspace: {workspace_filter}")

        print(f"\n📦 By Workspace:")
        for ws in sorted(workspace_sizes.keys(), key=lambda x: workspace_sizes[x], reverse=True):
            size = workspace_sizes[ws]
            count = workspace_counts[ws]
            print(f"  {ws:20s} {_human_size(size):>10s}  ({count} dataset(s))")

        if verbose and dataset_sizes:
            print(f"\n📁 By Dataset (top 20):")
            dataset_sizes.sort(key=lambda x: x[1], reverse=True)
            for ds_name, size in dataset_sizes[:20]:
                print(f"  {ds_name:40s} {_human_size(size):>10s}")
            if len(dataset_sizes) > 20:
                print(f"  ... and {len(dataset_sizes) - 20} more datasets")

        # Check for raw data
        raw_data_dir = cache.cache_dir / "raw_data"
        if raw_data_dir.exists():
            raw_size = _dir_size(raw_data_dir)
            if raw_size > 0:
                print(f"\n📦 Raw Data: {_human_size(raw_size)}")

        # Check for embeddings
        embeddings_total = 0
        for ds in datasets:
            ws = ds.get('workspace')
            name = ds.get('name')
            if not ws or not name:
                continue
            ds_dir = datasets_root / ws / Path(name)
            if ds_dir.exists():
                for version_dir in ds_dir.iterdir():
                    if version_dir.is_dir():
                        emb_dir = version_dir / "embeddings"
                        if emb_dir.exists():
                            embeddings_total += _dir_size(emb_dir)

        if embeddings_total > 0:
            print(f"🔢 Embeddings: {_human_size(embeddings_total)}")

        print("\n💡 Use 'warp cache prune' to remove old dataset versions")
        return

    if args.cache_cmd == 'prune':
        keep = max(int(getattr(args, 'keep', 1) or 1), 1)
        dry_run = bool(getattr(args, 'dry_run', False))
        workspace_filter = getattr(args, 'workspace', None)

        datasets_to_check = []
        dsarg = getattr(args, 'dataset_id', None)
        if dsarg:
            # Accept warpdata://workspace/name[/sub] or workspace/name[/sub]
            if '://' in dsarg:
                uri = parse_uri(dsarg)
                if not uri.is_warpdata:
                    print(f"Error: invalid dataset id '{dsarg}'. Expected warpdata:// URI", file=sys.stderr)
                    sys.exit(2)
                datasets_to_check.append((uri.workspace, uri.name))
            else:
                try:
                    workspace, name = dsarg.split('/', 1)
                except ValueError:
                    print(f"Error: invalid dataset id '{dsarg}'. Use workspace/name or warpdata://workspace/name", file=sys.stderr)
                    sys.exit(2)
                datasets_to_check.append((workspace, name))
        else:
            # Enumerate from registry to handle nested dataset names correctly
            if workspace_filter:
                items = registry.list_datasets(workspace_filter)
            else:
                items = registry.list_datasets()
            for it in items:
                ws = it.get('workspace'); name = it.get('name')
                if ws and name:
                    datasets_to_check.append((ws, name))

        if not datasets_to_check:
            print("No datasets found in cache to prune.")
            return

        total_removed = 0
        total_bytes = 0
        for (ws, name) in sorted(set(datasets_to_check)):
            # Handle nested dataset names by letting Path split 'name' into subdirs
            ds_dir = datasets_root / ws / Path(name)
            if not ds_dir.exists():
                continue
            # Collect version directories (exclude 'recipes' and non-directories)
            versions = []
            for vdir in ds_dir.iterdir():
                if not vdir.is_dir():
                    continue
                if vdir.name.lower() == 'recipes':
                    continue
                try:
                    mtime = vdir.stat().st_mtime
                except Exception:
                    mtime = 0
                versions.append((mtime, vdir))

            if len(versions) <= keep:
                continue

            versions.sort(reverse=True, key=lambda x: x[0])
            to_keep = [v for _, v in versions[:keep]]
            to_remove = [v for _, v in versions[keep:]]

            if not to_remove:
                continue

            print(f"{ws}/{name}: keeping {len(to_keep)} version(s), pruning {len(to_remove)}")
            for v in to_remove:
                size = _dir_size(v)
                if dry_run:
                    print(f"  DRY-RUN would remove {v} ({_human_size(size)})")
                else:
                    import shutil
                    try:
                        shutil.rmtree(v, ignore_errors=True)
                        print(f"  Removed {v} ({_human_size(size)})")
                        total_removed += 1
                        total_bytes += size
                    except Exception as e:
                        print(f"  Error removing {v}: {e}")

        if dry_run:
            print("\nDRY-RUN complete. No files were removed.")
        else:
            print(f"\nPrune complete. Removed {total_removed} version dir(s), reclaimed {_human_size(total_bytes)}.")
        return

    if args.cache_cmd == 'clean':
        dry_run = bool(getattr(args, 'dry_run', False))
        workspace_filter = getattr(args, 'workspace', None)
        clean_recipes = bool(getattr(args, 'recipes', False))

        if not clean_recipes:
            print("Usage: warp cache clean --recipes [--dry-run] [--workspace <ws>]")
            print("\nOptions:")
            print("  --recipes    Remove recipe folders (duplicated after materialization)")
            print("  --dry-run    Show what would be removed without deleting")
            print("  --workspace  Filter to a specific workspace")
            return

        # Find all recipe folders that have a sibling materialized version
        import shutil
        total_size = 0
        total_removed = 0
        recipes_found = []

        # Scan all dataset directories
        for ws_dir in datasets_root.iterdir():
            if not ws_dir.is_dir():
                continue
            ws_name = ws_dir.name
            if workspace_filter and ws_name != workspace_filter:
                continue

            # Handle nested dataset structures
            for ds_path in ws_dir.rglob("recipes"):
                if not ds_path.is_dir():
                    continue
                ds_dir = ds_path.parent

                # Check if there's a materialized version (hash folder with materialized.parquet)
                has_materialized = False
                for sibling in ds_dir.iterdir():
                    if sibling.is_dir() and sibling.name != 'recipes':
                        # Check if it has materialized.parquet
                        if (sibling / "materialized.parquet").exists():
                            has_materialized = True
                            break

                if has_materialized:
                    size = _dir_size(ds_path)
                    if size > 0:  # Only count non-empty
                        recipes_found.append((ds_path, size))
                        total_size += size

        if not recipes_found:
            print("No recipe folders found to clean.")
            return

        # Sort by size descending
        recipes_found.sort(key=lambda x: -x[1])

        # First, fix registry entries that point to recipe files
        if not dry_run:
            print("🔧 Fixing registry entries to point to materialized files...")
            import json
            import sqlite3
            conn = sqlite3.connect(registry.db_path)
            fixed_registry = 0

            for recipe_path, _ in recipes_found:
                ds_dir = recipe_path.parent
                ws_name = ds_dir.parent.name
                ds_name = ds_dir.name

                # Handle nested dataset names
                rel_to_root = ds_dir.relative_to(datasets_root)
                parts = list(rel_to_root.parts)
                if len(parts) > 2:
                    ws_name = parts[0]
                    ds_name = '/'.join(parts[1:])

                # Find local materialized.parquet
                local_mat_path = None
                local_version = None
                for vdir in ds_dir.iterdir():
                    if vdir.is_dir() and vdir.name != 'recipes':
                        mat_path = vdir / "materialized.parquet"
                        if mat_path.exists():
                            local_mat_path = mat_path
                            local_version = vdir.name
                            break

                if not local_mat_path or not local_version:
                    continue

                # Check if manifest points to recipes
                cur = conn.execute(
                    'SELECT manifest_json FROM versions WHERE workspace=? AND name=? AND version_hash=?',
                    (ws_name, ds_name, local_version)
                )
                row = cur.fetchone()
                if not row:
                    continue

                manifest = json.loads(row[0])
                resources = manifest.get('resources', [])
                needs_fix = any('/recipes/' in r.get('uri', '') for r in resources)

                if needs_fix:
                    new_uri = f"file://{local_mat_path}"
                    manifest['resources'] = [{
                        "uri": new_uri, "checksum": None,
                        "size": local_mat_path.stat().st_size, "type": "file"
                    }]
                    conn.execute(
                        'UPDATE versions SET manifest_json=? WHERE workspace=? AND name=? AND version_hash=?',
                        (json.dumps(manifest), ws_name, ds_name, local_version)
                    )
                    conn.execute('DELETE FROM resources WHERE workspace=? AND name=? AND version_hash=?',
                        (ws_name, ds_name, local_version))
                    conn.execute(
                        'INSERT INTO resources (workspace, name, version_hash, uri, checksum, size, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime("now"))',
                        (ws_name, ds_name, local_version, new_uri, None, local_mat_path.stat().st_size)
                    )
                    conn.execute('UPDATE datasets SET latest_version=? WHERE workspace=? AND name=?',
                        (local_version, ws_name, ds_name))
                    fixed_registry += 1

            conn.commit()
            conn.close()
            if fixed_registry > 0:
                print(f"   Fixed {fixed_registry} registry entries")

        print(f"\n🧹 Found {len(recipes_found)} recipe folders ({_human_size(total_size)} total)")
        print("=" * 70)

        for recipe_path, size in recipes_found:
            rel_path = recipe_path.relative_to(datasets_root)
            if dry_run:
                print(f"  DRY-RUN would remove {rel_path} ({_human_size(size)})")
            else:
                try:
                    shutil.rmtree(recipe_path, ignore_errors=True)
                    print(f"  Removed {rel_path} ({_human_size(size)})")
                    total_removed += 1
                except Exception as e:
                    print(f"  Error removing {rel_path}: {e}")

        print()
        if dry_run:
            print(f"DRY-RUN complete. Would remove {len(recipes_found)} folders, reclaiming {_human_size(total_size)}.")
        else:
            print(f"✅ Clean complete. Removed {total_removed} recipe folders, reclaimed {_human_size(total_size)}.")
        return


def cmd_embeddings(args):
    """Handle embeddings commands."""
    if args.embeddings_cmd == 'add':
        try:
            kwargs = {}
            if hasattr(args, 'batch_size') and args.batch_size:
                kwargs['batch_size'] = args.batch_size
            if hasattr(args, 'max_rows') and args.max_rows:
                kwargs['max_rows'] = args.max_rows
            if hasattr(args, 'rows_per_chunk') and args.rows_per_chunk:
                kwargs['rows_per_chunk'] = args.rows_per_chunk
            if hasattr(args, 'device') and args.device:
                kwargs['device'] = args.device
            if hasattr(args, 'write_rows_per_group') and args.write_rows_per_group:
                kwargs['write_rows_per_group'] = args.write_rows_per_group
            wd.add_embeddings(
                dataset_id=args.dataset_id,
                space=args.space,
                provider=args.provider,
                model=args.model,
                source={"columns": [args.column]},
                **kwargs,
            )
            print(f"✅ Added embeddings: {args.space}")
        except Exception as e:
            print(f"Error adding embeddings: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.embeddings_cmd == 'search':
        try:
            results = wd.search_embeddings(
                args.dataset_id,
                space=args.space,
                query=args.query,
                top_k=args.top_k
            )
            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. Distance: {result['distance']:.3f}")
                # Print first available field for context (text or image path)
                for key in ['text', 'title', 'review_text', 'content', 'image_path']:
                    if key in result:
                        print(f"   {result[key][:100]}...")
                        break
        except Exception as e:
            print(f"Error searching embeddings: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.embeddings_cmd == 'list':
        try:
            spaces = wd.list_embeddings(args.dataset_id, all_versions=getattr(args, 'all', False))
            if not spaces:
                print(f"No embeddings found for {args.dataset_id}")
            else:
                print(f"Embedding spaces for {args.dataset_id}:")
                for s in spaces:
                    if isinstance(s, dict):
                        nm = s.get('space_name', '')
                        sp = s.get('storage_path')
                        ok = Path(sp).joinpath('vectors.parquet').exists() if sp else False
                        status = "OK" if ok else "missing"
                        print(f"  - {nm} [{status}] {sp or ''}")
                    else:
                        print(f"  - {s}")
        except Exception as e:
            print(f"Error listing embeddings: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.embeddings_cmd == 'remove':
        try:
            wd.remove_embeddings(args.dataset_id, space=args.space, delete_files=getattr(args, 'delete_files', False))
            print(f"✅ Removed embeddings: {args.space}")
        except Exception as e:
            print(f"Error removing embeddings: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.embeddings_cmd == 'migrate':
        try:
            moved = wd.migrate_embeddings_to_latest(args.dataset_id, move=getattr(args, 'move', False), copy=getattr(args, 'copy', False))
            if not moved:
                print("No spaces needed migration (already on latest or duplicates present).")
            else:
                print("Migrated spaces:")
                for m in moved:
                    print(f"  - {m['space']}: {m['from_version'][:8]} -> {m['to_version'][:8]} ({m['provider']}:{m['model']})")
        except Exception as e:
            print(f"Error migrating embeddings: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.embeddings_cmd == 'run':
        # Smart defaults wrapper around 'add'
        try:
            column = getattr(args, 'column', None)
            provider = getattr(args, 'provider', None)
            model = getattr(args, 'model', None)
            batch_size = getattr(args, 'batch_size', None)
            max_rows = getattr(args, 'max_rows', None)
            rows_per_chunk = getattr(args, 'rows_per_chunk', None)
            device = getattr(args, 'device', None)
            write_rows_per_group = getattr(args, 'write_rows_per_group', None)

            if column is None:
                schema = wd.schema(args.dataset_id) or {}
                cols = {c.lower(): c for c in schema.keys()}
                candidates = [
                    'image_path', 'filepath', 'path',
                    'first_caption', 'all_captions', 'caption', 'captions',
                    'text', 'content', 'review_text', 'body', 'abstract', 'sentence', 'title'
                ]
                for lc in candidates:
                    if lc in cols:
                        column = cols[lc]
                        break
                if column is None:
                    raise ValueError("Could not infer a column to embed; please pass --column")

            if provider is None:
                if column.lower() in {'image_path', 'filepath', 'path'}:
                    provider = 'clip'
                else:
                    provider = 'sentence-transformers'

            kwargs = {}
            if batch_size is not None:
                kwargs['batch_size'] = batch_size
            if max_rows is not None:
                kwargs['max_rows'] = max_rows
            if rows_per_chunk is not None:
                kwargs['rows_per_chunk'] = rows_per_chunk
            if device is not None:
                kwargs['device'] = device
            if write_rows_per_group is not None:
                kwargs['write_rows_per_group'] = write_rows_per_group

            wd.add_embeddings(
                dataset_id=args.dataset_id,
                space=args.space,
                provider=provider,
                model=model,
                source={"columns": [column]},
                **kwargs,
            )
            print(f"✅ Added embeddings: {args.space} ({provider}:{model or 'default'}) on column '{column}'")
        except Exception as e:
            print(f"Error running embeddings: {e}", file=sys.stderr)
            sys.exit(1)


def _parse_kv_params(params: Optional[list[str]]) -> dict:
    opts: dict = {}
    if not params:
        return opts
    for p in params:
        if '=' not in p:
            continue
        k, v = p.split('=', 1)
        k = k.strip()
        v = v.strip()
        # basic type coercion
        if v.lower() in {"true", "false"}:
            coerced = (v.lower() == "true")
        # Check for comma-separated list (e.g., "QQQ,AAPL,MSFT")
        elif ',' in v:
            # Split into list and coerce each element
            items = [item.strip() for item in v.split(',')]
            coerced_items = []
            for item in items:
                if item.lower() in {"true", "false"}:
                    coerced_items.append(item.lower() == "true")
                else:
                    try:
                        if '.' in item:
                            coerced_items.append(float(item))
                        else:
                            coerced_items.append(int(item))
                    except ValueError:
                        coerced_items.append(item)
            coerced = coerced_items
        else:
            try:
                if '.' in v:
                    coerced = float(v)
                else:
                    coerced = int(v)
            except ValueError:
                coerced = v
        opts[k] = coerced
    return opts


def cmd_recipes(args):
    """Handle recipes commands."""
    if args.recipes_cmd == 'list':
        recipes = wd.list_recipes()
        print(f"Available recipes ({len(recipes)}):")
        for recipe in recipes:
            print(f"  - {recipe}")

    elif args.recipes_cmd == 'run':
        try:
            # collect options
            options = _parse_kv_params(getattr(args, 'params', None))
            # convenience flags
            if getattr(args, 'limit', None) is not None:
                options['limit'] = args.limit
            if getattr(args, 'data_dir', None):
                options['data_dir'] = args.data_dir
            if getattr(args, 'data_root', None):
                options['data_root'] = args.data_root

            version = wd.run_recipe(
                args.recipe_name,
                args.dataset_id,
                with_materialize=getattr(args, 'materialize', False),
                work_dir=Path(args.work_dir).resolve() if getattr(args, 'work_dir', None) else None,
                **options,
            )
            print(f"✅ Recipe '{args.recipe_name}' completed")
            print(f"   Dataset: {args.dataset_id}")
            print(f"   Version: {version if isinstance(version, str) else version.get('main')}")

            # Optional upload
            if getattr(args, 'upload', False):
                backend = getattr(args, 'backend', 's3')
                bucket = getattr(args, 'bucket', None)
                if backend == 's3' and not bucket:
                    print("Error: --bucket is required for --upload with s3 backend", file=sys.stderr)
                    sys.exit(2)
                info = wd.backup_dataset(args.dataset_id, backend=backend, bucket=bucket, include_raw=True)
                print(f"\n☁️  Uploaded to {backend}://{bucket}")
                print(f"   Files: {info['total_files']}  Size: {info['total_size']/1e6:.1f} MB")
        except Exception as e:
            print(f"Error running recipe: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_provenance(args):
    """Show dataset provenance (raw data sources)."""
    try:
        sources = wd.get_raw_data_sources(args.dataset_id)

        if not sources:
            print(f"No raw data sources found for {args.dataset_id}")
            return

        print(f"Raw Data Sources for {args.dataset_id}:\n")
        total_size = 0

        for source in sources:
            size_mb = source['size'] / (1024 * 1024) if source['size'] else 0
            total_size += source['size'] if source['size'] else 0

            print(f"  📁 {source['source_type']}: {source['source_path']}")
            print(f"     Size: {size_mb:.2f} MB")
            if source.get('content_hash'):
                print(f"     Hash: {source['content_hash'][:16]}...")
            print()

        print(f"Total: {len(sources)} source(s), {total_size / (1024**3):.2f} GB")

    except Exception as e:
        print(f"Error getting provenance: {e}", file=sys.stderr)
        sys.exit(1)


def _registry_target_from_args(path: Optional[str], bucket: Optional[str]) -> str:
    """Resolve registry path/URL from CLI args."""
    default_key = "warpdata/registry.db"
    if path:
        return path
    if bucket:
        from warpdata.core.storage.bucket_utils import normalize_bucket_name
        bucket = normalize_bucket_name(bucket)
        return f"s3://{bucket}/{default_key}"
    raise ValueError("Provide --bucket or explicit path/URL for registry location")


def cmd_registry(args):
    """Export or import registry.db to/from a path or bucket."""
    try:
        if args.registry_cmd == 'export':
            destination = _registry_target_from_args(getattr(args, 'dest', None), getattr(args, 'bucket', None))
            result = wd.export_registry(destination, overwrite=getattr(args, 'overwrite', False))
            print(f"✅ Exported registry to {result}")
        elif args.registry_cmd == 'import':
            source = _registry_target_from_args(getattr(args, 'src', None), getattr(args, 'bucket', None))
            target = wd.import_registry(source, overwrite=getattr(args, 'overwrite', True))
            print(f"✅ Imported registry into {target}")
        else:
            print("Please specify 'export' or 'import' for registry command", file=sys.stderr)
            sys.exit(2)
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error handling registry: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_backup(args):
    """Backup dataset to cloud storage."""
    try:
        print(f"Backing up {args.dataset_id} to {args.backend}...")

        info = wd.backup_dataset(
            args.dataset_id,
            backend=args.backend,
            bucket=args.bucket,
            include_raw=not args.no_raw,
        )

        print(f"\n✓ Backup complete!")
        print(f"  Files uploaded: {info['total_files']}")
        print(f"  Total size: {info['total_size'] / (1024**2):.2f} MB")
        print(f"  Version: {info['version_hash'][:16]}...")

    except Exception as e:
        print(f"Error backing up dataset: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_sync(args):
    """Sync datasets to cloud storage (all, by workspace, by dataset, or from folder)."""
    try:
        from ..core.storage.bucket_utils import normalize_bucket_name

        # Parse max_size if provided (e.g., "10GB", "500MB", "1.5GB", "unlimited")
        max_raw_size_bytes = None
        if args.max_raw_size:
            size_str = args.max_raw_size.upper()
            if size_str == 'UNLIMITED':
                max_raw_size_bytes = None  # No limit
            else:
                try:
                    if size_str.endswith('GB'):
                        max_raw_size_bytes = int(float(size_str[:-2]) * 1024**3)
                    elif size_str.endswith('MB'):
                        max_raw_size_bytes = int(float(size_str[:-2]) * 1024**2)
                    elif size_str.endswith('KB'):
                        max_raw_size_bytes = int(float(size_str[:-2]) * 1024)
                    else:
                        max_raw_size_bytes = int(size_str)
                except ValueError:
                    print(f"Error: Invalid size format '{args.max_raw_size}'. Use format like '10GB', '500MB', 'unlimited', etc.", file=sys.stderr)
                    sys.exit(1)

        bucket = normalize_bucket_name(args.bucket)

        # Handle different sync modes
        if args.dataset:
            # Sync single dataset
            print(f"📤 Syncing dataset: {args.dataset}")
            print(f"  → s3://{bucket}/")
            result = wd.backup_dataset(
                args.dataset,
                backend=args.backend,
                bucket=bucket,
                include_raw=not args.no_raw,
            )
            print(f"\n✅ Sync complete!")
            print(f"  Files: {result['total_files']}")
            print(f"  Size: {result['total_size'] / 1e6:.1f} MB")

        elif args.workspaces:
            # Sync all datasets in specified workspaces
            ws_list = args.workspaces
            print(f"📤 Syncing workspaces: {', '.join(ws_list)}")
            print(f"  → s3://{bucket}/")

            datasets = []
            for ws in ws_list:
                datasets.extend(wd.list_datasets(workspace=ws))
            if not datasets:
                print(f"No datasets found in workspaces: {', '.join(ws_list)}")
                return

            print(f"  Found {len(datasets)} datasets across {len(ws_list)} workspace(s)")

            if args.dry_run:
                print("\n🔍 DRY RUN - Would sync:")
                for ds in datasets:
                    print(f"    • {ds['workspace']}/{ds['name']}")
                return

            from tqdm import tqdm

            # Sort datasets by size (lightest first)
            from warpdata.core.registry import get_registry_readonly
            from warpdata.core.cache import get_cache

            def get_dataset_size(ds):
                try:
                    reg = get_registry_readonly()
                    manifest = reg.get_manifest(ds['workspace'], ds['name'], ds['latest_version'])
                    if not manifest:
                        return 0
                    cache = get_cache()
                    total = 0
                    for res in manifest.get('resources', []):
                        uri = res if isinstance(res, str) else res.get('uri', '')
                        try:
                            local_path = cache.get(uri)
                            if local_path and local_path.exists():
                                total += local_path.stat().st_size
                        except:
                            pass
                    return total
                except:
                    return 0

            print("  Calculating dataset sizes...")
            datasets_with_size = [(ds, get_dataset_size(ds)) for ds in tqdm(datasets, desc="  Sizing", unit="dataset", leave=False)]
            datasets_with_size.sort(key=lambda x: x[1])
            datasets = [ds for ds, _ in datasets_with_size]
            print(f"  Sorted {len(datasets)} datasets by size (lightest first)")

            total_files = 0
            total_size = 0
            errors = 0

            pbar = tqdm(datasets, desc="Syncing", unit="dataset")
            for ds in pbar:
                dataset_id = f"warpdata://{ds['workspace']}/{ds['name']}"
                pbar.set_postfix_str(f"{ds['workspace']}/{ds['name']}")
                try:
                    result = wd.backup_dataset(
                        dataset_id,
                        backend=args.backend,
                        bucket=bucket,
                        include_raw=not args.no_raw,
                        progress=False,  # Disable inner progress bar
                    )
                    total_files += result['total_files']
                    total_size += result['total_size']
                except Exception as e:
                    tqdm.write(f"  ✗ {dataset_id}: {e}")
                    errors += 1

            print(f"\n✅ Workspace(s) sync complete!")
            print(f"  Datasets: {len(datasets) - errors}/{len(datasets)}")
            print(f"  Files: {total_files}")
            print(f"  Size: {total_size / 1e6:.1f} MB")

            if errors:
                sys.exit(1)

        elif args.folder:
            # Sync datasets from a folder
            print(f"📤 Syncing folder: {args.folder}")
            print(f"  → s3://{bucket}/")

            from pathlib import Path
            folder = Path(args.folder).resolve()

            if not folder.exists():
                print(f"Error: Folder not found: {folder}", file=sys.stderr)
                sys.exit(1)

            # Find all parquet files in folder
            parquet_files = list(folder.glob("**/*.parquet"))
            if not parquet_files:
                print(f"No parquet files found in {folder}")
                return

            print(f"  Found {len(parquet_files)} parquet files")

            if args.dry_run:
                print("\n🔍 DRY RUN - Would sync:")
                for f in parquet_files[:10]:
                    print(f"    • {f.relative_to(folder)}")
                if len(parquet_files) > 10:
                    print(f"    • ... and {len(parquet_files) - 10} more")
                return

            # TODO: Implement folder-based sync
            # For now, suggest using register + sync
            print("\n💡 To sync from a folder:")
            print("  1. Register datasets from the folder:")
            print(f"     warp register warpdata://workspace/name {folder}/*.parquet")
            print("  2. Then sync:")
            print(f"     warp sync --bucket {args.bucket}")

        else:
            # Sync all datasets (default)
            print(f"📤 Syncing all datasets → s3://{bucket}/")

            result = wd.sync_to_cloud(
                backend=args.backend,
                bucket=bucket,
                include_raw=not args.no_raw,
                dry_run=args.dry_run,
                max_raw_size=max_raw_size_bytes,
                force=(args.force or args.overwrite),
                verify=getattr(args, 'verify', False),
            )

            # Result already prints during execution
            # Just exit with appropriate code
            if result['errors']:
                sys.exit(1)

        # Upload registry if requested
        if getattr(args, 'upload_registry', False) and not args.dry_run:
            from ..api.storage import upload_registry_to_cloud
            print(f"\n📤 Uploading registry...")
            try:
                upload_registry_to_cloud(bucket=bucket, backend=args.backend)
            except Exception as e:
                print(f"  ⚠️  Failed to upload registry: {e}")

    except Exception as e:
        print(f"\nError syncing datasets: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_refresh(args):
    """Refresh dataset manifests by re-registering from actual file locations.

    This fixes stale manifests that point to non-existent paths by finding
    the actual data files and updating the registry.
    """
    from pathlib import Path
    from tqdm import tqdm
    from warpdata.core.registry import get_registry
    from warpdata.core.cache import get_cache
    import warpdata as wd

    cache = get_cache()
    datasets_dir = cache.datasets_dir

    # Get datasets to refresh (use write mode since we'll be modifying)
    reg = get_registry()
    if args.workspace:
        datasets = reg.list_datasets(args.workspace)
        print(f"🔄 Refreshing datasets in workspace: {args.workspace}")
    else:
        datasets = reg.list_datasets()
        print(f"🔄 Refreshing all datasets")

    if not datasets:
        print("  No datasets found")
        return

    print(f"  Found {len(datasets)} datasets in registry")

    refreshed = 0
    skipped = 0
    errors = []

    for ds in tqdm(datasets, desc="Refreshing", unit="dataset"):
        workspace = ds['workspace']
        name = ds['name']
        dataset_id = f"warpdata://{workspace}/{name}"

        # Find actual data file in cache
        dataset_cache_dir = datasets_dir / workspace / name

        if not dataset_cache_dir.exists():
            if args.verbose:
                tqdm.write(f"  ⚠️  {dataset_id}: cache dir not found")
            errors.append((dataset_id, "cache directory not found"))
            continue

        # Look for data.duckdb or parquet files in version subdirs
        data_file = None
        for version_dir in dataset_cache_dir.iterdir():
            if not version_dir.is_dir():
                continue

            # Prefer data.duckdb
            duckdb_file = version_dir / "data.duckdb"
            if duckdb_file.exists():
                data_file = duckdb_file
                break

            # Fall back to parquet files
            parquet_files = list(version_dir.glob("*.parquet"))
            if parquet_files:
                data_file = parquet_files[0]
                break

        if not data_file:
            if args.verbose:
                tqdm.write(f"  ⚠️  {dataset_id}: no data file found")
            errors.append((dataset_id, "no data file found"))
            continue

        # Check if manifest already points to correct location
        manifest = reg.get_manifest(workspace, name, ds['latest_version'])
        if manifest and 'resources' in manifest:
            resources = manifest['resources']
            if resources:
                first_resource = resources[0]
                resource_path = first_resource if isinstance(first_resource, str) else first_resource.get('uri', '')
                if Path(resource_path).exists():
                    if args.verbose:
                        tqdm.write(f"  ✓ {dataset_id}: already valid")
                    skipped += 1
                    continue

        if args.dry_run:
            tqdm.write(f"  Would refresh: {dataset_id} → {data_file}")
            refreshed += 1
            continue

        # Re-register with correct path using registry directly (no ingest needed for duckdb)
        try:
            version_hash = data_file.parent.name
            reg.register_dataset(
                workspace=workspace,
                name=name,
                version_hash=version_hash,
                manifest={
                    "resources": [str(data_file)],
                    "format": "duckdb",
                },
                storage_path=str(data_file),
            )
            if args.verbose:
                tqdm.write(f"  ✓ {dataset_id}: refreshed from {data_file.name}")
            refreshed += 1
        except Exception as e:
            tqdm.write(f"  ✗ {dataset_id}: {e}")
            errors.append((dataset_id, str(e)))

    print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}✅ Refresh complete!")
    print(f"  Refreshed: {refreshed}")
    print(f"  Skipped (already valid): {skipped}")
    print(f"  Errors: {len(errors)}")

    if errors and args.verbose:
        print("\n  Errors:")
        for ds_id, err in errors:
            print(f"    • {ds_id}: {err}")


def cmd_restore(args):
    """Restore dataset from cloud storage."""
    try:
        print(f"Restoring {args.dataset_id} from {args.backend}...")

        info = wd.restore_dataset(
            args.dataset_id,
            backend=args.backend,
            bucket=args.bucket,
            include_raw=not args.no_raw,
            output_dir=args.output_dir,
        )

        print(f"\n✓ Restore complete!")
        print(f"  Files downloaded: {info['total_files']}")
        print(f"  Total size: {info['total_size'] / (1024**2):.2f} MB")
        print(f"  Output directory: {info['output_dir']}")

    except Exception as e:
        print(f"Error restoring dataset: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args):
    """Pull (download) datasets from cloud storage."""
    try:
        from ..core.storage.bucket_utils import normalize_bucket_name
        bucket = normalize_bucket_name(args.bucket)

        # Download registry first if requested
        if getattr(args, 'with_registry', False):
            from ..api.storage import download_registry_from_cloud
            print(f"📥 Downloading registry from s3://{bucket}...")
            try:
                download_registry_from_cloud(bucket=bucket, backend=args.backend)
            except FileNotFoundError as e:
                print(f"  ⚠️  {e}")
            except Exception as e:
                print(f"  ⚠️  Failed to download registry: {e}")

        # Helper to parse size strings (e.g., "100MB", "1GB")
        def parse_size(size_str: str) -> int:
            if not size_str:
                return None
            size_str = size_str.upper()
            if size_str == 'UNLIMITED':
                return None
            try:
                if size_str.endswith('GB'):
                    return int(float(size_str[:-2]) * 1024**3)
                elif size_str.endswith('MB'):
                    return int(float(size_str[:-2]) * 1024**2)
                elif size_str.endswith('KB'):
                    return int(float(size_str[:-2]) * 1024)
                else:
                    return int(size_str)
            except ValueError:
                raise ValueError(f"Invalid size format '{size_str}'")

        # Parse max_size if provided
        max_raw_size_bytes = None
        if hasattr(args, 'max_raw_size') and args.max_raw_size:
            try:
                max_raw_size_bytes = parse_size(args.max_raw_size)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        # Parse max_bytes if provided
        max_bytes = None
        if hasattr(args, 'max_bytes') and args.max_bytes:
            try:
                max_bytes = parse_size(args.max_bytes)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        # Get other new args
        mode = getattr(args, 'mode', 'full')
        max_files = getattr(args, 'max_files', None)

        # List datasets if requested
        if args.list:
            print(f"📋 Listing datasets in s3://{bucket}...")
            datasets = wd.list_remote_datasets(backend=args.backend, bucket=bucket)

            if not datasets:
                print("  No datasets found")
                return

            print(f"\n  Found {len(datasets)} datasets:")
            for ds in datasets:
                print(f"    {ds['dataset']:40s} v:{ds['version'][:8]} {ds['size'] / 1e6:>8.1f} MB")
            return

        # Pull specific dataset or all datasets
        include_raw = not getattr(args, 'no_raw', False)

        if args.dataset_id:
            workers = getattr(args, 'workers', 1)
            mode_suffix = f" (mode={mode})" if mode != 'full' else ""
            workers_suffix = f" [{workers} workers]" if workers > 1 else ""
            print(f"📥 Pulling {args.dataset_id} from s3://{bucket}...{mode_suffix}{workers_suffix}")
            result = wd.pull_dataset(
                dataset_id=args.dataset_id,
                backend=args.backend,
                bucket=bucket,
                dry_run=args.dry_run,
                include_raw=include_raw,
                max_raw_size=max_raw_size_bytes,
                mode=mode,
                max_bytes=max_bytes,
                max_files=max_files,
                workers=workers,
            )
        else:
            workers = getattr(args, 'workers', 1)
            print(f"📥 Pulling all datasets from s3://{bucket}..." + (f" (parallel={workers})" if workers > 1 else ""))
            result = wd.pull_all_datasets(
                backend=args.backend,
                bucket=bucket,
                dry_run=args.dry_run,
                include_raw=include_raw,
                max_raw_size=max_raw_size_bytes,
                workers=workers,
            )

        if args.dry_run:
            print(f"\n🔍 DRY RUN - Would download:")
            if 'total_datasets' in result:
                print(f"  Datasets: {result['total_datasets']}")
            print(f"  Files:    {result.get('total_files', 0)}")
            print(f"  Size:     {result.get('total_size', 0) / 1e9:.2f} GB")
        else:
            print(f"\n✅ Pull complete!")
            print(f"  Downloaded: {result.get('total_files', 0)} files")
            print(f"  Total size: {result.get('total_size', 0) / 1e9:.2f} GB")

    except Exception as e:
        print(f"Error pulling datasets: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_manifest(args):
    """Manage cloud manifests."""
    from warpdata.api.storage import generate_manifests_for_bucket

    if args.manifest_cmd == 'generate':
        try:
            result = generate_manifests_for_bucket(
                bucket=args.bucket,
                backend=args.backend,
                workers=args.workers,
                dry_run=args.dry_run,
                progress=True,
            )

            if args.dry_run:
                print(f"\n[DRY RUN] Would create {result.get('would_create', 0)} manifests")
            else:
                print(f"\nCreated {result.get('manifests_created', 0)} manifests")

        except Exception as e:
            print(f"Error generating manifests: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("Usage: warp manifest generate --bucket <bucket>", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    """Create a new recipe template."""
    from pathlib import Path

    recipe_name = args.name
    output_path = Path(f"{recipe_name}.py")

    if output_path.exists() and not args.force:
        print(f"Error: {output_path} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    # Generate recipe template
    template = f'''"""
{recipe_name.replace('_', ' ').title()} dataset recipe.

Source: TODO: Add source URL or description
License: TODO: Add license information

Examples:
    import warpdata as wd

    # Create the dataset
    wd.run_recipe('{recipe_name}', 'warpdata://workspace/{recipe_name}')

    # Load the dataset
    df = wd.load('warpdata://workspace/{recipe_name}', as_format='pandas')
"""
from pathlib import Path
from typing import Optional

from ..api.recipes import RecipeContext
from ..recipes.base import RecipeOutput, SubDataset
from ..core.utils import safe_filename


def {recipe_name}(ctx: RecipeContext, **options) -> RecipeOutput:
    """
    Process {recipe_name.replace('_', ' ')} dataset.

    Args:
        ctx: Recipe context with download, storage, and DuckDB engine
        **options: Additional options
            - limit: Optional[int] - Limit number of records
            - custom_param: Any - Example custom parameter

    Returns:
        RecipeOutput with main dataset and optional subdatasets
    """
    # Extract options
    limit = options.get('limit', None)

    # TODO: Download or load raw data
    # Example: Download from URL
    # raw_file = ctx.download(
    #     url='https://example.com/data.csv',
    #     filename='raw_data.csv'
    # )

    # TODO: Load and process data with DuckDB
    # Example: Load CSV and transform
    # df = ctx.engine.conn.execute(f"""
    #     SELECT *
    #     FROM read_csv('{{raw_file}}')
    #     {{f'LIMIT {{limit}}' if limit else ''}}
    # """).df()

    # TODO: Process your data here
    # Example transformation:
    # processed = df.copy()
    # processed['new_column'] = processed['old_column'].apply(lambda x: x.upper())

    # TODO: Write main dataset
    # main_path = ctx.write_parquet(processed, 'main.parquet')

    # TODO: Optional - Create subdatasets (only if different schema!)
    # subdatasets = {{}}
    # if create_subdataset:
    #     subdataset_df = process_subdataset(df)
    #     subdataset_path = ctx.write_parquet(subdataset_df, 'subdataset.parquet')
    #     subdatasets['{recipe_name}-subdataset'] = SubDataset(
    #         name='{recipe_name}-subdataset',
    #         files=[subdataset_path],
    #         description='Description of subdataset with different schema'
    #     )

    # TODO: Generate documentation
    # readme = f"""
    # # {{recipe_name.replace('_', ' ').title()}} Dataset
    #
    # ## Description
    # TODO: Add dataset description
    #
    # ## Schema
    # TODO: Document columns and types
    #
    # ## Statistics
    # - Total rows: {{len(processed):,}}
    # - Columns: {{len(processed.columns)}}
    #
    # ## Usage
    # ```python
    # import warpdata as wd
    # df = wd.load('warpdata://workspace/{recipe_name}', as_format='pandas')
    # ```
    # """
    # ctx.write_documentation(readme.strip())

    # TODO: Return output (uncomment and modify)
    # return RecipeOutput(
    #     main=[main_path],
    #     subdatasets=subdatasets,
    #     metadata={{
    #         'source': 'TODO: Add source',
    #         'license': 'TODO: Add license',
    #         'num_rows': len(processed),
    #         'num_columns': len(processed.columns),
    #     }}
    # )

    raise NotImplementedError("TODO: Implement recipe logic above")
'''

    # Write template to file
    output_path.write_text(template)

    print(f"✅ Created recipe template: {output_path}")
    print(f"\n📝 Next steps:")
    print(f"   1. Edit {output_path} and implement the TODO sections")
    print(f"   2. Add your recipe to warpdata/recipes/__init__.py:")
    print(f"      - Import: from .{recipe_name} import {recipe_name}")
    print(f"      - Register: register_recipe('{recipe_name}', {recipe_name})")
    print(f"   3. Test your recipe:")
    print(f"      python -c \"import warpdata as wd; wd.run_recipe('{recipe_name}', 'warpdata://workspace/{recipe_name}')\"")


def cmd_scaffold_py(args):
    """Generate a smart Python loader for a dataset."""
    dataset_id = args.dataset_id
    filename = getattr(args, 'filename', None) or getattr(args, 'output', None)

    # File extension -> loader mapping
    LOADERS = {
        '.tif': ('tifffile', 'tifffile.imread(path)'),
        '.tiff': ('tifffile', 'tifffile.imread(path)'),
        '.png': ('PIL.Image', 'Image.open(path)'),
        '.jpg': ('PIL.Image', 'Image.open(path)'),
        '.jpeg': ('PIL.Image', 'Image.open(path)'),
        '.webp': ('PIL.Image', 'Image.open(path)'),
        '.gif': ('PIL.Image', 'Image.open(path)'),
        '.npy': ('numpy', 'np.load(path)'),
        '.npz': ('numpy', 'np.load(path)'),
        '.wav': ('librosa', 'librosa.load(path)'),
        '.mp3': ('librosa', 'librosa.load(path)'),
        '.flac': ('librosa', 'librosa.load(path)'),
        '.json': ('json', 'json.load(open(path))'),
        '.parquet': ('pandas', 'pd.read_parquet(path)'),
        '.csv': ('pandas', 'pd.read_csv(path)'),
        '.pt': ('torch', 'torch.load(path)'),
        '.pth': ('torch', 'torch.load(path)'),
    }

    try:
        info = wd.dataset_info(dataset_id)
        schema = wd.schema(dataset_id)
    except Exception as e:
        print(f"Error: failed to inspect dataset {dataset_id}: {e}", file=sys.stderr)
        sys.exit(1)

    # Gather additional info
    row_count = None
    embeddings = []
    is_image = False
    path_column = None
    file_ext = None
    metadata = info.get('manifest', {}).get('metadata', {})

    try:
        rel = wd.load(dataset_id)
        row_count = rel.count("*").fetchone()[0]
    except Exception:
        pass

    try:
        embeddings = wd.list_embeddings(dataset_id) or []
    except Exception:
        pass

    try:
        is_image = wd.is_image_dataset(dataset_id)
    except Exception:
        pass

    # Detect path columns
    path_keywords = ['path', 'file', 'uri', 'url']
    path_columns = [c for c in (schema or {}) if any(p in c.lower() for p in path_keywords)]
    if path_columns:
        path_column = path_columns[0]
        try:
            sample = wd.load(dataset_id).limit(1).df()
            if not sample.empty and path_column in sample.columns:
                sample_path = str(sample[path_column].iloc[0])
                file_ext = Path(sample_path).suffix.lower()
        except Exception:
            pass

    # Build output filename
    workspace = info.get("workspace", "")
    name = info.get("name", "")
    if workspace and name:
        base = f"{workspace}_{name}"
    else:
        base = dataset_id.replace("://", "_").replace("/", "_")
    safe_base = safe_filename(base)

    if not filename:
        filename = f"{safe_base}_loader.py"

    out_path = Path.cwd() / filename
    if out_path.exists() and not args.force:
        print(f"Error: {out_path} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    # Build template sections
    schema_compact = ", ".join(f"{col} ({dtype})" for col, dtype in (schema or {}).items())
    row_str = f"{row_count:,}" if row_count else "unknown"

    # Header
    header = f'''"""
Dataset: {dataset_id}
Rows: {row_str}
Schema: {schema_compact or "(unavailable)"}
"""
import warpdata as wd
'''

    # Base loading
    base_code = f'''
# Load dataset
ds = wd.load("{dataset_id}")

# Preview
print(ds.limit(5).df())
'''

    # Conditional sections
    extra_sections = []

    # Embedded images
    if is_image:
        extra_sections.append(f'''
# --- Embedded Images ---
# This dataset has embedded images (BLOB columns)
df = wd.load_images("{dataset_id}", limit=10)
# Images are now PIL.Image objects in the image column
''')

    # Embeddings / semantic search
    if embeddings:
        space_name = embeddings[0].get('space_name', 'default')
        extra_sections.append(f'''
# --- Semantic Search ---
# Embedding space: {space_name}
results = wd.search("{dataset_id}", "your query here", space="{space_name}", k=10)
print(results)
''')

    # External file paths
    if path_column and file_ext:
        loader_info = LOADERS.get(file_ext)
        if loader_info:
            module, call = loader_info
            # Handle PIL special case
            if module == 'PIL.Image':
                import_line = "from PIL import Image"
                call = call.replace('Image.open', 'Image.open')
            else:
                import_line = f"import {module.split('.')[0]}"

            extra_sections.append(f'''
# --- External Files ({file_ext} format) ---
{import_line}  # pip install {module.split('.')[0]}

def load_file(path):
    """Load external file."""
    return {call}

# Example: load first file
row = ds.limit(1).df().iloc[0]
data = load_file(row['{path_column}'])
print(f"Loaded: {{row['{path_column}']}}")
''')
        else:
            extra_sections.append(f'''
# --- External Files ---
# Path column: {path_column}
# File extension: {file_ext or "unknown"}
row = ds.limit(1).df().iloc[0]
file_path = row['{path_column}']
# Load with appropriate library based on file type
''')

    # Filter example for datasets with common columns
    if schema:
        if 'symbol' in schema:
            extra_sections.append('''
# --- Filter Example ---
# btc = ds.filter("symbol = 'BTCUSDT'").df()
''')
        elif 'split' in schema:
            extra_sections.append('''
# --- Filter by Split ---
# train = ds.filter("split = 'train'").df()
# test = ds.filter("split = 'test'").df()
''')

    # Main block
    main_block = '''
if __name__ == "__main__":
    # Run preview
    print(ds.limit(5).df())
'''

    # Combine template
    template = header + base_code + "".join(extra_sections) + main_block

    out_path.write_text(template)
    print(f"✅ Created loader: {out_path}")
    print(f"   Dataset: {dataset_id}")
    if row_count:
        print(f"   Rows: {row_count:,}")
    if is_image:
        print(f"   Type: Image dataset (embedded)")
    if path_column:
        print(f"   External files: {path_column} ({file_ext or 'unknown'})")
    if embeddings:
        print(f"   Embeddings: {len(embeddings)} space(s)")


def main():
    """Main CLI entry point."""
    # Use invoked script name for PROG to support both 'warp' and 'warpdata' entry points
    invoked = Path(sys.argv[0]).name if sys.argv and len(sys.argv) > 0 else 'warp'
    parser = argparse.ArgumentParser(
        prog=invoked,
        description='''warpdata - Fast data loading for ML/AI

Quick Python usage:
  import warpdata as wd

  # Standard loading (DuckDB relation - lazy, memory-efficient)
  rel = wd.load("crypto/coingecko/hourly")
  df = rel.limit(1000).df()  # Slice first, then convert to pandas

  # Zero-copy streaming (huge datasets, 100GB+)
  for batch in wd.stream("text/wikipedia-main", batch_size=50000):
      process(batch)  # PyArrow RecordBatch

  # Multi-worker training (file-level sharding)
  from src.data.warp_loader import create_loader
  loader = create_loader(
      "text/fineweb2-mix",
      batch_size=2048,
      num_workers=8,  # Each worker reads different files
      use_arrow_streaming=True  # Zero-copy Arrow (default)
  )''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXTENDED_HELP
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Load command
    load_parser = subparsers.add_parser('load', help='Load and display dataset')
    load_parser.add_argument('source', help='Data source (file, URL, dataset ID)')
    load_parser.add_argument('--limit', type=int, help='Limit number of rows (default: 100 for safety)')
    load_parser.add_argument('--head', type=int, default=5, help='Number of rows to display')
    load_parser.add_argument('--include-rid', action='store_true', help='Include row ID (rid) column for embeddings workflows')
    load_parser.set_defaults(func=cmd_load)

    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Show dataset schema')
    schema_parser.add_argument('source', help='Data source')
    schema_parser.set_defaults(func=cmd_schema)

    # List command
    list_parser = subparsers.add_parser('list', help='List datasets')
    list_parser.add_argument('--workspace', help='Filter by workspace')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show full version hashes')
    list_parser.add_argument('--remote', action='store_true', help='List remote datasets instead of local')
    list_parser.add_argument('--backend', default='s3', help='Remote backend (default: s3)')
    list_parser.add_argument('--bucket', help='Remote bucket name (required for --remote)')
    list_parser.set_defaults(func=cmd_list)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show dataset information')
    info_parser.add_argument('dataset_id', help='Dataset ID (e.g., warpdata://workspace/name)')
    info_parser.set_defaults(func=cmd_info)

    # Detect frames command
    df_parser = subparsers.add_parser('detect-frames', help='Detect likely frames column')
    df_parser.add_argument('dataset_id', help='Dataset ID (e.g., warpdata://workspace/name)')
    df_parser.add_argument('--table', help='Optional logical table (e.g., signals)')
    df_parser.set_defaults(func=cmd_detect_frames)

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a dataset')
    register_parser.add_argument('dataset_id', help='Dataset ID')
    register_parser.add_argument('resources', nargs='+', help='Resource files or patterns')
    register_parser.add_argument('--metadata', help='Metadata JSON string')
    register_parser.set_defaults(func=cmd_register)

    # Materialize command
    materialize_parser = subparsers.add_parser('materialize', help='Materialize dataset with row IDs')
    materialize_parser.add_argument('dataset_id', help='Dataset ID')
    materialize_parser.add_argument('--force', action='store_true', help='Force re-materialization')
    materialize_parser.add_argument('--update-registry', action='store_true', help='Re-register dataset to point to materialized file (default: false)')
    materialize_parser.set_defaults(func=cmd_materialize)

    # Embeddings command
    embeddings_parser = subparsers.add_parser('embeddings', help='Manage embeddings')
    embeddings_subparsers = embeddings_parser.add_subparsers(dest='embeddings_cmd', help='Embeddings command')

    emb_add = embeddings_subparsers.add_parser('add', help='Add embedding space')
    emb_add.add_argument('dataset_id', help='Dataset ID')
    emb_add.add_argument('--space', required=True, help='Embedding space name')
    emb_add.add_argument('--provider', default='sentence-transformers', help='Provider (numpy|sentence-transformers|openai|clip|clip-text)')
    emb_add.add_argument('--model', help='Model name (defaults depend on provider)')
    emb_add.add_argument('--device', help='Device hint for provider (e.g., cpu, cuda, cuda:0)')
    emb_add.add_argument('--column', required=True, help='Column to embed')
    emb_add.add_argument('--batch-size', type=int, help='Batch size for embedding computation (default: 100)')
    emb_add.add_argument('--max-rows', type=int, help='Maximum rows to embed (subset). Useful for very large datasets (e.g., 800000).')
    emb_add.add_argument('--rows-per-chunk', type=int, help='Rows to embed per micro-chunk when streaming (controls memory). Default: 5000')
    emb_add.add_argument('--write-rows-per-group', type=int, help='Accumulate this many rows before writing to Parquet (reduces I/O overhead). Default: 4096')

    # Smart alias: infers column/provider when omitted
    emb_run = embeddings_subparsers.add_parser('run', help='Add embeddings (smart defaults)')
    emb_run.add_argument('dataset_id', help='Dataset ID (e.g., vision/celeba-attrs)')
    emb_run.add_argument('--space', default='default', help='Embedding space name (default: default)')
    emb_run.add_argument('--provider', help='Provider; auto if omitted (clip for images, sentence-transformers for text)')
    emb_run.add_argument('--model', help='Model name (defaults depend on provider)')
    emb_run.add_argument('--device', help='Device hint for provider (e.g., cpu, cuda, cuda:0)')
    emb_run.add_argument('--column', help='Column to embed (auto-detect if omitted)')
    emb_run.add_argument('--batch-size', type=int, help='Batch size for embedding computation (default: 100)')
    emb_run.add_argument('--max-rows', type=int, help='Maximum rows to embed (subset). Useful for very large datasets (e.g., 800000).')
    emb_run.add_argument('--rows-per-chunk', type=int, help='Rows to embed per micro-chunk when streaming (controls memory). Default: 5000')
    emb_run.add_argument('--write-rows-per-group', type=int, help='Accumulate this many rows before writing to Parquet (reduces I/O overhead). Default: 4096')

    emb_search = embeddings_subparsers.add_parser('search', help='Search embeddings')
    emb_search.add_argument('dataset_id', help='Dataset ID')
    emb_search.add_argument('--space', required=True, help='Embedding space name')
    emb_search.add_argument('--query', required=True, help='Search query')
    emb_search.add_argument('--top-k', type=int, default=10, help='Number of results')

    emb_list = embeddings_subparsers.add_parser('list', help='List embedding spaces')
    emb_list.add_argument('dataset_id', help='Dataset ID')
    emb_list.add_argument('--all', action='store_true', help='List across all versions')

    emb_remove = embeddings_subparsers.add_parser('remove', help='Remove an embedding space')
    emb_remove.add_argument('dataset_id', help='Dataset ID')
    emb_remove.add_argument('--space', required=True, help='Embedding space name')
    emb_remove.add_argument('--delete-files', action='store_true', help='Delete embedding files on disk')

    emb_migrate = embeddings_subparsers.add_parser('migrate', help='Migrate all spaces to latest version')
    emb_migrate.add_argument('dataset_id', help='Dataset ID')
    emb_migrate.add_argument('--move', action='store_true', help='Move files into latest version dir')
    emb_migrate.add_argument('--copy', action='store_true', help='Copy files into latest version dir')

    embeddings_parser.set_defaults(func=cmd_embeddings)

    # Module command
    module_parser = subparsers.add_parser('module', help='Resolve and use dataset modules (providers)')
    module_subparsers = module_parser.add_subparsers(dest='module_cmd', help='Module command')

    mod_schema = module_subparsers.add_parser('schema', help='Show module schema')
    mod_schema.add_argument('--id', required=True, help='Module id (e.g., warp.dataset.gsm8k)')
    mod_schema.add_argument('--json', action='store_true', help='Output JSON')

    mod_fetch = module_subparsers.add_parser('fetch', help='Fetch (materialize) module data to local cache')
    mod_fetch.add_argument('--id', required=True, help='Module id (e.g., warp.dataset.gsm8k)')
    mod_fetch.add_argument('--split', default='', help='Optional split key for cache layout')
    mod_fetch.add_argument('--cache-dir', help='Cache root (defaults to CWD)')
    mod_fetch.add_argument('--force', action='store_true', help='Force re-materialization')

    module_parser.set_defaults(func=cmd_module)

    # Recipes command
    recipes_parser = subparsers.add_parser('recipes', help='Work with recipes')
    recipes_subparsers = recipes_parser.add_subparsers(dest='recipes_cmd', help='Recipes command')

    recipes_subparsers.add_parser('list', help='List available recipes')

    rec_run = recipes_subparsers.add_parser('run', help='Run a recipe')
    rec_run.add_argument('recipe_name', help='Recipe name')
    rec_run.add_argument('dataset_id', help='Output dataset ID (e.g., warpdata://arc/arcagi)')
    rec_run.add_argument('--work-dir', help='Working directory for recipe outputs')
    rec_run.add_argument('--materialize', action='store_true', help='Materialize after registering')
    rec_run.add_argument('--limit', type=int, help='Recipe-specific limit (e.g., number of tasks)')
    rec_run.add_argument('--data-dir', help='Path to raw data directory (e.g., .../ARCAGI/data)')
    rec_run.add_argument('--data-root', help='Path to raw repo root (parent of data/)')
    rec_run.add_argument('-p', '--param', dest='params', action='append', help='Additional key=value recipe params (repeatable)')
    rec_run.add_argument('--upload', action='store_true', help='Upload resulting dataset to cloud storage')
    rec_run.add_argument('--backend', default='s3', help='Storage backend for upload (default: s3)')
    rec_run.add_argument('--bucket', help='Bucket name for upload')

    recipes_parser.set_defaults(func=cmd_recipes)

    # Provenance command
    prov_parser = subparsers.add_parser('provenance', help='Show dataset provenance (raw data sources)')
    prov_parser.add_argument('dataset_id', help='Dataset ID')
    prov_parser.set_defaults(func=cmd_provenance)

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup dataset to cloud storage')
    backup_parser.add_argument('dataset_id', help='Dataset ID')
    backup_parser.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    backup_parser.add_argument('--bucket', help='S3 bucket name (required for s3)')
    backup_parser.add_argument('--no-raw', action='store_true', help='Skip raw data sources')
    backup_parser.set_defaults(func=cmd_backup)

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore dataset from cloud storage')
    restore_parser.add_argument('dataset_id', help='Dataset ID')
    restore_parser.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    restore_parser.add_argument('--bucket', help='S3 bucket name (required for s3)')
    restore_parser.add_argument('--no-raw', action='store_true', help='Skip raw data sources')
    restore_parser.add_argument('--output-dir', help='Output directory (default: cache)')
    restore_parser.set_defaults(func=cmd_restore)

    # Registry command
    registry_parser = subparsers.add_parser('registry', help='Export/import registry.db')
    registry_subparsers = registry_parser.add_subparsers(dest='registry_cmd', help='Registry command')

    reg_export = registry_subparsers.add_parser('export', help='Export local registry.db to a path or bucket')
    reg_export.add_argument('--bucket', help='S3 bucket name (warpbucket- prefix added automatically)')
    reg_export.add_argument('--dest', help='Destination path or URL (e.g., s3://bucket/warpdata/registry.db)')
    reg_export.add_argument('--overwrite', action='store_true', help='Overwrite destination if it exists')
    reg_export.set_defaults(func=cmd_registry)

    reg_import = registry_subparsers.add_parser('import', help='Import registry.db from a path or bucket')
    reg_import.add_argument('--bucket', help='S3 bucket name (warpbucket- prefix added automatically)')
    reg_import.add_argument('--src', help='Source path or URL (e.g., s3://bucket/warpdata/registry.db)')
    reg_import.add_argument('--no-overwrite', dest='overwrite', action='store_false', help='Do not overwrite local registry if it exists (default: overwrite)')
    reg_import.set_defaults(func=cmd_registry, overwrite=True)

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync datasets to cloud storage')
    sync_parser.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    sync_parser.add_argument('--bucket', required=True, help='S3 bucket name (warpbucket- prefix added automatically)')
    sync_parser.add_argument('--workspace', action='append', dest='workspaces', metavar='WORKSPACE',
                             help='Sync only datasets in this workspace. Can be specified multiple times (e.g., --workspace crypto --workspace equities)')
    sync_parser.add_argument('--dataset', help='Sync only this dataset (e.g., warpdata://nlp/reviews)')
    sync_parser.add_argument('--folder', help='Sync datasets from this folder/directory')
    sync_parser.add_argument('--no-raw', action='store_true', help='Skip raw data sources entirely')
    sync_parser.add_argument('--max-raw-size', type=str, default='20GB', help='Max size for raw data per dataset (default: 20GB). Use "unlimited" for no limit. Examples: "200GB", "500MB"')
    sync_parser.add_argument('--dry-run', action='store_true', help='Show what would be synced without uploading')
    sync_parser.add_argument('--force', action='store_true', help='Re-upload all files even if already present')
    sync_parser.add_argument('--overwrite', action='store_true', help='Alias for --force (re-upload all files)')
    sync_parser.add_argument('--verify', action='store_true', help='Verify files exist in storage after upload')
    sync_parser.add_argument('--upload-registry', action='store_true', help='Also upload the local registry.duckdb for cross-machine sharing')
    sync_parser.set_defaults(func=cmd_sync)

    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh dataset manifests from actual file locations')
    refresh_parser.add_argument('--workspace', help='Only refresh datasets in this workspace')
    refresh_parser.add_argument('--dry-run', action='store_true', help='Show what would be refreshed without making changes')
    refresh_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed progress')
    refresh_parser.set_defaults(func=cmd_refresh)

    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Download datasets from cloud storage')
    pull_parser.add_argument('dataset_id', nargs='?', help='Dataset ID to pull (optional, pulls all if omitted)')
    pull_parser.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    pull_parser.add_argument('--bucket', required=True, help='S3 bucket name (warpbucket- prefix added automatically)')
    pull_parser.add_argument('--list', action='store_true', help='List available datasets in bucket')
    pull_parser.add_argument('--no-raw', action='store_true', help='Skip downloading raw data sources')
    pull_parser.add_argument('--max-raw-size', type=str, default='20GB', help='Max size for raw data per dataset (default: 20GB). Use "unlimited" for no limit')
    pull_parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')
    pull_parser.add_argument('--workers', '-j', type=int, default=1, help='Number of parallel download workers (default: 1)')
    pull_parser.add_argument('--mode', choices=['full', 'register-only', 'metadata'], default='full',
                            help='Pull mode: full (download all), register-only (register without download), metadata (schema only)')
    pull_parser.add_argument('--max-bytes', type=str, help='Maximum bytes to download (e.g., 100MB, 1GB)')
    pull_parser.add_argument('--max-files', type=int, help='Maximum number of files to download')
    pull_parser.add_argument('--with-registry', action='store_true', help='Download registry.duckdb from cloud before pulling')
    pull_parser.set_defaults(func=cmd_pull)

    # Manifest command
    manifest_parser = subparsers.add_parser('manifest', help='Manage cloud manifests')
    manifest_sub = manifest_parser.add_subparsers(dest='manifest_cmd', help='Manifest command')

    manifest_generate = manifest_sub.add_parser('generate', help='Generate manifests for legacy bucket (migration)')
    manifest_generate.add_argument('--bucket', required=True, help='S3 bucket to migrate')
    manifest_generate.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    manifest_generate.add_argument('--workers', '-j', type=int, default=32, help='Parallel workers for scanning')
    manifest_generate.add_argument('--dry-run', action='store_true', help='Show what would be generated')

    manifest_parser.set_defaults(func=cmd_manifest)

    # Cache command
    cache_parser = subparsers.add_parser('cache', help='Manage local cache')
    cache_sub = cache_parser.add_subparsers(dest='cache_cmd', help='Cache command')

    cache_stats = cache_sub.add_parser('stats', help='Show cache statistics and disk usage')
    cache_stats.add_argument('--workspace', help='Filter to a specific workspace')
    cache_stats.add_argument('--verbose', '-v', action='store_true', help='Show detailed per-dataset breakdown')

    cache_prune = cache_sub.add_parser('prune', help='Prune cached dataset versions')
    cache_prune.add_argument('--dataset-id', help='Dataset ID (e.g., warpdata://workspace/name or workspace/name)')
    cache_prune.add_argument('--workspace', help='Filter to a specific workspace')
    cache_prune.add_argument('--keep', type=int, default=1, help='Number of newest versions to keep (default: 1)')
    cache_prune.add_argument('--dry-run', action='store_true', help='Show what would be removed without deleting')

    cache_clean = cache_sub.add_parser('clean', help='Clean up cache (remove duplicated/unnecessary data)')
    cache_clean.add_argument('--recipes', action='store_true', help='Remove recipe folders (duplicated after materialization)')
    cache_clean.add_argument('--dry-run', action='store_true', help='Show what would be removed without deleting')
    cache_clean.add_argument('--workspace', help='Filter to a specific workspace')
    cache_parser.set_defaults(func=cmd_cache)

    # Register remote dataset command (create local registry entry from cloud)
    reg_remote = subparsers.add_parser('register-remote', help='Register dataset manifest from remote storage')
    reg_remote.add_argument('dataset_id', help='Dataset ID (e.g., warpdata://arc/arcagi)')
    reg_remote.add_argument('--backend', default='s3', help='Storage backend (default: s3)')
    reg_remote.add_argument('--bucket', required=True, help='S3 bucket name (warpbucket- prefix added automatically)')
    reg_remote.add_argument('--version', help='Version hash to register (defaults to latest found)')
    def cmd_register_remote(args):
        try:
            from ..api.storage import register_remote_dataset
            version = register_remote_dataset(args.dataset_id, backend=args.backend, bucket=args.bucket, version=args.version)
            print(f"✅ Registered {args.dataset_id} from {args.backend}://{args.bucket}")
            print(f"   Version: {version[:16]}...")
        except Exception as e:
            print(f"Error registering remote dataset: {e}", file=sys.stderr)
            sys.exit(1)
    reg_remote.set_defaults(func=cmd_register_remote)

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new recipe template')
    create_parser.add_argument('name', help='Recipe name (e.g., my_dataset)')
    create_parser.add_argument('--force', action='store_true', help='Overwrite existing file')
    create_parser.set_defaults(func=cmd_create)

    # Top-level run alias for convenience
    run_parser = subparsers.add_parser('run', help='Run a recipe (alias)')
    run_parser.add_argument('recipe_name', help='Recipe name')
    run_parser.add_argument('dataset_id', nargs='?', help='Output dataset ID (defaults for known recipes)')
    run_parser.add_argument('--work-dir', help='Working directory for recipe outputs')
    run_parser.add_argument('--materialize', action='store_true', help='Materialize after registering')
    run_parser.add_argument('--limit', type=int, help='Recipe-specific limit (e.g., number of tasks)')
    run_parser.add_argument('--data-dir', help='Path to raw data directory (e.g., .../ARCAGI/data)')
    run_parser.add_argument('--data-root', help='Path to raw repo root (parent of data/)')
    run_parser.add_argument('-p', '--param', dest='params', action='append', help='Additional key=value recipe params (repeatable)')
    run_parser.add_argument('--upload', action='store_true', help='Upload resulting dataset to cloud storage')
    run_parser.add_argument('--backend', default='s3', help='Storage backend for upload (default: s3)')
    run_parser.add_argument('--bucket', help='Bucket name for upload')

    def cmd_run(args):
        # default dataset_id for known recipes if omitted
        dataset_id = args.dataset_id
        if not dataset_id:
            if args.recipe_name in {"arcagi", "arcagi2"}:
                dataset_id = f"warpdata://arc/{args.recipe_name}"
            else:
                print("Error: dataset_id is required for this recipe", file=sys.stderr)
                sys.exit(2)
        # reuse recipes runner
        class _Args:
            pass
        rargs = _Args()
        rargs.recipes_cmd = 'run'
        rargs.recipe_name = args.recipe_name
        rargs.dataset_id = dataset_id
        rargs.work_dir = args.work_dir
        rargs.materialize = args.materialize
        rargs.limit = args.limit
        rargs.data_dir = args.data_dir
        rargs.data_root = args.data_root
        rargs.params = args.params
        cmd_recipes(rargs)

    run_parser.set_defaults(func=cmd_run)

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify datasets exist and are consistent')
    verify_parser.add_argument('--workspace', help='Filter by workspace')
    verify_parser.add_argument('--deep', action='store_true', help='Deep checks (hash/etag, file sizes)')
    verify_parser.add_argument('--materialize', action='store_true', help='Attempt to materialize each dataset')
    verify_parser.add_argument('--json', action='store_true', help='Output JSON report')
    def cmd_verify(args):
        try:
            report = wd.verify_datasets(workspace=args.workspace, deep=args.deep, materialize_check=args.materialize)
            if args.json:
                print(json.dumps(report, indent=2, default=str))
            else:
                total = report['total']
                issues = report['with_issues']
                print(f"Checked {total} dataset(s); {issues} with issues\n")
                for r in report['results']:
                    status = 'OK' if r['ok'] else 'ISSUES'
                    print(f"- {r['dataset_id']}: {status}")
                    if not r['ok']:
                        for msg in r['issues'][:5]:
                            print(f"    • {msg}")
                        if len(r['issues']) > 5:
                            print(f"    • (+{len(r['issues'])-5} more)")
        except Exception as e:
            print(f"Error verifying datasets: {e}", file=sys.stderr)
            sys.exit(1)
    verify_parser.set_defaults(func=cmd_verify)

    # Scaffold-py command (legacy name)
    scaffold_parser = subparsers.add_parser(
        'scaffold-py',
        help='Create a Python loader for a dataset (alias: scaffold)',
    )
    scaffold_parser.add_argument('dataset_id', help='Dataset ID (e.g., warpdata://nlp/imdb)')
    scaffold_parser.add_argument(
        '--filename', '-o',
        help='Output filename (default: <workspace>_<name>_loader.py)',
    )
    scaffold_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing file if it exists',
    )
    scaffold_parser.set_defaults(func=cmd_scaffold_py)

    # Scaffold command (preferred name)
    scaffold2_parser = subparsers.add_parser(
        'scaffold',
        help='Generate smart Python loader for a dataset',
    )
    scaffold2_parser.add_argument('dataset_id', help='Dataset ID (e.g., vision/vesuvius-scrolls)')
    scaffold2_parser.add_argument(
        '--output', '-o',
        help='Output filename (default: <workspace>_<name>_loader.py)',
    )
    scaffold2_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing file',
    )
    scaffold2_parser.set_defaults(func=cmd_scaffold_py)

    # Binance data download command
    binance_parser = subparsers.add_parser('binance', help='Download Binance market data')
    binance_parser.add_argument('data_type', choices=['klines', 'funding', 'aggtrades'],
                                help='Data type: klines (OHLCV), funding (funding rates), aggtrades')
    binance_parser.add_argument('--asset', default='um', choices=['spot', 'um', 'cm'],
                                help='Asset type: spot, um (USDT-M futures), cm (COIN-M futures)')
    binance_parser.add_argument('--interval', default='1h',
                                help='Klines interval: 1m, 5m, 15m, 1h, 4h, 1d (default: 1h)')
    binance_parser.add_argument('--symbols', help='Comma-separated symbols (default: from binance-klines-spot-1d)')
    binance_parser.add_argument('--top-n', type=int, help='Use top N symbols by market cap from CoinGecko')
    binance_parser.add_argument('--workers', type=int, default=8, help='Parallel download workers (default: 8)')
    binance_parser.add_argument('--out-dir', help='Output directory (default: ~/.warpdata/raw/binance/<asset>/<type>)')
    binance_parser.add_argument('--no-curate', action='store_true', help='Skip curation step (just download)')

    def cmd_binance(args):
        import subprocess
        import os

        script = Path(__file__).parent.parent.parent / 'scripts' / 'binance_bulk_fetch.py'
        if not script.exists():
            print(f"Error: binance_bulk_fetch.py not found at {script}", file=sys.stderr)
            sys.exit(1)

        # Map data_type to script params
        data_type_map = {'klines': 'klines', 'funding': 'fundingRate', 'aggtrades': 'aggTrades'}
        data_type = data_type_map[args.data_type]

        # Build output dir
        if args.out_dir:
            out_dir = args.out_dir
        else:
            suffix = f"_{args.interval}" if args.data_type == 'klines' else ""
            out_dir = os.path.expanduser(f"~/.warpdata/raw/binance/{args.asset}/{data_type}{suffix}")

        # Build dataset ID for curation
        if args.data_type == 'klines':
            dataset_id = f"warpdata://crypto/binance-klines-{args.asset}-{args.interval}"
        elif args.data_type == 'funding':
            dataset_id = f"warpdata://crypto/binance-funding-{args.asset}"
        else:
            dataset_id = f"warpdata://crypto/binance-aggtrades-{args.asset}"

        # Build command
        cmd = [
            sys.executable, str(script),
            '--data-type', data_type,
            '--asset', args.asset,
            '--out-dir', out_dir,
            '--workers', str(args.workers),
        ]

        if args.data_type == 'klines':
            cmd.extend(['--data-frequency', args.interval])

        if args.symbols:
            cmd.extend(['--symbols', args.symbols])
        elif args.top_n:
            cmd.extend(['--from-coingecko', 'warpdata://crypto/coingecko-hourly', '--top-n', str(args.top_n)])

        if not args.no_curate and args.data_type in ('klines', 'funding'):
            curate_type = 'klines' if args.data_type == 'klines' else 'fundingRate'
            cmd.extend(['--curate', curate_type, '--curated-out', dataset_id])

        print(f"🚀 Running: {' '.join(cmd)}")
        subprocess.run(cmd)

    binance_parser.set_defaults(func=cmd_binance)

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n💡 For detailed help: warp help")
        sys.exit(0)

    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
