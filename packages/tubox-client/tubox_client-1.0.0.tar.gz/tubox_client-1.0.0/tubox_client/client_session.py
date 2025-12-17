"""
MongoDB-style client sessions for transaction management.

Provides ClientSession for starting transactions, managing session state,
and handling transaction lifecycle with automatic cleanup.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Dict, List
from enum import Enum
from datetime import datetime, timedelta, timezone
import uuid
from contextlib import asynccontextmanager

from .transaction_errors import (
    TransactionError,
    SessionError,
    SessionExpiredError,
    SessionStateError,
)

if TYPE_CHECKING:
    from .api_client import TuboxAPIClient, TuboxAPICollection


class SessionState(Enum):
    """Enumeration of session states."""
    ACTIVE = "active"
    TRANSACTION_IN_PROGRESS = "transaction_in_progress"
    CLOSED = "closed"


class ClientSession:
    """
    MongoDB-style client session for managing transactions.
    
    A session encapsulates a sequence of transaction operations on the server.
    Sessions are used to start transactions and manage their lifecycle.
    
    Usage:
        async with api_client.start_session() as session:
            async with session.start_transaction() as transaction:
                await collection.insert_one(doc, session=session)
                # Auto-commits on exit if no errors
    
    Attributes:
        session_id: Unique session identifier
        api_client: Reference to client managing this session
        created_at: Session creation timestamp
        last_activity_at: Last operation timestamp
        timeout_seconds: Session inactivity timeout
    """
    
    def __init__(
        self,
        api_client: TuboxAPIClient,
        session_id: Optional[str] = None,
        timeout_seconds: int = 3600,
        default_isolation_level: str = "READ_COMMITTED"
    ):
        """
        Initialize a new session.
        
        Args:
            api_client: Client managing this session
            session_id: Optional custom session ID (auto-generated if omitted)
            timeout_seconds: Inactivity timeout (default 1 hour)
            default_isolation_level: Default isolation for transactions started in this session
        """
        self.api_client = api_client
        self.session_id = session_id or str(uuid.uuid4())
        self.state = SessionState.ACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.last_activity_at = self.created_at
        self.timeout_seconds = timeout_seconds
        self.default_isolation_level = default_isolation_level
        
        # Track active transaction
        self._active_transaction: Optional[ClientTransaction] = None
    
    @property
    def is_active(self) -> bool:
        """Whether session is active (not closed)."""
        return self.state != SessionState.CLOSED
    
    @property
    def in_transaction(self) -> bool:
        """Whether transaction is currently active."""
        return self.state == SessionState.TRANSACTION_IN_PROGRESS
    
    @property
    def is_expired(self) -> bool:
        """Whether session has exceeded inactivity timeout."""
        elapsed = (datetime.now(timezone.utc) - self.last_activity_at).total_seconds()
        return elapsed > self.timeout_seconds
    
    def _check_active(self) -> None:
        """Verify session is active, raise SessionExpiredError if not."""
        if self.state == SessionState.CLOSED:
            raise SessionExpiredError(
                f"Session {self.session_id} has been closed"
            )
        if self.is_expired:
            self.state = SessionState.CLOSED
            raise SessionExpiredError(
                f"Session {self.session_id} has expired due to inactivity"
            )
    
    def _update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.now(timezone.utc)
    
    def start_transaction(
        self,
        isolation_level: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> ClientTransaction:
        """
        Start a new transaction in this session.
        
        Args:
            isolation_level: Isolation level (uses session default if None)
            timeout_seconds: Transaction timeout (uses API client default if None)
        
        Returns:
            ClientTransaction configured for this session
        
        Raises:
            SessionExpiredError: If session has been closed or expired
            SessionStateError: If transaction already active in session
        """
        self._check_active()
        
        if self.in_transaction:
            raise SessionStateError(
                f"Transaction already active in session {self.session_id}"
            )
        
        self.state = SessionState.TRANSACTION_IN_PROGRESS
        
        transaction = ClientTransaction(
            api_client=self.api_client,
            session=self,
            isolation_level=isolation_level or self.default_isolation_level,
            timeout_seconds=timeout_seconds
        )
        self._active_transaction = transaction
        self._update_activity()
        
        return transaction
    
    async def commit_transaction(self) -> Dict[str, Any]:
        """
        Commit the active transaction.
        
        Returns:
            Commit result from server
        
        Raises:
            SessionStateError: If no transaction is active
            SessionExpiredError: If session has been closed or expired
        """
        self._check_active()
        
        if not self.in_transaction or not self._active_transaction:
            raise SessionStateError(
                f"No transaction active in session {self.session_id}"
            )
        
        try:
            result = await self._active_transaction.commit()
            return result
        finally:
            self.state = SessionState.ACTIVE
            self._active_transaction = None
            self._update_activity()
    
    async def abort_transaction(self) -> None:
        """
        Abort the active transaction.
        
        Raises:
            SessionStateError: If no transaction is active
            SessionExpiredError: If session has been closed or expired
        """
        self._check_active()
        
        if not self.in_transaction or not self._active_transaction:
            raise SessionStateError(
                f"No transaction active in session {self.session_id}"
            )
        
        try:
            await self._active_transaction.abort()
        finally:
            self.state = SessionState.ACTIVE
            self._active_transaction = None
            self._update_activity()
    
    async def close(self) -> None:
        """
        Close the session.
        
        Aborts any active transaction before closing.
        Safe to call multiple times - idempotent.
        """
        if self.state == SessionState.CLOSED:
            return
        
        if self.in_transaction and self._active_transaction:
            try:
                await self._active_transaction.abort()
            except Exception:
                pass  # Best effort abort
        
        self.state = SessionState.CLOSED
        self._update_activity()
    
    async def __aenter__(self) -> ClientSession:
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - closes session."""
        await self.close()
        return False


