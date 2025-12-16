"""
Response Caching Module for LMAPP

Caches LLM responses to provide instant answers for repeated queries.
Uses TTL (Time-To-Live) based eviction and SQLite storage for persistence.
"""

import hashlib
import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from loguru import logger


class ResponseCache:
    """
    Manages caching of LLM responses with TTL-based eviction.
    
    Features:
    - Persistent SQLite storage
    - TTL-based automatic expiration
    - Content hash-based key generation
    - Statistics tracking (hit rate, cache size)
    """
    
    DEFAULT_TTL_HOURS = 24
    CACHE_DB_NAME = "response_cache.db"
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = DEFAULT_TTL_HOURS):
        """
        Initialize the response cache.
        
        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.lmapp/cache/
            ttl_hours: Time-to-live for cached responses in hours
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".lmapp" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / self.CACHE_DB_NAME
        self.ttl = timedelta(hours=ttl_hours)
        
        # Initialize database
        self._init_database()
        
        logger.debug(f"Cache initialized at {self.db_path} with TTL={ttl_hours}h")
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE NOT NULL,
                    query_text TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP NOT NULL
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_hash ON cache(query_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
            """)
            
            conn.commit()
            conn.close()
            
            logger.debug("Cache database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise
    
    @staticmethod
    def _hash_query(query: str, model: str, backend: str, temperature: float) -> str:
        """
        Generate a hash key for a query.
        
        Considers query text, model, backend, and temperature to ensure
        different configurations have separate cache entries.
        """
        key_str = f"{query.strip()}|{model}|{backend}|{temperature}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, 
            query: str,
            model: str,
            backend: str,
            temperature: float = 0.7) -> Optional[str]:
        """
        Retrieve a cached response if available and not expired.
        
        Args:
            query: The user's query
            model: The LLM model used
            backend: The backend system (ollama, llamafile, etc)
            temperature: The temperature parameter used
        
        Returns:
            The cached response, or None if not cached or expired
        """
        query_hash = self._hash_query(query, model, backend, temperature)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for valid cache entry
            cursor.execute("""
                SELECT response, expires_at FROM cache
                WHERE query_hash = ?
            """, (query_hash,))
            
            result = cursor.fetchone()
            
            if result is None:
                conn.close()
                return None
            
            response, expires_at = result
            expires_dt = datetime.fromisoformat(expires_at)
            
            # Check if expired
            if datetime.now() > expires_dt:
                # Delete expired entry
                cursor.execute("DELETE FROM cache WHERE query_hash = ?", (query_hash,))
                conn.commit()
                conn.close()
                logger.debug(f"Cache expired for query hash {query_hash[:8]}...")
                return None
            
            # Update access stats
            cursor.execute("""
                UPDATE cache
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE query_hash = ?
            """, (datetime.now().isoformat(), query_hash))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Cache hit for query hash {query_hash[:8]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to retrieve from cache: {e}")
            return None
    
    def set(self,
            query: str,
            response: str,
            model: str,
            backend: str,
            temperature: float = 0.7) -> bool:
        """
        Store a response in the cache.
        
        Args:
            query: The user's query
            response: The LLM response to cache
            model: The LLM model used
            backend: The backend system
            temperature: The temperature parameter used
        
        Returns:
            True if successful, False otherwise
        """
        query_hash = self._hash_query(query, model, backend, temperature)
        now = datetime.now()
        expires_at = now + self.ttl
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache
                (query_hash, query_text, response, model, backend, temperature,
                 created_at, expires_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query_hash,
                query,
                response,
                model,
                backend,
                temperature,
                now.isoformat(),
                expires_at.isoformat(),
                1,
                now.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Cached response for query hash {query_hash[:8]}... (expires in {self.ttl})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store in cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats (size, hit rate, etc)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count total entries
            cursor.execute("SELECT COUNT(*) FROM cache")
            total_entries = cursor.fetchone()[0]
            
            # Count expired entries
            cursor.execute("""
                SELECT COUNT(*) FROM cache
                WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            expired_entries = cursor.fetchone()[0]
            
            # Get total accesses
            cursor.execute("SELECT SUM(access_count) FROM cache")
            total_accesses = cursor.fetchone()[0] or 0
            
            # Get cache size
            cache_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            conn.close()
            
            hit_rate = total_accesses / max(1, total_entries) if total_entries > 0 else 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "total_accesses": total_accesses,
                "hit_rate": round(hit_rate, 2),
                "cache_size_mb": round(cache_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {}
    
    def clear(self, expired_only: bool = True) -> int:
        """
        Clear cache entries.
        
        Args:
            expired_only: If True, only remove expired entries.
                         If False, clear entire cache.
        
        Returns:
            Number of entries removed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if expired_only:
                cursor.execute("""
                    DELETE FROM cache
                    WHERE expires_at < ?
                """, (datetime.now().isoformat(),))
            else:
                cursor.execute("DELETE FROM cache")
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} cache entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    def get_by_query(self, query: str) -> list[Dict[str, Any]]:
        """
        Get all cached entries for a specific query text.
        
        Useful for finding all cached variants of the same question.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT query_hash, model, backend, temperature, created_at, access_count
                FROM cache
                WHERE query_text = ?
                ORDER BY last_accessed DESC
            """, (query.strip(),))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "hash": r[0],
                    "model": r[1],
                    "backend": r[2],
                    "temperature": r[3],
                    "created": r[4],
                    "access_count": r[5]
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to query cache: {e}")
            return []


__all__ = ['ResponseCache']
