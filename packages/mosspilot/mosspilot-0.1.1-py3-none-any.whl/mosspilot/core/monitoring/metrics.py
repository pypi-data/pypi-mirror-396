"""
MossPilot 指标收集器
"""

import time
import json
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from mosspilot.core.config import settings
from mosspilot.core.monitoring.logger import Logger


@dataclass
class Metric:
    """指标数据类"""
    name: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.logger = Logger("metrics")
        self.metrics: List[Metric] = []
        self.webhook_url = settings.monitoring.webhook_url
        self.enabled = settings.monitoring.metrics_enabled
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None) -> None:
        """记录指标"""
        if not self.enabled:
            return
        
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        self.logger.log_performance_metric(name, value, unit)
    
    def record_test_execution(self, test_name: str, status: str, duration: float, test_type: str) -> None:
        """记录测试执行指标"""
        self.record_metric("test_execution_count", 1, "count", {
            "test_name": test_name,
            "status": status,
            "test_type": test_type
        })
        
        self.record_metric("test_execution_duration", duration, "seconds", {
            "test_name": test_name,
            "test_type": test_type
        })
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float) -> None:
        """记录API请求指标"""
        self.record_metric("api_request_count", 1, "count", {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code)
        })
        
        self.record_metric("api_request_duration", duration, "seconds", {
            "method": method,
            "endpoint": endpoint
        })
    
    def record_ui_action(self, action: str, element: str, success: bool, duration: float) -> None:
        """记录UI操作指标"""
        self.record_metric("ui_action_count", 1, "count", {
            "action": action,
            "element": element,
            "success": str(success)
        })
        
        self.record_metric("ui_action_duration", duration, "seconds", {
            "action": action
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics:
            return {}
        
        summary = {
            "total_metrics": len(self.metrics),
            "time_range": {
                "start": min(m.timestamp for m in self.metrics),
                "end": max(m.timestamp for m in self.metrics)
            },
            "metrics_by_name": {}
        }
        
        # 按名称分组统计
        for metric in self.metrics:
            name = metric.name
            if name not in summary["metrics_by_name"]:
                summary["metrics_by_name"][name] = {
                    "count": 0,
                    "total_value": 0,
                    "avg_value": 0,
                    "unit": metric.unit
                }
            
            summary["metrics_by_name"][name]["count"] += 1
            summary["metrics_by_name"][name]["total_value"] += metric.value
            summary["metrics_by_name"][name]["avg_value"] = (
                summary["metrics_by_name"][name]["total_value"] / 
                summary["metrics_by_name"][name]["count"]
            )
        
        return summary
    
    def send_to_webhook(self, data: Dict[str, Any]) -> bool:
        """发送数据到webhook"""
        if not self.webhook_url:
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            self.logger.info(f"指标数据已发送到webhook: {self.webhook_url}")
            return True
        except Exception as e:
            self.logger.error(f"发送指标数据到webhook失败: {e}")
            return False
    
    def flush_metrics(self) -> None:
        """刷新指标到外部系统"""
        if not self.metrics:
            return
        
        summary = self.get_metrics_summary()
        
        # 发送到webhook
        if self.webhook_url:
            webhook_data = {
                "timestamp": time.time(),
                "source": "mosspilot_test_framework",
                "summary": summary,
                "raw_metrics": [
                    {
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "timestamp": m.timestamp,
                        "tags": m.tags
                    }
                    for m in self.metrics
                ]
            }
            self.send_to_webhook(webhook_data)
        
        # 清空已发送的指标
        self.metrics.clear()
        self.logger.info("指标数据已刷新")
    
    def export_metrics(self, format_type: str = "json") -> str:
        """导出指标数据"""
        if format_type == "json":
            return json.dumps([
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp,
                    "tags": m.tags
                }
                for m in self.metrics
            ], indent=2, ensure_ascii=False)
        else:
            return str(self.get_metrics_summary())


# 全局指标收集器实例
metrics_collector = MetricsCollector()