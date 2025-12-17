"""Application services for sqlit.

This package provides shared business logic used by both the TUI and CLI,
ensuring consistent behavior across interfaces.

Services:
- QueryService: Unified query execution with history tracking
- ConnectionSession: Connection lifecycle management with cleanup guarantees
- DatabaseExecutor: Serialized database operation execution

Protocols:
- AdapterProtocol: Interface for database adapters
- HistoryStoreProtocol: Interface for query history storage
- ConnectionStoreProtocol: Interface for connection storage
- SettingsStoreProtocol: Interface for settings storage
"""

from .cancellable import CancellableQuery
from .executor import DatabaseExecutor
from .protocols import (
    AdapterFactoryProtocol,
    AdapterProtocol,
    ConnectionStoreProtocol,
    HistoryStoreProtocol,
    SettingsStoreProtocol,
    TunnelFactoryProtocol,
)
from .query import NonQueryResult, QueryResult, QueryService, is_select_query
from .session import ConnectionSession

__all__ = [
    # Query service
    "QueryService",
    "QueryResult",
    "NonQueryResult",
    "is_select_query",
    # Session
    "ConnectionSession",
    # Executor
    "DatabaseExecutor",
    # Cancellable query
    "CancellableQuery",
    # Protocols
    "AdapterProtocol",
    "AdapterFactoryProtocol",
    "HistoryStoreProtocol",
    "TunnelFactoryProtocol",
    "ConnectionStoreProtocol",
    "SettingsStoreProtocol",
]
