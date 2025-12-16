"""
SQLite optimization and maintenance utilities.

These utilities provide memory-efficient SQLite operations to prevent
memory issues with large databases. Critical for preventing the 50 GB
memory spike observed with 11 GB+ databases.

Functions:
    optimize_sqlite_connection: Apply memory-efficient PRAGMA settings
    get_database_stats: Get database statistics for monitoring
    vacuum_database: Reclaim disk space
    check_database_integrity: Verify database health
    checkpoint_wal: Checkpoint Write-Ahead Log
    format_database_stats: Format stats for display
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def optimize_sqlite_connection(conn: sqlite3.Connection) -> None:
    """
    Apply memory-efficient PRAGMA settings to SQLite connection.

    This is CRITICAL for preventing memory issues with large databases.
    For an 11 GB database, these settings prevent:
    - 11 GB+ memory mapping (mmap_size=0)
    - Unbounded cache growth (cache_size limit)
    - Large WAL files (wal_autocheckpoint)

    Args:
        conn: SQLite connection (either sqlite3.Connection or DBAPI connection)

    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("/path/to/database.db")
        >>> optimize_sqlite_connection(conn)

        Or with SQLAlchemy event:
        >>> from sqlalchemy import event, create_engine
        >>> engine = create_engine("sqlite:///database.db")
        >>> @event.listens_for(engine, "connect")
        >>> def receive_connect(dbapi_conn, connection_record):
        >>>     optimize_sqlite_connection(dbapi_conn)
    """
    cursor = conn.cursor()

    try:
        # CRITICAL: Limit page cache to 32 MB (negative value = KB)
        # Default can grow unbounded, causing memory issues
        cursor.execute("PRAGMA cache_size = -32000")
        logger.debug("Set cache_size to 32 MB")

        # CRITICAL: Disable memory mapping
        # Without this, 11 GB database can be mapped into 11 GB+ virtual memory
        cursor.execute("PRAGMA mmap_size = 0")
        logger.debug("Disabled memory mapping (mmap_size = 0)")

        # Use Write-Ahead Logging for better concurrency
        # Check current mode first to avoid unnecessary changes
        current_mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
        if current_mode.lower() != "wal":
            cursor.execute("PRAGMA journal_mode = WAL")
            logger.debug("Enabled WAL (Write-Ahead Logging) mode")

        # Checkpoint WAL every 1000 pages to prevent unbounded growth
        # Prevents WAL file from growing to GBs in size
        cursor.execute("PRAGMA wal_autocheckpoint = 1000")
        logger.debug("Set WAL autocheckpoint to 1000 pages")

        # Use memory for temporary tables (faster than disk)
        cursor.execute("PRAGMA temp_store = MEMORY")
        logger.debug("Set temp_store to MEMORY")

        # Use NORMAL synchronous mode (balance of safety and performance)
        cursor.execute("PRAGMA synchronous = NORMAL")
        logger.debug("Set synchronous mode to NORMAL")

        # Optimize query planner
        cursor.execute("PRAGMA optimize")
        logger.debug("Ran PRAGMA optimize")

        conn.commit()
        logger.info("Applied memory-efficient PRAGMA settings to SQLite connection")

    except Exception as e:
        logger.error(f"Error applying PRAGMA settings: {e}")
        raise
    finally:
        cursor.close()


def get_database_stats(db_path: Path) -> Dict:
    """
    Get statistics about the SQLite database for monitoring and diagnostics.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        Dictionary containing:
        - file_size_mb: Database file size in MB
        - page_count: Number of pages in database
        - page_size: Size of each page in bytes
        - cache_size_mb: Configured cache size in MB
        - journal_mode: Current journal mode (WAL, DELETE, etc.)
        - mmap_size_mb: Memory mapping size in MB
        - wal_file_size_mb: WAL file size (if WAL mode)

    Example:
        >>> stats = get_database_stats(Path("/path/to/database.db"))
        >>> print(f"Database: {stats['file_size_mb']:.2f} MB")
        >>> print(f"Cache: {stats['cache_size_mb']:.2f} MB")
    """
    logger.debug(f"Gathering database statistics for {db_path}")

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        stats = {}

        # File size
        stats['file_size_mb'] = db_path.stat().st_size / (1024 * 1024)

        # Page information
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
        stats['page_count'] = page_count
        stats['page_size'] = page_size
        stats['theoretical_size_mb'] = (page_count * page_size) / (1024 * 1024)

        # Cache settings
        cache_size = conn.execute("PRAGMA cache_size").fetchone()[0]
        stats['cache_size'] = cache_size
        if cache_size < 0:
            # Negative = KB
            stats['cache_size_mb'] = abs(cache_size) / 1024
        else:
            # Positive = pages
            stats['cache_size_mb'] = (cache_size * page_size) / (1024 * 1024)

        # Journal mode
        stats['journal_mode'] = conn.execute("PRAGMA journal_mode").fetchone()[0]

        # Memory mapping
        stats['mmap_size'] = conn.execute("PRAGMA mmap_size").fetchone()[0]
        stats['mmap_size_mb'] = stats['mmap_size'] / (1024 * 1024)

        # Synchronous mode
        stats['synchronous'] = conn.execute("PRAGMA synchronous").fetchone()[0]

        # WAL information (if in WAL mode)
        if stats['journal_mode'].lower() == 'wal':
            # Check WAL file size
            wal_path = Path(str(db_path) + "-wal")
            if wal_path.exists():
                stats['wal_file_size_mb'] = wal_path.stat().st_size / (1024 * 1024)
            else:
                stats['wal_file_size_mb'] = 0

            # WAL checkpoint info
            try:
                wal_checkpoint = conn.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
                stats['wal_log_frames'] = wal_checkpoint[1]
                stats['wal_checkpointed_frames'] = wal_checkpoint[2]
            except Exception as e:
                logger.warning(f"Could not get WAL checkpoint info: {e}")

        return stats

    except Exception as e:
        logger.error(f"Error gathering database statistics: {e}")
        raise
    finally:
        conn.close()


def vacuum_database(db_path: Path, analyze: bool = True) -> Dict[str, float]:
    """
    Vacuum the database to reclaim space and optimize structure.

    VACUUM rebuilds the database file, repacking it into minimal disk space.
    Useful for databases that have grown large due to many updates/deletes.

    WARNING: Can take a long time on large databases and requires free
    disk space equal to the database size.

    Args:
        db_path: Path to the SQLite database
        analyze: Whether to run ANALYZE after VACUUM (default: True)

    Returns:
        Dictionary with 'size_before_mb', 'size_after_mb', and 'reclaimed_mb'

    Example:
        >>> result = vacuum_database(Path("/path/to/database.db"))
        >>> print(f"Reclaimed {result['reclaimed_mb']:.2f} MB")
    """
    logger.info(f"Starting VACUUM operation on {db_path}")

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Get size before vacuum
    size_before = db_path.stat().st_size / (1024 * 1024)  # MB
    logger.info(f"Database size before VACUUM: {size_before:.2f} MB")

    conn = sqlite3.connect(db_path)
    try:
        # VACUUM cannot be run inside a transaction
        conn.isolation_level = None

        logger.info("Running VACUUM (this may take a while for large databases)...")
        conn.execute("VACUUM")
        logger.info("VACUUM completed")

        if analyze:
            logger.info("Running ANALYZE...")
            conn.execute("ANALYZE")
            logger.info("ANALYZE completed")

        conn.commit()

    except Exception as e:
        logger.error(f"Error during VACUUM operation: {e}")
        raise
    finally:
        conn.close()

    # Get size after vacuum
    size_after = db_path.stat().st_size / (1024 * 1024)  # MB
    reclaimed = size_before - size_after

    logger.info(f"Database size after VACUUM: {size_after:.2f} MB")
    logger.info(f"Space reclaimed: {reclaimed:.2f} MB ({(reclaimed/size_before)*100:.1f}%)")

    return {
        'size_before_mb': size_before,
        'size_after_mb': size_after,
        'reclaimed_mb': reclaimed,
    }


def check_database_integrity(db_path: Path, quick: bool = False) -> bool:
    """
    Check database integrity.

    Args:
        db_path: Path to the SQLite database
        quick: If True, do quick check. If False, do full check (default: False)

    Returns:
        True if database is OK, False otherwise

    Example:
        >>> if check_database_integrity(Path("/path/to/database.db")):
        ...     print("Database is healthy")
        ... else:
        ...     print("Database has integrity issues!")
    """
    logger.info(f"Checking database integrity: {db_path}")

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        if quick:
            # Quick check - just verify the database can be opened and read
            result = conn.execute("PRAGMA quick_check").fetchone()[0]
        else:
            # Full integrity check
            result = conn.execute("PRAGMA integrity_check").fetchone()[0]

        if result == "ok":
            logger.info("Database integrity check: OK")
            return True
        else:
            logger.error(f"Database integrity check failed: {result}")
            return False

    except Exception as e:
        logger.error(f"Error checking database integrity: {e}")
        return False
    finally:
        conn.close()


def checkpoint_wal(db_path: Path, mode: str = "PASSIVE") -> Optional[Dict[str, int]]:
    """
    Checkpoint the WAL (Write-Ahead Log) file.

    Moves data from the WAL file back into the main database file,
    which helps prevent WAL files from growing too large.

    Args:
        db_path: Path to the SQLite database
        mode: Checkpoint mode - "PASSIVE", "FULL", "RESTART", or "TRUNCATE"
              - PASSIVE: Checkpoint as much as possible without blocking
              - FULL: Checkpoint all frames, may block
              - RESTART: Like FULL, also restarts the log
              - TRUNCATE: Like RESTART, also truncates WAL to 0 bytes

    Returns:
        Dictionary with checkpoint results or None if not in WAL mode

    Example:
        >>> result = checkpoint_wal(Path("/path/to/database.db"), "PASSIVE")
        >>> if result:
        ...     print(f"Checkpointed {result['moved_frames']} frames")
    """
    logger.info(f"Checkpointing WAL file for {db_path} (mode: {mode})")

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        # Check if in WAL mode
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        if journal_mode.lower() != "wal":
            logger.warning(f"Database is not in WAL mode (current: {journal_mode})")
            return None

        # Execute checkpoint
        result = conn.execute(f"PRAGMA wal_checkpoint({mode})").fetchone()

        checkpoint_info = {
            'busy': result[0],  # 0 if checkpoint completed, 1 if blocked
            'log_frames': result[1],  # Number of frames in log
            'moved_frames': result[2],  # Number of frames moved to database
        }

        logger.info(
            f"WAL checkpoint completed: {checkpoint_info['moved_frames']} "
            f"of {checkpoint_info['log_frames']} frames moved"
        )

        return checkpoint_info

    except Exception as e:
        logger.error(f"Error checkpointing WAL: {e}")
        raise
    finally:
        conn.close()


def format_database_stats(stats: Dict) -> str:
    """
    Format database statistics as a readable string.

    Args:
        stats: Statistics dictionary from get_database_stats()

    Returns:
        Formatted string representation of stats

    Example:
        >>> stats = get_database_stats(Path("/path/to/database.db"))
        >>> print(format_database_stats(stats))
    """
    lines = [
        "=" * 60,
        "DATABASE STATISTICS",
        "=" * 60,
        f"File Size:           {stats['file_size_mb']:>10.2f} MB",
        f"Page Count:          {stats['page_count']:>10,}",
        f"Page Size:           {stats['page_size']:>10,} bytes",
        f"Theoretical Size:    {stats['theoretical_size_mb']:>10.2f} MB",
        f"Cache Size (MB):     {stats['cache_size_mb']:>10.2f} MB",
        f"Journal Mode:        {stats['journal_mode']:>10}",
        f"Memory Mapping:      {stats['mmap_size_mb']:>10.2f} MB",
        f"Synchronous Mode:    {stats['synchronous']:>10}",
    ]

    if 'wal_file_size_mb' in stats:
        lines.extend([
            "",
            f"WAL File Size:       {stats['wal_file_size_mb']:>10.2f} MB",
        ])
        if 'wal_log_frames' in stats:
            lines.append(f"WAL Log Frames:      {stats['wal_log_frames']:>10,}")
        if 'wal_checkpointed_frames' in stats:
            lines.append(f"WAL Checkpointed:    {stats['wal_checkpointed_frames']:>10,}")

    lines.append("=" * 60)

    return "\n".join(lines)
