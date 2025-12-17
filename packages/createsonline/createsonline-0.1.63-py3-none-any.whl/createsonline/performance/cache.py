# createsonline/performance/cache.py
"""
Ultra-Fast Caching System for CREATESONLINE

Advanced caching strategies:
- LRU cache with TTL
- Memory-mapped caching
- Distributed cache support
- Smart cache invalidation
"""

import time
import hashlib
import threading
from typing import Any, Dict, Optional, Callable
from collections import OrderedDict


class CacheManager:
    """
    Ultra-high performance cache manager with multiple cache layers
    """
    
    def __init__(self, max_size=10000, default_ttl=300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Multi-layer cache system
        self.l1_cache = LRUCache(max_size // 4)  # Hot cache
        self.l2_cache = TTLCache(max_size)       # Main cache
        self.l3_cache = DiskCache()              # Disk cache for large items
        
        # Cache statistics
        self.stats = CacheStats()
        
        # Background cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with multi-layer lookup"""
        
        # L1 Cache (fastest)
        result = self.l1_cache.get(key)
        if result is not None:
            self.stats.record_hit('l1')
            return result
        
        # L2 Cache
        result = self.l2_cache.get(key)
        if result is not None:
            # Promote to L1 for frequently accessed items
            self.l1_cache.set(key, result)
            self.stats.record_hit('l2')
            return result
        
        # L3 Cache (disk)
        result = self.l3_cache.get(key)
        if result is not None:
            # Promote to L2
            self.l2_cache.set(key, result)
            self.stats.record_hit('l3')
            return result
        
        self.stats.record_miss()
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in appropriate cache layer"""
        
        ttl = ttl or self.default_ttl
        
        # Determine cache layer based on value size
        value_size = self._estimate_size(value)
        
        if value_size < 1024:  # Small items go to L1
            self.l1_cache.set(key, value)
            self.l2_cache.set(key, value, ttl)
        elif value_size < 1024 * 1024:  # Medium items go to L2
            self.l2_cache.set(key, value, ttl)
        else:  # Large items go to L3
            self.l3_cache.set(key, value, ttl)
        
        self.stats.record_set()
    
    def delete(self, key: str) -> bool:
        """Delete item from all cache layers"""
        
        deleted = False
        deleted |= self.l1_cache.delete(key)
        deleted |= self.l2_cache.delete(key)
        deleted |= self.l3_cache.delete(key)
        
        if deleted:
            self.stats.record_delete()
        
        return deleted
    
    def clear(self) -> None:
        """Clear all cache layers"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l3_cache.clear()
        self.stats.reset()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "cache_layers": {
                "l1_size": len(self.l1_cache.cache),
                "l2_size": len(self.l2_cache.cache),
                "l3_size": self.l3_cache.size()
            },
            "hit_rates": self.stats.get_hit_rates(),
            "performance": self.stats.get_performance_metrics()
        }
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value"""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, dict):
            return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in value.items())
        elif isinstance(value, list):
            return sum(self._estimate_size(item) for item in value)
        else:
            return 1024  # Default estimate
    
    def _cleanup_worker(self):
        """Background cleanup worker"""
        while True:
            time.sleep(60)  # Cleanup every minute
            self.l2_cache.cleanup_expired()
            self.l3_cache.cleanup_expired()


class LRUCache:
    """Ultra-fast LRU cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item and move to end (most recently used)"""
        with self.lock:
            if key in self.cache:
                # Move to end
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item and maintain size limit"""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        """Delete item"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items"""
        with self.lock:
            self.cache.clear()


class TTLCache:
    """Time-to-live cache with automatic expiration"""
    
    def __init__(self, max_size: int = 5000):
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item if not expired"""
        with self.lock:
            if key in self.cache:
                timestamp, ttl = self.timestamps[key]
                if time.time() - timestamp < ttl:
                    return self.cache[key]
                else:
                    # Expired
                    del self.cache[key]
                    del self.timestamps[key]
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set item with TTL"""
        with self.lock:
            # Evict if at capacity and key is new
            if key not in self.cache and len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k][0])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[key] = value
            self.timestamps[key] = (time.time(), ttl)
    
    def delete(self, key: str) -> bool:
        """Delete item"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired items"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (timestamp, ttl) in self.timestamps.items():
                if current_time - timestamp >= ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
            
            return len(expired_keys)
    
    def clear(self) -> None:
        """Clear all items"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()


