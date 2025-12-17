"""
Transaction error types and exception hierarchy.

Provides detailed error categories for transaction operations,
allowing applications to handle different failure modes appropriately.
"""

from typing import Dict, Any, Optional


class TransactionError(Exception):
    """
    Base exception for all transaction-related errors.
    
    Attributes:
        message: Error description
        code: Error code for programmatic handling
        details: Additional error context
        retryable: Whether operation can be safely retried
    """
    
    retryable = False
    
    def __init__(
        self,
        message: str,
        code: str = None,
        details: Dict[str, Any] = None,
        retryable: bool = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        if retryable is not None:
            self.retryable = retryable
        super().__init__(message)


class TransactionStateError(TransactionError):
    """
    Operation is invalid for current transaction state.
    
    Examples:
    - Calling commit() on already-committed transaction
    - Calling insert_one() on aborted transaction
    - Calling abort() on inactive transaction
    
    Not retryable - indicates programming error.
    """
    
    retryable = False


class TransactionConflictError(TransactionError):
    """
    Write conflict or deadlock detected during transaction.
    
    Typically occurs when:
    - Multiple transactions try to update same document
    - Deadlock cycle detected
    - Document version conflict
    
    Retryable - application should retry transaction.
    """
    
    retryable = True


class TransactionTimeoutError(TransactionError):
    """
    Transaction exceeded configured timeout.
    
    Occurs when:
    - Transaction takes longer than timeout_seconds
    - Network round-trip exceeds timeout
    - Server-side operation took too long
    
    Not automatically retryable - indicates data consistency issue
    or very slow operation. Manual retry with increased timeout possible.
    """
    
    retryable = False


class TransactionNetworkError(TransactionError):
    """
    Network failure during transaction operation.
    
    Occurs when:
    - Connection lost during operation
    - Timeout waiting for server response
    - Network unreachable
    
    Retryable - depends on operation idempotency and transaction state.
    Automatic retry may happen transparently.
    """
    
    retryable = True


class TransactionAbortedError(TransactionError):
    """
    Transaction was explicitly aborted (rolled back).
    
    Indicates:
    - Explicit abort() call by application
    - Server-side abort due to constraint violation
    - Automatic abort due to error in transaction block
    
    Not a failure per se - indicates deliberate abort.
    Not retryable - start new transaction if needed.
    """
    
    retryable = False


class SessionError(Exception):
    """Base exception for session-related errors."""
    pass


class SessionExpiredError(SessionError):
    """
    Session has expired or been closed.
    
    Occurs when:
    - Session lifetime exceeded
    - Explicit end_session() called
    - Server closed session
    
    Cannot be used further - must start new session.
    """
    pass


class SessionStateError(SessionError):
    """
    Operation is invalid for current session state.
    
    Examples:
    - Starting transaction on closed session
    - Ending already-closed session
    """
    pass


# Error code constants
ERROR_CODES = {
    "TRANSACTION_STATE_ERROR": "TXSTATE001",
    "TRANSACTION_CONFLICT": "TXCONF001",
    "TRANSACTION_TIMEOUT": "TXTIMEOUT001",
    "TRANSACTION_NETWORK": "TXNET001",
    "TRANSACTION_ABORTED": "TXABORT001",
    "SESSION_EXPIRED": "SESSEXP001",
    "SESSION_STATE_ERROR": "SESSSTATE001",
}
