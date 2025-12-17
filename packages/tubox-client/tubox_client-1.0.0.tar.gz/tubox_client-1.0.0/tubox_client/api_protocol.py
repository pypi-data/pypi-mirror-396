"""
Tubox API Protocol - Similar to MongoDB wire protocol
Defines request/response formats for client-server communication
"""

import crous
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class OperationType(Enum):
    """Types of operations."""
    AUTH = "auth"
    QUERY = "query"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    GET_INFO = "get_info"


@dataclass
class APIRequest:
    """Standard API request format."""
    operation: str  # auth, query, insert, update, delete, get_info
    session_id: Optional[str] = None
    database: Optional[str] = None
    collection: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    def to_crous(self) -> bytes:
        """Convert to Crous wire format."""
        payload = {
            "operation": self.operation,
        }
        if self.session_id:
            payload["session_id"] = self.session_id
        if self.database:
            payload["database"] = self.database
        if self.collection:
            payload["collection"] = self.collection
        if self.data:
            payload["data"] = self.data
        
        return crous.dumps(payload)


@dataclass
class APIResponse:
    """Standard API response format."""
    status: str  # "success" or "error"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: Optional[str] = None
    
    @staticmethod
    def from_crous(data: bytes) -> "APIResponse":
        """Parse Crous response."""
        try:
            # Remove trailing newline if present (added by server for line-based protocol)
            if data.endswith(b"\n"):
                data = data[:-1]
            obj = crous.loads(data)
            return APIResponse(
                status=obj.get("status", "error"),
                data=obj.get("data"),
                error=obj.get("error"),
                session_id=obj.get("session_id"),
            )
        except Exception as e:
            return APIResponse(status="error", error=f"Invalid Crous response: {str(e)}")
    
    def to_crous(self) -> bytes:
        """Convert to Crous wire format."""
        payload = {"status": self.status}
        if self.data:
            payload["data"] = self.data
        if self.error:
            payload["error"] = self.error
        if self.session_id:
            payload["session_id"] = self.session_id
        
        return crous.dumps(payload)


# Auth operations
class AuthRequest(APIRequest):
    """Authentication request."""
    
    @staticmethod
    def login(username: str, password: str) -> "AuthRequest":
        """Create login request."""
        return AuthRequest(
            operation="auth",
            data={"action": "login", "username": username, "password": password}
        )
    
    @staticmethod
    def logout(session_id: str) -> "AuthRequest":
        """Create logout request."""
        return AuthRequest(
            operation="auth",
            session_id=session_id,
            data={"action": "logout"}
        )
    
    @staticmethod
    def get_storage_info(session_id: str) -> "AuthRequest":
        """Get storage information."""
        return AuthRequest(
            operation="get_info",
            session_id=session_id,
            data={"info_type": "storage"}
        )


# CRUD operations
class CRUDRequest(APIRequest):
    """CRUD operations."""
    
    @staticmethod
    def insert(session_id: str, database: str, collection: str, document: Dict) -> "CRUDRequest":
        """Insert document."""
        return CRUDRequest(
            operation="insert",
            session_id=session_id,
            database=database,
            collection=collection,
            data={"document": document}
        )
    
    @staticmethod
    def find(session_id: str, database: str, collection: str, query: Dict = None, 
             projection: Dict = None, sort: List = None, skip: int = 0, 
             limit: int = 0, hint: str = None) -> "CRUDRequest":
        """Find documents with advanced options."""
        return CRUDRequest(
            operation="query",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "query": query or {},
                "projection": projection,
                "sort": sort,
                "skip": skip,
                "limit": limit,
                "hint": hint
            }
        )
    
    @staticmethod
    def update(session_id: str, database: str, collection: str, query: Dict, update: Dict, 
               upsert: bool = False, multi: bool = False) -> "CRUDRequest":
        """Update document(s) with advanced options."""
        return CRUDRequest(
            operation="update",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "query": query,
                "update": update,
                "upsert": upsert,
                "multi": multi
            }
        )
    
    @staticmethod
    def delete(session_id: str, database: str, collection: str, query: Dict, multi: bool = False) -> "CRUDRequest":
        """Delete document(s) with advanced options."""
        return CRUDRequest(
            operation="delete",
            session_id=session_id,
            database=database,
            collection=collection,
            data={"query": query, "multi": multi}
        )


