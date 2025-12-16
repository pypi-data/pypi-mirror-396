"""
Moss HTML报告生成器
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger
from mosspilot.core.database import db_ops


class HTMLReporter:
    """HTML报告生成器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or "core/reporting/templates"
        self.output_dir = settings.reporting.output_dir
        self.logger = Logger()
        self.env = self._setup_jinja_env()
    
    def _setup_jinja_env(self) -> Environment:
        """设置Jinja2环境"""
        template_path = Path(self.template_dir)
        if not template_path.exists():
            template_path.mkdir(parents=True, exist_ok=True)
        
        env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=True
        )
        
        # 添加自定义过滤器
        env.filters['format_duration'] = self._format_duration
        env.filters['format_timestamp'] = self._format_timestamp
        env.filters['percentage'] = self._format_percentage
        
        return env
    
    def generate_report(self, execution_id: str, template_name: str = "default") -> str:
        """生成HTML报告"""
        self.logger.info(f"开始生成HTML报告: {execution_id}")
        
        # 收集测试数据
        report_data = self._collect_report_data(execution_id)
        
        # 加载模板
        template = self._load_template(template_name)
        
        # 生成HTML内容
        html_content = template.render(**report_data)
        
        # 保存报告文件
        output_path = self._save_report(execution_id, html_content)
        
        # 记录报告到数据库
        self._record_report(execution_id, output_path, report_data)
        
        self.logger.info(f"HTML报告生成完成: {output_path}")
        return output_path
    
    def _collect_report_data(self, execution_id: str) -> Dict[str, Any]:
        """收集报告数据"""
        summary = db_ops.get_execution_summary(execution_id)
        
        # 获取执行记录
        executions = db_ops.session.query(db_ops.TestExecution).filter(
            db_ops.TestExecution.execution_id == execution_id
        ).all()
        
        # 统计数据
        test_results = []
        for execution in executions:
            test_case = execution.test_case
            results = execution.results
            
            test_results.append({
                'name': test_case.name,
                'description': test_case.description,
                'type': test_case.test_type,
                'status': execution.status,
                'duration': execution.duration or 0,
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'error_message': results[0].error_message if results and results[0].error_message else None,
                'screenshot_path': results[0].screenshot_path if results and results[0].screenshot_path else None
            })
        
        # 按类型分组统计
        type_stats = {}
        for result in test_results:
            test_type = result['type']
            if test_type not in type_stats:
                type_stats[test_type] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            type_stats[test_type]['total'] += 1
            type_stats[test_type][result['status']] += 1
        
        return {
            'execution_id': execution_id,
            'generated_at': datetime.now(),
            'summary': summary,
            'test_results': test_results,
            'type_stats': type_stats,
            'total_duration': sum(r['duration'] for r in test_results),
            'environment': executions[0].environment if executions else 'unknown'
        }
    
    def _load_template(self, template_name: str) -> Template:
        """加载模板"""
        template_file = f"{template_name}.html"
        
        try:
            return self.env.get_template(template_file)
        except Exception:
            # 如果模板不存在，创建默认模板
            self._create_default_template()
            return self.env.get_template("default.html")
    
    def _create_default_template(self) -> None:
        """创建默认模板"""
        template_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moss 测试报告 - {{ execution_id }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .meta { margin-top: 10px; opacity: 0.9; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .summary-card.passed { border-left-color: #28a745; }
        .summary-card.failed { border-left-color: #dc3545; }
        .summary-card.skipped { border-left-color: #ffc107; }
        .summary-card h3 { margin: 0 0 10px 0; color: #495057; }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #212529; }
        .content { padding: 0 30px 30px 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .test-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .test-table th, .test-table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        .test-table th { background-color: #f8f9fa; font-weight: 600; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500; }
        .status.passed { background-color: #d4edda; color: #155724; }
        .status.failed { background-color: #f8d7da; color: #721c24; }
        .status.skipped { background-color: #fff3cd; color: #856404; }
        .error-message { background-color: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 0.9em; margin-top: 5px; }
        .chart-container { margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Moss 测试报告</h1>
            <div class="meta">
                <p>执行ID: {{ execution_id }} | 生成时间: {{ generated_at | format_timestamp }} | 环境: {{ environment }}</p>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总用例数</h3>
                <div class="number">{{ summary.total_cases or 0 }}</div>
            </div>
            <div class="summary-card passed">
                <h3>通过</h3>
                <div class="number">{{ summary.passed_cases or 0 }}</div>
            </div>
            <div class="summary-card failed">
                <h3>失败</h3>
                <div class="number">{{ summary.failed_cases or 0 }}</div>
            </div>
            <div class="summary-card skipped">
                <h3>跳过</h3>
                <div class="number">{{ summary.skipped_cases or 0 }}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="number">{{ summary.success_rate | percentage }}%</div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="number">{{ total_duration | format_duration }}</div>
            </div>
        </div>
        
        <div class="content">
            {% if type_stats %}
            <div class="section">
                <h2>测试类型统计</h2>
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>测试类型</th>
                            <th>总数</th>
                            <th>通过</th>
                            <th>失败</th>
                            <th>跳过</th>
                            <th>成功率</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for type_name, stats in type_stats.items() %}
                        <tr>
                            <td>{{ type_name.upper() }}</td>
                            <td>{{ stats.total }}</td>
                            <td>{{ stats.passed }}</td>
                            <td>{{ stats.failed }}</td>
                            <td>{{ stats.skipped }}</td>
                            <td>{{ (stats.passed / stats.total * 100) | round(1) if stats.total > 0 else 0 }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            <div class="section">
                <h2>测试用例详情</h2>
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>用例名称</th>
                            <th>类型</th>
                            <th>状态</th>
                            <th>耗时</th>
                            <th>开始时间</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in test_results %}
                        <tr>
                            <td>
                                <strong>{{ result.name }}</strong>
                                {% if result.description %}
                                <br><small style="color: #6c757d;">{{ result.description }}</small>
                                {% endif %}
                                {% if result.error_message %}
                                <div class="error-message">{{ result.error_message }}</div>
                                {% endif %}
                            </td>
                            <td>{{ result.type.upper() }}</td>
                            <td><span class="status {{ result.status }}">{{ result.status.upper() }}</span></td>
                            <td>{{ result.duration | format_duration }}</td>
                            <td>{{ result.start_time | format_timestamp }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        template_path = Path(self.template_dir) / "default.html"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(template_content.strip(), encoding='utf-8')
    
    def _save_report(self, execution_id: str, html_content: str) -> str:
        """保存报告文件"""
        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{execution_id}_{timestamp}.html"
        output_path = output_dir / filename
        
        output_path.write_text(html_content, encoding='utf-8')
        return str(output_path)
    
    def _record_report(self, execution_id: str, file_path: str, report_data: Dict[str, Any]) -> None:
        """记录报告到数据库"""
        try:
            summary = report_data.get('summary', {})
            db_ops.create_report(
                execution_id=execution_id,
                report_type="html",
                file_path=file_path,
                total_cases=summary.get('total_cases', 0),
                passed_cases=summary.get('passed_cases', 0),
                failed_cases=summary.get('failed_cases', 0),
                skipped_cases=summary.get('skipped_cases', 0),
                execution_time=report_data.get('total_duration', 0)
            )
        except Exception as e:
            self.logger.error(f"记录报告到数据库失败: {e}")
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @staticmethod
    def _format_timestamp(timestamp) -> str:
        """格式化时间戳"""
        if isinstance(timestamp, str):
            return timestamp
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def _format_percentage(value: float) -> str:
        """格式化百分比"""
        return f"{value:.1f}"