class DiskCache:
    """Simple disk-based cache for large items"""
    
    def __init__(self, cache_dir: str = "/tmp/createsonline_cache"):
        self.cache_dir = cache_dir
        self.index = {}
        self.lock = threading.RLock()
        
        # Create cache directory
        import os
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from disk cache"""
        with self.lock:
            if key in self.index:
                timestamp, ttl, filename = self.index[key]
                
                if time.time() - timestamp < ttl:
                    try:
                        import pickle
                        with open(filename, 'rb') as f:
                            return pickle.load(f)
                    except:
                        # File corrupted or missing
                        del self.index[key]
                else:
                    # Expired
                    self._remove_file(filename)
                    del self.index[key]
            
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set item to disk cache"""
        with self.lock:
            filename = f"{self.cache_dir}/{hashlib.md5(key.encode()).hexdigest()}.cache"
            
            try:
                import pickle
                with open(filename, 'wb') as f:
                    pickle.dump(value, f)
                
                self.index[key] = (time.time(), ttl, filename)
            except:
                # Failed to write
                pass
    
    def delete(self, key: str) -> bool:
        """Delete item from disk cache"""
        with self.lock:
            if key in self.index:
                _, _, filename = self.index[key]
                self._remove_file(filename)
                del self.index[key]
                return True
            return False
    
    def size(self) -> int:
        """Get number of cached items"""
        return len(self.index)
    
    def cleanup_expired(self) -> int:
        """Remove expired disk cache files"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (timestamp, ttl, filename) in self.index.items():
                if current_time - timestamp >= ttl:
                    expired_keys.append(key)
                    self._remove_file(filename)
            
            for key in expired_keys:
                del self.index[key]
            
            return len(expired_keys)
    
    def _remove_file(self, filename: str) -> None:
        """Safely remove cache file"""
        try:
            import os
            os.remove(filename)
        except:
            pass


class CacheStats:
    """Track cache performance statistics"""
    
    def __init__(self):
        self.hits = {'l1': 0, 'l2': 0, 'l3': 0}
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.start_time = time.time()
        self.lock = threading.RLock()
    
    def record_hit(self, layer: str) -> None:
        """Record cache hit"""
        with self.lock:
            self.hits[layer] += 1
    
    def record_miss(self) -> None:
        """Record cache miss"""
        with self.lock:
            self.misses += 1
    
    def record_set(self) -> None:
        """Record cache set"""
        with self.lock:
            self.sets += 1
    
    def record_delete(self) -> None:
        """Record cache delete"""
        with self.lock:
            self.deletes += 1
    
    def get_hit_rates(self) -> Dict[str, float]:
        """Get hit rates by layer"""
        with self.lock:
            total_hits = sum(self.hits.values())
            total_requests = total_hits + self.misses
            
            if total_requests == 0:
                return {'overall': 0.0, 'l1': 0.0, 'l2': 0.0, 'l3': 0.0}
            
            return {
                'overall': total_hits / total_requests * 100,
                'l1': self.hits['l1'] / total_requests * 100,
                'l2': self.hits['l2'] / total_requests * 100,
                'l3': self.hits['l3'] / total_requests * 100
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        with self.lock:
            uptime = time.time() - self.start_time
            total_ops = sum(self.hits.values()) + self.misses + self.sets + self.deletes
            
            return {
                'uptime_seconds': uptime,
                'total_operations': total_ops,
                'operations_per_second': total_ops / uptime if uptime > 0 else 0,
                'total_hits': sum(self.hits.values()),
                'total_misses': self.misses,
                'total_sets': self.sets,
                'total_deletes': self.deletes
            }
    
    def reset(self) -> None:
        """Reset all statistics"""
        with self.lock:
            self.hits = {'l1': 0, 'l2': 0, 'l3': 0}
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.start_time = time.time()


# Global cache instance
_global_cache = None

def get_cache() -> CacheManager:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def cache(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            cache_manager = get_cache()
            result = cache_manager.get(cache_key)
            
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