# Information operations
class InfoRequest(APIRequest):
    """Information query operations."""
    
    @staticmethod
    def storage_info(session_id: str) -> "InfoRequest":
        """Get storage info."""
        return InfoRequest(
            operation="get_info",
            session_id=session_id,
            data={"info_type": "storage"}
        )
    
    @staticmethod
    def metrics(session_id: str) -> "InfoRequest":
        """Get server metrics."""
        return InfoRequest(
            operation="get_info",
            session_id=session_id,
            data={"info_type": "metrics"}
        )
    
    @staticmethod
    def databases(session_id: str) -> "InfoRequest":
        """Get databases list."""
        return InfoRequest(
            operation="get_info",
            session_id=session_id,
            data={"info_type": "databases"}
        )
    
    @staticmethod
    def collections(session_id: str, database: str) -> "InfoRequest":
        """Get collections in database."""
        return InfoRequest(
            operation="get_info",
            session_id=session_id,
            database=database,
            data={"info_type": "collections"}
        )


# Batch operations
class BatchRequest(APIRequest):
    """Batch/bulk operations."""
    
    @staticmethod
    def bulk_write(session_id: str, database: str, collection: str, 
                   operations: list, ordered: bool = True, atomic: bool = False) -> "BatchRequest":
        """Perform bulk write operations with optional atomic execution."""
        return BatchRequest(
            operation="bulk",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "type": "bulk_write",
                "operations": operations,
                "ordered": ordered,
                "atomic": atomic
            }
        )
    
    @staticmethod
    def bulk_write_atomic(session_id: str, database: str, collection: str, 
                         operations: list, ordered: bool = True) -> "BatchRequest":
        """Perform atomic bulk write operations (all or nothing)."""
        return BatchRequest(
            operation="bulk",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "type": "bulk_write",
                "operations": operations,
                "ordered": ordered,
                "atomic": True
            }
        )
    
    @staticmethod
    def transaction(session_id: str, operations: list, 
                    isolation_level: str = "SERIALIZABLE") -> "BatchRequest":
        """
        Perform multi-collection transactional operations.
        
        Args:
            session_id: Session ID
            operations: List of operations across multiple collections:
                [
                    {
                        "database": "db_name",
                        "collection": "col_name",
                        "action": "insert|update|delete",
                        "document": {...},  # for insert
                        "query": {...},     # for update/delete
                        "update": {...}     # for update
                    },
                    ...
                ]
            isolation_level: "READ_UNCOMMITTED", "READ_COMMITTED", "REPEATABLE_READ", "SERIALIZABLE"
        """
        return BatchRequest(
            operation="bulk",
            session_id=session_id,
            data={
                "type": "transaction",
                "operations": operations,
                "isolation_level": isolation_level
            }
        )


# Index management operations
class IndexRequest(APIRequest):
    """Index management operations."""
    
    @staticmethod
    def create_index(session_id: str, database: str, collection: str,
                    field: str, index_type: str = "standard",
                    unique: bool = False, sparse: bool = False,
                    ttl_seconds: int = None) -> "IndexRequest":
        """Create an index."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "create",
                "field": field,
                "type": index_type,
                "unique": unique,
                "sparse": sparse,
                "ttl_seconds": ttl_seconds,
            }
        )
    
    @staticmethod
    def create_compound_index(session_id: str, database: str, collection: str,
                             fields: list) -> "IndexRequest":
        """Create a compound index."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "create_compound",
                "fields": fields,
            }
        )
    
    @staticmethod
    def drop_index(session_id: str, database: str, collection: str,
                  index_name: str) -> "IndexRequest":
        """Drop an index."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "drop",
                "index_name": index_name,
            }
        )
    
    @staticmethod
    def drop_indexes_on_field(session_id: str, database: str, collection: str,
                             field: str) -> "IndexRequest":
        """Drop all indexes on a field."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "drop_field",
                "field": field,
            }
        )
    
    @staticmethod
    def drop_all_indexes(session_id: str, database: str, collection: str) -> "IndexRequest":
        """Drop all indexes in a collection."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "drop_all",
            }
        )
    
    @staticmethod
    def list_indexes(session_id: str, database: str, collection: str) -> "IndexRequest":
        """List all indexes."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "list",
            }
        )
    
    @staticmethod
    def get_index_stats(session_id: str, database: str, collection: str,
                       index_name: str) -> "IndexRequest":
        """Get index statistics."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "stats",
                "index_name": index_name,
            }
        )
    
    @staticmethod
    def rebuild_index(session_id: str, database: str, collection: str,
                     index_name: str) -> "IndexRequest":
        """Rebuild an index."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "rebuild",
                "index_name": index_name,
            }
        )
    
    @staticmethod
    def rebuild_all_indexes(session_id: str, database: str, collection: str) -> "IndexRequest":
        """Rebuild all indexes."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "rebuild_all",
            }
        )
    
    @staticmethod
    def analyze_indexes(session_id: str, database: str, collection: str) -> "IndexRequest":
        """Analyze indexes."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "analyze",
            }
        )
    
    @staticmethod
    def cleanup_ttl(session_id: str, database: str, collection: str) -> "IndexRequest":
        """Cleanup TTL indexes."""
        return IndexRequest(
            operation="index",
            session_id=session_id,
            database=database,
            collection=collection,
            data={
                "action": "cleanup_ttl",
            }
        )


