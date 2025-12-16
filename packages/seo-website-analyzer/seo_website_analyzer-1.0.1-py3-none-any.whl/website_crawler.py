#!/usr/bin/env python3
"""
网站爬虫模块 - 负责爬取网站页面
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Set, Dict, Optional
import logging
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebsiteCrawler:
    """网站爬虫类"""
    
    def __init__(self, config: Dict):
        """初始化爬虫"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config['crawler']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
        
        # 爬取配置
        self.max_pages = config['crawler']['max_pages']
        self.delay = config['crawler']['delay']
        self.timeout = config['crawler']['timeout']
        self.max_depth = config['crawler']['max_depth']
        
        # 排除规则
        self.exclude_extensions = ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.xml', '.txt', '.zip', '.doc', '.docx']
        self.exclude_paths = ['/admin', '/login', '/register', '/api', '/static', '/assets', '/wp-admin', '/wp-content']
        
        # URL去重规则 - 统一移除所有查询参数
        
        # 状态跟踪
        self.visited_urls: Set[str] = set()
        self.normalized_urls: Set[str] = set()  # 用于标准化URL去重
        self.url_queue: deque = deque()
        self.lock = threading.Lock()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def crawl_website_generator(self, base_url: str):
        """逐个爬取网站页面 - 生成器模式"""
        print(f"🕷️ 开始爬取网站: {base_url}")
        
        # 清理URL
        base_url = self.clean_url(base_url)
        if not base_url:
            print("❌ 无效的URL")
            return
        
        # 初始化
        self.visited_urls.clear()
        self.normalized_urls.clear()
        self.url_queue.clear()
        self.url_queue.append((base_url, 0))  # (url, depth)
        
        while self.url_queue and len(self.visited_urls) < self.max_pages:
            current_url, depth = self.url_queue.popleft()
            
            # 检查深度限制
            if depth > self.max_depth:
                continue
            
            # 标准化URL用于去重
            normalized_url = self.normalize_url(current_url)
            
            # 检查是否已访问（使用标准化URL）
            if normalized_url in self.normalized_urls:
                continue
            
            # 检查URL是否有效
            if not self.is_valid_url(current_url, base_url):
                continue
            
            try:
                # 获取页面内容
                response = self.get_page_content(current_url)
                if not response:
                    continue
                
                # 标记为已访问
                self.visited_urls.add(current_url)
                self.normalized_urls.add(normalized_url)
                
                print(f"✅ 已爬取: {current_url} (深度: {depth})")
                
                # 提取新链接
                soup = BeautifulSoup(response.text, 'html.parser')
                new_urls = self.extract_links(soup, current_url, base_url)
                
                # 添加新链接到队列（使用标准化URL检查）
                for new_url in new_urls:
                    normalized_new_url = self.normalize_url(new_url)
                    if normalized_new_url not in self.normalized_urls:
                        self.url_queue.append((new_url, depth + 1))
                
                # 延迟
                if self.delay > 0:
                    time.sleep(self.delay)
                
                # 返回当前URL供处理
                yield current_url
                
            except Exception as e:
                self.logger.error(f"爬取页面失败 {current_url}: {e}")
                continue
        
        print(f"🎉 爬取完成！共发现 {len(self.visited_urls)} 个页面")
    
    def crawl_website(self, base_url: str) -> List[str]:
        """爬取网站所有页面"""
        print(f"🕷️ 开始爬取网站: {base_url}")
        
        # 清理URL
        base_url = self.clean_url(base_url)
        if not base_url:
            print("❌ 无效的URL")
            return []
        
        # 初始化
        self.visited_urls.clear()
        self.url_queue.clear()
        self.url_queue.append((base_url, 0))  # (url, depth)
        
        all_urls = []
        
        while self.url_queue and len(self.visited_urls) < self.max_pages:
            current_url, depth = self.url_queue.popleft()
            
            # 检查深度限制
            if depth > self.max_depth:
                continue
            
            # 标准化URL用于去重
            normalized_url = self.normalize_url(current_url)
            
            # 检查是否已访问（使用标准化URL）
            if normalized_url in self.normalized_urls:
                continue
            
            # 检查URL是否有效
            if not self.is_valid_url(current_url, base_url):
                continue
            
            try:
                # 获取页面内容
                response = self.get_page_content(current_url)
                if not response:
                    continue
                
                # 标记为已访问
                self.visited_urls.add(current_url)
                self.normalized_urls.add(normalized_url)
                all_urls.append(current_url)
                
                print(f"✅ 已爬取: {current_url} (深度: {depth})")
                
                # 解析页面，提取链接
                soup = BeautifulSoup(response.text, 'html.parser')
                new_urls = self.extract_links(soup, current_url, base_url)
                
                # 添加新链接到队列（使用标准化URL检查）
                for new_url in new_urls:
                    normalized_new_url = self.normalize_url(new_url)
                    if normalized_new_url not in self.normalized_urls:
                        self.url_queue.append((new_url, depth + 1))
                
                # 延迟
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"爬取页面失败 {current_url}: {e}")
                continue
        
        print(f"🎉 爬取完成！共发现 {len(all_urls)} 个页面")
        return all_urls
    
    def get_page_content(self, url: str) -> Optional[requests.Response]:
        """获取页面内容"""
        try:
            response = self.session.get(
                url, 
                timeout=self.timeout,
                allow_redirects=True
            )
            # 不调用raise_for_status()，让调用者处理状态码
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取页面失败 {url}: {e}")
            return None
    
    def clean_url(self, url: str) -> str:
        """清理URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 移除fragment
        parsed = urlparse(url)
        cleaned = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ''))
        return cleaned
    
    def normalize_url(self, url: str) -> str:
        """标准化URL，用于去重 - 统一移除所有查询参数"""
        try:
            parsed = urlparse(url)
            
            # 统一移除所有查询参数和fragment
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                '',  # 移除所有查询参数
                ''   # 移除fragment
            ))
            
            return normalized
        except Exception:
            return url
    
    def is_valid_url(self, url: str, base_url: str) -> bool:
        """检查URL是否有效"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            
            # 检查域名
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # 检查文件扩展名
            path = parsed.path.lower()
            for ext in self.exclude_extensions:
                if path.endswith(ext):
                    return False
            
            # 检查路径
            for exclude_path in self.exclude_paths:
                if exclude_path in path:
                    return False
            
            # 检查查询参数和锚点
            if '#' in url or '?' in url:
                # 对于SEO检查，我们可能需要包含这些URL
                pass
            
            return True
            
        except Exception:
            return False
    
    def extract_links(self, soup: BeautifulSoup, current_url: str, base_url: str) -> List[str]:
        """从页面中提取链接"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            cleaned_url = self.clean_url(full_url)
            
            if cleaned_url and self.is_valid_url(cleaned_url, base_url):
                links.append(cleaned_url)
        
        return links
    
    def crawl_with_threading(self, base_url: str, max_workers: int = 5) -> List[str]:
        """使用多线程爬取网站"""
        print(f"🕷️ 开始多线程爬取网站: {base_url}")
        
        base_url = self.clean_url(base_url)
        if not base_url:
            return []
        
        self.visited_urls.clear()
        self.normalized_urls.clear()
        self.url_queue.clear()
        self.url_queue.append((base_url, 0))
        
        all_urls = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while self.url_queue and len(self.visited_urls) < self.max_pages:
                # 获取一批URL进行处理
                batch_urls = []
                while self.url_queue and len(batch_urls) < max_workers * 2:
                    if self.url_queue:
                        batch_urls.append(self.url_queue.popleft())
                
                if not batch_urls:
                    break
                
                # 提交任务
                future_to_url = {
                    executor.submit(self.process_url, url, depth, base_url): url 
                    for url, depth in batch_urls
                }
                
                # 处理结果
                for future in as_completed(future_to_url):
                    url, depth = future_to_url[future]
                    try:
                        result = future.result()
                        if result:
                            new_urls, page_url = result
                            normalized_url = self.normalize_url(page_url)
                            
                            with self.lock:
                                if normalized_url not in self.normalized_urls:
                                    self.visited_urls.add(page_url)
                                    self.normalized_urls.add(normalized_url)
                                    all_urls.append(page_url)
                                    
                                    # 添加新链接到队列（使用标准化URL检查）
                                    for new_url in new_urls:
                                        normalized_new_url = self.normalize_url(new_url)
                                        if normalized_new_url not in self.normalized_urls:
                                            self.url_queue.append((new_url, depth + 1))
                                
                                print(f"✅ 已爬取: {page_url}")
                    except Exception as e:
                        self.logger.error(f"处理URL失败 {url}: {e}")
        
        print(f"🎉 多线程爬取完成！共发现 {len(all_urls)} 个页面")
        return all_urls
    
    def process_url(self, url: str, depth: int, base_url: str) -> Optional[tuple]:
        """处理单个URL"""
        try:
            # 检查深度限制
            if depth > self.max_depth:
                return None
            
            # 检查是否已访问（使用标准化URL）
            normalized_url = self.normalize_url(url)
            if normalized_url in self.normalized_urls:
                return None
            
            # 检查URL是否有效
            if not self.is_valid_url(url, base_url):
                return None
            
            # 获取页面内容
            response = self.get_page_content(url)
            if not response:
                return None
            
            # 解析页面，提取链接
            soup = BeautifulSoup(response.text, 'html.parser')
            new_urls = self.extract_links(soup, url, base_url)
            
            # 延迟
            time.sleep(self.delay)
            
            return new_urls, url
            
        except Exception as e:
            self.logger.error(f"处理URL失败 {url}: {e}")
            return None
    
    def get_page_info(self, url: str) -> Optional[Dict]:
        """获取页面基本信息"""
        try:
            response = self.get_page_content(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取基本信息
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '').strip() if meta_keywords else ""
            
            h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')]
            
            # 计算内容长度
            content_length = len(soup.get_text())
            word_count = len(soup.get_text().split())
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'keywords': keywords,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'content_length': content_length,
                'word_count': word_count,
                'load_time': response.elapsed.total_seconds(),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'last_modified': response.headers.get('last-modified', ''),
                'content_encoding': response.headers.get('content-encoding', '')
            }
            
        except Exception as e:
            self.logger.error(f"获取页面信息失败 {url}: {e}")
            return None
