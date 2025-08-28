"""
Response compression middleware for improved performance.
Provides Gzip compression for API responses.
"""

from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import gzip
import json
from typing import Callable, Any
import structlog

from .monitoring import logger

class CompressionMiddleware(BaseHTTPMiddleware):
    """Custom compression middleware with selective compression."""
    
    def __init__(self, app, minimum_size: int = 1000, compress_content_types: list = None):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compress_content_types = compress_content_types or [
            "application/json",
            "text/html",
            "text/plain",
            "text/css",
            "application/javascript",
            "text/javascript"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response if appropriate."""
        response = await call_next(request)
        
        # Check if response should be compressed
        if self._should_compress(request, response):
            return await self._compress_response(response)
        
        return response
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed."""
        # Skip compression for certain paths
        skip_paths = ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return False
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in self.compress_content_types):
            return False
        
        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return False
        
        # Check if already compressed
        if "content-encoding" in response.headers:
            return False
        
        return True
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress response content."""
        try:
            # Get response body
            if hasattr(response, 'body'):
                body = response.body
            else:
                # For streaming responses, we need to read the content
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
            
            # Compress content
            compressed_body = gzip.compress(body)
            
            # Create new response with compressed content
            compressed_response = Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Add compression headers
            compressed_response.headers["content-encoding"] = "gzip"
            compressed_response.headers["content-length"] = str(len(compressed_body))
            compressed_response.headers["vary"] = "Accept-Encoding"
            
            # Log compression stats
            original_size = len(body)
            compressed_size = len(compressed_body)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            logger.debug(
                "Response compressed",
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=f"{compression_ratio:.1f}%"
            )
            
            return compressed_response
            
        except Exception as e:
            logger.error("Compression failed", error=str(e))
            return response

class SelectiveCompressionMiddleware(BaseHTTPMiddleware):
    """Middleware that compresses responses based on content type and size."""
    
    def __init__(self, app):
        super().__init__(app)
        self.gzip_middleware = GZipMiddleware(app, minimum_size=1000)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply selective compression."""
        # Skip compression for certain endpoints
        skip_paths = ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Apply compression for other endpoints
        return await self.gzip_middleware(request, call_next)

def setup_compression(app):
    """Setup compression middleware for the FastAPI app."""
    # Add compression middleware
    app.add_middleware(SelectiveCompressionMiddleware)
    
    logger.info("Compression middleware configured")

# Compression utilities
def compress_json_response(data: Any, status_code: int = 200) -> Response:
    """Create a compressed JSON response."""
    json_content = json.dumps(data, separators=(',', ':'))
    compressed_content = gzip.compress(json_content.encode('utf-8'))
    
    response = Response(
        content=compressed_content,
        status_code=status_code,
        media_type="application/json"
    )
    
    response.headers["content-encoding"] = "gzip"
    response.headers["content-length"] = str(len(compressed_content))
    response.headers["vary"] = "Accept-Encoding"
    
    return response

def should_compress_request(request: Request) -> bool:
    """Check if request accepts compression."""
    accept_encoding = request.headers.get("accept-encoding", "")
    return "gzip" in accept_encoding.lower()

def get_compression_stats(original_size: int, compressed_size: int) -> dict:
    """Calculate compression statistics."""
    if original_size == 0:
        return {
            "original_size": 0,
            "compressed_size": 0,
            "compression_ratio": 0,
            "bytes_saved": 0
        }
    
    compression_ratio = (1 - compressed_size / original_size) * 100
    bytes_saved = original_size - compressed_size
    
    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": round(compression_ratio, 2),
        "bytes_saved": bytes_saved
    }