# Management operations
class ManagementRequest(APIRequest):
    """Database and Collection management operations."""

    @staticmethod
    def drop_database(session_id: str, database: str) -> "ManagementRequest":
        """Drop a database."""
        return ManagementRequest(
            operation="drop_database", # Mapped to handler command
            session_id=session_id,
            data={
                "database": database
            }
        )

    @staticmethod
    def rename_database(session_id: str, old_name: str, new_name: str) -> "ManagementRequest":
        """Rename a database."""
        return ManagementRequest(
            operation="rename_database",
            session_id=session_id,
            data={
                "old_name": old_name,
                "new_name": new_name
            }
        )

    @staticmethod
    def drop_collection(session_id: str, database: str, collection: str) -> "ManagementRequest":
        """Drop a collection."""
        return ManagementRequest(
            operation="drop_collection",
            session_id=session_id,
            database=database,
            data={
                "collection": collection
            }
        )

    @staticmethod
    def rename_collection(session_id: str, database: str, old_name: str, new_name: str) -> "ManagementRequest":
        """Rename a collection."""
        return ManagementRequest(
            operation="rename_collection",
            session_id=session_id,
            database=database,
            collection=old_name,
            data={
                "new_name": new_name
            }
        )


# Transaction builder for convenient transaction construction
class TransactionBuilder:
    """
    Helper class to build multi-collection transactions.
    
    Example:
        txn = TransactionBuilder("user_123")
        txn.insert("mydb", "users", {"name": "Alice"})
        txn.insert("mydb", "profiles", {"user_id": "...", "bio": "..."})
        txn.update("mydb", "users", {"_id": "..."}, {"status": "active"})
        request = txn.build(isolation_level="SERIALIZABLE")
    """
    
    def __init__(self, session_id: str):
        """Initialize transaction builder."""
        self.session_id = session_id
        self.operations = []
    
    def insert(self, database: str, collection: str, document: Dict[str, Any]) -> "TransactionBuilder":
        """Add insert operation."""
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "insert",
            "document": document
        })
        return self
    
    def update(self, database: str, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> "TransactionBuilder":
        """Add update operation."""
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "update",
            "query": query,
            "update": update
        })
        return self
    
    def delete(self, database: str, collection: str, query: Dict[str, Any]) -> "TransactionBuilder":
        """Add delete operation."""
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "delete",
            "query": query
        })
        return self
    
    def add_operation(self, database: str, collection: str, action: str, **kwargs) -> "TransactionBuilder":
        """
        Add custom operation.
        
        Args:
            database: Database name
            collection: Collection name
            action: "insert", "update", or "delete"
            **kwargs: Additional operation data (document, query, update)
        """
        op = {
            "database": database,
            "collection": collection,
            "action": action
        }
        op.update(kwargs)
        self.operations.append(op)
        return self
    
    def build(self, isolation_level: str = "SERIALIZABLE") -> BatchRequest:
        """
        Build the transaction request.
        
        Args:
            isolation_level: "READ_UNCOMMITTED", "READ_COMMITTED", "REPEATABLE_READ", "SERIALIZABLE"
        
        Returns:
            BatchRequest ready to send to server
        """
        return BatchRequest.transaction(
            self.session_id,
            self.operations,
            isolation_level=isolation_level
        )
    
    def clear(self) -> "TransactionBuilder":
        """Clear all operations."""
        self.operations = []
        return self
    
    def count(self) -> int:
        """Get number of operations in transaction."""
        return len(self.operations)
    
    def __len__(self) -> int:
        """Allow len(builder) to get operation count."""
        return len(self.operations)
