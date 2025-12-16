"""
URI parsing and normalization for warpdata.

Supports:
- warpdata:// - Registered datasets
- file:// - Local files
- s3:// - S3 objects
- http:// / https:// - HTTP(S) resources
- hf:// - Hugging Face Hub datasets
"""
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse, ParseResult
import os


class URI:
    """
    Represents a parsed and normalized URI.
    """

    def __init__(
        self,
        scheme: str,
        path: str,
        workspace: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        netloc: str = "",
        query: str = "",
        fragment: str = "",
    ):
        """
        Initialize a URI.

        Args:
            scheme: URI scheme (e.g., 'file', 's3', 'warpdata')
            path: URI path
            workspace: Workspace name (for warpdata:// URIs)
            name: Dataset name (for warpdata:// URIs)
            version: Dataset version (for warpdata:// URIs)
            netloc: Network location (for remote URIs)
            query: Query string
            fragment: Fragment identifier
        """
        self.scheme = scheme
        self.path = path
        self.workspace = workspace
        self.name = name
        self.version = version
        self.netloc = netloc
        self.query = query
        self.fragment = fragment

    @property
    def is_warpdata(self) -> bool:
        """Check if this is a warpdata:// URI."""
        return self.scheme == "warpdata"

    @property
    def is_local(self) -> bool:
        """Check if this is a local file URI."""
        return self.scheme == "file" or self.scheme == ""

    @property
    def is_remote(self) -> bool:
        """Check if this is a remote URI."""
        return self.scheme in ("s3", "http", "https", "hf")

    @property
    def dataset_id(self) -> Optional[str]:
        """Get the dataset ID for warpdata:// URIs."""
        if self.is_warpdata and self.workspace and self.name:
            return f"warpdata://{self.workspace}/{self.name}"
        return None

    def to_fsspec_url(self) -> str:
        """
        Convert to an fsspec-compatible URL.

        Returns:
            fsspec URL string
        """
        if self.is_warpdata:
            raise ValueError("Cannot convert warpdata:// URI to fsspec URL directly")

        if self.is_local:
            # For local files, return absolute path
            return str(Path(self.path).resolve())

        # For remote URIs, reconstruct the URL
        url = f"{self.scheme}://"
        if self.netloc:
            url += self.netloc
        url += self.path

        if self.query:
            url += f"?{self.query}"
        if self.fragment:
            url += f"#{self.fragment}"

        return url

    def __str__(self) -> str:
        """String representation of the URI."""
        if self.is_warpdata:
            uri = f"warpdata://{self.workspace}/{self.name}"
            if self.version:
                uri += f"@{self.version}"
            return uri

        return self.to_fsspec_url()

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"URI({str(self)})"


def parse_uri(uri: str) -> URI:
    """
    Parse a URI string into a URI object.

    Args:
        uri: URI string to parse

    Returns:
        Parsed URI object

    Raises:
        ValueError: If URI format is invalid
    """
    # Handle bare file paths (no scheme)
    if "://" not in uri:
        # Treat as a local file path
        abs_path = str(Path(uri).resolve())
        return URI(scheme="file", path=abs_path)

    # Parse as URL
    parsed: ParseResult = urlparse(uri)

    # Handle warpdata:// URIs specially
    if parsed.scheme == "warpdata":
        return _parse_warpdata_uri(parsed)

    # Handle other URIs
    return URI(
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path=parsed.path,
        query=parsed.query,
        fragment=parsed.fragment,
    )


def _parse_warpdata_uri(parsed: ParseResult) -> URI:
    """
    Parse a warpdata:// URI.

    Format: warpdata://{workspace}/{name}[@{version}]

    Args:
        parsed: Parsed URL result

    Returns:
        URI object

    Raises:
        ValueError: If warpdata URI format is invalid
    """
    # For warpdata://workspace/name, urlparse puts workspace in netloc
    # and /name in path. We also support shorthand: warpdata://name,
    # which resolves to the configured default workspace.
    workspace = parsed.netloc
    path = parsed.path.lstrip("/")

    # Check for version tag (can be in path like name@version)
    version = None
    if "@" in workspace and path:
        # Only split workspace if a path (name) exists; otherwise this may be shorthand
        workspace, version = workspace.rsplit("@", 1)
    elif "@" in path:
        path, version = path.rsplit("@", 1)

    # Handle shorthand form: warpdata://name[@version]
    if not path and workspace:
        from .config import get_config
        # In shorthand, the netloc is actually the dataset name (possibly with @version)
        ds = workspace
        if "@" in ds and version is None:
            ds, version = ds.rsplit("@", 1)
        name = ds
        workspace = get_config().default_workspace
    else:
        # Normal form: path is the dataset name
        name = path

    # Validate
    if not workspace or not name:
        raise ValueError(
            f"Invalid warpdata URI format. Expected warpdata://{{workspace}}/{{name}}, got: {parsed.geturl()}"
        )

    return URI(
        scheme="warpdata",
        path=f"{workspace}/{name}",
        workspace=workspace,
        name=name,
        version=version,
    )


