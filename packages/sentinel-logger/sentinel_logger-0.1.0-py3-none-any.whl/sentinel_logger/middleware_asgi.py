import time
import asyncio
import random
from collections import deque
import logging
from typing import Callable, Awaitable

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger("sentinel_logger")
DEFAULT_URL = "https://sentinel-backend-9cgt.onrender.com/api/v1/track"


class SentinelLoggerASGI:
    """
    ASGI middleware that logs requests to Sentinel.
    Works with FastAPI, Starlette, Quart, and any ASGI-compliant framework.
    
    Usage with FastAPI:
        from fastapi import FastAPI
        from sentinel_logger import SentinelLoggerASGI
        
        app = FastAPI()
        app = SentinelLoggerASGI(app, api_key="YOUR_KEY")
    
    Or use add_middleware:
        app.add_middleware(SentinelLoggerASGI, api_key="YOUR_KEY")
    """
    
    def __init__(
        self,
        app,
        api_key: str,
        url: str = DEFAULT_URL,
        flush_interval: float = 0.5,
        max_queue: int = 10000,
        batch_size: int = 50,
        max_attempts: int = 5,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        
        self.app = app
        self.api_key = api_key
        self.url = url
        self.flush_interval = float(flush_interval)
        self.max_queue = int(max_queue)
        self.batch_size = int(batch_size)
        self.max_attempts = int(max_attempts)
        
        self._lock = asyncio.Lock()
        self._queue = deque()
        
        # HTTP session with keep-alive (same as WSGI version)
        # Note: We use sync requests in a thread executor to avoid blocking
        self.session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        })
        
        self._stop = False
        self._worker_task = None
    
    async def __call__(
        self,
        scope: dict,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ):
        """ASGI interface"""
        # Only intercept HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Start worker if not running
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
        
        start_time = time.perf_counter()
        status_code = [500]  # default fallback
        
        async def wrapped_send(message: dict):
            """Intercept response to capture status code"""
            if message["type"] == "http.response.start":
                try:
                    status_code[0] = message["status"]
                except (KeyError, TypeError):
                    pass
            await send(message)
        
        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            # Log after response completes (mirrors res.on('finish'))
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            path = scope.get("path", "/")
            method = scope.get("method", "GET")
            
            log = {
                "path": str(path),
                "method": method,
                "statusCode": status_code[0],
                "responseTime": round(duration_ms, 2),
            }
            await self._enqueue(log)
    
    async def _enqueue(self, data):
        """Add log to queue (async version)"""
        async with self._lock:
            if len(self._queue) >= self.max_queue:
                return  # drop silently
            self._queue.append({"data": data, "attempts": 0, "next": 0.0})
    
    async def _worker(self):
        """Background worker coroutine (async version of thread worker)"""
        loop = asyncio.get_event_loop()
        
        while not self._stop:
            now = time.time()
            to_send = []
            
            async with self._lock:
                count = 0
                while self._queue and count < self.batch_size:
                    item = self._queue[0]
                    if item["next"] <= now:
                        to_send.append(self._queue.popleft())
                        count += 1
                    else:
                        break
            
            if to_send:
                # Send requests in thread pool to avoid blocking event loop
                tasks = [
                    loop.run_in_executor(None, self._send_sync, item)
                    for item in to_send
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle failed items
                for item, result in zip(to_send, results):
                    if isinstance(result, Exception) or result is False:
                        await self._handle_retry(item)
            
            await asyncio.sleep(self.flush_interval)
    
    def _send_sync(self, item: dict) -> bool:
        """Synchronous send (runs in thread pool)"""
        try:
            resp = self.session.post(
                self.url, json=item["data"], timeout=3.0
            )
            status = resp.status_code
            # Don't retry 4xx client errors
            if 400 <= status < 500:
                return True  # Success (don't retry)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.debug("Send failed: %s", e)
            return False
    
    async def _handle_retry(self, item: dict):
        """Handle retry with exponential backoff"""
        item["attempts"] += 1
        if item["attempts"] > self.max_attempts:
            logger.debug("Dropping log after %d attempts", item["attempts"])
            return
        
        # Exponential backoff + jitter (same as WSGI version)
        base = 0.5
        delay = min(30.0, base * (2 ** (item["attempts"] - 1)))
        jitter = delay * 0.2 * (random.random() * 2 - 1)
        item["next"] = time.time() + max(0.0, delay + jitter)
        
        async with self._lock:
            self._queue.append(item)
    
    async def close(self, timeout: float = 1.0):
        """Flush and shutdown (async version)"""
        self._stop = True
        
        if self._worker_task:
            try:
                await asyncio.wait_for(self._worker_task, timeout=timeout)
            except asyncio.TimeoutError:
                self._worker_task.cancel()
        
        # Best-effort flush
        try:
            remaining = []
            async with self._lock:
                while self._queue:
                    remaining.append(self._queue.popleft())
            
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(None, self._send_sync, item)
                for item in remaining[:50]
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            pass
        finally:
            try:
                self.session.close()
            except Exception:
                pass