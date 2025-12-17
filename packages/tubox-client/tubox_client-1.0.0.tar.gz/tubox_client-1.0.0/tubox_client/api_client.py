"""
Tubox API Client - MongoDB-like driver for production use
Connects to Tubox server via API protocol (network-based)

Features:
- Connection pooling with automatic reuse
- Retry logic with exponential backoff
- Session management and authentication
- Comprehensive error handling and logging
- Metrics and monitoring
- Async and sync interfaces
- Scales to thousands of concurrent operations

Logging:
- DEBUG: Connection lifecycle, request/response details, pool operations
- INFO: Authentication, successful operations, pool metrics
- WARNING: Retries, timeouts, pool exhaustion
- ERROR: Connection failures, authentication failures, operation errors

Configuration:
- See tubox_client.config for production settings
"""

import asyncio
import crous
import logging
from typing import Dict, Any, Optional, List
import time
import uuid
from functools import wraps

from tubox_client.api_protocol import (
    APIRequest,
    APIResponse,
    AuthRequest,
    CRUDRequest,
    InfoRequest,
    BatchRequest,
    ManagementRequest,
)
from tubox_client.exceptions import (
    AuthenticationError, 
    UnauthorizedError,
    TuboxException,
    RateLimitExceededError
)
from tubox_client.transaction_errors import TransactionError

