#!/usr/bin/env python3
"""
Tests for performance profiler module
"""

import pytest
import time

from lmapp.utils.profiler import (
    PerformanceProfiler,
    OperationMetrics,
    get_profiler,
    profile_operation,
    enable_profiling,
    disable_profiling,
)


class TestOperationMetrics:
    """Test OperationMetrics dataclass"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = OperationMetrics(
            operation_name="test_op",
            start_time=0.0,
            end_time=1.0
        )
        assert metrics.operation_name == "test_op"
        assert metrics.duration_ms == 1000.0
        assert metrics.success is True
    
    def test_metrics_to_dict(self):
        """Test metrics serialization"""
        metrics = OperationMetrics(
            operation_name="test_op",
            start_time=0.0,
            end_time=0.1,
            memory_delta_bytes=1024 * 1024,
        )
        data = metrics.to_dict()
        assert data["operation"] == "test_op"
        assert data["duration_ms"] == 100.0
        assert data["memory_delta_kb"] > 0
        assert data["success"] is True


class TestPerformanceProfiler:
    """Test PerformanceProfiler"""
    
    def test_profiler_initialization(self):
        """Test profiler initialization"""
        profiler = PerformanceProfiler()
        assert profiler.enable_memory is True
        assert profiler.metrics == {}
        assert profiler.cache_stats['hits'] == 0
        assert profiler.cache_stats['misses'] == 0
    
    def test_track_operation_success(self):
        """Test successful operation tracking"""
        profiler = PerformanceProfiler()
        
        with profiler.track_operation("test_op"):
            time.sleep(0.01)
        
        assert len(profiler.metrics["test_op"]) == 1
        metrics = profiler.metrics["test_op"][0]
        assert metrics.success is True
        assert metrics.duration_ms >= 10  # At least 10ms
    
    def test_track_operation_failure(self):
        """Test failed operation tracking"""
        profiler = PerformanceProfiler()
        
        with pytest.raises(ValueError):
            with profiler.track_operation("test_op"):
                raise ValueError("Test error")
        
        metrics = profiler.metrics["test_op"][0]
        assert metrics.success is False
        assert metrics.error_message == "Test error"
    
    def test_cache_hit_recording(self):
        """Test cache hit recording"""
        profiler = PerformanceProfiler()
        
        profiler.record_cache_hit("query1")
        profiler.record_cache_hit("query2")
        profiler.record_cache_miss("query3")
        
        assert profiler.cache_stats['hits'] == 2
        assert profiler.cache_stats['misses'] == 1
        assert profiler.cache_stats['total_queries'] == 3
        assert profiler.cache_stats['hit_rate'] == pytest.approx(66.67, rel=0.01)
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        profiler = PerformanceProfiler()
        
        for _ in range(10):
            profiler.record_cache_hit("q")
        for _ in range(40):
            profiler.record_cache_miss("q")
        
        assert profiler.cache_stats['hit_rate'] == 20.0
    
    def test_get_summary(self):
        """Test performance summary generation"""
        profiler = PerformanceProfiler()
        
        with profiler.track_operation("op1"):
            time.sleep(0.01)
        
        with profiler.track_operation("op1"):
            time.sleep(0.01)
        
        profiler.record_cache_hit("q")
        profiler.record_cache_hit("q")
        
        summary = profiler.get_summary()
        
        assert 'uptime_seconds' in summary
        assert 'operations' in summary
        assert 'cache_performance' in summary
        assert 'memory_usage' in summary
        assert 'op1' in summary['operations']
        assert summary['operations']['op1']['count'] == 2
        assert summary['operations']['op1']['total_ms'] >= 20
        assert summary['cache_performance']['hit_rate'] == 100.0
    
    def test_summary_with_multiple_operations(self):
        """Test summary with multiple different operations"""
        profiler = PerformanceProfiler()
        
        with profiler.track_operation("fast_op"):
            time.sleep(0.001)
        
        with profiler.track_operation("slow_op"):
            time.sleep(0.01)
        
        summary = profiler.get_summary()
        
        assert 'fast_op' in summary['operations']
        assert 'slow_op' in summary['operations']
        assert summary['operations']['slow_op']['avg_ms'] > summary['operations']['fast_op']['avg_ms']
    
    def test_profile_function_decorator(self):
        """Test function profiling decorator"""
        profiler = PerformanceProfiler()
        
        @profiler.profile_function("custom_name")
        def test_func():
            time.sleep(0.001)
            return "result"
        
        result = test_func()
        
        assert result == "result"
        assert "custom_name" in profiler.metrics
        assert len(profiler.metrics["custom_name"]) == 1
    
    def test_memory_tracking(self):
        """Test memory tracking"""
        profiler = PerformanceProfiler(enable_memory_tracking=True)
        
        with profiler.track_operation("mem_test"):
            # Allocate some memory
            _ = [0] * 1000000
        
        metrics = profiler.metrics["mem_test"][0]
        # Memory delta should be tracked
        assert metrics.memory_delta_bytes >= 0
    
    def test_memory_tracking_disabled(self):
        """Test with memory tracking disabled"""
        profiler = PerformanceProfiler(enable_memory_tracking=False)
        
        with profiler.track_operation("no_mem_test"):
            time.sleep(0.001)
        
        metrics = profiler.metrics["no_mem_test"][0]
        assert metrics.memory_start_bytes == 0
        assert metrics.memory_end_bytes == 0


class TestGlobalProfiler:
    """Test global profiler functions"""
    
    def test_get_profiler_singleton(self):
        """Test global profiler singleton"""
        profiler1 = get_profiler()
        profiler2 = get_profiler()
        
        assert profiler1 is profiler2
    
    def test_enable_disable_profiling(self):
        """Test enable/disable profiling"""
        disable_profiling()
        
        enable_profiling()
        profiler = get_profiler()
        
        assert profiler is not None
        assert profiler.enable_memory is True
    
    def test_profile_operation_decorator(self):
        """Test profile_operation decorator"""
        @profile_operation("decorated_op")
        def test_func():
            time.sleep(0.001)
            return "done"
        
        result = test_func()
        
        assert result == "done"
        profiler = get_profiler()
        assert "decorated_op" in profiler.metrics


class TestProfilerReporting:
    """Test profiler reporting"""
    
    def test_print_report_with_operations(self, capsys):
        """Test printing report with operations"""
        profiler = PerformanceProfiler()
        
        with profiler.track_operation("op1"):
            time.sleep(0.001)
        
        with profiler.track_operation("op2"):
            time.sleep(0.002)
        
        profiler.print_report()
        
        captured = capsys.readouterr()
        assert "Performance Report" in captured.out
        assert "op1" in captured.out
        assert "op2" in captured.out
    
    def test_export_metrics(self, tmp_path):
        """Test exporting metrics to file"""
        profiler = PerformanceProfiler()
        
        with profiler.track_operation("test_op"):
            time.sleep(0.001)
        
        output_file = tmp_path / "metrics.json"
        profiler.export_metrics(str(output_file))
        
        assert output_file.exists()
        
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert 'timestamp' in data
        assert 'operations' in data
        assert 'test_op' in data['operations']

