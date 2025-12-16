import threading
import time
import random
from collections import deque
import logging

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger("sentinel_logger")
DEFAULT_URL = "https://sentinel-backend-9cgt.onrender.com/api/v1/track"

class SentinelLogger:
    """
    WSGI middleware that logs requests to Sentinel.
    Works with Flask, Django, Bottle, and any WSGI-compliant framework.
    
    Usage:
        app.wsgi_app = SentinelLogger(app.wsgi_app, api_key="KEY")
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
        
        self._lock = threading.Lock()
        self._queue = deque()
        
        # HTTP session with keep-alive (mirrors your axios keep-alive)
        self.session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        })
        
        self._stop = False
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
    
    def __call__(self, environ, start_response):
        """WSGI interface"""
        start_time = time.perf_counter()
        
        # Capture status from start_response
        status_code = [500]  # default fallback
        
        def _start_response(status, response_headers, exc_info=None):
            try:
                status_code[0] = int(status.split(" ", 1)[0])
            except (ValueError, IndexError):
                pass
            return start_response(status, response_headers, exc_info)
        
        # Call the wrapped app
        try:
            response = self.app(environ, _start_response)
            # Consume iterator to ensure app completes
            response_data = []
            for chunk in response:
                response_data.append(chunk)
            return response_data
        finally:
            # Log after response completes (mirrors res.on('finish'))
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            path = environ.get("PATH_INFO", "/")
            method = environ.get("REQUEST_METHOD", "GET")
            
            log = {
                "path": str(path),
                "method": method,
                "statusCode": status_code[0],
                "responseTime": round(duration_ms, 2),
            }
            self._enqueue(log)
    
    def _enqueue(self, data):
        with self._lock:
            if len(self._queue) >= self.max_queue:
                return  # drop silently
            self._queue.append({"data": data, "attempts": 0, "next": 0.0})
    
    def _worker(self):
        """Background thread (mirrors your setInterval + flushQueue)"""
        while not self._stop:
            now = time.time()
            to_send = []
            
            with self._lock:
                count = 0
                while self._queue and count < self.batch_size:
                    item = self._queue[0]
                    if item["next"] <= now:
                        to_send.append(self._queue.popleft())
                        count += 1
                    else:
                        break
            
            if to_send:
                for item in to_send:
                    if self._stop:
                        break
                    try:
                        resp = self.session.post(
                            self.url, json=item["data"], timeout=3.0
                        )
                        status = resp.status_code
                        # Don't retry 4xx client errors
                        if 400 <= status < 500:
                            continue
                        resp.raise_for_status()
                    except Exception:
                        item["attempts"] += 1
                        if item["attempts"] > self.max_attempts:
                            logger.debug("Dropping log after %d attempts", item["attempts"])
                            continue
                        
                        # Exponential backoff + jitter (mirrors scheduleRequeue)
                        base = 0.5
                        delay = min(30.0, base * (2 ** (item["attempts"] - 1)))
                        jitter = delay * 0.2 * (random.random() * 2 - 1)
                        item["next"] = time.time() + max(0.0, delay + jitter)
                        
                        with self._lock:
                            self._queue.append(item)
            
            time.sleep(self.flush_interval)
    
    def close(self, timeout: float = 1.0):
        """Flush and shutdown (mirrors process.on('beforeExit'))"""
        self._stop = True
        self._thread.join(timeout=timeout)
        
        try:
            remaining = []
            with self._lock:
                while self._queue:
                    remaining.append(self._queue.popleft())
            
            for item in remaining[:50]:  # best-effort flush up to 50 items
                try:
                    self.session.post(self.url, json=item["data"], timeout=1.0)
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            try:
                self.session.close()
            except Exception:
                pass