# infrastructure/cache.py
"""
Analysis Cache - Simplified
===========================

Responsibilities:
- Cache analysis results
- Check TTL
- Clean expired entries
"""

import hashlib
import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalysisCache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = ".security_cache", ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Cache directory path
            ttl_hours: Time to live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        
        # Create directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean expired on init
        self._cleanup_expired()
        
        logger.info(f"💾 Cache initialized: {cache_dir} (TTL: {ttl_hours}h)")
    
    def get(
        self,
        content: str,
        language: Optional[str] = None,
        tool_hint: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached result
        
        Args:
            content: File content (used for key)
            language: Programming language
            tool_hint: Tool hint
        
        Returns:
            Cached data or None if not found/expired
        """
        try:
            cache_key = self._generate_key(content, language, tool_hint)
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            # Check exists
            if not cache_file.exists():
                return None
            
            # Check TTL
            file_age = datetime.now() - datetime.fromtimestamp(
                cache_file.stat().st_mtime
            )
            
            if file_age > timedelta(hours=self.ttl_hours):
                logger.debug(f"Cache expired: {cache_key}")
                cache_file.unlink()
                return None
            
            # Load data
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"✅ Cache hit: {cache_key}")
            return data
            
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
            return None
    
    def put(
        self,
        content: str,
        data: Dict[str, Any],
        language: Optional[str] = None,
        tool_hint: Optional[str] = None
    ) -> None:
        """
        Store result in cache
        
        Args:
            content: File content (used for key)
             Data to cache
            language: Programming language
            tool_hint: Tool hint
        """
        try:
            cache_key = self._generate_key(content, language, tool_hint)
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            # Write data
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"💾 Cached: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    def clear(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        count = 0
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {cache_file}: {e}")
        
        logger.info(f"🗑️  Cache cleared: {count} entries")
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.cache"))
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "total_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_hours
        }
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    def _generate_key(
        self,
        content: str,
        language: Optional[str],
        tool_hint: Optional[str]
    ) -> str:
        """Generate cache key from content hash"""
        key_data = f"{content}|{language or ''}|{tool_hint or ''}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)
            removed = 0
            
            for cache_file in self.cache_dir.glob("*.cache"):
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    removed += 1
            
            if removed > 0:
                logger.info(f"🗑️  Cleaned {removed} expired cache entries")
                
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {e}")
