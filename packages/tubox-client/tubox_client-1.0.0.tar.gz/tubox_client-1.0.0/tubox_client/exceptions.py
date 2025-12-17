"""Exception classes for Tubox."""


class TuboxException(Exception):
    """Base exception for all Tubox errors."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class AuthenticationError(TuboxException):
    """Raised when authentication fails."""

    def __init__(self, message: str):
        super().__init__(message, code="AUTHENTICATION_FAILED")


class AuthenticationFailedError(AuthenticationError):
    """Alias for AuthenticationError."""

    pass


class UnauthorizedError(TuboxException):
    """Raised when user lacks authorization for operation."""

    def __init__(self, message: str):
        super().__init__(message, code="UNAUTHORIZED")


class QuotaExceededError(TuboxException):
    """Raised when storage or operation quota exceeded."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="QUOTA_EXCEEDED", details=details)


class QuotaExceededException(QuotaExceededError):
    """Alias for QuotaExceededError."""

    pass


class RateLimitExceededError(TuboxException):
    """Raised when rate limit exceeded."""

    def __init__(self, message: str):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED")


class NotFoundError(TuboxException):
    """Raised when resource not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} not found: {resource_id}"
        code = f"{resource_type.upper()}_NOT_FOUND"
        super().__init__(message, code=code)


class DocumentNotFoundError(NotFoundError):
    """Raised when document not found."""

    def __init__(self, doc_id: str):
        super().__init__("document", doc_id)


class CollectionNotFoundError(NotFoundError):
    """Raised when collection not found."""

    def __init__(self, col_name: str):
        super().__init__("collection", col_name)


class DatabaseNotFoundError(NotFoundError):
    """Raised when database not found."""

    def __init__(self, db_name: str):
        super().__init__("database", db_name)


class StorageError(TuboxException):
    """Raised when storage/persistence operation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="STORAGE_ERROR")


class SnapshotLoadError(StorageError):
    """Raised when snapshot load fails."""

    def __init__(self, path: str, reason: str = None):
        message = f"Failed to load snapshot: {path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class OplogCorruptionError(StorageError):
    """Raised when oplog is corrupted."""

    def __init__(self, path: str):
        super().__init__(f"Oplog corruption detected: {path}")


class InvalidQueryError(TuboxException):
    """Raised when query is invalid."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_QUERY")


class QueryTimeoutError(TuboxException):
    """Raised when query exceeds timeout."""

    def __init__(self, timeout_seconds: float):
        message = f"Query timeout after {timeout_seconds} seconds"
        super().__init__(message, code="QUERY_TIMEOUT")


class TooManyDocumentsError(TuboxException):
    """Raised when result set too large."""

    def __init__(self, doc_count: int, limit: int):
        message = f"Too many documents returned ({doc_count}), limit: {limit}"
        super().__init__(message, code="TOO_MANY_DOCUMENTS")


class InvalidSessionError(TuboxException):
    """Raised when session is invalid or expired."""

    def __init__(self, message: str = "Invalid session"):
        super().__init__(message, code="INVALID_SESSION")


class DatabaseLimitError(TuboxException):
    """Raised when database limit exceeded."""

    def __init__(self, limit: int):
        message = f"Database limit exceeded: {limit}"
        super().__init__(message, code="DATABASE_LIMIT_EXCEEDED")


class CollectionLimitError(TuboxException):
    """Raised when collection limit exceeded."""

    def __init__(self, limit: int):
        message = f"Collection limit exceeded: {limit}"
        super().__init__(message, code="COLLECTION_LIMIT_EXCEEDED")
