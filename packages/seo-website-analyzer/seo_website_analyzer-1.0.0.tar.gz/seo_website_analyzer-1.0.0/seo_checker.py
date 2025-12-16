#!/usr/bin/env python3
"""
网站SEO优化检查器 - 主程序
根据seo.md文档进行全面SEO检查
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
import argparse
import sys
import os
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Dict, Set, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib

# 导入自定义模块
from website_crawler import WebsiteCrawler
from seo_analyzer import SEOAnalyzer
from report_generator import ReportGenerator
from seo_api_client import SEOAPIClient, create_seo_issue_data

@dataclass
class SEOIssue:
    """SEO问题数据类"""
    page_url: str
    issue_type: str
    severity: str  # critical, warning, info
    message: str
    suggestion: str
    element: str = ""
    line_number: int = 0

@dataclass
class PageSEOData:
    """页面SEO数据类"""
    url: str
    title: str
    meta_description: str
    meta_keywords: str
    h1_tags: List[str]
    h2_tags: List[str]
    h3_tags: List[str]
    images: List[Dict]
    internal_links: List[str]
    external_links: List[str]
    content_length: int
    word_count: int
    load_time: float
    issues: List[SEOIssue]
    html: str = ""  # 添加HTML内容属性
    score: float = 0.0
    response_time: int = None
    page_size: int = None
    status_code: int = None

class SEOChecker:
    """SEO检查器主类"""
    
    def __init__(self, config_file: str = "seo_config.json"):
        """初始化SEO检查器"""
        self.config = self.load_config(config_file)
        self.crawler = WebsiteCrawler(self.config)
        self.analyzer = SEOAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # 数据存储
        self.visited_urls: Set[str] = set()
        self.pages_data: List[PageSEOData] = []
        self.issues_summary: Dict[str, int] = defaultdict(int)
        self.overall_score: float = 0.0
        self.api_client = None
        
        # 初始化API客户端（如果启用数据库存储）
        if self.config.get('database', {}).get('enabled', False):
            api_url = self.config['database'].get('api_url', 'http://localhost:3000')
            api_key = self.config['database'].get('api_key', '')
            if api_key:
                self.api_client = SEOAPIClient(api_url, api_key)
                print("✅ 数据库存储已启用")
            else:
                print("⚠️ 数据库存储已启用但未配置API密钥")
        
        # 设置日志
        self.setup_logging()
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件 {config_file} 不存在，使用默认配置")
            return self.get_default_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "crawler": {
                "max_pages": 100,
                "delay": 1.0,
                "timeout": 30,
                "max_depth": 5,
                "user_agent": "SEO-Checker/1.0"
            },
            "seo_rules": {
                "title_min_length": 30,
                "title_max_length": 60,
                "description_min_length": 120,
                "description_max_length": 160,
                "h1_required": True,
                "max_h1_count": 1,
                "min_content_length": 300,
                "keyword_density_min": 0.5,
                "keyword_density_max": 3.0
            },
            "output": {
                "generate_html": True,
                "generate_excel": False,
                "generate_json": False,
                "include_screenshots": False
            },
            "database": {
                "enabled": False,
                "api_url": "http://localhost:3000",
                "api_key": ""
            }
        }
    
    def setup_logging(self):
        """设置日志"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/seo_checker_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_website(self, base_url: str) -> Dict:
        """检查单个网站 - 一条一条爬取，一条一条分析，一条一条入库"""
        print(f"🔍 开始检查网站: {base_url}")
        self.logger.info(f"开始检查网站: {base_url}")
        
        # 初始化数据存储
        self.pages_data = []
        page_count = 0
        
        # 1. 逐个爬取、分析、保存（一条龙处理）
        print("🔄 开始一条龙处理：爬取 → 分析 → 入库")
        
        for page_url in self.crawler.crawl_website_generator(base_url):
            page_count += 1
            try:
                print(f"📄 正在处理第 {page_count} 个页面: {page_url}")
                
                # 分析当前页面
                page_data = self.analyze_page(page_url, None)  # 不传递总页面数，因为我们是逐个处理
                
                if page_data:
                    self.pages_data.append(page_data)
                    print(f"✅ 分析完成: {page_url}")
                    
                    # 立即保存当前页面的问题到数据库
                    if self.api_client and page_data.issues:
                        self.save_single_page_issues(base_url, page_data)
                    elif self.api_client:
                        print(f"ℹ️ 页面 {page_url} 没有发现SEO问题")
                else:
                    print(f"❌ 分析失败: {page_url}")
                    
            except Exception as e:
                self.logger.error(f"处理页面失败 {page_url}: {e}")
                print(f"❌ 处理失败: {page_url}")
        
        # 2. 计算总体评分
        self.calculate_overall_score()
        
        # 3. 生成报告
        print("📊 正在生成报告...")
        report_data = self.generate_report_data()
        
        # 4. 保存报告
        self.save_reports(report_data, base_url)
        
        print(f"🎉 SEO检查完成！共处理 {page_count} 个页面，总体评分: {self.overall_score:.1f}/100")
        return report_data
    
    def save_single_page_issues(self, base_url: str, page_data):
        """保存单个页面的SEO问题到数据库"""
        if not self.api_client:
            return
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(base_url).netloc
            check_batch_id = f"batch_{int(datetime.now().timestamp())}"
            
            issues = []
            for issue in page_data.issues:
                # 生成问题标识符
                issue_identifier = self.generate_issue_identifier(issue)
                
                # 创建问题数据
                issue_data = create_seo_issue_data(
                    domain=domain,
                    page_url=page_data.url,
                    page_title=page_data.title,
                    issue_type=issue.issue_type,
                    issue_identifier=issue_identifier,
                    issue_name=issue.message,
                    issue_severity=issue.severity,
                    issue_description=issue.message,
                    issue_suggestion=issue.suggestion,
                    issue_value=issue.element,
                    check_batch_id=check_batch_id,
                    response_time=page_data.response_time,
                    page_size=page_data.page_size,
                    status_code=page_data.status_code
                )
                issues.append(issue_data)
            
            if issues:
                result = self.api_client.submit_seo_issues(issues)
                if result.get('success'):
                    print(f"💾 已保存 {len(issues)} 个问题到数据库")
                else:
                    print(f"❌ 保存问题到数据库失败: {result.get('message', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 保存问题到数据库时发生错误: {e}")
            self.logger.error(f"保存问题到数据库失败: {e}")
    
    def save_issues_to_database(self, base_url: str):
        """保存SEO问题到数据库"""
        if not self.api_client:
            return
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(base_url).netloc
            check_batch_id = f"batch_{int(datetime.now().timestamp())}"
            
            issues = []
            for page_data in self.pages_data:
                for issue in page_data.issues:
                    # 生成问题标识符
                    issue_identifier = self.generate_issue_identifier(issue)
                    
                    # 创建问题数据
                    issue_data = create_seo_issue_data(
                        domain=domain,
                        page_url=page_data.url,
                        page_title=page_data.title,
                        issue_type=issue.issue_type,
                        issue_identifier=issue_identifier,
                        issue_name=issue.message,
                        issue_severity=issue.severity,
                        issue_description=issue.message,
                        issue_suggestion=issue.suggestion,
                        issue_value=issue.element,
                        check_batch_id=check_batch_id,
                        response_time=page_data.response_time,
                        page_size=page_data.page_size,
                        status_code=page_data.status_code
                    )
                    issues.append(issue_data)
            
            if issues:
                result = self.api_client.submit_seo_issues(issues)
                if result.get('success'):
                    print(f"✅ 成功保存 {len(issues)} 个问题到数据库")
                else:
                    print(f"❌ 保存问题到数据库失败: {result.get('message', '未知错误')}")
            else:
                print("ℹ️ 没有发现SEO问题")
                
        except Exception as e:
            print(f"❌ 保存问题到数据库时发生错误: {e}")
            self.logger.error(f"保存问题到数据库失败: {e}")
    
    def generate_issue_identifier(self, issue) -> str:
        """生成问题标识符"""
        # 基于问题类型和内容生成唯一标识符
        identifier_parts = [
            issue.issue_type,
            issue.severity,
            issue.message[:50] if issue.message else "",
            issue.element[:20] if issue.element else ""
        ]
        return "_".join(identifier_parts).replace(" ", "_").replace(":", "").replace(";", "")
    
    def _create_404_page_data(self, page_url: str) -> PageSEOData:
        """创建404页面的SEO数据"""
        # 创建404错误的问题
        issue = SEOIssue(
            page_url=page_url,
            issue_type="page_not_found",
            severity="critical",
            message="页面返回404错误",
            suggestion="检查页面URL是否正确，或考虑设置301重定向",
            element="http_status"
        )
        
        # 创建页面数据对象
        page_data = PageSEOData(
            url=page_url,
            title="404 Not Found",
            meta_description="",
            meta_keywords="",
            h1_tags=[],
            h2_tags=[],
            h3_tags=[],
            images=[],
            internal_links=[],
            external_links=[],
            content_length=0,
            word_count=0,
            load_time=0.0,
            issues=[issue],
            html="",
            status_code=404
        )
        
        return page_data
    
    def analyze_page(self, page_url: str, total_pages: int = None) -> PageSEOData:
        """分析单个页面的SEO"""
        try:
            # 获取页面内容
            response = self.crawler.get_page_content(page_url)
            if not response:
                # 创建404错误的SEO问题
                return self._create_404_page_data(page_url)
            
            # 检查HTTP状态码
            if response.status_code == 404:
                # 创建404错误的SEO问题
                return self._create_404_page_data(page_url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取基础信息
            title = self.extract_title(soup)
            meta_description = self.extract_meta_description(soup)
            meta_keywords = self.extract_meta_keywords(soup)
            h1_tags = self.extract_h_tags(soup, 'h1')
            h2_tags = self.extract_h_tags(soup, 'h2')
            h3_tags = self.extract_h_tags(soup, 'h3')
            images = self.extract_images(soup)
            internal_links, external_links = self.extract_links(soup, page_url)
            content_length = len(soup.get_text())
            word_count = len(soup.get_text().split())
            
            # 计算页面加载时间
            load_time = response.elapsed.total_seconds()
            
            # 创建页面数据对象
            page_data = PageSEOData(
                url=page_url,
                title=title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                h1_tags=h1_tags,
                h2_tags=h2_tags,
                h3_tags=h3_tags,
                images=images,
                internal_links=internal_links,
                external_links=external_links,
                content_length=content_length,
                word_count=word_count,
                load_time=load_time,
                issues=[],
                html=response.text  # 添加HTML内容
            )
            
            # 进行SEO检查
            issues = self.analyzer.check_page_seo(page_data, soup, total_pages)
            page_data.issues = issues
            
            # 计算页面评分
            page_data.score = self.calculate_page_score(page_data, issues)
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"分析页面失败 {page_url}: {e}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def extract_meta_description(self, soup: BeautifulSoup) -> str:
        """提取Meta描述"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """提取Meta关键词"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""
    
    def extract_h_tags(self, soup: BeautifulSoup, tag_name: str) -> List[str]:
        """提取H标签"""
        tags = soup.find_all(tag_name)
        return [tag.get_text().strip() for tag in tags]
    
    def extract_images(self, soup: BeautifulSoup) -> List[Dict]:
        """提取图片信息"""
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        return images
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str]]:
        """提取内部和外部链接"""
        internal_links = []
        external_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            link_domain = urlparse(full_url).netloc
            
            if link_domain == base_domain:
                internal_links.append(full_url)
            else:
                external_links.append(full_url)
        
        return internal_links, external_links
    
    def calculate_page_score(self, page_data: PageSEOData, issues: List[SEOIssue]) -> float:
        """计算页面SEO评分"""
        base_score = 100.0
        
        # 根据问题严重程度扣分
        for issue in issues:
            if issue.severity == 'critical':
                base_score -= 10
            elif issue.severity == 'warning':
                base_score -= 5
            elif issue.severity == 'info':
                base_score -= 2
        
        # 确保评分不低于0
        return max(0.0, base_score)
    
    def calculate_overall_score(self):
        """计算总体评分"""
        if not self.pages_data:
            self.overall_score = 0.0
            return
        
        total_score = sum(page.score for page in self.pages_data)
        self.overall_score = total_score / len(self.pages_data)
        
        # 统计问题类型
        for page in self.pages_data:
            for issue in page.issues:
                self.issues_summary[issue.issue_type] += 1
    
    def generate_report_data(self) -> Dict:
        """生成报告数据"""
        return {
            'overall_score': self.overall_score,
            'total_pages': len(self.pages_data),
            'issues_summary': dict(self.issues_summary),
            'pages_data': [asdict(page) for page in self.pages_data],
            'check_time': datetime.now().isoformat(),
            'config': self.config
        }
    
    def save_reports(self, report_data: Dict, base_url: str):
        """保存报告"""
        # 创建输出目录
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        domain = urlparse(base_url).netloc
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{domain}_{timestamp}"
        
        # 保存JSON报告
        if self.config['output']['generate_json']:
            json_file = f"{output_dir}/{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"📄 JSON报告已保存: {json_file}")
        
        # 生成HTML报告
        if self.config['output']['generate_html']:
            html_file = f"{output_dir}/{base_filename}.html"
            self.report_generator.generate_html_report(report_data, html_file)
            print(f"🌐 HTML报告已保存: {html_file}")
        
        # 生成Excel报告
        if self.config['output']['generate_excel']:
            excel_file = f"{output_dir}/{base_filename}.xlsx"
            self.report_generator.generate_excel_report(report_data, excel_file)
            print(f"📊 Excel报告已保存: {excel_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='网站SEO优化检查器')
    parser.add_argument('urls', nargs='+', help='要检查的网站URL')
    parser.add_argument('--config', default='seo_config.json', help='配置文件路径')
    parser.add_argument('--report', action='store_true', help='生成详细报告')
    parser.add_argument('--excel', action='store_true', help='生成Excel报告')
    parser.add_argument('--batch', action='store_true', help='批量检查模式')
    parser.add_argument('--input', help='批量检查的输入文件')
    parser.add_argument('--rules', help='自定义检查规则文件')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    parser.add_argument('--max-pages', type=int, help='最大采集页面数 (覆盖配置文件设置)')
    
    args = parser.parse_args()
    
    # 创建SEO检查器
    checker = SEOChecker(args.config)
    
    # 如果指定了max-pages参数，覆盖配置文件设置
    if args.max_pages:
        checker.config['crawler']['max_pages'] = args.max_pages
        print(f"📊 设置最大采集页面数: {args.max_pages}")
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.batch and args.input:
            # 批量检查模式
            with open(args.input, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            for url in urls:
                print(f"\n{'='*60}")
                print(f"检查网站: {url}")
                print(f"{'='*60}")
                checker.check_website(url)
        else:
            # 单个网站检查
            for url in args.urls:
                print(f"\n{'='*60}")
                print(f"检查网站: {url}")
                print(f"{'='*60}")
                checker.check_website(url)
                
    except KeyboardInterrupt:
        print("\n\n⏹️ 检查被用户中断")
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