logger = logging.getLogger("tubox.client")
# Ensure logger has a handler in production
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class APIConnection:
    """
    Single network connection to Tubox server.
    
    Features:
    - Automatic reconnection
    - Request/response timeout
    - Metrics tracking
    - Health checking
    """
    
    def __init__(self, host: str, port: int, connection_id: str = None, 
                 connect_timeout: float = 10.0, request_timeout: float = 30.0):
        self.host = host
        self.port = port
        self.connection_id = connection_id or str(uuid.uuid4())[:8]
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.created_at = time.time()
        self.last_used = time.time()
        self._lock = asyncio.Lock()
        
        # Metrics
        self.metrics = {
            "requests_sent": 0,
            "requests_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "errors": 0,
            "reconnects": 0,
            "last_request_latency_ms": 0.0,
            "avg_latency_ms": 0.0,
        }
        self._latencies: List[float] = []
    
    async def connect(self, max_retries: int = 3) -> bool:
        """Establish connection to server with retries."""
        for attempt in range(max_retries):
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=self.connect_timeout
                )
                logger.debug(f"Connected [{self.connection_id}] to {self.host}:{self.port}")
                return True
            except asyncio.TimeoutError:
                logger.warning(f"Connection timeout [{self.connection_id}] attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
            except Exception as e:
                logger.error(f"Connection failed [{self.connection_id}] attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))
        
        logger.error(f"Failed to connect [{self.connection_id}] after {max_retries} attempts")
        return False
    
    async def send_request(self, request: APIRequest, max_retries: int = 2) -> Optional[APIResponse]:
        """Send request and get response with retry logic."""
        if not self.writer:
            logger.error(f"Connection not established [{self.connection_id}]")
            return None
        
        for attempt in range(max_retries):
            try:
                async with self._lock:
                    start_time = time.time()
                    
                    # Send request
                    request_data = request.to_crous()
                    request_len = len(request_data)
                    
                    # Send 4-byte length prefix + data
                    self.writer.write(request_len.to_bytes(4, byteorder='big'))
                    self.writer.write(request_data)
                    await asyncio.wait_for(self.writer.drain(), timeout=self.request_timeout)
                    
                    self.metrics["requests_sent"] += 1
                    self.metrics["bytes_sent"] += (4 + len(request_data))
                    
                    # Receive response length
                    len_bytes = await asyncio.wait_for(
                        self.reader.read(4),
                        timeout=self.request_timeout
                    )
                    
                    if not len_bytes or len(len_bytes) != 4:
                        logger.warning(f"Connection closed or invalid length by server [{self.connection_id}]")
                        self.metrics["errors"] += 1
                        return None
                    
                    response_len = int.from_bytes(len_bytes, byteorder='big')
                    
                    # Receive response body
                    response_data = await asyncio.wait_for(
                        self.reader.readexactly(response_len), 
                        timeout=self.request_timeout
                    )
                    
                    response = APIResponse.from_crous(response_data)
                    
                    # Update metrics
                    latency_ms = (time.time() - start_time) * 1000
                    self.metrics["requests_received"] += 1
                    self.metrics["bytes_received"] += (4 + len(response_data))
                    self.metrics["last_request_latency_ms"] = latency_ms
                    self._latencies.append(latency_ms)
                    if len(self._latencies) > 100:
                        self._latencies.pop(0)
                    self.metrics["avg_latency_ms"] = sum(self._latencies) / len(self._latencies)
                    self.last_used = time.time()
                    
                    return response
            
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout [{self.connection_id}] attempt {attempt + 1}/{max_retries}")
                self.metrics["errors"] += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.05 * (2 ** attempt))
                else:
                    return None
            except Exception as e:
                logger.error(f"Request error [{self.connection_id}]: {e}")
                self.metrics["errors"] += 1
                return None
        
        return None
    
    async def close(self):
        """Close connection."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
                logger.debug(f"Closed connection [{self.connection_id}]")
            except Exception as e:
                logger.debug(f"Error closing connection [{self.connection_id}]: {e}")
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        if not self.reader or not self.writer:
            return False
        
        # Connection is unhealthy if error rate is too high
        if self.metrics["requests_sent"] > 0:
            error_rate = self.metrics["errors"] / (self.metrics["requests_sent"] + 1)
            if error_rate > 0.5:  # More than 50% errors
                return False
        
        return True
    
    def is_idle(self, idle_timeout: float = 300.0) -> bool:
        """Check if connection has been idle."""
        return (time.time() - self.last_used) > idle_timeout


class TuboxAPIClient:
    """
    Tubox async client with connection pooling and session management.
    
    Similar to MongoDB Python driver. Features:
    - Connection pooling
    - Automatic reconnection
    - Session-based authentication
    - Comprehensive error handling
    - Metrics and monitoring
    
    Usage:
        client = TuboxAPIClient("localhost", 7188)
        await client.connect()
        await client.authenticate("user@example.com", "password")
        db = client.database("mydb")
        col = db.collection("users")
        await col.insert_one({"name": "Alice"})
        await client.close()
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 7188,
        max_pool_size: int = 10,
        max_connections: int = 100,
        connect_timeout: float = 10.0,
        request_timeout: float = 30.0,
    ):
        self.host = host
        self.port = port
        self.max_pool_size = max_pool_size
        self.max_connections = max_connections
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        
        # Connection pool
        self._pool: List[APIConnection] = []
        self._available: asyncio.Queue = None
        self._semaphore: asyncio.Semaphore = None
        self._pool_lock = asyncio.Lock()
        self._next_conn_id = 0
        
        # Session
        self.session_id: Optional[str] = None
        self._authenticated = False
        
        # Metrics
        self.metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "pooled_connections": 0,
            "total_requests": 0,
            "total_errors": 0,
            "avg_latency_ms": 0.0,
        }
    
    async def _init_pool(self):
        """Initialize connection pool."""
        if self._available is None:
            self._available = asyncio.Queue(maxsize=self.max_pool_size)
            self._semaphore = asyncio.Semaphore(self.max_connections)
    
    async def connect(self) -> bool:
        """Connect to server and initialize pool."""
        await self._init_pool()
        
        # Test connection
        test_conn = APIConnection(
            self.host, self.port, 
            "test",
            self.connect_timeout,
            self.request_timeout
        )
        if not await test_conn.connect():
            logger.error(f"Failed to connect to {self.host}:{self.port}")
            return False
        
        await test_conn.close()
        logger.info(f"Connected to {self.host}:{self.port}")
        return True
    
    async def _acquire_connection(self) -> Optional[APIConnection]:
        """
        Acquire connection from pool or create new one.
        
        Features:
        - Reuses healthy pooled connections
        - Creates new connections up to max_connections limit
        - Implements semaphore-based concurrency control
        """
        await self._init_pool()
        
        # Try to get available connection
        try:
            conn = self._available.get_nowait()
            if conn.is_healthy():
                logger.debug(f"Reusing pooled connection [{conn.connection_id}]")
                return conn
            else:
                logger.debug(f"Discarding unhealthy connection [{conn.connection_id}]")
                await conn.close()
                self.metrics["active_connections"] -= 1
        except asyncio.QueueEmpty:
            pass
        
        # Create new connection
        await self._semaphore.acquire()
        
        async with self._pool_lock:
            self._next_conn_id += 1
            conn_id = f"conn_{self._next_conn_id}"
        
        conn = APIConnection(
            self.host, self.port, 
            conn_id,
            self.connect_timeout,
            self.request_timeout
        )
        
        if not await conn.connect():
            logger.warning(f"Failed to create new connection [{conn_id}]")
            self._semaphore.release()
            return None
        
        async with self._pool_lock:
            self._pool.append(conn)
            self.metrics["total_connections"] += 1
            self.metrics["active_connections"] += 1
        
        logger.debug(f"Created new connection [{conn.connection_id}] "
                    f"(total: {self.metrics['total_connections']}, "
                    f"active: {self.metrics['active_connections']})")
        return conn
    
    async def _release_connection(self, conn: APIConnection):
        """
        Release connection back to pool.
        
        - Returns healthy connections to pool for reuse
        - Closes unhealthy connections or when pool is full
        - Tracks pool utilization metrics
        """
        if conn and conn.is_healthy():
            try:
                self._available.put_nowait(conn)
                self.metrics["pooled_connections"] += 1
                logger.debug(f"Returned connection [{conn.connection_id}] to pool "
                           f"(pooled: {self.metrics['pooled_connections']})")
                return
            except asyncio.QueueFull:
                logger.debug(f"Pool full - closing connection [{conn.connection_id}]")
        
        # Connection unhealthy or pool full, close it
        await conn.close()
        async with self._pool_lock:
            self._pool.remove(conn) if conn in self._pool else None
            self.metrics["active_connections"] -= 1
        self._semaphore.release()
        logger.debug(f"Closed connection [{conn.connection_id}] "
                    f"(active: {self.metrics['active_connections']})")
    
    async def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with server.
        
        Args:
            username: User email or username
            password: User password
            
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        logger.debug(f"Starting authentication for user: {username}")
        conn = await self._acquire_connection()
        if not conn:
            logger.error(f"Authentication failed for {username}: Cannot connect to server")
            raise AuthenticationError("Cannot connect to server")
        
        try:
            request = AuthRequest.login(username, password)
            logger.debug(f"Sending login request for {username} to {conn.host}:{conn.port}")
            response = await conn.send_request(request)
            
            if not response or response.status != "success":
                error = response.error if response else "Connection failed"
                logger.warning(f"Authentication failed for {username}: {error}")
                raise AuthenticationError(error)
            
            self.session_id = response.data.get("session_id")
            self._authenticated = True
            logger.info(f"Successfully authenticated as {username} (session: {self.session_id[:8]}...)")
            return True
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication for {username}: {e}", exc_info=True)
            raise AuthenticationError(f"Authentication error: {e}")
        finally:
            await self._release_connection(conn)
    
    async def _check_auth(self):
        """Check if authenticated."""
        if not self._authenticated or not self.session_id:
            raise UnauthorizedError("Not authenticated")
    
    async def _execute_request(self, request: APIRequest) -> Optional[APIResponse]:
        """
        Execute request with connection from pool.
        
        Args:
            request: APIRequest to execute
            
        Returns:
            APIResponse from server or None on failure
            
        Raises:
            TuboxException: If connection pool exhausted
        """
        logger.debug(f"Executing {request.operation} request")
        conn = await self._acquire_connection()
        if not conn:
            logger.error("Failed to acquire connection from pool - pool exhausted?")
            self.metrics["total_errors"] += 1
            raise TuboxException("Cannot acquire connection from pool")
        
        try:
            response = await conn.send_request(request)
            self.metrics["total_requests"] += 1
            
            if response and response.status == "success":
                latency = conn.metrics["last_request_latency_ms"]
                self.metrics["avg_latency_ms"] = latency
                logger.debug(f"{request.operation} succeeded (latency: {latency:.1f}ms)")
            else:
                error_msg = response.error if response else "No response"
                self.metrics["total_errors"] += 1
                logger.warning(f"{request.operation} failed: {error_msg}")
            
            return response
        except Exception as e:
            logger.error(f"Exception during {request.operation}: {e}", exc_info=True)
            self.metrics["total_errors"] += 1
            raise
        finally:
            await self._release_connection(conn)
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get storage usage information."""
        await self._check_auth()
        
        request = InfoRequest.storage_info(self.session_id)
        response = await self._execute_request(request)
        
        if response and response.status == "success":
            return response.data or {}
        
        return {"storage_used_bytes": 0, "storage_quota_bytes": 500_000_000}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics."""
        await self._check_auth()
        
        request = InfoRequest.metrics(self.session_id)
        response = await self._execute_request(request)
        
        if response and response.status == "success":
            return response.data or {}
        
        return {}
    
    async def list_databases(self) -> List[str]:
        """List all databases."""
        await self._check_auth()
        
        request = InfoRequest.databases(self.session_id)
        response = await self._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("databases", [])
        
        return []
    
    async def list_collections(self, db_name: str) -> List[str]:
        """List collections in database."""
        await self._check_auth()
        
        request = InfoRequest.collections(self.session_id, db_name)
        response = await self._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("collections", [])
        
        return []

    async def drop_database(self, db_name: str) -> bool:
        """Drop a database."""
        await self._check_auth()

        request = ManagementRequest.drop_database(self.session_id, db_name)
        response = await self._execute_request(request)

        if response and response.status == "success":
            logger.info(f"Dropped database {db_name}")
            return True
        return False

    async def rename_database(self, old_name: str, new_name: str) -> bool:
        """Rename a database."""
        await self._check_auth()

        request = ManagementRequest.rename_database(self.session_id, old_name, new_name)
        response = await self._execute_request(request)

        if response and response.status == "success":
            logger.info(f"Renamed database {old_name} to {new_name}")
            return True
        return False
    
    # =========================================================================
    # MongoDB-Style Session Management
    # =========================================================================
    
    async def start_session(
        self,
        session_id: Optional[str] = None,
        timeout_seconds: int = 3600,
        default_isolation_level: str = "READ_COMMITTED"
    ) -> "ClientSession":
        """
        Start a new MongoDB-style client session.
        
        Sessions provide:
        - Transaction management (start_transaction())
        - Automatic cleanup on close
        - Inactivity timeout
        - Configurable isolation level
        
        Args:
            session_id: Optional custom session ID (auto-generated if None)
            timeout_seconds: Session inactivity timeout in seconds (default 1 hour)
            default_isolation_level: Default isolation level for transactions
        
        Returns:
            ClientSession object for managing transactions
        
        Example:
            async with api_client.start_session() as session:
                async with session.start_transaction() as txn:
                    await collection.insert_one(doc, session=session)
                    # Auto-commits on successful exit
        
        Note:
            This is the MongoDB-style API for transaction management.
            For legacy SQL-like API, use collection.transaction_manager().
        """
        from tubox_client.client_session import ClientSession
        
        await self._check_auth()
        
        session = ClientSession(
            api_client=self,
            session_id=session_id,
            timeout_seconds=timeout_seconds,
            default_isolation_level=default_isolation_level
        )
        
        logger.info(f"Created session {session.session_id[:8]}... (timeout: {timeout_seconds}s)")
        return session
    
    # =========================================================================
    # MongoDB-Style Transaction Operations
    # =========================================================================
    # These methods are called by ClientTransaction and ClientSession
    # to implement the MongoDB-style transaction protocol
    
    async def _commit_transaction(
        self,
        transaction_id: str,
        session_id: str,
        isolation_level: str = "READ_COMMITTED"
    ) -> Dict[str, Any]:
        """
        Commit a transaction (internal API).
        
        Called by ClientTransaction.commit()
        
        Args:
            transaction_id: Transaction to commit
            session_id: Session owning the transaction
            isolation_level: Isolation level used for transaction
        
        Returns:
            Commit result from server
        
        Note:
            Currently a placeholder implementation that returns success.
            Server-side transaction protocol will be implemented in next phase.
        """
        await self._check_auth()
        
        # Placeholder: return success
        # TODO: Implement actual commit protocol with server
        logger.debug(f"Transaction {transaction_id} committed (placeholder)")
        return {"transaction_id": transaction_id, "status": "committed"}
    
    async def _rollback_transaction(
        self,
        transaction_id: str,
        session_id: str
    ) -> None:
        """
        Rollback (abort) a transaction (internal API).
        
        Called by ClientTransaction.abort()
        
        Args:
            transaction_id: Transaction to rollback
            session_id: Session owning the transaction
        
        Note:
            Currently a placeholder implementation.
            Server-side transaction protocol will be implemented in next phase.
        """
        await self._check_auth()
        
        # Placeholder: return success
        # TODO: Implement actual rollback protocol with server
        logger.debug(f"Transaction {transaction_id} rolled back (placeholder)")
        return

    
    def database(self, db_name: str) -> "TuboxAPIDatabase":
        """Get database reference."""
        return TuboxAPIDatabase(self, db_name)
    
    def __getitem__(self, db_name: str) -> "TuboxAPIDatabase":
        """Shorthand: client["mydb"]"""
        return self.database(db_name)
    
    def use(self, db_name: str) -> "TuboxAPIDatabase":
        """Use a database (MongoDB-style). Alias for database()."""
        return self.database(db_name)
    
    async def close(self):
        """Close all connections in pool."""
        for conn in self._pool:
            await conn.close()
        
        # Drain remaining pooled connections
        if self._available:
            while not self._available.empty():
                try:
                    conn = self._available.get_nowait()
                    await conn.close()
                except asyncio.QueueEmpty:
                    break
        
        logger.info("Closed all connections")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        return self.metrics.copy()


