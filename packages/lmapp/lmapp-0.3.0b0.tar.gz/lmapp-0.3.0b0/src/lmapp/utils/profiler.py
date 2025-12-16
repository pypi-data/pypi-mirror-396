#!/usr/bin/env python3
"""
Performance Profiling Module for LMAPP
Tracks execution time, memory usage, cache hit rates, and identifies bottlenecks
"""

import time
import psutil
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
from datetime import datetime

from lmapp.utils.logging import logger


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    memory_start_bytes: int = 0
    memory_end_bytes: int = 0
    memory_delta_bytes: int = 0
    cpu_percent: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    call_count: int = 1
    
    def __post_init__(self):
        self._update_duration()
    
    def _update_duration(self):
        if self.end_time:
            self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation_name,
            "duration_ms": round(self.duration_ms, 2),
            "memory_delta_kb": round(self.memory_delta_bytes / 1024, 2),
            "cpu_percent": round(self.cpu_percent, 1),
            "success": self.success,
            "calls": self.call_count,
        }


class PerformanceProfiler:
    """
    Performance profiling and monitoring
    Tracks execution time, memory usage, and cache performance
    """
    
    def __init__(self, enable_memory_tracking: bool = True):
        """
        Initialize profiler
        
        Args:
            enable_memory_tracking: Whether to track memory usage
        """
        self.enable_memory = enable_memory_tracking
        self.metrics: Dict[str, List[OperationMetrics]] = defaultdict(list)
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'hit_rate': 0.0,
            'total_queries': 0,
        }
    
    @contextmanager
    def track_operation(self, operation_name: str):
        """
        Context manager for tracking operation performance
        
        Args:
            operation_name: Name of the operation
        """
        metrics = OperationMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            memory_start_bytes=self.process.memory_info().rss if self.enable_memory else 0,
        )
        
        try:
            start_cpu = self.process.cpu_percent()
            yield metrics
            metrics.end_time = time.time()
            metrics.cpu_percent = self.process.cpu_percent() - start_cpu
            metrics.success = True
        except Exception as e:
            metrics.end_time = time.time()
            metrics.success = False
            metrics.error_message = str(e)
            raise
        finally:
            if self.enable_memory:
                metrics.memory_end_bytes = self.process.memory_info().rss
                metrics.memory_delta_bytes = metrics.memory_end_bytes - metrics.memory_start_bytes
            
            # Ensure duration is calculated
            if metrics.end_time:
                metrics._update_duration()
            
            self.metrics[operation_name].append(metrics)
            logger.debug(f"Profiled {operation_name}: {metrics.duration_ms:.2f}ms")
    
    def profile_function(self, func: Optional[str] = None) -> Callable:
        """
        Decorator for profiling function execution
        
        Args:
            func: Function name (uses actual function name if not provided)
        """
        def decorator(f: Callable) -> Callable:
            func_name = func or f.__name__
            
            @wraps(f)
            def wrapper(*args, **kwargs):
                with self.track_operation(func_name):
                    return f(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def record_cache_hit(self, query: str):
        """Record a cache hit"""
        self.cache_stats['hits'] += 1
        self.cache_stats['total_queries'] += 1
        self._update_hit_rate()
    
    def record_cache_miss(self, query: str):
        """Record a cache miss"""
        self.cache_stats['misses'] += 1
        self.cache_stats['total_queries'] += 1
        self._update_hit_rate()
    
    def _update_hit_rate(self):
        """Update cache hit rate"""
        total = self.cache_stats['total_queries']
        if total > 0:
            self.cache_stats['hit_rate'] = (
                self.cache_stats['hits'] / total * 100
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary
        
        Returns:
            Dictionary with performance metrics
        """
        summary = {
            'uptime_seconds': time.time() - self.start_time,
            'operations': {},
            'cache_performance': self.cache_stats,
            'memory_usage': self._get_memory_summary(),
        }
        
        for op_name, metrics_list in self.metrics.items():
            if metrics_list:
                durations = [m.duration_ms for m in metrics_list]
                memory_deltas = [m.memory_delta_bytes for m in metrics_list]
                
                summary['operations'][op_name] = {
                    'count': len(metrics_list),
                    'total_ms': sum(durations),
                    'avg_ms': sum(durations) / len(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'total_memory_kb': sum(memory_deltas) / 1024 if self.enable_memory else 0,
                    'success_rate': sum(1 for m in metrics_list if m.success) / len(metrics_list) * 100,
                }
        
        return summary
    
    def _get_memory_summary(self) -> Dict[str, float]:
        """Get memory usage summary"""
        try:
            mem_info = self.process.memory_info()
            return {
                'rss_mb': mem_info.rss / (1024 * 1024),
                'vms_mb': mem_info.vms / (1024 * 1024),
                'percent': self.process.memory_percent(),
            }
        except Exception as e:
            logger.debug(f"Could not get memory info: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
    
    def print_report(self, top_n: int = 10):
        """
        Print performance report
        
        Args:
            top_n: Number of top operations to show
        """
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("LMAPP Performance Report")
        print("="*80)
        
        print(f"\nUptime: {summary['uptime_seconds']:.1f}s")
        
        # Cache performance
        cache = summary['cache_performance']
        print(f"\nCache Performance:")
        print(f"  Hits: {cache['hits']}")
        print(f"  Misses: {cache['misses']}")
        print(f"  Hit Rate: {cache['hit_rate']:.1f}%")
        
        # Memory usage
        mem = summary['memory_usage']
        print(f"\nMemory Usage:")
        print(f"  RSS: {mem['rss_mb']:.1f} MB")
        print(f"  VMS: {mem['vms_mb']:.1f} MB")
        print(f"  Process: {mem['percent']:.1f}%")
        
        # Top operations
        if summary['operations']:
            print(f"\nTop {top_n} Operations by Total Time:")
            print(f"{'Operation':<30} {'Count':>6} {'Total':>8} {'Avg':>8} {'Min':>8} {'Max':>8}")
            print("-" * 80)
            
            sorted_ops = sorted(
                summary['operations'].items(),
                key=lambda x: x[1]['total_ms'],
                reverse=True
            )
            
            for op_name, metrics in sorted_ops[:top_n]:
                print(
                    f"{op_name:<30} "
                    f"{metrics['count']:>6d} "
                    f"{metrics['total_ms']:>7.1f}ms "
                    f"{metrics['avg_ms']:>7.1f}ms "
                    f"{metrics['min_ms']:>7.1f}ms "
                    f"{metrics['max_ms']:>7.1f}ms"
                )
        
        print("\n" + "="*80 + "\n")
    
    def export_metrics(self, filename: str):
        """
        Export metrics to JSON file
        
        Args:
            filename: Output filename
        """
        import json
        
        summary = self.get_summary()
        summary['timestamp'] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {filename}")


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get or create global profiler instance"""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def profile_operation(operation_name: str):
    """Decorator to profile an operation"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            profiler = get_profiler()
            with profiler.track_operation(operation_name or f.__name__):
                return f(*args, **kwargs)
        return wrapper
    return decorator


def enable_profiling():
    """Enable global profiling"""
    global _global_profiler
    _global_profiler = PerformanceProfiler(enable_memory_tracking=True)
    logger.info("Performance profiling enabled")


def disable_profiling():
    """Disable global profiling"""
    global _global_profiler
    _global_profiler = None
    logger.info("Performance profiling disabled")


def print_profiler_report(top_n: int = 10):
    """Print profiler report"""
    profiler = get_profiler()
    profiler.print_report(top_n)