class ClientTransaction:
    """
    MongoDB-style transaction object for executing multiple operations.
    
    Transactions group multiple operations into an all-or-nothing unit.
    Operations must be explicitly committed or will abort on context exit.
    
    Usage:
        transaction = session.start_transaction()
        await collection.insert_one(doc, session=session)
        await collection.update_one(..., session=session)
        await transaction.commit()  # or await transaction.abort()
    
    Context manager form (preferred):
        async with session.start_transaction() as transaction:
            await collection.insert_one(doc, session=session)
            # Auto-commits on successful exit
    
    Attributes:
        session: Parent session
        transaction_id: Unique transaction identifier
        isolation_level: Isolation level for this transaction
        timeout_seconds: Maximum execution time
        state: Current transaction state
    """
    
    class State(Enum):
        """Transaction state enumeration."""
        STARTED = "started"
        COMMITTED = "committed"
        ABORTED = "aborted"
    
    def __init__(
        self,
        api_client: TuboxAPIClient,
        session: ClientSession,
        isolation_level: str = "READ_COMMITTED",
        timeout_seconds: Optional[int] = None
    ):
        """
        Initialize a new transaction.
        
        Args:
            api_client: Client managing operations
            session: Parent session
            isolation_level: ACID isolation level
            timeout_seconds: Maximum transaction duration
        """
        self.api_client = api_client
        self.session = session
        self.transaction_id = str(uuid.uuid4())
        self.isolation_level = isolation_level
        self.timeout_seconds = timeout_seconds
        self.state = self.State.STARTED
        self.started_at = datetime.now(timezone.utc)
        
        # Operations buffer (for future batching)
        self._operations: List[Dict[str, Any]] = []
    
    @property
    def is_active(self) -> bool:
        """Whether transaction can accept new operations."""
        return self.state == self.State.STARTED
    
    @property
    def is_committed(self) -> bool:
        """Whether transaction has been committed."""
        return self.state == self.State.COMMITTED
    
    @property
    def is_aborted(self) -> bool:
        """Whether transaction has been aborted."""
        return self.state == self.State.ABORTED
    
    def _check_active(self) -> None:
        """Verify transaction is active, raise error if not."""
        if self.state == self.State.COMMITTED:
            raise TransactionError(
                f"Transaction {self.transaction_id} has been committed"
            )
        if self.state == self.State.ABORTED:
            raise TransactionError(
                f"Transaction {self.transaction_id} has been aborted"
            )
    
    def add_operation(
        self,
        operation_type: str,
        collection: str,
        **kwargs
    ) -> None:
        """
        Add operation to transaction.
        
        Args:
            operation_type: Type of operation (insert, update, delete, etc.)
            collection: Collection name
            **kwargs: Operation-specific parameters
        """
        self._check_active()
        
        self._operations.append({
            "type": operation_type,
            "collection": collection,
            **kwargs
        })
    
    async def commit(self) -> Dict[str, Any]:
        """
        Commit the transaction.
        
        Returns:
            Commit result from server
        
        Raises:
            TransactionError: If transaction not active or commit fails
        """
        self._check_active()
        
        try:
            # Submit transaction for commit
            result = await self.api_client._commit_transaction(
                transaction_id=self.transaction_id,
                session_id=self.session.session_id,
                isolation_level=self.isolation_level
            )
            self.state = self.State.COMMITTED
            return result
        except Exception as e:
            self.state = self.State.ABORTED
            raise
    
    async def abort(self) -> None:
        """
        Abort the transaction.
        
        Rolls back any operations that were part of transaction.
        Safe to call multiple times - idempotent.
        """
        if self.state != self.State.STARTED:
            return  # Already terminal state
        
        try:
            await self.api_client._rollback_transaction(
                transaction_id=self.transaction_id,
                session_id=self.session.session_id
            )
        except Exception:
            pass  # Best effort abort
        finally:
            self.state = self.State.ABORTED
    
    async def close(self) -> None:
        """
        Close transaction (abort if still active).
        
        Safe to call multiple times - idempotent.
        """
        if self.is_active:
            await self.abort()
    
    async def __aenter__(self) -> ClientTransaction:
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Async context manager exit.
        
        Auto-commits on success, auto-aborts on exception.
        Only commits/aborts if transaction is still active (idempotent).
        """
        try:
            # Only attempt commit/abort if transaction is still active
            if self.is_active:
                if exc_type is not None:
                    # Exception occurred - abort transaction
                    await self.abort()
                    return False  # Re-raise exception
                else:
                    # No exception - commit transaction
                    try:
                        await self.commit()
                    except Exception:
                        await self.abort()
                        raise
        finally:
            # Reset session state back to ACTIVE after transaction completes
            if self.session and self.session.state == SessionState.TRANSACTION_IN_PROGRESS:
                self.session.state = SessionState.ACTIVE
                self.session._active_transaction = None
        return False