class TuboxAPIDatabase:
    """Database reference."""
    
    def __init__(self, client: TuboxAPIClient, name: str):
        self.client = client
        self.name = name
    
    def collection(self, col_name: str) -> "TuboxAPICollection":
        """Get collection reference."""
        return TuboxAPICollection(self.client, self.name, col_name)
    
    async def drop(self) -> bool:
        """Drop this database."""
        return await self.client.drop_database(self.name)

    async def rename(self, new_name: str) -> bool:
        """Rename this database."""
        success = await self.client.rename_database(self.name, new_name)
        if success:
            self.name = new_name
        return success

    def __getitem__(self, col_name: str) -> "TuboxAPICollection":
        """Shorthand: db["users"]"""
        return self.collection(col_name)
    
    def use(self, col_name: str) -> "TuboxAPICollection":
        """Use a collection (MongoDB-style). Alias for collection()."""
        return self.collection(col_name)


class TuboxAPICollection:
    """Collection reference."""
    
    def __init__(self, client: TuboxAPIClient, db_name: str, col_name: str):
        self.client = client
        self.db_name = db_name
        self.col_name = col_name

    async def drop(self) -> bool:
        """Drop this collection."""
        await self.client._check_auth()
        request = ManagementRequest.drop_collection(
            self.client.session_id, self.db_name, self.col_name
        )
        response = await self.client._execute_request(request)
        return response and response.status == "success"

    async def rename(self, new_name: str) -> bool:
        """Rename this collection."""
        await self.client._check_auth()
        request = ManagementRequest.rename_collection(
            self.client.session_id, self.db_name, self.col_name, new_name
        )
        response = await self.client._execute_request(request)
        if response and response.status == "success":
            self.col_name = new_name
            return True
        return False
    
    async def insert_one(self, document: Dict[str, Any]) -> OperationResult:
        """Insert single document."""
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.insert(
            self.client.session_id,
            self.db_name,
            self.col_name,
            document
        )
        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        logger.debug(f"Insert response: {response}")
        
        if response and response.status == "success":
            inserted_id = response.data.get("inserted_id")
            return OperationResult(
                success=True,
                data=inserted_id,
                operation_type="insert_one",
                execution_time_ms=execution_time_ms
            )
        
        error_msg = response.error if response else "Unknown error"
        logger.error(f"Insert failed: {error_msg}")
        return OperationResult(
            success=False,
            error=error_msg,
            operation_type="insert_one",
            execution_time_ms=execution_time_ms
        )
    
    async def find(self, query: Dict = None, projection: Dict = None, 
                   sort: List = None, skip: int = 0, limit: int = 0, 
                   hint: str = None) -> OperationResult:
        """
        Find documents with advanced querying.
        
        Args:
            query: Filter with operators ($eq, $gt, $regex, etc.)
            projection: Field selection {field: 1}
            sort: Sort specification [[field, direction]]
            skip: Documents to skip
            limit: Maximum documents to return
            hint: Index hint
            
        Returns:
            OperationResult with list of matching documents
        """
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.find(
            self.client.session_id,
            self.db_name,
            self.col_name,
            query,
            projection=projection,
            sort=sort,
            skip=skip,
            limit=limit,
            hint=hint
        )

        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if response and response.status == "success":
            docs = response.data.get("documents", []) if isinstance(response.data, dict) else (response.data or [])
            return OperationResult(
                success=True,
                data=docs,
                operation_type="find",
                execution_time_ms=execution_time_ms
            )
        
        error_msg = response.error if response else "Unknown error"
        return OperationResult(
            success=False,
            data=[],
            error=error_msg,
            operation_type="find",
            execution_time_ms=execution_time_ms
        )
    
    async def find_one(self, query: Dict = None) -> OperationResult:
        """Find single document."""
        start_time = time.time()
        result = await self.find(query)
        execution_time_ms = (time.time() - start_time) * 1000
        
        doc = result.documents[0] if result.documents else None
        return OperationResult(
            success=result.success,
            data=doc,
            error=result.error,
            operation_type="find_one",
            execution_time_ms=execution_time_ms
        )
    
    async def update_one(self, query: Dict, update: Dict, upsert: bool = False) -> OperationResult:
        """
        Update single document with advanced operators.
        
        Args:
            query: Filter with operators
            update: Update operators ($set, $inc, $push, etc.)
            upsert: Create if not found
            
        Returns:
            OperationResult with modified_count and upserted_id
        """
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.update(
            self.client.session_id,
            self.db_name,
            self.col_name,
            query,
            update,
            upsert=upsert,
            multi=False
        )

        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if response and response.status == "success":
            return OperationResult(
                success=True,
                data=response.data,
                operation_type="update_one",
                execution_time_ms=execution_time_ms
            )
        
        return OperationResult(
            success=False,
            data={"modified_count": 0},
            error=response.error if response else "Unknown error",
            operation_type="update_one",
            execution_time_ms=execution_time_ms
        )
    
    async def update_many(self, query: Dict, update: Dict, upsert: bool = False) -> OperationResult:
        """
        Update multiple documents with advanced operators.
        
        Args:
            query: Filter with operators
            update: Update operators ($set, $inc, $push, etc.)
            upsert: Create if not found
            
        Returns:
            OperationResult with modified_count and upserted_id
        """
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.update(
            self.client.session_id,
            self.db_name,
            self.col_name,
            query,
            update,
            upsert=upsert,
            multi=True
        )

        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if response and response.status == "success":
            return OperationResult(
                success=True,
                data=response.data,
                operation_type="update_many",
                execution_time_ms=execution_time_ms
            )
        
        return OperationResult(
            success=False,
            data={"modified_count": 0},
            error=response.error if response else "Unknown error",
            operation_type="update_many",
            execution_time_ms=execution_time_ms
        )
    
    async def delete_one(self, query: Dict) -> OperationResult:
        """
        Delete single document with advanced filters.
        
        Args:
            query: Filter with operators
            
        Returns:
            OperationResult with deleted_count
        """
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.delete(
            self.client.session_id,
            self.db_name,
            self.col_name,
            query,
            multi=False
        )
        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if response and response.status == "success":
            return OperationResult(
                success=True,
                data=response.data,
                operation_type="delete_one",
                execution_time_ms=execution_time_ms
            )
        
        return OperationResult(
            success=False,
            data={"deleted_count": 0},
            error=response.error if response else "Unknown error",
            operation_type="delete_one",
            execution_time_ms=execution_time_ms
        )
    
    async def delete_many(self, query: Dict) -> OperationResult:
        """
        Delete multiple documents with advanced filters.
        
        Args:
            query: Filter with operators
            
        Returns:
            OperationResult with deleted_count
        """
        start_time = time.time()
        await self.client._check_auth()
        
        request = CRUDRequest.delete(
            self.client.session_id,
            self.db_name,
            self.col_name,
            query,
            multi=True
        )
        response = await self.client._execute_request(request)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if response and response.status == "success":
            return OperationResult(
                success=True,
                data=response.data,
                operation_type="delete_many",
                execution_time_ms=execution_time_ms
            )
        
        return OperationResult(
            success=False,
            data={"deleted_count": 0},
            error=response.error if response else "Unknown error",
            operation_type="delete_many",
            execution_time_ms=execution_time_ms
        )
    
    async def bulk_write(self, operations: List[Dict], ordered: bool = True, atomic: bool = False) -> Dict[str, Any]:
        """
        Perform bulk write operations.
        
        Args:
            operations: List of operations. Each operation is a dict with:
                - action: "insert", "update", or "delete"
                - document: For insert
                - query: For update and delete
                - update: For update
            ordered: If True, stop on first error; if False, continue with remaining
            atomic: If True, all operations succeed or all fail together
        
        Returns:
            Dict with results including inserted_ids, modified_count, deleted_count
        """
        await self.client._check_auth()
        
        request = BatchRequest.bulk_write(
            self.client.session_id,
            self.db_name,
            self.col_name,
            operations,
            ordered=ordered,
            atomic=atomic
        )
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data or {}
        
        return {"inserted_ids": [], "modified_count": 0, "deleted_count": 0}
    
    async def bulk_write_atomic(self, operations: List[Dict], ordered: bool = True) -> Dict[str, Any]:
        """
        Perform atomic bulk write operations (all or nothing).
        
        Args:
            operations: List of operations (insert, update, delete)
            ordered: If True, stop on first error
        
        Returns:
            Dict with results - either all succeed or all fail
        """
        return await self.bulk_write(operations, ordered=ordered, atomic=True)
    
    async def execute_transaction(self, operations: List[Dict], isolation_level: str = "SERIALIZABLE") -> Dict[str, Any]:
        """
        Execute multi-collection transaction (all or nothing).
        
        Args:
            operations: List of operations across multiple collections:
                [
                    {
                        "database": "db_name",
                        "collection": "col_name",
                        "action": "insert",
                        "document": {...}
                    },
                    ...
                ]
            isolation_level: "READ_UNCOMMITTED", "READ_COMMITTED", "REPEATABLE_READ", "SERIALIZABLE"
        
        Returns:
            Dict with results including success_count
        """
        await self.client._check_auth()
        
        from tubox_client.api_protocol import BatchRequest
        
        request = BatchRequest.transaction(
            self.client.session_id,
            operations,
            isolation_level=isolation_level
        )
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data or {}
        
        raise Exception(f"Transaction failed: {response.error if response else 'Unknown error'}")
    
    def transaction_builder(self) -> "TransactionBuilder":
        """
        Create a transaction builder for convenient transaction construction.
        
        Returns:
            TransactionBuilder instance
        """
        from tubox_client.api_protocol import TransactionBuilder
        return TransactionBuilder(self.client.session_id)
    
    def transaction_manager(self) -> "ClientTransactionManager":
        """
        Create a transaction manager for SQL-like commit/rollback control.
        
        Usage:
            async with collection.transaction_manager() as txn:
                txn.add_insert("db", "col", {...})
                txn.add_update("db", "col", {...}, {...})
                await txn.commit()
        
        Returns:
            ClientTransactionManager instance bound to this collection
        """
        from tubox_client.transactions import ClientTransactionManager
        return ClientTransactionManager(self.client)
    
    async def start_transaction(
        self,
        session_id: Optional[str] = None,
        timeout_seconds: int = 3600,
        default_isolation_level: str = "READ_COMMITTED"
    ) -> "ClientSession":
        """
        Start a new MongoDB-style transaction session.
        
        Recommended for new code - provides MongoDB-compatible transaction API.
        
        Args:
            session_id: Optional custom session ID
            timeout_seconds: Session inactivity timeout
            default_isolation_level: Default isolation level for transactions
        
        Returns:
            ClientSession for managing transactions
        
        Example:
            async with await col.start_transaction() as session:
                async with session.start_transaction() as txn:
                    await col.insert_one(doc, session=session)
        
        Note:
            This creates a new session for this collection's operations.
            For session-less transactions, use transaction_manager() instead.
        """
        return await self.client.start_session(
            session_id=session_id,
            timeout_seconds=timeout_seconds,
            default_isolation_level=default_isolation_level
        )

    # =========================================================================
    # Index Management
    # =========================================================================

    async def create_index(
        self,
        field: str,
        index_type: str = "standard",
        unique: bool = False,
        sparse: bool = False,
        ttl_seconds: int = None,
    ) -> str:
        """Create an index on a field."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.create_index(
            self.client.session_id,
            self.db_name,
            self.col_name,
            field=field,
            index_type=index_type,
            unique=unique,
            sparse=sparse,
            ttl_seconds=ttl_seconds,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("index_name", "")
        
        raise Exception(f"Failed to create index: {response.error if response else 'Unknown error'}")

    async def create_compound_index(self, fields: List[tuple]) -> str:
        """Create a compound index on multiple fields."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        # Convert tuples to lists for Crous serialization compatibility
        serializable_fields = [list(f) if isinstance(f, tuple) else f for f in fields]
        
        request = IndexRequest.create_compound_index(
            self.client.session_id,
            self.db_name,
            self.col_name,
            fields=serializable_fields,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("index_name", "")
        
        raise Exception(f"Failed to create compound index: {response.error if response else 'Unknown error'}")

    async def drop_index(self, index_name: str) -> bool:
        """Drop an index by name."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_index(
            self.client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        response = await self.client._execute_request(request)
        
        return response and response.status == "success"

    async def drop_indexes_on_field(self, field: str) -> int:
        """Drop all indexes on a specific field."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_indexes_on_field(
            self.client.session_id,
            self.db_name,
            self.col_name,
            field=field,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("dropped_count", 0)
        
        return 0

    async def drop_all_indexes(self) -> int:
        """Drop all indexes in the collection."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_all_indexes(
            self.client.session_id,
            self.db_name,
            self.col_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("dropped_count", 0)
        
        return 0

    async def list_indexes(self) -> Dict[str, Dict[str, Any]]:
        """Get all indexes for this collection."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.list_indexes(
            self.client.session_id,
            self.db_name,
            self.col_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("indexes", {})
        
        return {}

    async def get_index_stats(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific index."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.get_index_stats(
            self.client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("stats")
        
        return None

    async def rebuild_index(self, index_name: str) -> bool:
        """Rebuild a specific index from all documents."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.rebuild_index(
            self.client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        response = await self.client._execute_request(request)
        
        return response and response.status == "success"

    async def rebuild_all_indexes(self) -> int:
        """Rebuild all indexes. Returns count rebuilt."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.rebuild_all_indexes(
            self.client.session_id,
            self.db_name,
            self.col_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("rebuilt_count", 0)
        
        return 0

    async def analyze_indexes(self) -> Dict[str, Any]:
        """Get comprehensive index analysis and recommendations."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.analyze_indexes(
            self.client.session_id,
            self.db_name,
            self.col_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("analysis", {})
        
        return {}

    async def cleanup_ttl_indexes(self) -> int:
        """Clean up expired documents in TTL indexes."""
        await self.client._check_auth()
        
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.cleanup_ttl(
            self.client.session_id,
            self.db_name,
            self.col_name,
        )
        
        response = await self.client._execute_request(request)
        
        if response and response.status == "success":
            return response.data.get("expired_count", 0)
        
        return 0


# Synchronous wrapper for convenience
class TuboxClient:
    """
    Synchronous wrapper around async API client.
    
    Production-ready MongoDB-like API for Python applications.
    
    Supports context manager for automatic resource cleanup:
    
    Example:
        # Explicit resource management
        client = TuboxClient("localhost", 7188, "user@example.com", "password")
        db = client["mydb"]
        col = db["users"]
        doc_id = col.insert_one({"name": "Alice", "age": 30})
        docs = col.find({"name": "Alice"})
        col.update_one({"_id": doc_id}, {"age": 31})
        col.delete_one({"_id": doc_id})
        storage = client.get_storage_info()
        client.close()
        
        # Context manager (recommended for production)
        with TuboxClient("localhost", 7188, "user@example.com", "password") as client:
            db = client["mydb"]
            col = db["users"]
            col.insert_one({"name": "Alice", "age": 30})
            docs = col.find({"age": {"$gt": 25}})
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 7188,
        username: str = None,
        password: str = None,
        max_pool_size: int = 10,
        max_connections: int = 100,
        **kwargs
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._client = None
        self._loop = None
        self._authenticated = False
        self._init_coro = None
        self._is_connected = False
        
        # Connect and authenticate immediately
        self._init_and_auth(max_pool_size, max_connections)
    
    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        if self._client:
            return self._client.session_id
        return None
    
    def _get_loop(self):
        """Get or create event loop."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, try to get the current event loop
                try:
                    self._loop = asyncio.get_event_loop()
                    if self._loop.is_closed():
                        self._loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(self._loop)
                except RuntimeError:
                    # No event loop at all, create one
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
        return self._loop
    
    def _init_and_auth(self, max_pool_size: int, max_connections: int):
        """Initialize and authenticate."""
        async def _init():
            logger.debug(f"Initializing TuboxClient for {self.host}:{self.port}")
            self._client = TuboxAPIClient(
                self.host,
                self.port,
                max_pool_size=max_pool_size,
                max_connections=max_connections
            )
            if not await self._client.connect():
                logger.error(f"Failed to connect to {self.host}:{self.port}")
                raise TuboxException(f"Cannot connect to {self.host}:{self.port}")
            
            logger.debug(f"Connected to {self.host}:{self.port}")
            
            if self.username and self.password:
                logger.debug(f"Authenticating user: {self.username}")
                await self._client.authenticate(self.username, self.password)
                self._authenticated = True
                self._authenticated = True
                logger.info(f"TuboxClient initialized and authenticated for {self.username}")
            
            self._is_connected = True
        
        try:
            # Check if there's already a running event loop
            try:
                asyncio.get_running_loop()
                # There's a running loop, we're in an async context
                # Store the coroutine to be run later
                self._init_coro = _init()
                logger.warning("TuboxClient created in async context - initialization deferred")
            except RuntimeError:
                # No running loop, safe to use run_until_complete
                loop = self._get_loop()
                loop.run_until_complete(_init())
        except Exception as e:
            logger.error(f"TuboxClient initialization failed: {e}", exc_info=True)
            raise
    
    def get_database(self, db_name: str) -> "SyncDatabase":
        """Get database reference."""
        return SyncDatabase(self, db_name)
    
    def __getitem__(self, db_name: str) -> "SyncDatabase":
        """Shorthand: client['dbname']."""
        return self.get_database(db_name)
    
    def use(self, db_name: str) -> "SyncDatabase":
        """Use a database (MongoDB-style). Alias for get_database()."""
        return self.get_database(db_name)

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage info."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.get_storage_info())
    
    def get_server_metrics(self) -> Dict[str, Any]:
        """Get server metrics."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.get_metrics())
    
    def list_databases(self) -> List[str]:
        """List all databases."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.list_databases())
    
    def list_collections(self, db_name: str) -> List[str]:
        """List collections in database."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.list_collections(db_name))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client and connection pool metrics."""
        if self._client:
            return self._client.get_metrics()
        return {}

    def drop_database(self, db_name: str) -> bool:
        """Drop a database."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.drop_database(db_name))

    def rename_database(self, old_name: str, new_name: str) -> bool:
        """Rename a database."""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.rename_database(old_name, new_name))
    
    def start_session(self, timeout: int = 3600):
        """
        Start a MongoDB-style session for transaction management.
        
        Args:
            timeout: Session timeout in seconds (default: 3600)
            
        Returns:
            SyncSession: Sync wrapper around async session
            
        Example:
            with client.start_session() as session:
                txn = session.start_transaction()
                # ... execute operations ...
                txn.commit()
        """
        loop = self._get_loop()
        async_session = loop.run_until_complete(self._client.start_session(timeout_seconds=timeout))
        return SyncSession(async_session, loop)
    
    def close(self):
        """Close client and all connections."""
        loop = self._get_loop()
        loop.run_until_complete(self._client.close())
        self._is_connected = False
    
    def __enter__(self) -> "TuboxClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        try:
            self.close()
        except Exception as e:
            logger.error(f"Error during context manager cleanup: {e}")
        return False


class SyncDatabase:
    """Sync database wrapper."""
    
    def __init__(self, client, name: str):
        """Initialize with TuboxClient instance."""
        self.client = client  # TuboxClient instance
        self.name = name
    
    def get_collection(self, col_name: str) -> "SyncCollection":
        """Get collection."""
        return SyncCollection(self.client._client, self.name, col_name)
    
    def create_collection(self, col_name: str) -> "SyncCollection":
        """Create collection by accessing it (forces creation on server)."""
        col = self.get_collection(col_name)
        # Trigger server-side collection creation by listing (this ensures dir is created)
        try:
            # Try a find operation to trigger collection creation on the server
            col.find({})
        except Exception:
            # If find fails, that's OK - collection should still be created
            pass
        return col
    
    def list_collections(self) -> List[str]:
        """List all collections in this database."""
        loop = self.client._get_loop()
        return loop.run_until_complete(self.client._client.list_collections(self.name))
    
    def __getitem__(self, col_name: str) -> "SyncCollection":
        """Shorthand: db['collection']."""
        return self.get_collection(col_name)
    
    def use(self, col_name: str) -> "SyncCollection":
        """Use a collection (MongoDB-style). Alias for get_collection()."""
        return self.get_collection(col_name)

    def drop(self) -> bool:
        """Drop this database."""
        return self.client.drop_database(self.name)

    def rename(self, new_name: str) -> bool:
        """Rename this database."""
        success = self.client.rename_database(self.name, new_name)
        if success:
            self.name = new_name
        return success


class SyncCollection:
    """
    Synchronous collection wrapper.
    
    Provides MongoDB-like CRUD operations with batch support.
    
    Features:
    - Single document operations: insert_one, find_one, update_one, delete_one
    - Batch operations: insert_many, update_many, delete_many
    - Query operations: find with optional query, count documents
    - Aggregation: distinct values
    - Error handling with proper exceptions
    
    Examples:
        col = db["users"]
        
        # Single operations
        doc_id = col.insert_one({"name": "Alice"})
        doc = col.find_one({"_id": doc_id})
        col.update_one({"_id": doc_id}, {"age": 30})
        deleted = col.delete_one({"_id": doc_id})
        
        # Batch operations
        ids = col.insert_many([
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35}
        ])
        updated = col.update_many({"age": {"$lt": 30}}, {"verified": True})
        deleted_count = col.delete_many({"verified": False})
        
        # Queries
        docs = col.find({"age": {"$gte": 18}}).all()
        count = col.count({"verified": True})
    """
    
    def __init__(self, api_client: TuboxAPIClient, db_name: str, col_name: str):
        self.api_client = api_client
        self.db_name = db_name
        self.col_name = col_name
    
    def _get_loop(self):
        """Get event loop."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def insert_one(self, document: Dict[str, Any]) -> OperationResult:
        """Insert single document and return OperationResult."""
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.insert_one(document))
            logger.debug(f"Inserted document: {result}")
            return result
        except Exception as e:
            logger.error(f"Insert error: {e}")
            return OperationResult(
                success=False,
                error=str(e),
                operation_type="insert_one"
            )
    
    def insert_many(self, documents: List[Dict[str, Any]], ordered: bool = True) -> List[str]:
        """
        Insert multiple documents.
        
        Args:
            documents: List of documents to insert
            ordered: If True, stop on first error; if False, continue with remaining
        
        Returns:
            List of inserted document IDs
        """
        logger.debug(f"Batch inserting {len(documents)} documents into {self.db_name}.{self.col_name} (ordered={ordered})")
        ids = []
        for i, doc in enumerate(documents):
            try:
                doc_id = self.insert_one(doc)
                ids.append(doc_id)
            except Exception as e:
                if ordered:
                    logger.error(f"Batch insert stopped at document {i}/{len(documents)}: {e}")
                    raise
                else:
                    logger.warning(f"Batch insert skipped document {i}/{len(documents)}: {e}")
        
        logger.debug(f"Successfully inserted {len(ids)}/{len(documents)} documents")
        return ids
    
    def find(self, query: Dict = None, projection: Optional[Dict] = None, 
             sort: Optional[List] = None, skip: int = 0, limit: int = 0, 
             hint: Optional[str] = None) -> OperationResult:
        """
        Find documents matching query with advanced options.
        
        Args:
            query: MongoDB-style query dict with operators
            projection: Fields to include/exclude
            sort: Sort specification [[field, direction]]
            skip: Documents to skip
            limit: Maximum documents to return
            hint: Index hint
        
        Returns:
            OperationResult with list of documents
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.find(
                query, 
                projection=projection,
                sort=sort,
                skip=skip,
                limit=limit,
                hint=hint
            ))
            logger.debug(f"Found {len(result.documents) if isinstance(result, OperationResult) else 0} documents")
            return result
        except Exception as e:
            logger.error(f"Find error: {e}")
            return OperationResult(
                success=False,
                data=[],
                error=str(e),
                operation_type="find"
            )
    
    def find_one(self, query: Dict = None) -> OperationResult:
        """Find single document."""
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.find_one(query))
            return result
        except Exception as e:
            logger.error(f"Find one error: {e}")
            return OperationResult(
                success=False,
                data=None,
                error=str(e),
                operation_type="find_one"
            )
    
    def update_one(self, query: Dict, update: Dict, upsert: bool = False) -> OperationResult:
        """
        Update single document matching query with advanced operators.
        
        Args:
            query: MongoDB-style query dict
            update: Update operators ($set, $inc, $push, etc.)
            upsert: Create if not found
            
        Returns:
            OperationResult with modified_count and upserted_id
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.update_one(query, update, upsert=upsert))
            logger.debug(f"Updated {result.modified_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Update error: {e}")
            return OperationResult(
                success=False,
                data={"modified_count": 0},
                error=str(e),
                operation_type="update_one"
            )
    
    def update_many(self, query: Dict, update: Dict, upsert: bool = False) -> OperationResult:
        """
        Update all documents matching query with advanced operators.
        
        Args:
            query: MongoDB-style query dict
            update: Update operators ($set, $inc, $push, etc.)
            upsert: Create if not found
            
        Returns:
            OperationResult with modified_count and upserted_id
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.update_many(query, update, upsert=upsert))
            logger.debug(f"Updated {result.modified_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Update many error: {e}")
            return OperationResult(
                success=False,
                data={"modified_count": 0},
                error=str(e),
                operation_type="update_many"
            )
    
    def delete_one(self, query: Dict) -> OperationResult:
        """
        Delete single document matching query with advanced filters.
        
        Args:
            query: MongoDB-style query dict with operators
            
        Returns:
            OperationResult with deleted_count
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.delete_one(query))
            logger.debug(f"Deleted {result.deleted_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return OperationResult(
                success=False,
                data={"deleted_count": 0},
                error=str(e),
                operation_type="delete_one"
            )
    
    def delete_many(self, query: Dict) -> OperationResult:
        """
        Delete all documents matching query with advanced filters.
        
        Args:
            query: MongoDB-style query dict with operators
            
        Returns:
            OperationResult with deleted_count
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.delete_many(query))
            logger.debug(f"Deleted {result.deleted_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Delete many error: {e}")
            return OperationResult(
                success=False,
                data={"deleted_count": 0},
                error=str(e),
                operation_type="delete_many"
            )
    
    def count(self, query: Dict = None) -> int:
        """Count documents matching query."""
        try:
            result = self.find(query)
            if result.success:
                docs = result.documents
                return len(docs) if isinstance(docs, list) else 0
            return 0
        except Exception as e:
            logger.error(f"Count error: {e}")
            return 0
    
    def drop(self) -> bool:
        """Drop this collection."""
        loop = self._get_loop()
        col = self.api_client.database(self.db_name).collection(self.col_name)
        return loop.run_until_complete(col.drop())

    def rename(self, new_name: str) -> bool:
        """Rename this collection."""
        loop = self._get_loop()
        col = self.api_client.database(self.db_name).collection(self.col_name)
        success = loop.run_until_complete(col.rename(new_name))
        if success:
            self.col_name = new_name
        return success
    
    def bulk_write(self, operations: List[Dict], ordered: bool = True, atomic: bool = False) -> Dict[str, Any]:
        """
        Perform bulk write operations.
        
        Args:
            operations: List of operations. Each operation is a dict with:
                - action: "insert", "update", or "delete"
                - document: For insert
                - query: For update and delete
                - update: For update
            ordered: If True, stop on first error; if False, continue with remaining
            atomic: If True, all operations succeed or all fail together
        
        Returns:
            Dict with results including inserted_ids, modified_count, deleted_count
        
        Example:
            operations = [
                {"action": "insert", "document": {"name": "Alice"}},
                {"action": "update", "query": {"name": "Bob"}, "update": {"age": 30}},
                {"action": "delete", "query": {"name": "Charlie"}}
            ]
            result = col.bulk_write(operations, atomic=True)
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.bulk_write(operations, ordered=ordered, atomic=atomic))
            logger.debug(f"Bulk write completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Bulk write error: {e}")
            raise
    
    def bulk_write_atomic(self, operations: List[Dict], ordered: bool = True) -> Dict[str, Any]:
        """
        Perform atomic bulk write operations (all or nothing).
        
        Args:
            operations: List of operations (insert, update, delete)
            ordered: If True, stop on first error
        
        Returns:
            Dict with results - either all succeed or all fail
        """
        return self.bulk_write(operations, ordered=ordered, atomic=True)

    def execute_transaction(self, operations: List[Dict], isolation_level: str = "SERIALIZABLE") -> Dict[str, Any]:
        """
        Execute multi-collection transaction (all or nothing).
        
        Args:
            operations: List of operations across multiple collections:
                [
                    {
                        "database": "db_name",
                        "collection": "col_name",
                        "action": "insert",
                        "document": {...}
                    },
                    {
                        "database": "db_name",
                        "collection": "col_name",
                        "action": "update",
                        "query": {...},
                        "update": {...}
                    },
                    {
                        "database": "db_name",
                        "collection": "col_name",
                        "action": "delete",
                        "query": {...}
                    }
                ]
            isolation_level: "READ_UNCOMMITTED", "READ_COMMITTED", "REPEATABLE_READ", "SERIALIZABLE"
        
        Returns:
            Dict with results including success_count
        
        Example:
            operations = [
                {
                    "database": "app",
                    "collection": "users",
                    "action": "insert",
                    "document": {"name": "Alice", "email": "alice@example.com"}
                },
                {
                    "database": "app",
                    "collection": "profiles",
                    "action": "insert",
                    "document": {"user_id": "...", "bio": "Software engineer"}
                }
            ]
            result = col.execute_transaction(operations)
            # Both inserts succeed or both fail
        """
        col = self.api_client.database(self.db_name).collection(self.col_name)
        loop = self._get_loop()
        try:
            result = loop.run_until_complete(col.execute_transaction(operations, isolation_level=isolation_level))
            logger.debug(f"Transaction completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise
    
    def transaction_builder(self) -> "TransactionBuilder":
        """
        Create a transaction builder for convenient transaction construction.
        
        Returns:
            TransactionBuilder instance
        
        Example:
            txn = col.transaction_builder()
            txn.insert("db1", "users", {"name": "Alice"})
            txn.insert("db1", "profiles", {"user_id": "...", "bio": "..."})
            txn.update("db1", "users", {"_id": "..."}, {"status": "active"})
            result = col.execute_transaction(txn.build().data["operations"])
        """
        from tubox_client.api_protocol import TransactionBuilder
        return TransactionBuilder(self.api_client.session_id)
    
    def transaction_manager(self):
        """
        Create a transaction manager for SQL-like commit/rollback control.
        
        Note: Sync wrapper - use async version for better performance.
        
        Usage:
            txn = col.transaction_manager()
            txn.add_insert("db", "col", {...})
            txn.add_update("db", "col", {...}, {...})
            loop = asyncio.get_event_loop()
            loop.run_until_complete(txn.commit())
        
        Returns:
            ClientTransactionManager instance bound to this collection
        """
        from tubox_client.transactions import ClientTransactionManager
        return ClientTransactionManager(self.api_client)
    
    def start_transaction(
        self,
        session_id: Optional[str] = None,
        timeout_seconds: int = 3600,
        default_isolation_level: str = "READ_COMMITTED"
    ) -> "ClientSession":
        """
        Start a new MongoDB-style transaction session (sync wrapper).
        
        Note: This is a sync wrapper around async start_session.
        Recommended for new code - provides MongoDB-compatible transaction API.
        
        Args:
            session_id: Optional custom session ID
            timeout_seconds: Session inactivity timeout
            default_isolation_level: Default isolation level for transactions
        
        Returns:
            ClientSession for managing transactions (must use with async)
        
        Example:
            async def work():
                async with await col.start_transaction() as session:
                    async with session.start_transaction() as txn:
                        await col.insert_one(doc, session=session)
        
            # In sync code, run with asyncio
            asyncio.run(work())
        """
        from tubox_client.client_session import ClientSession
        
        session = ClientSession(
            api_client=self.api_client,
            session_id=session_id,
            timeout_seconds=timeout_seconds,
            default_isolation_level=default_isolation_level
        )
        return session

    # =========================================================================
    # Index Management
    # =========================================================================

    def create_index(
        self,
        field: str,
        index_type: str = "standard",
        unique: bool = False,
        sparse: bool = False,
        ttl_seconds: int = None,
    ) -> str:
        """
        Create an index on a field.
        
        Args:
            field: Field name to index
            index_type: "standard", "unique", "hash", "text", "geo", "ttl"
            unique: Enforce uniqueness constraint
            sparse: Skip null/missing values
            ttl_seconds: TTL duration for TTL indexes
        
        Returns:
            Index name
        """
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.create_index(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            field=field,
            index_type=index_type,
            unique=unique,
            sparse=sparse,
            ttl_seconds=ttl_seconds,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                index_name = response.data.get("index_name")
                logger.info(f"Created {index_type} index: {index_name} on field '{field}'")
                return index_name
            else:
                error_msg = response.error if response else "Unknown error"
                raise Exception(f"Failed to create index: {error_msg}")
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            raise

    def create_compound_index(self, fields: List[tuple]) -> str:
        """
        Create a compound index on multiple fields.
        
        Args:
            fields: List of (field_name, direction) tuples
                   direction: 1 for ascending, -1 for descending
        
        Returns:
            Index name
        """
        from tubox_client.api_protocol import IndexRequest
        
        # Convert tuples to lists for Crous serialization compatibility
        serializable_fields = [list(f) if isinstance(f, tuple) else f for f in fields]
        
        request = IndexRequest.create_compound_index(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            fields=serializable_fields,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                index_name = response.data.get("index_name")
                logger.info(f"Created compound index: {index_name}")
                return index_name
            else:
                error_msg = response.error if response else "Unknown error"
                raise Exception(f"Failed to create compound index: {error_msg}")
        except Exception as e:
            logger.error(f"Compound index creation error: {e}")
            raise

    def drop_index(self, index_name: str) -> bool:
        """Drop an index by name."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_index(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                logger.info(f"Dropped index: {index_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Index drop error: {e}")
            raise

    def drop_indexes_on_field(self, field: str) -> int:
        """Drop all indexes on a specific field. Returns count dropped."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_indexes_on_field(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            field=field,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                count = response.data.get("dropped_count", 0)
                logger.info(f"Dropped {count} indexes on field '{field}'")
                return count
            return 0
        except Exception as e:
            logger.error(f"Index drop error: {e}")
            raise

    def drop_all_indexes(self) -> int:
        """Drop all indexes in the collection. Returns count dropped."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.drop_all_indexes(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                count = response.data.get("dropped_count", 0)
                logger.info(f"Dropped all {count} indexes")
                return count
            return 0
        except Exception as e:
            logger.error(f"Index drop error: {e}")
            raise

    def list_indexes(self) -> Dict[str, Dict[str, Any]]:
        """Get all indexes for this collection."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.list_indexes(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                indexes = response.data.get("indexes", {})
                logger.debug(f"Retrieved {len(indexes)} indexes")
                return indexes
            return {}
        except Exception as e:
            logger.error(f"List indexes error: {e}")
            raise

    def get_index_stats(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific index."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.get_index_stats(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                return response.data.get("stats")
            return None
        except Exception as e:
            logger.error(f"Get index stats error: {e}")
            raise

    def rebuild_index(self, index_name: str) -> bool:
        """Rebuild a specific index from all documents."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.rebuild_index(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
            index_name=index_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                logger.info(f"Rebuilt index: {index_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Rebuild index error: {e}")
            raise

    def rebuild_all_indexes(self) -> int:
        """Rebuild all indexes. Returns count rebuilt."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.rebuild_all_indexes(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                count = response.data.get("rebuilt_count", 0)
                logger.info(f"Rebuilt all {count} indexes")
                return count
            return 0
        except Exception as e:
            logger.error(f"Rebuild indexes error: {e}")
            raise

    def analyze_indexes(self) -> Dict[str, Any]:
        """Get comprehensive index analysis and recommendations."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.analyze_indexes(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                return response.data.get("analysis", {})
            return {}
        except Exception as e:
            logger.error(f"Analyze indexes error: {e}")
            raise

    def cleanup_ttl_indexes(self) -> int:
        """Clean up expired documents in TTL indexes. Returns count expired."""
        from tubox_client.api_protocol import IndexRequest
        
        request = IndexRequest.cleanup_ttl(
            self.api_client.session_id,
            self.db_name,
            self.col_name,
        )
        
        loop = self._get_loop()
        try:
            response = loop.run_until_complete(self.api_client._execute_request(request))
            if response and response.status == "success":
                count = response.data.get("expired_count", 0)
                logger.info(f"Cleaned up {count} expired documents")
                return count
            return 0
        except Exception as e:
            logger.error(f"TTL cleanup error: {e}")
            raise


class SyncSession:
    """
    Synchronous wrapper around async ClientSession.
    
    Provides MongoDB-style session management with transaction support.
    
    Example:
        with client.start_session() as session:
            txn = session.start_transaction()
            # ... operations ...
            txn.commit()
    """
    
    def __init__(self, async_session, loop):
        """Initialize with async session and event loop."""
        self.async_session = async_session
        self.loop = loop
    
    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self.async_session.session_id
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.async_session.is_active
    
    @property
    def in_transaction(self) -> bool:
        """Check if session is currently in a transaction."""
        return self.async_session.in_transaction
    
    def start_transaction(self, isolation_level: str = "snapshot"):
        """
        Start a transaction within this session.
        
        Args:
            isolation_level: Transaction isolation level ("snapshot", "serializable", "read_committed")
            
        Returns:
            SyncTransaction: Sync wrapper around async transaction
        """
        async_txn = self.async_session.start_transaction(isolation_level=isolation_level)
        return SyncTransaction(async_txn, self.loop)
    
    async def commit_transaction(self):
        """Commit the current transaction."""
        return await self.async_session.commit_transaction()
    
    async def abort_transaction(self):
        """Abort the current transaction."""
        return await self.async_session.abort_transaction()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        if not exc_type and self.in_transaction:
            # No exception, transaction will auto-commit
            pass
        elif exc_type and self.in_transaction:
            # Exception occurred, auto-abort
            self.loop.run_until_complete(self.async_session.abort_transaction())
        return False


class SyncTransaction:
    """
    Synchronous wrapper around async ClientTransaction.
    
    Provides MongoDB-style transaction operations.
    
    Example:
        txn = session.start_transaction()
        # ... operations ...
        txn.commit()
    """
    
    def __init__(self, async_txn, loop):
        """Initialize with async transaction and event loop."""
        self.async_txn = async_txn
        self.loop = loop
    
    @property
    def transaction_id(self) -> str:
        """Get transaction ID."""
        return self.async_txn.transaction_id
    
    @property
    def state(self) -> str:
        """Get current transaction state."""
        return self.async_txn.state
    
    def add_operation(self, operation: Dict[str, Any]):
        """
        Add an operation to the transaction.
        
        Args:
            operation: Operation dict with 'type', 'database', 'collection', 'data', etc.
        """
        self.async_txn.add_operation(operation)
    
    def commit(self):
        """Commit the transaction."""
        return self.loop.run_until_complete(self.async_txn.commit())
    
    def abort(self):
        """Abort the transaction."""
        return self.loop.run_until_complete(self.async_txn.abort())
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic commit/abort.
        
        Only commits/aborts if transaction is still active (idempotent).
        Safe to call multiple times - if already committed, does nothing.
        """
        # Only attempt commit/abort if transaction is still active
        if self.async_txn.is_active:
            if not exc_type:
                # No exception, auto-commit
                self.loop.run_until_complete(self.async_txn.commit())
            else:
                # Exception occurred, auto-abort
                self.loop.run_until_complete(self.async_txn.abort())
        return False


class OperationResult:
    """
    Standard result class for all database operations.
    
    Provides consistent interface for success/failure handling across
    insert, update, delete, find, and other operations.
    
    Attributes:
        success: Whether operation succeeded
        data: Operation-specific data (inserted IDs, modified count, documents, etc.)
        error: Error message if operation failed
        operation_type: Type of operation (insert, update, delete, find, etc.)
        execution_time_ms: Operation execution time in milliseconds
    """
    
    def __init__(
        self,
        success: bool = True,
        data: Any = None,
        error: Optional[str] = None,
        operation_type: str = "unknown",
        execution_time_ms: float = 0.0
    ):
        self.success = success
        self.data = data
        self.error = error
        self.operation_type = operation_type
        self.execution_time_ms = execution_time_ms
    
    def __repr__(self) -> str:
        if self.success:
            return f"OperationResult(success=True, operation={self.operation_type}, data={self.data})"
        else:
            return f"OperationResult(success=False, operation={self.operation_type}, error={self.error})"
    
    def __bool__(self) -> bool:
        """Allow truthiness check: if result: ..."""
        return self.success
    
    @property
    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self.success
    
    @property
    def is_error(self) -> bool:
        """Check if operation failed."""
        return not self.success
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from data dict (for compatibility with dict-like access)."""
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        return default
    
    def __getitem__(self, key: str) -> Any:
        """Get value from data dict using bracket notation."""
        if isinstance(self.data, dict):
            return self.data[key]
        raise TypeError(f"Cannot index {self.operation_type} result data")
    
    # Convenience accessors for common operation results
    
    @property
    def inserted_ids(self) -> List[str]:
        """Get inserted document IDs (insert operations)."""
        if isinstance(self.data, list):
            return self.data
        return self.get("inserted_ids", [])
    
    @property
    def inserted_id(self) -> Optional[str]:
        """Get single inserted document ID (insert_one operations)."""
        if isinstance(self.data, str):
            return self.data
        return self.get("inserted_id")
    
    @property
    def modified_count(self) -> int:
        """Get number of modified documents (update operations)."""
        return self.get("modified_count", 0)
    
    @property
    def upserted_id(self) -> Optional[str]:
        """Get upserted document ID (update with upsert=True)."""
        return self.get("upserted_id")
    
    @property
    def deleted_count(self) -> int:
        """Get number of deleted documents (delete operations)."""
        return self.get("deleted_count", 0)
    
    @property
    def documents(self) -> List[Dict]:
        """Get documents from find result."""
        if isinstance(self.data, list):
            return self.data
        return self.get("documents", [])
    
    def all(self) -> List[Dict]:
        """Get all documents (find operations)."""
        return self.documents


class FindResult(OperationResult):
    """Result from find operation (extends OperationResult)."""
    
    def __init__(self, documents: List[Dict]):
        super().__init__(
            success=True,
            data=documents,
            operation_type="find"
        )
        self.documents = documents
    
    def all(self) -> List[Dict]:
        """Get all documents."""
        return self.documents
