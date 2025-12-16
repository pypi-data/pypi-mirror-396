"""
Moss Jenkins集成脚本
"""

import os
import json
import requests
import time
from typing import Dict, Any, Optional
from pathlib import Path
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger
from mosspilot.core.database import db_ops


class JenkinsIntegration:
    """Jenkins集成类"""
    
    def __init__(self):
        self.logger = Logger("jenkins")
        self.enabled = settings.jenkins.enabled
        self.callback_url = settings.jenkins.callback_url
        self.auth_token = settings.jenkins.auth_token
    
    def notify_test_start(self, execution_id: str, build_number: str = None) -> bool:
        """通知测试开始"""
        if not self.enabled or not self.callback_url:
            return False
        
        data = {
            "event": "test_start",
            "execution_id": execution_id,
            "build_number": build_number,
            "timestamp": time.time(),
            "status": "started"
        }
        
        return self._send_callback(data)
    
    def notify_test_complete(self, execution_id: str, summary: Dict[str, Any]) -> bool:
        """通知测试完成"""
        if not self.enabled or not self.callback_url:
            return False
        
        data = {
            "event": "test_complete",
            "execution_id": execution_id,
            "timestamp": time.time(),
            "status": "completed",
            "summary": summary
        }
        
        return self._send_callback(data)
    
    def notify_test_failure(self, execution_id: str, error_message: str) -> bool:
        """通知测试失败"""
        if not self.enabled or not self.callback_url:
            return False
        
        data = {
            "event": "test_failure",
            "execution_id": execution_id,
            "timestamp": time.time(),
            "status": "failed",
            "error_message": error_message
        }
        
        return self._send_callback(data)
    
    def _send_callback(self, data: Dict[str, Any]) -> bool:
        """发送回调数据"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = requests.post(
                self.callback_url,
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info(f"Jenkins回调成功: {data['event']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Jenkins回调失败: {e}")
            return False
    
    def generate_junit_xml(self, execution_id: str, output_path: str) -> str:
        """生成JUnit XML报告"""
        summary = db_ops.get_execution_summary(execution_id)
        
        # 获取执行记录
        executions = db_ops.session.query(db_ops.TestExecution).filter(
            db_ops.TestExecution.execution_id == execution_id
        ).all()
        
        xml_content = self._build_junit_xml(executions, summary)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(xml_content, encoding='utf-8')
        
        self.logger.info(f"JUnit XML报告已生成: {output_path}")
        return str(output_file)
    
    def _build_junit_xml(self, executions, summary: Dict[str, Any]) -> str:
        """构建JUnit XML内容"""
        total_time = sum(e.duration or 0 for e in executions)
        
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuite name="Moss Test Suite" tests="{summary.get("total_cases", 0)}" '
            f'failures="{summary.get("failed_cases", 0)}" '
            f'skipped="{summary.get("skipped_cases", 0)}" '
            f'time="{total_time:.2f}">',
        ]
        
        for execution in executions:
            test_case = execution.test_case
            duration = execution.duration or 0
            
            xml_lines.append(
                f'  <testcase classname="{test_case.test_type}" '
                f'name="{test_case.name}" time="{duration:.2f}">'
            )
            
            if execution.status == "failed":
                results = execution.results
                error_msg = results[0].error_message if results and results[0].error_message else "Test failed"
                xml_lines.append(f'    <failure message="{error_msg}"/>')
            elif execution.status == "skipped":
                xml_lines.append('    <skipped/>')
            
            xml_lines.append('  </testcase>')
        
        xml_lines.append('</testsuite>')
        return '\n'.join(xml_lines)


def main():
    """主函数，用于Jenkins调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Moss Jenkins集成脚本")
    parser.add_argument("--execution-id", required=True, help="测试执行ID")
    parser.add_argument("--action", choices=["start", "complete", "failure"], required=True, help="操作类型")
    parser.add_argument("--build-number", help="Jenkins构建号")
    parser.add_argument("--error-message", help="错误信息（用于failure操作）")
    parser.add_argument("--junit-output", help="JUnit XML输出路径")
    
    args = parser.parse_args()
    
    jenkins = JenkinsIntegration()
    
    if args.action == "start":
        jenkins.notify_test_start(args.execution_id, args.build_number)
    elif args.action == "complete":
        summary = db_ops.get_execution_summary(args.execution_id)
        jenkins.notify_test_complete(args.execution_id, summary)
        
        # 生成JUnit XML报告
        if args.junit_output:
            jenkins.generate_junit_xml(args.execution_id, args.junit_output)
    elif args.action == "failure":
        error_msg = args.error_message or "测试执行失败"
        jenkins.notify_test_failure(args.execution_id, error_msg)


if __name__ == "__main__":
    main()