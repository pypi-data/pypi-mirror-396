#!/usr/bin/env python3
"""
报告生成器 - 生成HTML、Excel和JSON格式的SEO报告
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd
import logging

class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, config: Dict):
        """初始化报告生成器"""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_html_report(self, report_data: Dict, output_file: str):
        """生成HTML报告"""
        try:
            html_content = self.create_html_content(report_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML报告已生成: {output_file}")
            
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            raise
    
    def generate_excel_report(self, report_data: Dict, output_file: str):
        """生成Excel报告"""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 总体概览
                overview_data = {
                    '指标': ['总体评分', '检查页面数', '严重问题', '警告问题', '信息问题'],
                    '数值': [
                        f"{report_data.get('overall_score', 0):.1f}",
                        report_data.get('total_pages', 0),
                        report_data.get('issues_summary', {}).get('critical', 0),
                        report_data.get('issues_summary', {}).get('warning', 0),
                        report_data.get('issues_summary', {}).get('info', 0)
                    ]
                }
                overview_df = pd.DataFrame(overview_data)
                overview_df.to_excel(writer, sheet_name='总体概览', index=False)
                
                # 页面详情
                pages_data = report_data.get('pages_data', [])
                if pages_data:
                    pages_df = pd.DataFrame(pages_data)
                    pages_df.to_excel(writer, sheet_name='页面详情', index=False)
            
            self.logger.info(f"Excel报告已生成: {output_file}")
            
        except Exception as e:
            self.logger.error(f"生成Excel报告失败: {e}")
            raise
    
    def create_html_content(self, report_data: Dict) -> str:
        """创建HTML内容"""
        overall_score = report_data.get('overall_score', 0)
        total_pages = report_data.get('total_pages', 0)
        issues_summary = report_data.get('issues_summary', {})
        pages_data = report_data.get('pages_data', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO优化检查报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .header {{ text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .score {{ font-size: 3em; font-weight: bold; color: #007bff; margin: 20px 0; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .issue-item {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .critical {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .info {{ color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SEO优化检查报告</h1>
            <div class="score">{overall_score:.1f}/100</div>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>检查页面数</h3>
                <div class="number">{total_pages}</div>
            </div>
            <div class="summary-card">
                <h3>严重问题</h3>
                <div class="number critical">{issues_summary.get('critical', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>警告问题</h3>
                <div class="number warning">{issues_summary.get('warning', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>信息问题</h3>
                <div class="number info">{issues_summary.get('info', 0)}</div>
            </div>
        </div>
        
        <div class="issues-section">
            <h2>📊 问题汇总</h2>
        """
        
        for page in pages_data:
            if page.get('issues'):
                html += f"""
                <div class="page-section">
                    <h3>{page.get('url', '')} - 评分: {page.get('score', 0):.1f}/100</h3>
                """
                
                for issue in page.get('issues', []):
                    severity_class = issue.get('severity', 'info')
                    html += f"""
                    <div class="issue-item">
                        <span class="{severity_class}">{issue.get('severity', '')}</span>
                        <strong>{issue.get('message', '')}</strong>
                        <p>{issue.get('suggestion', '')}</p>
                    </div>
                    """
                
                html += "</div>"
        
        html += """
        </div>
        
        <div class="footer">
            <p>本报告由SEO优化检查系统自动生成</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html