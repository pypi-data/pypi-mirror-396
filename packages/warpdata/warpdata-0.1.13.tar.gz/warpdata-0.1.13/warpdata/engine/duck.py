"""
DuckDB engine wrapper for high-performance data processing.
"""
import duckdb
import threading
from pathlib import Path
from typing import List, Union, Optional, Dict, Any, Iterator
import pyarrow as pa


class DuckDBEngine:
    """
    Wrapper around DuckDB for reading and querying data.
    """

    def __init__(self, connection: Optional[duckdb.DuckDBPyConnection] = None):
        """
        Initialize DuckDB engine.

        Args:
            connection: Existing DuckDB connection (creates new if None)
        """
        self.conn = connection if connection is not None else duckdb.connect(":memory:")

    def read_file(
        self, file_path: Union[str, Path], file_format: Optional[str] = None
    ) -> duckdb.DuckDBPyRelation:
        """
        Read a data file into a DuckDB relation.

        Args:
            file_path: Path to file
            file_format: File format (auto-detected if None)

        Returns:
            DuckDB relation
        """
        file_path = str(file_path)

        # Auto-detect format from extension
        if file_format is None:
            file_format = self._detect_format(file_path)

        # Read based on format
        if file_format == "parquet":
            return self.conn.read_parquet(file_path)
        elif file_format == "arrow":
            # Read Arrow IPC stream (HuggingFace uses streaming format)
            import pyarrow.ipc as ipc
            with open(file_path, 'rb') as f:
                reader = ipc.open_stream(f)
                table = reader.read_all()
            return self.conn.from_arrow(table)
        elif file_format in ("csv", "tsv"):
            # Use appropriate delimiter for CSV vs TSV
            sep = "\t" if file_format == "tsv" else ","
            return self.conn.read_csv(file_path, header=True, sep=sep)
        elif file_format in ("jsonl", "ndjson", "json"):
            # For JSONL, read as newline-delimited JSON
            return self.conn.read_json(file_path, format="newline_delimited")
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def read_files(
        self, file_paths: List[Union[str, Path]], file_format: Optional[str] = None
    ) -> duckdb.DuckDBPyRelation:
        """
        Read multiple files and union them into a single relation.

        Args:
            file_paths: List of file paths
            file_format: File format (auto-detected if None)

        Returns:
            DuckDB relation
        """
        if not file_paths:
            raise ValueError("No files provided")

        # If only one file, just read it directly
        if len(file_paths) == 1:
            return self.read_file(file_paths[0], file_format)

        # Auto-detect format from first file
        if file_format is None:
            file_format = self._detect_format(str(file_paths[0]))

        # For Parquet, DuckDB can read multiple files efficiently with a list
        if file_format == "parquet":
            paths_str = [str(p) for p in file_paths]
            return self.conn.read_parquet(paths_str)

        # For other formats, union the results
        relations = [self.read_file(path, file_format) for path in file_paths]

        # Union all relations
        result = relations[0]
        for rel in relations[1:]:
            result = result.union(rel)

        return result

    def get_schema(
        self, file_path: Union[str, Path], file_format: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get schema of a data file.

        Args:
            file_path: Path to file
            file_format: File format (auto-detected if None)

        Returns:
            Dictionary mapping column names to types
        """
        relation = self.read_file(file_path, file_format)

        # Get column names and types
        schema = {}
        for col_name, col_type in zip(relation.columns, relation.types):
            schema[col_name] = str(col_type)

        return schema

    def head(
        self, file_path: Union[str, Path], n: int = 5, file_format: Optional[str] = None
    ) -> duckdb.DuckDBPyRelation:
        """
        Get the first N rows of a data file.

        Args:
            file_path: Path to file
            n: Number of rows to return
            file_format: File format (auto-detected if None)

        Returns:
            DuckDB relation with first N rows
        """
        relation = self.read_file(file_path, file_format)
        return relation.limit(n)

    def _detect_format(self, file_path: str) -> str:
        """
        Detect file format from extension.

        Args:
            file_path: File path

        Returns:
            Format string ('parquet', 'csv', 'jsonl')
        """
        path = Path(file_path)
        ext = path.suffix.lower().lstrip(".")

        format_map = {
            "parquet": "parquet",
            "pq": "parquet",
            "arrow": "arrow",  # Arrow IPC format
            "ipc": "arrow",    # Arrow IPC format
            "feather": "arrow",  # Feather is Arrow IPC v2
            "csv": "csv",
            "tsv": "tsv",  # Tab-separated values
            "txt": "csv",  # Assume comma-separated for .txt
            "jsonl": "jsonl",
            "ndjson": "jsonl",
            "json": "json",
        }

        if ext in format_map:
            return format_map[ext]

        raise ValueError(f"Cannot detect format for file: {file_path}")

    def query(self, sql: str) -> duckdb.DuckDBPyRelation:
        """
        Execute a SQL query.

        Args:
            sql: SQL query string

        Returns:
            DuckDB relation with query results
        """
        return self.conn.sql(sql)

    def to_df(self, relation: duckdb.DuckDBPyRelation, format: str = "pandas"):
        """
        Convert a DuckDB relation to a DataFrame.

        Args:
            relation: DuckDB relation
            format: Target format ('pandas', 'polars', 'arrow')

        Returns:
            DataFrame in requested format
        """
        if format == "pandas":
            return relation.df()
        elif format == "polars":
            return relation.pl()
        elif format == "arrow":
            return relation.arrow()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def stream_arrow(
        self, relation: duckdb.DuckDBPyRelation, batch_size: int = 10000
    ) -> Iterator[pa.RecordBatch]:
        """
        Zero-copy streaming iterator yielding PyArrow RecordBatches.

        This enables processing datasets larger than RAM by streaming
        chunks directly from disk through DuckDB into Arrow format.

        Args:
            relation: DuckDB relation to stream
            batch_size: Number of rows per batch

        Yields:
            PyArrow RecordBatch objects

        Example:
            >>> engine = get_engine()
            >>> rel = engine.read_file('huge_data.parquet')
            >>> for batch in engine.stream_arrow(rel, batch_size=50000):
            ...     # Process batch without loading full dataset
            ...     process(batch)
        """
        # Optimize for sequential scan (allows parallel reading of Parquet)
        self.conn.execute("PRAGMA preserve_insertion_order=FALSE")

        # Get Arrow RecordBatchReader (zero-copy from DuckDB -> Arrow)
        arrow_reader = relation.record_batch(batch_size)

        for batch in arrow_reader:
            yield batch


# Thread-local DuckDB connection (avoid cross-thread pending result errors)
_thread_local = threading.local()


def get_engine() -> DuckDBEngine:
    """
    Get a DuckDB engine instance with a shared connection.

    Returns:
        DuckDBEngine instance
    """
    # One DuckDB connection per thread for safety
    conn = getattr(_thread_local, "conn", None)
    if conn is None:
        conn = duckdb.connect(":memory:")
        _thread_local.conn = conn
    return DuckDBEngine(conn)


def reset_engine():
    """Reset the thread-local engine connection (useful for testing)."""
    conn = getattr(_thread_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        finally:
            _thread_local.conn = None
