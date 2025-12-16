"""
Utility functions for recipe development.

Provides common patterns for:
- File discovery and pattern matching
- Filename parsing with regex
- CSV/JSON loading and merging
- Data validation and cleaning
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Pattern
import pandas as pd


def discover_files(
    directory: Path,
    patterns: List[str],
    recursive: bool = False
) -> List[Path]:
    """
    Discover files matching glob patterns.

    Args:
        directory: Directory to search
        patterns: List of glob patterns (e.g., ['*.csv', '*.json'])
        recursive: If True, search recursively with **/ prefix

    Returns:
        List of matching file paths

    Examples:
        >>> files = discover_files(Path('./data'), ['*.bdf', '*.xdf'])
        >>> eeg_files = discover_files(Path('./eeg'), ['**/*.edf'], recursive=True)
    """
    files = []
    for pattern in patterns:
        if recursive and not pattern.startswith('**'):
            pattern = f"**/{pattern}"

        if recursive:
            files.extend(directory.rglob(pattern[3:]))  # Remove **/ prefix
        else:
            files.extend(directory.glob(pattern))

    return sorted(files)


def parse_filename_pattern(
    filepath: Path,
    pattern: str,
    groups: Dict[str, int],
    transform: Optional[Dict[str, Callable]] = None
) -> Dict[str, Any]:
    r"""
    Parse filename using regex pattern and extract named fields.

    Args:
        filepath: File path to parse
        pattern: Regex pattern with capturing groups
        groups: Mapping of field names to group indices (1-indexed)
        transform: Optional dict of field_name -> transform_function

    Returns:
        Dictionary with extracted fields

    Examples:
        >>> parse_filename_pattern(
        ...     Path('S01_DMT_session.bdf'),
        ...     r'S(\d+)_([A-Z]+)_',
        ...     {'subject_id': 1, 'condition': 2},
        ...     transform={'subject_id': lambda x: f'S{x.zfill(2)}'}
        ... )
        {'subject_id': 'S01', 'condition': 'DMT'}
    """
    match = re.search(pattern, filepath.name)
    if not match:
        return {}

    result = {}
    for field_name, group_idx in groups.items():
        try:
            value = match.group(group_idx)
            if transform and field_name in transform:
                value = transform[field_name](value)
            result[field_name] = value
        except (IndexError, AttributeError):
            continue

    return result


def load_auxiliary_data(
    filepath: Path,
    file_format: str = 'csv',
    index_col: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Load auxiliary data (CSV, JSON, etc.) for merging with main data.

    Args:
        filepath: Path to auxiliary data file
        file_format: Format ('csv', 'json', 'jsonl')
        index_col: Column to use as index (for dict conversion)
        **kwargs: Additional arguments passed to loader

    Returns:
        Dictionary representation of data

    Examples:
        >>> scales = load_auxiliary_data(
        ...     Path('./scales_results.csv'),
        ...     file_format='csv',
        ...     index_col='subject_id'
        ... )
    """
    if not filepath.exists():
        return {}

    try:
        if file_format == 'csv':
            df = pd.read_csv(filepath, **kwargs)
            if index_col:
                df = df.set_index(index_col)
            return df.to_dict('index')

        elif file_format == 'json':
            import json
            with open(filepath, 'r') as f:
                return json.load(f)

        elif file_format == 'jsonl':
            import json
            data = []
            with open(filepath, 'r') as f:
                for line in f:
                    data.append(json.loads(line))
            return data

        else:
            raise ValueError(f"Unsupported format: {file_format}")

    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return {}


def group_files_by_key(
    files: List[Path],
    key_extractor: Callable[[Path], Optional[str]]
) -> Dict[str, List[Path]]:
    r"""
    Group files by a key extracted from filename or path.

    Args:
        files: List of file paths
        key_extractor: Function that extracts grouping key from path

    Returns:
        Dictionary mapping keys to lists of files

    Examples:
        >>> # Group by subject ID
        >>> def extract_subject(p: Path) -> str:
        ...     match = re.search(r'S(\d+)', p.name)
        ...     return f'S{match.group(1)}' if match else None
        >>> groups = group_files_by_key(eeg_files, extract_subject)
    """
    groups: Dict[str, List[Path]] = {}

    for filepath in files:
        key = key_extractor(filepath)
        if key:
            if key not in groups:
                groups[key] = []
            groups[key].append(filepath)

    return groups


def validate_file_group(
    files: List[Path],
    expected_count: Optional[int] = None,
    required_patterns: Optional[List[Pattern]] = None
) -> Dict[str, Any]:
    """
    Validate a group of files meets expected criteria.

    Args:
        files: List of file paths to validate
        expected_count: Expected number of files
        required_patterns: List of regex patterns that must be present

    Returns:
        Validation result with 'valid', 'missing', 'extra' fields

    Examples:
        >>> result = validate_file_group(
        ...     subject_files,
        ...     expected_count=3,
        ...     required_patterns=[
        ...         re.compile(r'_DMT_'),
        ...         re.compile(r'_EC_'),
        ...         re.compile(r'_EO_')
        ...     ]
        ... )
        >>> if not result['valid']:
        ...     print(f"Missing: {result['missing']}")
    """
    result = {
        'valid': True,
        'file_count': len(files),
        'missing': [],
        'extra': [],
    }

    # Check count
    if expected_count is not None and len(files) != expected_count:
        result['valid'] = False
        if len(files) < expected_count:
            result['missing'].append(f"{expected_count - len(files)} files")
        else:
            result['extra'].append(f"{len(files) - expected_count} extra files")

    # Check required patterns
    if required_patterns:
        for pattern in required_patterns:
            found = any(pattern.search(f.name) for f in files)
            if not found:
                result['valid'] = False
                result['missing'].append(f"pattern: {pattern.pattern}")

    return result


def compute_file_stats(files: List[Path]) -> Dict[str, Any]:
    """
    Compute statistics for a group of files.

    Args:
        files: List of file paths

    Returns:
        Dictionary with file statistics

    Examples:
        >>> stats = compute_file_stats(subject_files)
        >>> print(f"Total size: {stats['total_size_mb']:.2f}MB")
    """
    total_size = sum(f.stat().st_size for f in files if f.exists())

    formats = set(f.suffix.lower().lstrip('.') for f in files)

    return {
        'file_count': len(files),
        'total_size_bytes': total_size,
        'total_size_mb': total_size / (1024 * 1024),
        'file_formats': sorted(list(formats)),
        'filenames': [f.name for f in files],
    }