def normalize_uri(uri: str) -> str:
    """
    Normalize a URI to a standard form.

    Args:
        uri: URI to normalize

    Returns:
        Normalized URI string
    """
    parsed = parse_uri(uri)
    return str(parsed)


def resolve_dataset_id(dataset_id: str) -> str:
    """
    Resolve a dataset ID, supporting shorthand forms.

    This function centralizes the auto-finding logic used by load() and schema().
    It supports:
    - Full warpdata:// URIs: "warpdata://workspace/name"
    - Workspace/name shorthand: "workspace/name"
    - Name-only shorthand: "name" (searches across all workspaces)

    Args:
        dataset_id: Dataset ID in any supported format

    Returns:
        Normalized warpdata:// URI string

    Raises:
        ValueError: If dataset cannot be found or is ambiguous
    """
    # If already a warpdata:// URI, just normalize it
    if "://" in dataset_id:
        uri = parse_uri(dataset_id)
        if uri.is_warpdata:
            return str(uri)
        # Not a warpdata URI, return as-is for caller to handle
        return dataset_id

    # Check if it's a local path that exists
    p = Path(dataset_id)
    if p.exists():
        # It's a local file, not a dataset ID
        return dataset_id

    # Import here to avoid circular dependency
    from .registry import get_registry_readonly
    from .config import get_config

    reg = get_registry_readonly()

    # Support shorthand 'workspace/name' as well as plain 'name'
    if "/" in dataset_id:
        try:
            workspace, name = dataset_id.split("/", 1)
        except ValueError:
            workspace, name = None, None
        if workspace and name:
            info = reg.get_dataset_version(workspace, name, "latest")
            if info is not None:
                return f"warpdata://{workspace}/{name}"
            # Not found locally, but still return as warpdata:// URI
            # so that auto-register from remote can be attempted
            return f"warpdata://{workspace}/{name}"

    # Find all datasets matching this name across workspaces
    matches = [ds for ds in reg.list_datasets() if ds.get("name") == dataset_id]
    if len(matches) == 1:
        ws = matches[0].get("workspace") or get_config().default_workspace
        return f"warpdata://{ws}/{dataset_id}"
    elif len(matches) > 1:
        # Prefer default workspace if present
        default_ws = get_config().default_workspace
        preferred = [m for m in matches if m.get("workspace") == default_ws]
        if len(preferred) == 1:
            return f"warpdata://{default_ws}/{dataset_id}"
        else:
            raise ValueError(
                "Ambiguous dataset name. Found in workspaces: "
                + ", ".join(sorted({m.get('workspace') for m in matches}))
                + ". Specify full ID like 'warpdata://workspace/" + dataset_id + "' "
                + "or set WARPDATA_DEFAULT_WORKSPACE."
            )

    # No matches found, return as-is and let caller decide how to handle
    return dataset_id


def split_dataset_id(dataset_id: str) -> Tuple[str, str]:
    """
    Split a dataset ID into workspace and name.

    Args:
        dataset_id: Dataset ID (e.g., 'warpdata://nlp/imdb')

    Returns:
        Tuple of (workspace, name)

    Raises:
        ValueError: If dataset ID format is invalid
    """
    parsed = parse_uri(dataset_id)

    if not parsed.is_warpdata:
        raise ValueError(f"Not a warpdata:// URI: {dataset_id}")

    if not parsed.workspace or not parsed.name:
        raise ValueError(f"Invalid dataset ID format: {dataset_id}")

    return parsed.workspace, parsed.name


def require_warpdata_id(dataset_id: str) -> str:
    """
    Resolve shorthand dataset IDs and ensure the result is a warpdata:// URI.

    This is the strict resolver for APIs that require a dataset (not a file).
    Use this in management, storage, embeddings, and streaming APIs.

    Args:
        dataset_id: Dataset ID in any supported format

    Returns:
        Normalized warpdata:// URI string

    Raises:
        ValueError: If the input resolves to a file path or non-warpdata URI

    Examples:
        >>> require_warpdata_id("crypto/binance")
        'warpdata://crypto/binance'
        >>> require_warpdata_id("/tmp/file.parquet")
        ValueError: Expected a dataset ID...
    """
    resolved = resolve_dataset_id(dataset_id)
    uri = parse_uri(resolved)
    if not uri.is_warpdata:
        raise ValueError(
            f"Expected a dataset ID (warpdata://workspace/name), got: {dataset_id!r}"
        )
    return resolved
