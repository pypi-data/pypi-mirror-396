"""
StackSense FastAPI Application
==============================
Async API with Redis caching for fast responses.

Run with: uvicorn api.main:app --reload
"""

import os
import json
import time
import hashlib
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Optional Redis import
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Optional aiohttp for async Ollama calls
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    import requests as aiohttp
    AIOHTTP_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default


# =============================================================================
# Request/Response Models
# =============================================================================
class ChatRequest(BaseModel):
    query: str
    workspace: str = "."
    model: str = "phi3:mini"
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    files_used: list = []
    cached: bool = False
    time_seconds: float = 0.0


class WarmupRequest(BaseModel):
    model: str = "phi3:mini"


class DiagramRequest(BaseModel):
    workspace: str
    force_rebuild: bool = False


# =============================================================================
# FastAPI App
# =============================================================================
app = FastAPI(
    title="StackSense API",
    description="AI-powered code intelligence with caching",
    version="0.1.0"
)

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Redis Cache Manager
# =============================================================================
class CacheManager:
    """Redis cache for diagrams and query responses"""
    
    def __init__(self):
        self.redis = None
        self._connect()
    
    def _connect(self):
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(REDIS_URL, decode_responses=True)
                self.redis.ping()
                print("✅ Redis connected")
            except Exception as e:
                print(f"⚠️ Redis not available: {e}")
                self.redis = None
    
    def _hash_key(self, workspace: str, query: str) -> str:
        """Create cache key from workspace + query"""
        content = f"{workspace}:{query}"
        return f"ss:{hashlib.md5(content.encode()).hexdigest()}"
    
    def get_cached_response(self, workspace: str, query: str) -> Optional[str]:
        """Get cached response if exists"""
        if not self.redis:
            return None
        
        key = self._hash_key(workspace, query)
        return self.redis.get(key)
    
    def cache_response(self, workspace: str, query: str, response: str):
        """Cache a response"""
        if not self.redis:
            return
        
        key = self._hash_key(workspace, query)
        self.redis.setex(key, CACHE_TTL, response)
    
    def get_diagram(self, workspace: str) -> Optional[dict]:
        """Get cached diagram"""
        if not self.redis:
            return None
        
        data = self.redis.get(f"diagram:{workspace}")
        return json.loads(data) if data else None
    
    def cache_diagram(self, workspace: str, diagram: dict, ttl: int = 86400):
        """Cache diagram for 24 hours"""
        if not self.redis:
            return
        
        self.redis.setex(f"diagram:{workspace}", ttl, json.dumps(diagram))
    
    def invalidate_diagram(self, workspace: str):
        """Invalidate cached diagram (on file changes)"""
        if self.redis:
            self.redis.delete(f"diagram:{workspace}")


# =============================================================================
# Async Ollama Client
# =============================================================================
class AsyncOllamaClient:
    """Async client for Ollama API"""
    
    def __init__(self):
        self.session = None
        self.model = "phi3:mini"
    
    async def init(self):
        """Initialize async session"""
        if AIOHTTP_AVAILABLE and self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def warm_up(self, model: str = None):
        """Warm up model"""
        model = model or self.model
        
        if AIOHTTP_AVAILABLE and self.session:
            async with self.session.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": "ready",
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {"num_predict": 1}
                }
            ) as response:
                return response.status == 200
        else:
            # Fallback to sync
            import requests
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": "ready",
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {"num_predict": 1}
                },
                timeout=60
            )
            return response.status_code == 200
    
    async def generate(self, prompt: str, model: str = None, max_tokens: int = 500) -> str:
        """Generate response from Ollama"""
        model = model or self.model
        
        if AIOHTTP_AVAILABLE and self.session:
            async with self.session.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1
                    }
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                return f"Error: {response.status}"
        else:
            # Fallback to sync
            import requests
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "30m",
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1
                    }
                },
                timeout=180
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            return f"Error: {response.status_code}"


# =============================================================================
# Global instances
# =============================================================================
cache = CacheManager()
ollama = AsyncOllamaClient()


# =============================================================================
# Startup/Shutdown Events
# =============================================================================
@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    await ollama.init()
    print("🚀 StackSense API started")
    
    # Warm up model in background
    asyncio.create_task(ollama.warm_up())


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await ollama.close()
    print("👋 StackSense API shutdown")


# =============================================================================
# API Endpoints
# =============================================================================
@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "StackSense API",
        "version": "0.1.0",
        "status": "running",
        "redis": cache.redis is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """
    Process a chat query with caching.
    
    - Checks cache first (instant response)
    - Falls back to Ollama if not cached
    - Caches result in background
    """
    start = time.time()
    
    # 1. Check cache
    cached_response = cache.get_cached_response(request.workspace, request.query)
    if cached_response:
        return ChatResponse(
            answer=cached_response,
            files_used=[],
            cached=True,
            time_seconds=time.time() - start
        )
    
    # 2. Build prompt with StackSense identity
    from . import prompts
    prompt = prompts.build_chat_prompt(request.query, request.workspace)
    
    # 3. Generate response
    answer = await ollama.generate(
        prompt=prompt,
        model=request.model,
        max_tokens=800
    )
    
    # 4. Cache in background
    background_tasks.add_task(
        cache.cache_response,
        request.workspace,
        request.query,
        answer
    )
    
    return ChatResponse(
        answer=answer,
        files_used=[],
        cached=False,
        time_seconds=time.time() - start
    )


@app.post("/warmup")
async def warmup(request: WarmupRequest):
    """Warm up a model"""
    success = await ollama.warm_up(request.model)
    return {"warmed": success, "model": request.model}


@app.post("/diagram")
async def build_diagram(
    request: DiagramRequest,
    background_tasks: BackgroundTasks
):
    """
    Build or retrieve cached diagram.
    """
    # Check cache first
    if not request.force_rebuild:
        cached = cache.get_diagram(request.workspace)
        if cached:
            return {"diagram": cached, "cached": True}
    
    # Build diagram (async wrapper)
    diagram = await asyncio.to_thread(
        _build_diagram_sync,
        request.workspace
    )
    
    # Cache in background
    background_tasks.add_task(
        cache.cache_diagram,
        request.workspace,
        diagram
    )
    
    return {"diagram": diagram, "cached": False}


@app.delete("/cache/{workspace}")
async def invalidate_cache(workspace: str):
    """Invalidate cache for a workspace"""
    cache.invalidate_diagram(workspace)
    return {"invalidated": True, "workspace": workspace}


# =============================================================================
# Helper Functions
# =============================================================================
def _build_diagram_sync(workspace: str) -> dict:
    """Synchronous diagram building"""
    try:
        from ..diagram_builder import DiagramBuilder
        builder = DiagramBuilder()
        diagram = builder.build_diagram(Path(workspace))
        return diagram
    except Exception as e:
        return {"error": str(e)}
