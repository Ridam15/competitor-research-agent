"""
Performance Optimization System

Advanced performance monitoring, optimization, and caching system for the
Competitor Research Agent.
"""

import time
import functools
import hashlib
import json
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import asyncio
import aiohttp
import sqlite3
from contextlib import contextmanager

from src.utils.logger import logger


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    function_name: str
    execution_time: float
    memory_before: float
    memory_after: float
    timestamp: str
    success: bool
    error_message: Optional[str] = None
    cache_hit: bool = False
    optimization_applied: bool = False


class PerformanceMonitor:
    """Advanced performance monitoring and optimization"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        self.function_stats: Dict[str, Dict[str, float]] = {}
        self.slow_functions: Dict[str, int] = {}
        self.optimization_suggestions: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
        
    def record_performance(self, 
                         function_name: str,
                         execution_time: float,
                         memory_before: float,
                         memory_after: float,
                         success: bool,
                         error_message: Optional[str] = None,
                         cache_hit: bool = False) -> None:
        """Record performance metrics for a function"""
        
        with self._lock:
            metrics = PerformanceMetrics(
                function_name=function_name,
                execution_time=execution_time,
                memory_before=memory_before,
                memory_after=memory_after,
                timestamp=datetime.now().isoformat(),
                success=success,
                error_message=error_message,
                cache_hit=cache_hit
            )
            
            self.metrics.append(metrics)
            
            # Maintain max metrics limit
            if len(self.metrics) > self.max_metrics:
                self.metrics.pop(0)
            
            # Update function statistics
            self._update_function_stats(function_name, execution_time, success, cache_hit)
            
            # Check for slow functions
            if execution_time > 30.0:  # Functions taking more than 30 seconds
                self.slow_functions[function_name] = self.slow_functions.get(function_name, 0) + 1
                self._generate_optimization_suggestions(function_name, execution_time)
    
    def _update_function_stats(self, function_name: str, execution_time: float, 
                             success: bool, cache_hit: bool):
        """Update aggregated statistics for functions"""
        if function_name not in self.function_stats:
            self.function_stats[function_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'cache_hits': 0,
                'cache_hit_rate': 0.0
            }
        
        stats = self.function_stats[function_name]
        stats['total_calls'] += 1
        
        if success:
            stats['successful_calls'] += 1
        else:
            stats['failed_calls'] += 1
        
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['total_calls']
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        
        if cache_hit:
            stats['cache_hits'] += 1
        
        if stats['total_calls'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_calls'] * 100
    
    def _generate_optimization_suggestions(self, function_name: str, execution_time: float):
        """Generate optimization suggestions for slow functions"""
        suggestions = []
        
        if execution_time > 60:
            suggestions.append("Consider implementing caching for this function")
            suggestions.append("Break down function into smaller, more focused operations")
        
        if execution_time > 30:
            suggestions.append("Implement async processing where possible")
            suggestions.append("Add progress indicators for long-running operations")
        
        # Check for specific function types
        if 'search' in function_name.lower():
            suggestions.extend([
                "Optimize search queries for better performance",
                "Implement result pagination",
                "Use parallel search requests"
            ])
        elif 'scrape' in function_name.lower():
            suggestions.extend([
                "Implement concurrent scraping with rate limiting",
                "Cache scraped content to avoid repeated requests",
                "Use lightweight parsers for content extraction"
            ])
        elif 'pdf' in function_name.lower():
            suggestions.extend([
                "Generate PDFs in background tasks",
                "Use streaming for large reports",
                "Optimize image and chart generation"
            ])
        
        self.optimization_suggestions[function_name] = suggestions
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No performance data available for the specified period"}
        
        # Calculate overall statistics
        total_execution_time = sum(m.execution_time for m in recent_metrics)
        avg_execution_time = total_execution_time / len(recent_metrics)
        successful_calls = sum(1 for m in recent_metrics if m.success)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        
        # Find slowest functions
        slowest_calls = sorted(recent_metrics, key=lambda x: x.execution_time, reverse=True)[:10]
        
        # Calculate memory usage
        memory_usage = [m.memory_after - m.memory_before for m in recent_metrics]
        avg_memory_delta = sum(memory_usage) / len(memory_usage) if memory_usage else 0
        
        return {
            "period": f"Last {hours} hours",
            "total_function_calls": len(recent_metrics),
            "successful_calls": successful_calls,
            "success_rate": (successful_calls / len(recent_metrics)) * 100,
            "total_execution_time_seconds": round(total_execution_time, 2),
            "average_execution_time_seconds": round(avg_execution_time, 2),
            "cache_hits": cache_hits,
            "cache_hit_rate": (cache_hits / len(recent_metrics)) * 100,
            "average_memory_delta_mb": round(avg_memory_delta, 2),
            "slowest_functions": [
                {
                    "function": call.function_name,
                    "execution_time": call.execution_time,
                    "timestamp": call.timestamp,
                    "success": call.success,
                    "cache_hit": call.cache_hit
                }
                for call in slowest_calls
            ],
            "function_statistics": dict(self.function_stats),
            "optimization_suggestions": dict(self.optimization_suggestions)
        }


class IntelligentCache:
    """Intelligent caching system with TTL, compression, and smart eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600, cache_dir: str = "cache"):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # In-memory cache for frequently accessed items
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # SQLite for persistent cache metadata
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_database()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'compressions': 0
        }
        
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize SQLite database for cache metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    compressed BOOLEAN DEFAULT FALSE,
                    size_bytes INTEGER DEFAULT 0
                )
            """)
            conn.commit()
    
    def _get_cache_key(self, key: str) -> str:
        """Generate a safe cache key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _get_file_path(self, cache_key: str, compressed: bool = False) -> Path:
        """Get file path for cached data"""
        ext = ".gz" if compressed else ".cache"
        return self.cache_dir / f"{cache_key}{ext}"
    
    def _should_compress(self, data: Any) -> bool:
        """Determine if data should be compressed"""
        # Compress large data or specific types
        serialized_size = len(pickle.dumps(data))
        return serialized_size > 1024  # Compress if larger than 1KB
    
    def _store_data(self, cache_key: str, data: Any, ttl: int) -> bool:
        """Store data to cache with optional compression"""
        try:
            should_compress = self._should_compress(data)
            file_path = self._get_file_path(cache_key, should_compress)
            
            # Serialize data
            serialized_data = pickle.dumps(data)
            
            if should_compress:
                # Compress data
                compressed_data = gzip.compress(serialized_data)
                with open(file_path, 'wb') as f:
                    f.write(compressed_data)
                self.stats['compressions'] += 1
                data_size = len(compressed_data)
            else:
                with open(file_path, 'wb') as f:
                    f.write(serialized_data)
                data_size = len(serialized_data)
            
            # Update database metadata
            expires_at = datetime.now() + timedelta(seconds=ttl)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_metadata 
                    (key, filename, expires_at, compressed, size_bytes, last_accessed)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (cache_key, file_path.name, expires_at, should_compress, data_size))
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store cache data for key {cache_key}: {e}")
            return False
    
    def _load_data(self, cache_key: str) -> Optional[Any]:
        """Load data from cache"""
        try:
            # Check metadata first
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT filename, expires_at, compressed, access_count
                    FROM cache_metadata 
                    WHERE key = ?
                """, (cache_key,))
                result = cursor.fetchone()
            
            if not result:
                return None
            
            filename, expires_at_str, compressed, access_count = result
            
            # Check if expired
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() > expires_at:
                    self._remove_cache_entry(cache_key)
                    return None
            
            # Load data from file
            file_path = self.cache_dir / filename
            if not file_path.exists():
                self._remove_cache_entry(cache_key)
                return None
            
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            if compressed:
                raw_data = gzip.decompress(raw_data)
            
            data = pickle.loads(raw_data)
            
            # Update access statistics
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE cache_metadata 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE key = ?
                """, (cache_key,))
                conn.commit()
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load cache data for key {cache_key}: {e}")
            self._remove_cache_entry(cache_key)
            return None
    
    def _remove_cache_entry(self, cache_key: str):
        """Remove cache entry and associated files"""
        try:
            # Get filename from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT filename FROM cache_metadata WHERE key = ?", (cache_key,))
                result = cursor.fetchone()
                
                if result:
                    filename = result[0]
                    file_path = self.cache_dir / filename
                    
                    # Remove file
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Remove from database
                    conn.execute("DELETE FROM cache_metadata WHERE key = ?", (cache_key,))
                    conn.commit()
                    
                    self.stats['evictions'] += 1
            
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Failed to remove cache entry {cache_key}: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        with self._lock:
            cache_key = self._get_cache_key(key)
            
            # Check memory cache first
            if cache_key in self.memory_cache:
                cache_data = self.memory_cache[cache_key]
                if datetime.now() < cache_data['expires_at']:
                    self.stats['hits'] += 1
                    return cache_data['data']
                else:
                    del self.memory_cache[cache_key]
            
            # Check persistent cache
            data = self._load_data(cache_key)
            if data is not None:
                self.stats['hits'] += 1
                return data
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache"""
        with self._lock:
            ttl = ttl or self.default_ttl
            cache_key = self._get_cache_key(key)
            
            # Store in memory cache for frequently accessed items
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[cache_key] = {
                'data': data,
                'expires_at': expires_at
            }
            
            # Also store persistently
            success = self._store_data(cache_key, data, ttl)
            
            # Manage cache size
            self._enforce_size_limits()
            
            return success
    
    def _enforce_size_limits(self):
        """Enforce cache size limits using LRU eviction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_metadata")
                count = cursor.fetchone()[0]
                
                if count > self.max_size:
                    # Remove oldest, least accessed entries
                    excess_count = count - self.max_size
                    cursor = conn.execute("""
                        SELECT key FROM cache_metadata 
                        ORDER BY last_accessed ASC, access_count ASC 
                        LIMIT ?
                    """, (excess_count,))
                    
                    keys_to_remove = [row[0] for row in cursor.fetchall()]
                    for key in keys_to_remove:
                        self._remove_cache_entry(key)
        
        except Exception as e:
            logger.error(f"Failed to enforce cache size limits: {e}")
    
    def clear(self, pattern: Optional[str] = None):
        """Clear cache entries, optionally matching a pattern"""
        with self._lock:
            try:
                if pattern:
                    # Clear entries matching pattern
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute("SELECT key FROM cache_metadata WHERE key LIKE ?", (f"%{pattern}%",))
                        keys_to_remove = [row[0] for row in cursor.fetchall()]
                else:
                    # Clear all entries
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute("SELECT key FROM cache_metadata")
                        keys_to_remove = [row[0] for row in cursor.fetchall()]
                
                for key in keys_to_remove:
                    self._remove_cache_entry(key)
                
                # Clear memory cache
                if pattern:
                    keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                else:
                    self.memory_cache.clear()
                
                logger.info(f"Cleared {len(keys_to_remove)} cache entries")
                
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT 
                            COUNT(*) as total_entries,
                            SUM(size_bytes) as total_size_bytes,
                            AVG(access_count) as avg_access_count,
                            SUM(CASE WHEN compressed THEN 1 ELSE 0 END) as compressed_entries
                        FROM cache_metadata
                    """)
                    db_stats = cursor.fetchone()
                
                total_entries, total_size_bytes, avg_access_count, compressed_entries = db_stats
                hit_rate = (self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])) * 100 if (self.stats['hits'] + self.stats['misses']) > 0 else 0
                
                return {
                    'total_entries': total_entries or 0,
                    'memory_cache_entries': len(self.memory_cache),
                    'total_size_mb': round((total_size_bytes or 0) / (1024 * 1024), 2),
                    'compressed_entries': compressed_entries or 0,
                    'average_access_count': round(avg_access_count or 0, 2),
                    'hit_rate_percent': round(hit_rate, 2),
                    'cache_hits': self.stats['hits'],
                    'cache_misses': self.stats['misses'],
                    'evictions': self.stats['evictions'],
                    'compressions': self.stats['compressions']
                }
                
            except Exception as e:
                logger.error(f"Failed to get cache stats: {e}")
                return {'error': str(e)}


# Global instances
performance_monitor = PerformanceMonitor()
intelligent_cache = IntelligentCache()


def performance_tracker(cache_key: Optional[str] = None, cache_ttl: int = 3600):
    """
    Decorator for performance tracking and caching
    
    Usage:
        @performance_tracker(cache_key="search_{args[0]}", cache_ttl=1800)
        def search_function(query):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Get memory usage before
            try:
                import psutil
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                memory_before = 0
            
            success = False
            result = None
            error_message = None
            cache_hit = False
            
            try:
                # Check cache if cache_key is provided
                if cache_key:
                    # Format cache key with function arguments
                    formatted_cache_key = cache_key.format(
                        func=func.__name__,
                        args=args,
                        kwargs=kwargs
                    )
                    
                    # Try to get from cache
                    cached_result = intelligent_cache.get(formatted_cache_key)
                    if cached_result is not None:
                        cache_hit = True
                        success = True
                        result = cached_result
                    else:
                        # Execute function and cache result
                        result = func(*args, **kwargs)
                        success = True
                        intelligent_cache.set(formatted_cache_key, result, cache_ttl)
                else:
                    # Execute function without caching
                    result = func(*args, **kwargs)
                    success = True
                
            except Exception as e:
                error_message = str(e)
                raise
            
            finally:
                # Get memory usage after
                try:
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                except (NameError, ImportError):
                    memory_after = memory_before
                
                # Record performance
                execution_time = time.time() - start_time
                performance_monitor.record_performance(
                    function_name=func.__name__,
                    execution_time=execution_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    success=success,
                    error_message=error_message,
                    cache_hit=cache_hit
                )
            
            return result
        return wrapper
    return decorator


