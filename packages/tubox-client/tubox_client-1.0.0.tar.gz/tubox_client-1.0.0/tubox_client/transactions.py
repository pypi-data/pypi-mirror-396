"""
Client-side transaction support for Tubox.

Provides both MongoDB-style (session-based) and SQL-like transaction APIs.

Features:
- MongoDB-style session-based transactions (primary)
- SQL-like explicit commit/rollback (legacy)
- Fluent transaction builder pattern (legacy)
- Isolation level control (4 levels)
- Automatic retry with exponential backoff
- Multi-collection transaction support

Modern MongoDB-Style Usage:
    async with api_client.start_session() as session:
        async with session.start_transaction() as txn:
            await collection.insert_one(doc, session=session)
            await collection.update_one(..., session=session)
            # Auto-commits on successful exit

Legacy SQL-Like Usage:
    async with collection.transaction_manager() as txn:
        try:
            txn.add_insert("db", "col", {...})
            txn.add_update("db", "col", {...}, {...})
            await txn.commit()
        except Exception:
            await txn.rollback()
            raise

Legacy Fluent API Usage:
    async def transfer(txn):
        txn.add_insert("db", "col1", {...})
        txn.add_update("db", "col2", {...}, {...})
    
    result = await client.execute_transaction(transfer)
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional, Callable, Coroutine
from enum import Enum

# Import new MongoDB-style classes
from .client_session import ClientSession, ClientTransaction as MongoDBClientTransaction, SessionState
from .transaction_errors import TransactionError, SessionError

logger = logging.getLogger("tubox.client.transactions")


class IsolationLevel(Enum):
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "READ_UNCOMMITTED"
    READ_COMMITTED = "READ_COMMITTED"
    REPEATABLE_READ = "REPEATABLE_READ"
    SERIALIZABLE = "SERIALIZABLE"


class TransactionState(Enum):
    """Transaction lifecycle states."""
    PENDING = "pending"          # Operations being added
    SUBMITTED = "submitted"      # Submitted to server, awaiting commit/rollback
    COMMITTED = "committed"      # Successfully committed
    ROLLED_BACK = "rolled_back"  # Rolled back
    FAILED = "failed"            # Error occurred


# =============================================================================
# Explicit Commit/Rollback Transaction (SQL-like)
# =============================================================================

class ClientTransaction:
    """
    Client-side transaction with explicit commit/rollback (SQL-like).
    
    Supports SQL transaction semantics:
        async with txn_context.begin() as txn:
            try:
                txn.add_insert(...)
                txn.add_update(...)
                await txn.commit()
            except Exception:
                await txn.rollback()
                raise
    
    Or with automatic commit on success:
        async with txn_manager.transaction() as txn:
            txn.add_insert(...)
            txn.add_update(...)
            # Auto-commits on context exit if no error
    """
    
    def __init__(self, 
                 session_id: str,
                 isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE,
                 transaction_id: Optional[str] = None,
                 api_client: Optional[Any] = None):
        """
        Initialize transaction.
        
        Args:
            session_id: Client session ID
            isolation_level: Isolation level for transaction
            transaction_id: Unique transaction ID (generated if not provided)
            api_client: API client for commit/rollback operations
        """
        self.session_id = session_id
        self.isolation_level = isolation_level
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.api_client = api_client
        self.operations: List[Dict[str, Any]] = []
        self.state = TransactionState.PENDING
        self.is_built = False
        self._lock = asyncio.Lock()
        self._submitted_result: Optional[Dict[str, Any]] = None
    
    def add_insert(self, database: str, collection: str, document: Dict[str, Any]) -> "ClientTransaction":
        """Add insert operation to transaction."""
        if self.is_built:
            raise RuntimeError("Cannot add operations to built transaction")
        if self.state != TransactionState.PENDING:
            raise RuntimeError(f"Cannot add operations to {self.state.value} transaction")
        
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "insert",
            "document": document
        })
        return self
    
    def add_update(self, database: str, collection: str, query: Dict, update: Dict) -> "ClientTransaction":
        """Add update operation to transaction."""
        if self.is_built:
            raise RuntimeError("Cannot add operations to built transaction")
        if self.state != TransactionState.PENDING:
            raise RuntimeError(f"Cannot add operations to {self.state.value} transaction")
        
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "update",
            "query": query,
            "update": update
        })
        return self
    
    def add_delete(self, database: str, collection: str, query: Dict) -> "ClientTransaction":
        """Add delete operation to transaction."""
        if self.is_built:
            raise RuntimeError("Cannot add operations to built transaction")
        if self.state != TransactionState.PENDING:
            raise RuntimeError(f"Cannot add operations to {self.state.value} transaction")
        
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "delete",
            "query": query
        })
        return self
    
    def add_operation(self, database: str, collection: str, action: str, **kwargs) -> "ClientTransaction":
        """
        Add custom operation to transaction.
        
        Args:
            database: Database name
            collection: Collection name
            action: "insert", "update", or "delete"
            **kwargs: Additional operation data
        """
        if self.state != TransactionState.PENDING:
            raise RuntimeError(f"Cannot add operations to {self.state.value} transaction")
        
        op = {
            "database": database,
            "collection": collection,
            "action": action
        }
        op.update(kwargs)
        self.operations.append(op)
        return self
    
    def with_isolation_level(self, level: IsolationLevel) -> "ClientTransaction":
        """Set isolation level for transaction."""
        if isinstance(level, str):
            level = IsolationLevel[level]
        self.isolation_level = level
        return self
    
    async def submit(self) -> Dict[str, Any]:
        """
        Submit transaction to server for execution (prepare phase).
        
        Returns:
            Result from server submission
        """
        async with self._lock:
            if self.state != TransactionState.PENDING:
                raise RuntimeError(f"Cannot submit {self.state.value} transaction")
            
            if not self.api_client:
                raise RuntimeError("No API client configured")
            
            try:
                result = await self.api_client._execute_transaction(
                    self.operations,
                    isolation_level=self.isolation_level.value,
                    transaction_id=self.transaction_id
                )
                
                self._submitted_result = result
                self.state = TransactionState.SUBMITTED
                logger.info(f"Transaction {self.transaction_id} submitted")
                return result
            
            except Exception as e:
                self.state = TransactionState.FAILED
                logger.error(f"Transaction {self.transaction_id} submission failed: {e}")
                raise
    
    async def commit(self) -> Dict[str, Any]:
        """
        Commit transaction (explicit commit phase).
        
        Returns:
            Commit result from server
        """
        async with self._lock:
            if self.state == TransactionState.PENDING:
                await self.submit()
            
            if self.state != TransactionState.SUBMITTED:
                raise RuntimeError(f"Cannot commit {self.state.value} transaction")
            
            if not self.api_client:
                raise RuntimeError("No API client configured")
            
            try:
                result = await self.api_client._commit_transaction(self.transaction_id)
                self.state = TransactionState.COMMITTED
                logger.info(f"Transaction {self.transaction_id} committed")
                return result
            
            except Exception as e:
                self.state = TransactionState.FAILED
                logger.error(f"Transaction {self.transaction_id} commit failed: {e}")
                raise
    
    async def rollback(self) -> Dict[str, Any]:
        """
        Rollback transaction (explicit rollback phase).
        
        Returns:
            Rollback result from server
        """
        async with self._lock:
            if self.state == TransactionState.COMMITTED:
                raise RuntimeError("Cannot rollback committed transaction")
            
            if self.state == TransactionState.ROLLED_BACK:
                logger.warning(f"Transaction {self.transaction_id} already rolled back")
                return {"transaction_id": self.transaction_id, "status": "rolled_back"}
            
            if not self.api_client:
                raise RuntimeError("No API client configured")
            
            try:
                if self.state in (TransactionState.SUBMITTED, TransactionState.FAILED):
                    result = await self.api_client._rollback_transaction(self.transaction_id)
                else:
                    result = {"transaction_id": self.transaction_id, "status": "rolled_back"}
                
                self.state = TransactionState.ROLLED_BACK
                logger.info(f"Transaction {self.transaction_id} rolled back")
                return result
            
            except Exception as e:
                logger.error(f"Transaction {self.transaction_id} rollback failed: {e}")
                raise
    
    # State query methods
    def get_state(self) -> str:
        """Get current transaction state."""
        return self.state.value
    
    def is_committed(self) -> bool:
        """Check if transaction is committed."""
        return self.state == TransactionState.COMMITTED
    
    def is_rolled_back(self) -> bool:
        """Check if transaction is rolled back."""
        return self.state == TransactionState.ROLLED_BACK
    
    def is_pending(self) -> bool:
        """Check if transaction is still pending."""
        return self.state == TransactionState.PENDING
    
    def is_failed(self) -> bool:
        """Check if transaction failed."""
        return self.state == TransactionState.FAILED
    
    def get_operation_count(self) -> int:
        """Get number of operations."""
        return len(self.operations)
    
    def clear(self) -> "ClientTransaction":
        """Clear all operations."""
        if self.is_built:
            raise RuntimeError("Cannot clear built transaction")
        if self.state != TransactionState.PENDING:
            raise RuntimeError("Cannot clear non-pending transaction")
        self.operations = []
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build transaction dict (legacy API)."""
        self.is_built = True
        return {
            "transaction_id": self.transaction_id,
            "operations": self.operations,
            "isolation_level": self.isolation_level.value,
            "state": self.state.value
        }
    
    # Context manager support (async)
    async def __aenter__(self) -> "ClientTransaction":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit with auto-rollback on error."""
        if exc_type is not None:
            try:
                await self.rollback()
            except Exception as e:
                logger.error(f"Rollback on error failed: {e}")
            return False
        
        # Auto-commit on success
        if self.state == TransactionState.PENDING:
            try:
                await self.submit()
                await self.commit()
            except Exception as e:
                logger.error(f"Implicit commit failed: {e}")
                try:
                    await self.rollback()
                except:
                    pass
                raise
        
        return False


# =============================================================================
# Transaction Manager (Collection-level)
# =============================================================================

class ClientTransactionManager:
    """
    Manages transactions for a collection.
    
    Provides SQL-like context manager interface:
    
        async with collection.transaction_manager() as txn:
            try:
                txn.add_insert(...)
                await txn.commit()
            except Exception:
                await txn.rollback()
                raise
    
    Or with automatic commit:
    
        async with collection.transaction_manager() as txn:
            txn.add_insert(...)
            # Auto-commits on success
    """
    
    def __init__(self, collection):
        """Initialize manager for collection."""
        self.collection = collection
        self.transaction: Optional[ClientTransaction] = None
    
    def create_transaction(
        self,
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
    ) -> ClientTransaction:
        """Create new transaction for collection."""
        api_client = getattr(self.collection, '_client', None)
        if not api_client:
            raise RuntimeError("Collection has no API client")
        
        session_id = getattr(api_client, 'session_id', None)
        if not session_id:
            raise RuntimeError("No active session")
        
        return ClientTransaction(
            session_id=session_id,
            isolation_level=isolation_level,
            api_client=api_client
        )
    
    async def __aenter__(self) -> ClientTransaction:
        """Context manager entry."""
        self.transaction = self.create_transaction()
        return self.transaction
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        if self.transaction is None:
            return False
        
        if exc_type is not None:
            try:
                await self.transaction.rollback()
            except Exception as e:
                logger.error(f"Rollback failed: {e}")
            return False
        
        # Auto-commit
        if self.transaction.state == TransactionState.PENDING:
            try:
                await self.transaction.submit()
                await self.transaction.commit()
            except Exception as e:
                logger.error(f"Implicit commit failed: {e}")
                try:
                    await self.transaction.rollback()
                except:
                    pass
                raise
        
        return False


# =============================================================================
# Transaction Context (API Client-level)
# =============================================================================

class TransactionContext:
    """
    Transaction context for explicit control.
    
    Usage:
        txn_ctx = TransactionContext(api_client)
        
        # Option 1: Explicit control
        txn = txn_ctx.begin()
        try:
            txn.add_insert(...)
            await txn.commit()
        except Exception:
            await txn.rollback()
            raise
        
        # Option 2: Context manager
        async with txn_ctx.begin() as txn:
            txn.add_insert(...)
            await txn.commit()
        
        # Option 3: Fluent executor
        async def executor(txn):
            txn.add_insert(...)
            txn.add_update(...)
        result = await txn_ctx.execute(executor)
    """
    
    def __init__(self, api_client):
        """Initialize context."""
        self.api_client = api_client
    
    def begin(
        self,
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
    ) -> ClientTransaction:
        """Begin new transaction with explicit control."""
        if not self.api_client.session_id:
            raise RuntimeError("No active session")
        
        return ClientTransaction(
            session_id=self.api_client.session_id,
            isolation_level=isolation_level,
            api_client=self.api_client
        )
    
    async def execute(
        self,
        executor: Callable[[ClientTransaction], Coroutine],
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE,
        max_retries: int = 1,
        backoff_sec: float = 0.1
    ) -> Dict[str, Any]:
        """
        Execute transaction with auto-commit and retry.
        
        Args:
            executor: Async function that builds transaction
            isolation_level: Isolation level
            max_retries: Retry attempts
            backoff_sec: Backoff seconds
            
        Returns:
            Commit result
        """
        last_error = None
        
        for attempt in range(max_retries):
            txn = self.begin(isolation_level)
            
            try:
                await executor(txn)
                await txn.submit()
                return await txn.commit()
            
            except Exception as e:
                last_error = e
                logger.warning(f"Transaction attempt {attempt + 1}/{max_retries} failed: {e}")
                
                try:
                    await txn.rollback()
                except:
                    pass
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_sec * (2 ** attempt))
                else:
                    logger.error(f"Transaction failed after {max_retries} attempts")
                    raise
        
        if last_error:
            raise last_error


# =============================================================================
# Fluent Transaction Builder
# =============================================================================

class TransactionBuilder:
    """
    Fluent builder for transactions (legacy fluent API).
    
    Example:
        builder = TransactionBuilder(session_id)
        builder.insert("db", "col", {...})
        builder.update("db", "col", {...}, {...})
        result = await client.execute_transaction(builder.build())
    """
    
    def __init__(self, session_id: str):
        """Initialize builder."""
        self.session_id = session_id
        self.operations: List[Dict[str, Any]] = []
        self.isolation_level = "SERIALIZABLE"
    
    def insert(self, database: str, collection: str, document: Dict[str, Any]) -> "TransactionBuilder":
        """Add insert operation."""
        self.operations.append({
            "database": database,
            "collection": collection,
            "action": "insert",
            "document": document
        })
        return self
    
    def update(
        self,
        database: str,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any]
    ) -> "TransactionBuilder":
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
        """Add custom operation."""
        op = {
            "database": database,
            "collection": collection,
            "action": action
        }
        op.update(kwargs)
        self.operations.append(op)
        return self
    
    def with_isolation_level(self, level: str) -> "TransactionBuilder":
        """Set isolation level."""
        self.isolation_level = level
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build transaction."""
        return {
            "operations": self.operations,
            "isolation_level": self.isolation_level
        }
    
    def clear(self) -> "TransactionBuilder":
        """Clear operations."""
        self.operations = []
        return self
    
    def count(self) -> int:
        """Get operation count."""
        return len(self.operations)


