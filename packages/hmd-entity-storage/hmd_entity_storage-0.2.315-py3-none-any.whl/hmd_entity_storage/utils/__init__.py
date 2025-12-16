"""
Utility functions for hmd-entity-storage.

This module provides database optimization and maintenance utilities,
particularly for SQLite databases used with the storage engine.
"""

from .sqlite_utils import (
    optimize_sqlite_connection,
    get_database_stats,
    vacuum_database,
    check_database_integrity,
    checkpoint_wal,
    format_database_stats,
)

__all__ = [
    'optimize_sqlite_connection',
    'get_database_stats',
    'vacuum_database',
    'check_database_integrity',
    'checkpoint_wal',
    'format_database_stats',
]