def async_batch_processor(batch_size: int = 10, max_workers: int = 5):
    """
    Decorator for processing items in batches asynchronously
    
    Usage:
        @async_batch_processor(batch_size=5, max_workers=3)
        def process_items(items):
            # Function that processes a list of items
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(items: List[Any], *args, **kwargs):
            if not items:
                return []
            
            # Split items into batches
            batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
            results = []
            
            # Process batches in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_batch = {
                    executor.submit(func, batch, *args, **kwargs): batch 
                    for batch in batches
                }
                
                for future in as_completed(future_to_batch):
                    try:
                        batch_result = future.result()
                        results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
                    except Exception as e:
                        logger.error(f"Batch processing failed: {e}")
                        batch = future_to_batch[future]
                        # Try processing items individually as fallback
                        for item in batch:
                            try:
                                individual_result = func([item], *args, **kwargs)
                                results.extend(individual_result if isinstance(individual_result, list) else [individual_result])
                            except Exception as item_error:
                                logger.error(f"Individual item processing failed: {item_error}")
            
            return results
        return wrapper
    return decorator


class ResourceManager:
    """System resource management and optimization"""
    
    def __init__(self):
        self.resource_limits = {
            'max_memory_mb': 2048,
            'max_cpu_percent': 80,
            'max_disk_usage_percent': 90
        }
        self.monitoring_active = False
    
    @contextmanager
    def resource_monitor(self, operation_name: str = "operation"):
        """Context manager for monitoring resource usage during operations"""
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial resource usage
            initial_memory = process.memory_info().rss / 1024 / 1024
            initial_cpu = process.cpu_percent()
            
            logger.info(f"Starting {operation_name} - Memory: {initial_memory:.1f}MB, CPU: {initial_cpu:.1f}%")
            
            start_time = time.time()
            yield
            
            # Get final resource usage
            final_memory = process.memory_info().rss / 1024 / 1024
            final_cpu = process.cpu_percent()
            execution_time = time.time() - start_time
            
            logger.info(f"Completed {operation_name} in {execution_time:.2f}s - "
                       f"Memory: {final_memory:.1f}MB (Δ{final_memory-initial_memory:+.1f}MB), "
                       f"CPU: {final_cpu:.1f}%")
            
            # Check for resource warnings
            if final_memory > self.resource_limits['max_memory_mb']:
                logger.warning(f"High memory usage detected: {final_memory:.1f}MB")
            
            if final_cpu > self.resource_limits['max_cpu_percent']:
                logger.warning(f"High CPU usage detected: {final_cpu:.1f}%")
        
        except ImportError:
            logger.warning("psutil not available for resource monitoring")
            yield
        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")
            yield


# Global resource manager
resource_manager = ResourceManager()