# Legacy API support (backward compatibility)
class ClientTransactionContext:
    """
    Legacy transaction context (backward compatibility).
    
    Use TransactionContext instead for new code.
    """
    
    def __init__(self, api_client):
        """Initialize context."""
        self.api_client = api_client
    
    async def execute_transaction(
        self,
        executor: Callable[[ClientTransaction], Coroutine],
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE,
        max_retries: int = 1,
        backoff_sec: float = 0.1,
    ) -> Any:
        """Execute transaction with retry (legacy)."""
        ctx = TransactionContext(self.api_client)
        return await ctx.execute(executor, isolation_level, max_retries, backoff_sec)
    
    async def execute_atomic(
        self,
        operations: List[Dict[str, Any]],
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE,
        max_retries: int = 1,
        backoff_sec: float = 0.1,
    ) -> Dict[str, Any]:
        """Execute atomic operations (legacy)."""
        async def executor(txn):
            for op in operations:
                txn.add_operation(**op)
        
        ctx = TransactionContext(self.api_client)
        return await ctx.execute(executor, isolation_level, max_retries, backoff_sec)
    
    async def execute_with_retry(
        self,
        executor: Callable[[ClientTransaction], Coroutine],
        max_retries: int = 3,
        backoff_sec: float = 0.1,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
    ) -> Any:
        """Execute with retry (legacy)."""
        ctx = TransactionContext(self.api_client)
        return await ctx.execute(executor, isolation_level, max_retries, backoff_sec)
    
    def create_transaction(
        self,
        isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
    ) -> ClientTransaction:
        """Create transaction (legacy)."""
        ctx = TransactionContext(self.api_client)
        return ctx.begin(isolation_level)
    
    async def bulk_write_atomic(
        self,
        database: str,
        collection: str,
        operations: List[Dict[str, Any]],
        ordered: bool = True,
    ) -> Dict[str, Any]:
        """Bulk write atomic (legacy)."""
        await self.api_client._check_auth()
        
        from tubox_client.api_protocol import BatchRequest
        
        request = BatchRequest.bulk_write(
            self.api_client.session_id,
            database,
            collection,
            operations,
            ordered=ordered,
            atomic=True
        )
        response = await self.api_client._execute_request(request)
        
        if response and response.status == "success":
            return response.data or {}
        
        raise Exception(f"Bulk write failed: {response.error if response else 'Unknown error'}")


# =============================================================================
# Public API - Re-exports of MongoDB-style classes
# =============================================================================

# Export new MongoDB-style classes
__all__ = [
    # New MongoDB-style API
    'ClientSession',
    'MongoDBClientTransaction',  # Renamed to avoid conflict
    'SessionState',
    
    # Legacy API (for backward compatibility)
    'ClientTransaction',
    'ClientTransactionManager',
    'TransactionContext',
    'ClientTransactionContext',
    'TransactionBuilder',
    'IsolationLevel',
    'TransactionState',
    
    # Error hierarchy
    'TransactionError',
    'SessionError',
]
