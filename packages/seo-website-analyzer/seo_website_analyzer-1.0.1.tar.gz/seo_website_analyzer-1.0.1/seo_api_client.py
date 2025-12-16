"""
SEO检查结果API客户端
用于将SEO检查结果提交到Next.js后端API
"""

import requests
import time
import random
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import hashlib
from datetime import datetime


class SEOAPIClient:
    """SEO检查结果API客户端"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL，如 "http://localhost:3000"
            api_key: API密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.max_retries = 5
        self.base_delay = 2
        
    def _retry_with_backoff(self, func, *args, **kwargs):
        """带指数退避的重试机制"""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if isinstance(result, dict) and result.get('success') is not None:
                    return result
                elif isinstance(result, dict) and 'error' in result:
                    return result
                else:
                    raise Exception(f"API返回格式异常: {result}")
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"🔄 API调用失败，{delay:.1f}秒后重试 (第{attempt + 1}次): {str(e)}")
                    time.sleep(delay)
                else:
                    print(f"❌ API调用最终失败，已重试{self.max_retries}次: {str(e)}")
        return {"success": False, "message": f"API调用失败: {str(last_exception)}"}
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP请求失败: {str(e)}")
    
    def generate_issue_code(self, issue_type: str, issue_identifier: str) -> str:
        """
        生成问题唯一代码
        
        Args:
            issue_type: 问题类型 (title, meta, content, etc.)
            issue_identifier: 问题标识符
            
        Returns:
            问题代码，格式: issue_type_identifier_hash
        """
        # 生成问题标识符的哈希值（确保唯一性）
        identifier_hash = hashlib.md5(
            f"{issue_type}_{issue_identifier}".encode()
        ).hexdigest()[:8]
        
        # 组合生成问题代码
        issue_code = f"{issue_type}_{identifier_hash}"
        
        return issue_code
    
    def submit_seo_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        提交SEO问题数据
        
        Args:
            issues: SEO问题列表
            
        Returns:
            API响应结果
        """
        def _submit():
            return self._make_request('POST', '/api/admin/seo-check', data={'issues': issues})
        
        return self._retry_with_backoff(_submit)
    
    def get_seo_issues(self, 
                      domain: Optional[str] = None,
                      issue_type: Optional[str] = None,
                      issue_severity: Optional[str] = None,
                      is_resolved: Optional[bool] = None,
                      check_batch_id: Optional[str] = None,
                      page: int = 1,
                      limit: int = 20) -> Dict[str, Any]:
        """
        获取SEO问题列表
        
        Args:
            domain: 域名筛选
            issue_type: 问题类型筛选
            issue_severity: 问题严重性筛选
            is_resolved: 是否已解决筛选
            check_batch_id: 检查批次ID筛选
            page: 页码
            limit: 每页数量
            
        Returns:
            API响应结果
        """
        def _get():
            params = {
                'page': page,
                'limit': limit
            }
            if domain:
                params['domain'] = domain
            if issue_type:
                params['issueType'] = issue_type
            if issue_severity:
                params['issueSeverity'] = issue_severity
            if is_resolved is not None:
                params['isResolved'] = str(is_resolved).lower()
            if check_batch_id:
                params['checkBatchId'] = check_batch_id
                
            return self._make_request('GET', '/api/admin/seo-check', params=params)
        
        return self._retry_with_backoff(_get)
    
    def mark_issue_resolved(self, issue_id: int) -> Dict[str, Any]:
        """
        标记问题为已解决
        
        Args:
            issue_id: 问题ID
            
        Returns:
            API响应结果
        """
        def _mark():
            return self._make_request('PUT', f'/api/admin/seo-check/{issue_id}/resolve')
        
        return self._retry_with_backoff(_mark)
    
    def get_issue_statistics(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        获取问题统计信息
        
        Args:
            domain: 域名筛选
            
        Returns:
            统计信息
        """
        def _get_stats():
            params = {'limit': 1000}  # 获取大量数据用于统计
            if domain:
                params['domain'] = domain
            return self._make_request('GET', '/api/admin/seo-check', params=params)
        
        result = self._retry_with_backoff(_get_stats)
        
        if not result.get('success'):
            return result
        
        issues = result.get('data', {}).get('results', [])
        
        # 计算统计信息
        stats = {
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i.get('issue_severity') == 'critical']),
            'warning_issues': len([i for i in issues if i.get('issue_severity') == 'warning']),
            'info_issues': len([i for i in issues if i.get('issue_severity') == 'info']),
            'resolved_issues': len([i for i in issues if i.get('is_resolved') == True]),
            'unresolved_issues': len([i for i in issues if i.get('is_resolved') == False]),
            'domains': list(set([i.get('domain') for i in issues if i.get('domain')])),
            'issue_types': {}
        }
        
        # 按问题类型统计
        for issue in issues:
            issue_type = issue.get('issue_type', 'unknown')
            if issue_type not in stats['issue_types']:
                stats['issue_types'][issue_type] = 0
            stats['issue_types'][issue_type] += 1
        
        return {
            'success': True,
            'data': stats
        }


def create_seo_issue_data(domain: str, page_url: str, page_title: str, 
                         issue_type: str, issue_identifier: str, 
                         issue_name: str, issue_severity: str,
                         issue_description: str, issue_suggestion: str = None,
                         issue_value: str = None, check_batch_id: str = None,
                         response_time: int = None, page_size: int = None,
                         status_code: int = None) -> Dict[str, Any]:
    """
    创建SEO问题数据字典
    
    Args:
        domain: 域名
        page_url: 页面URL
        page_title: 页面标题
        issue_type: 问题类型
        issue_identifier: 问题标识符
        issue_name: 问题名称
        issue_severity: 问题严重性
        issue_description: 问题描述
        issue_suggestion: 改进建议
        issue_value: 问题值
        check_batch_id: 检查批次ID
        response_time: 响应时间
        page_size: 页面大小
        status_code: 状态码
        
    Returns:
        SEO问题数据字典
    """
    # 生成问题代码
    client = SEOAPIClient("", "")  # 临时实例用于生成代码
    issue_code = client.generate_issue_code(issue_type, issue_identifier)
    
    return {
        'domain': domain,
        'page_url': page_url,
        'page_title': page_title,
        'issue_code': issue_code,
        'issue_name': issue_name,
        'issue_type': issue_type,
        'issue_severity': issue_severity,
        'issue_description': issue_description,
        'issue_suggestion': issue_suggestion,
        'issue_value': issue_value,
        'check_batch_id': check_batch_id or f"batch_{int(datetime.now().timestamp())}",
        'response_time': response_time,
        'page_size': page_size,
        'status_code': status_code
    }


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = SEOAPIClient("http://localhost:3000", "your-api-key")
    
    # 创建问题数据
    issues = [
        create_seo_issue_data(
            domain="example.com",
            page_url="https://example.com/page1",
            page_title="Page 1",
            issue_type="title",
            issue_identifier="missing",
            issue_name="标题缺失",
            issue_severity="critical",
            issue_description="页面缺少title标签",
            issue_suggestion="请为页面添加title标签"
        ),
        create_seo_issue_data(
            domain="example.com",
            page_url="https://example.com/page2",
            page_title="Page 2",
            issue_type="meta",
            issue_identifier="description_too_long",
            issue_name="元描述过长",
            issue_severity="warning",
            issue_description="meta description超过160字符",
            issue_suggestion="请将meta description控制在160字符以内"
        )
    ]
    
    # 提交问题数据
    result = client.submit_seo_issues(issues)
    print(f"提交结果: {result}")
    
    # 获取问题列表
    issues_result = client.get_seo_issues(domain="example.com")
    print(f"问题列表: {issues_result}")
    
    # 获取统计信息
    stats = client.get_issue_statistics(domain="example.com")
    print(f"统计信息: {stats}")
