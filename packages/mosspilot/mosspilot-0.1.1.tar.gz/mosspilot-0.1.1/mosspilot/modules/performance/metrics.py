"""
Moss 性能指标收集模块
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from mosspilot.core.monitoring import Logger


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    name: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.logger = Logger()
        self.metrics: List[PerformanceMetric] = []
        self.response_times: List[float] = []
        self.request_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start_collection(self) -> None:
        """开始收集指标"""
        self.start_time = time.time()
        self.logger.info("开始收集性能指标")
    
    def stop_collection(self) -> None:
        """停止收集指标"""
        self.end_time = time.time()
        self.logger.info("停止收集性能指标")
    
    def record_response_time(self, response_time: float, endpoint: str = "default") -> None:
        """记录响应时间"""
        self.response_times.append(response_time)
        self.add_metric("response_time", response_time, "ms", {"endpoint": endpoint})
    
    def record_request(self, endpoint: str, method: str = "GET") -> None:
        """记录请求"""
        key = f"{method} {endpoint}"
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        self.add_metric("request_count", 1, "count", {"endpoint": endpoint, "method": method})
    
    def record_error(self, endpoint: str, error_type: str, method: str = "GET") -> None:
        """记录错误"""
        key = f"{method} {endpoint} {error_type}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        self.add_metric("error_count", 1, "count", {
            "endpoint": endpoint, 
            "method": method, 
            "error_type": error_type
        })
    
    def add_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None) -> None:
        """添加自定义指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def get_response_time_stats(self) -> Dict[str, float]:
        """获取响应时间统计"""
        if not self.response_times:
            return {}
        
        return {
            "min": min(self.response_times),
            "max": max(self.response_times),
            "avg": statistics.mean(self.response_times),
            "median": statistics.median(self.response_times),
            "p95": self._percentile(self.response_times, 95),
            "p99": self._percentile(self.response_times, 99)
        }
    
    def get_throughput(self) -> float:
        """获取吞吐量（请求/秒）"""
        if not self.start_time or not self.end_time:
            return 0.0
        
        duration = self.end_time - self.start_time
        total_requests = sum(self.request_counts.values())
        return total_requests / duration if duration > 0 else 0.0
    
    def get_error_rate(self) -> float:
        """获取错误率"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        return (total_errors / total_requests * 100) if total_requests > 0 else 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        
        return {
            "duration": duration,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "throughput": self.get_throughput(),
            "error_rate": self.get_error_rate(),
            "response_time_stats": self.get_response_time_stats(),
            "request_breakdown": self.request_counts,
            "error_breakdown": self.error_counts
        }
    
    def export_metrics(self, format_type: str = "json") -> str:
        """导出指标数据"""
        summary = self.get_summary()
        
        if format_type == "json":
            import json
            return json.dumps(summary, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            return self._export_csv(summary)
        else:
            return str(summary)
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _export_csv(self, summary: Dict[str, Any]) -> str:
        """导出CSV格式"""
        lines = ["指标,值,单位"]
        
        lines.append(f"总请求数,{summary['total_requests']},个")
        lines.append(f"总错误数,{summary['total_errors']},个")
        lines.append(f"吞吐量,{summary['throughput']:.2f},请求/秒")
        lines.append(f"错误率,{summary['error_rate']:.2f},%")
        
        if summary['response_time_stats']:
            stats = summary['response_time_stats']
            lines.append(f"最小响应时间,{stats['min']:.2f},ms")
            lines.append(f"最大响应时间,{stats['max']:.2f},ms")
            lines.append(f"平均响应时间,{stats['avg']:.2f},ms")
            lines.append(f"中位数响应时间,{stats['median']:.2f},ms")
            lines.append(f"95%响应时间,{stats['p95']:.2f},ms")
            lines.append(f"99%响应时间,{stats['p99']:.2f},ms")
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """重置所有指标"""
        self.metrics.clear()
        self.response_times.clear()
        self.request_counts.clear()
        self.error_counts.clear()
        self.start_time = None
        self.end_time = None
        self.logger.info("性能指标已重置")


class MetricsCollector:
    """全局指标收集器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metrics = PerformanceMetrics()
        return cls._instance
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取指标实例"""
        return self.metrics
    
    def reset_metrics(self) -> None:
        """重置指标"""
        self.metrics.reset()


# 全局指标收集器实例
metrics_collector = MetricsCollector()