"""
High-performance connection pool for Tubox client.
Features:
- Async connection pooling with semaphores
- Connection reuse and lifecycle management
- Health checks and automatic reconnection
- Metrics tracking
- Configurable pool sizing
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import crous

logger = logging.getLogger("tubox.client.pool")


@dataclass
class PoolConfig:
    """Configuration for client connection pool."""
    host: str = "localhost"
    port: int = 7188
    max_connections: int = 100  # Max concurrent connections
    max_pool_size: int = 10  # Reusable connections in pool
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    idle_timeout: float = 300.0  # Close idle connections after 5 min
    max_retries: int = 3
    retry_delay: float = 0.1


@dataclass
class ConnectionMetrics:
    """Metrics for a single connection."""
    connection_id: str
    created_at: float
    last_used: float
    requests_sent: int = 0
    requests_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    errors: int = 0
    latency_ms: float = 0.0


class NetworkConnection:
    """Single network connection to server."""
    
    def __init__(self, connection_id: str, config: PoolConfig):
        self.connection_id = connection_id
        self.config = config
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.metrics = ConnectionMetrics(
            connection_id=connection_id,
            created_at=time.time(),
            last_used=time.time()
        )
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Establish connection to server."""
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.host, self.config.port),
                timeout=self.config.connection_timeout
            )
            logger.debug(f"Connected: {self.connection_id}")
            return True
        except Exception as e:
            logger.error(f"Connection failed for {self.connection_id}: {e}")
            return False
    
    async def send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request and get response."""
        if not self.writer:
            return None
        
        try:
            async with self._lock:
                # Send request
                request_data = crous.dumps(request) + b"\n"
                self.writer.write(request_data)
                await asyncio.wait_for(
                    self.writer.drain(),
                    timeout=self.config.write_timeout
                )
                self.metrics.bytes_sent += len(request_data)
                self.metrics.requests_sent += 1
                
                # Receive response
                # Receive response
                start_time = time.time()
                response_line = await asyncio.wait_for(
                    self.reader.readline(),
                    timeout=self.config.read_timeout
                )
                latency = (time.time() - start_time) * 1000
                
                if not response_line:
                    logger.error(f"Connection closed: {self.connection_id}")
                    return None
                
                # Remove trailing newline for crous decoding
                data = response_line[:-1] if response_line.endswith(b"\n") else response_line
                response = crous.loads(data)
                self.metrics.bytes_received += len(response_line)
                self.metrics.requests_received += 1
                self.metrics.latency_ms = latency
                self.metrics.last_used = time.time()
                
                return response
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {self.connection_id}")
            self.metrics.errors += 1
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            self.metrics.errors += 1
            return None
    
    async def close(self):
        """Close connection."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                logger.debug(f"Error closing connection: {e}")
            finally:
                self.reader = None
                self.writer = None
    
    def is_idle(self) -> bool:
        """Check if connection is idle."""
        idle_time = time.time() - self.metrics.last_used
        return idle_time > self.config.idle_timeout
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return self.writer is not None and self.metrics.errors < 5


class ConnectionPool:
    """Async connection pool for client."""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.active_connections: Dict[str, NetworkConnection] = {}
        self.available_connections: asyncio.Queue = asyncio.Queue(maxsize=config.max_pool_size)
        self._semaphore = asyncio.Semaphore(config.max_connections)
        self._next_connection_id = 0
        self._lock = asyncio.Lock()
        self.metrics: Dict[str, Any] = {
            "total_connections": 0,
            "active_connections": 0,
            "pooled_connections": 0,
            "total_requests": 0,
            "total_errors": 0,
            "avg_latency_ms": 0.0,
        }
    
    async def acquire(self) -> Optional[NetworkConnection]:
        """Acquire a connection from pool."""
        # Check if we have available connection in pool
        try:
            conn = self.available_connections.get_nowait()
            if conn.is_healthy():
                self.metrics["pooled_connections"] -= 1
                logger.debug(f"Reused connection: {conn.connection_id}")
                return conn
            else:
                # Connection unhealthy, close it
                await conn.close()
        except asyncio.QueueEmpty:
            pass
        
        # Need new connection
        await self._semaphore.acquire()
        
        try:
            async with self._lock:
                self._next_connection_id += 1
                conn_id = f"conn_{self._next_connection_id}"
            
            conn = NetworkConnection(conn_id, self.config)
            
            # Try to connect with retries
            for attempt in range(self.config.max_retries):
                if await conn.connect():
                    self.active_connections[conn_id] = conn
                    self.metrics["total_connections"] += 1
                    self.metrics["active_connections"] += 1
                    logger.debug(f"Created new connection: {conn_id}")
                    return conn
                
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
            
            logger.error(f"Failed to connect after {self.config.max_retries} attempts")
            self._semaphore.release()
            return None
        
        except Exception as e:
            logger.error(f"Error acquiring connection: {e}")
            self._semaphore.release()
            return None
    
    async def release(self, conn: NetworkConnection):
        """Release connection back to pool."""
        if conn and conn.is_healthy():
            try:
                self.available_connections.put_nowait(conn)
                self.metrics["pooled_connections"] += 1
                logger.debug(f"Released connection: {conn.connection_id}")
                return
            except asyncio.QueueFull:
                pass
        
        # Connection unhealthy or pool full, close it
        await conn.close()
        self.metrics["active_connections"] -= 1
        self._semaphore.release()
    
    async def execute(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute request using a connection from pool."""
        conn = await self.acquire()
        if not conn:
            self.metrics["total_errors"] += 1
            return None
        
        try:
            response = await conn.send_request(request)
            self.metrics["total_requests"] += 1
            if response and "error" not in response:
                self.metrics["avg_latency_ms"] = conn.metrics.latency_ms
            else:
                self.metrics["total_errors"] += 1
            return response
        finally:
            await self.release(conn)
    
    async def cleanup_idle(self):
        """Remove idle connections."""
        to_remove = []
        for conn_id, conn in self.active_connections.items():
            if conn.is_idle():
                to_remove.append(conn_id)
                await conn.close()
        
        for conn_id in to_remove:
            del self.active_connections[conn_id]
            self.metrics["active_connections"] -= 1
            logger.debug(f"Removed idle connection: {conn_id}")
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} idle connections")
    
    async def close_all(self):
        """Close all connections."""
        for conn in self.active_connections.values():
            await conn.close()
        
        # Drain remaining queued connections
        while not self.available_connections.empty():
            try:
                conn = self.available_connections.get_nowait()
                await conn.close()
            except asyncio.QueueEmpty:
                break
        
        logger.info("Closed all connections")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics."""
        return self.metrics.copy()
