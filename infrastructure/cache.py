# infrastructure/cache.py
import hashlib
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AnalysisCache:
    """Cache optimizado para resultados de análisis"""
    
    def __init__(self, cache_dir: str = ".security_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(exist_ok=True)
        self._cleanup_expired()
    
    def _get_cache_key(self, content: str, language: Optional[str], tool_hint: Optional[str]) -> str:
        """Generate cache key from content hash"""
        key_data = f"{content}|{language or ''}|{tool_hint or ''}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def get(self, content: str, language: Optional[str] = None, 
            tool_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get from cache with TTL check"""
        try:
            cache_key = self._get_cache_key(content, language, tool_hint)
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            if not cache_file.exists():
                return None
            
            # Check TTL
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(hours=self.ttl_hours):
                cache_file.unlink()
                return None
            
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
            return None
    
    def put(self, content: str, data: Dict[str, Any], 
            language: Optional[str] = None, tool_hint: Optional[str] = None) -> None:
        """Store in cache"""
        try:
            cache_key = self._get_cache_key(content, language, tool_hint)
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
                
            logger.debug(f"Cached result: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    def _cleanup_expired(self) -> None:
        """Clean up expired cache files"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)
            
            for cache_file in self.cache_dir.glob("*.cache"):
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {e}")
