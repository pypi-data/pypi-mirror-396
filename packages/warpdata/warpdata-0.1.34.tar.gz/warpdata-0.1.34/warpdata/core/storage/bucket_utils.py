"""
Utility functions for S3 bucket naming and management.
"""


def normalize_bucket_name(bucket: str) -> str:
    """
    Normalize bucket name with warpbucket- prefix.

    Args:
        bucket: Raw bucket name (e.g., 'mydata', 'warpbucket-mydata', 'warp-alerad')

    Returns:
        Normalized bucket name with warpbucket- prefix

    Examples:
        >>> normalize_bucket_name('mydata')
        'warpbucket-mydata'
        >>> normalize_bucket_name('warpbucket-mydata')
        'warpbucket-mydata'
        >>> normalize_bucket_name('warp-alerad')  # Legacy
        'warp-alerad'  # Unchanged for backwards compatibility
    """
    # Already has warpbucket- prefix
    if bucket.startswith('warpbucket-'):
        return bucket

    # Legacy bucket (warp-*) - keep as-is for backwards compatibility
    if bucket.startswith('warp-'):
        return bucket

    # Add warpbucket- prefix
    return f'warpbucket-{bucket}'


def get_bucket_display_name(bucket: str) -> str:
    """
    Get display name for bucket (without prefix).

    Args:
        bucket: Bucket name with or without prefix

    Returns:
        Display name without warpbucket- prefix

    Examples:
        >>> get_bucket_display_name('warpbucket-mydata')
        'mydata'
        >>> get_bucket_display_name('mydata')
        'mydata'
    """
    if bucket.startswith('warpbucket-'):
        return bucket[11:]  # Remove 'warpbucket-' prefix
    return bucket
