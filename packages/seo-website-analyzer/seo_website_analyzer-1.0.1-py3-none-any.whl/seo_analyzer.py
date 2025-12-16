# SEO分析引擎 - 待完成
#!/usr/bin/env python3
"""
SEO分析引擎 - 根据seo.md文档进行SEO检查
"""

import re
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from urllib.parse import urlparse, urljoin
import requests
from datetime import datetime

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

class SEOAnalyzer:
    """SEO分析引擎"""
    
    def __init__(self, config: Dict):
        """初始化SEO分析器"""
        self.config = config
        self.seo_rules = config.get('seo_rules', {})
        self.logger = logging.getLogger(__name__)
        
        # 关键词密度检查配置
        self.keyword_density_min = self.seo_rules.get('keyword_density_min', 0.5)
        self.keyword_density_max = self.seo_rules.get('keyword_density_max', 3.0)
        
        # 页面基础优化规则
        self.title_min_length = self.seo_rules.get('title_min_length', 30)
        self.title_max_length = self.seo_rules.get('title_max_length', 60)
        self.description_min_length = self.seo_rules.get('description_min_length', 120)
        self.description_max_length = self.seo_rules.get('description_max_length', 160)
        self.h1_required = self.seo_rules.get('h1_required', True)
        self.max_h1_count = self.seo_rules.get('max_h1_count', 1)
        self.min_content_length = self.seo_rules.get('min_content_length', 300)
    
    def check_page_seo(self, page_data, soup: BeautifulSoup, total_pages: int = None) -> List[SEOIssue]:
        """检查页面SEO"""
        issues = []
        
        # 1. 检查页面标题
        issues.extend(self.check_title(page_data, soup))
        
        # 2. 检查Meta描述
        issues.extend(self.check_meta_description(page_data, soup))
        
        # 3. 检查Meta关键词
        issues.extend(self.check_meta_keywords(page_data, soup))
        
        # 4. 检查H标签结构
        issues.extend(self.check_heading_structure(page_data, soup))
        
        # 5. 检查图片优化
        issues.extend(self.check_images(page_data, soup))
        
        # 6. 检查内部链接
        issues.extend(self.check_internal_links(page_data, soup))
        
        # 7. 检查外部链接
        issues.extend(self.check_external_links(page_data, soup))
        
        # 8. 检查内容质量
        issues.extend(self.check_content_quality(page_data, soup))
        
        # 9. 检查页面速度
        issues.extend(self.check_page_speed(page_data, soup))
        
        # 10. 检查移动端优化
        issues.extend(self.check_mobile_optimization(page_data, soup))
        
        # 11. 检查结构化数据
        issues.extend(self.check_structured_data(page_data, soup, total_pages))
        
        # 12. 检查URL结构
        issues.extend(self.check_url_structure(page_data, soup))
        
        # 13. 检查单页网站特有功能（仅在特定条件下）
        if self._is_single_page_website(page_data, total_pages):
            issues.extend(self.check_single_page_navigation(page_data, soup))
            
            # 14. 检查行动号召
            issues.extend(self.check_call_to_action(page_data, soup))
            
            # 15. 检查内容章节结构
            issues.extend(self.check_content_sections(page_data, soup))
            
            # 16. 检查隐藏内容
            issues.extend(self.check_hidden_content(page_data, soup))
        
        # 17. 检查面包屑导航
        issues.extend(self.check_breadcrumb_navigation(page_data, soup))
        
        # 18. 检查Canonical标签
        issues.extend(self.check_canonical_tag(page_data, soup))
        
        # 19. 检查内容新鲜度
        issues.extend(self.check_content_freshness(page_data, soup))
        
        # 19. 检查社交分享
        issues.extend(self.check_social_sharing(page_data, soup))
        
        # 20. 检查视频和图片SEO
        issues.extend(self.check_media_seo(page_data, soup))
        
        # 21. 检查网站可访问性
        issues.extend(self.check_accessibility(page_data, soup))
        
        # 22. 检查EEAT相关元素
        issues.extend(self.check_eeat_elements(page_data, soup))
        
        # 23. 检查内容新鲜度
        issues.extend(self.check_content_freshness(page_data, soup))
        
        # 24. 检查死链接
        issues.extend(self.check_broken_links(page_data, soup))
        
        return issues
    
    def check_title(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查页面标题"""
        issues = []
        title = page_data.title
        
        # 检查标题是否存在
        if not title:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="title_missing",
                severity="critical",
                message="页面缺少标题标签",
                suggestion="为页面添加<title>标签"
            ))
            return issues
        
        # 检查标题长度
        title_length = len(title)
        if title_length < self.title_min_length:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="title_too_short",
                severity="warning",
                message=f"页面标题过短 ({title_length}字符)",
                suggestion=f"建议标题长度在{self.title_min_length}-{self.title_max_length}字符之间",
                element="title"
            ))
        elif title_length > self.title_max_length:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="title_too_long",
                severity="warning",
                message=f"页面标题过长 ({title_length}字符)",
                suggestion=f"建议标题长度在{self.title_min_length}-{self.title_max_length}字符之间",
                element="title"
            ))
        
        # 检查标题是否包含关键词
        if not self.contains_keywords(title):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="title_no_keywords",
                severity="info",
                message="页面标题未包含关键词",
                suggestion="在标题中添加相关关键词",
                element="title"
            ))
        
        # 检查标题重复
        if self.is_duplicate_title(title):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="title_duplicate",
                severity="warning",
                message="页面标题与其他页面重复",
                suggestion="为每个页面创建唯一的标题",
                element="title"
            ))
        
        return issues
    
    def check_meta_description(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查Meta描述"""
        issues = []
        description = page_data.meta_description
        
        # 检查描述是否存在
        if not description:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="description_missing",
                severity="warning",
                message="页面缺少Meta描述",
                suggestion="为页面添加<meta name='description'>标签"
            ))
            return issues
        
        # 检查描述长度
        desc_length = len(description)
        if desc_length < self.description_min_length:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="description_too_short",
                severity="warning",
                message=f"Meta描述过短 ({desc_length}字符)",
                suggestion=f"建议描述长度在{self.description_min_length}-{self.description_max_length}字符之间",
                element="meta description"
            ))
        elif desc_length > self.description_max_length:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="description_too_long",
                severity="warning",
                message=f"Meta描述过长 ({desc_length}字符)",
                suggestion=f"建议描述长度在{self.description_min_length}-{self.description_max_length}字符之间",
                element="meta description"
            ))
        
        # 检查描述是否包含关键词
        if not self.contains_keywords(description):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="description_no_keywords",
                severity="info",
                message="Meta描述未包含关键词",
                suggestion="在描述中添加相关关键词",
                element="meta description"
            ))
        
        return issues
    
    def check_meta_keywords(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查Meta关键词"""
        issues = []
        keywords = page_data.meta_keywords
        
        # 检查关键词是否存在
        if not keywords:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="keywords_missing",
                severity="info",
                message="页面缺少Meta关键词",
                suggestion="为页面添加<meta name='keywords'>标签"
            ))
            return issues
        
        # 检查关键词数量
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        if len(keyword_list) > 10:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="keywords_too_many",
                severity="warning",
                message=f"Meta关键词过多 ({len(keyword_list)}个)",
                suggestion="建议关键词数量控制在3-5个",
                element="meta keywords"
            ))
        
        return issues
    
    def check_heading_structure(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查H标签结构"""
        issues = []
        
        # 检查H1标签
        h1_count = len(page_data.h1_tags)
        if self.h1_required and h1_count == 0:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="h1_missing",
                severity="critical",
                message="页面缺少H1标签",
                suggestion="为页面添加H1标签"
            ))
        elif h1_count > self.max_h1_count:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="h1_too_many",
                severity="warning",
                message=f"页面H1标签过多 ({h1_count}个)",
                suggestion=f"建议每页只有{self.max_h1_count}个H1标签",
                element="h1"
            ))
        
        # 检查H标签层次结构
        heading_structure = self.analyze_heading_structure(soup)
        if not self.is_valid_heading_structure(heading_structure):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="heading_structure_invalid",
                severity="warning",
                message="H标签层次结构不正确",
                suggestion="按照H1→H2→H3的顺序使用H标签",
                element="heading tags"
            ))
        
        # 检查H标签是否包含关键词
        for i, h1 in enumerate(page_data.h1_tags):
            if not self.contains_keywords(h1):
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="h1_no_keywords",
                    severity="info",
                    message=f"H1标签未包含关键词: {h1}",
                    suggestion="在H1标签中添加相关关键词",
                    element=f"h1[{i}]"
                ))
        
        return issues
    
    def check_images(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查图片优化"""
        issues = []
        
        for i, img in enumerate(page_data.images):
            # 检查Alt属性
            if not img.get('alt'):
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="image_no_alt",
                    severity="warning",
                    message=f"图片缺少Alt属性: {img.get('src', 'Unknown')}",
                    suggestion="为图片添加描述性的Alt属性",
                    element=f"img[{i}]"
                ))
            elif len(img.get('alt', '')) < 5:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="image_alt_too_short",
                    severity="info",
                    message=f"图片Alt属性过短: {img.get('alt', '')}",
                    suggestion="为图片添加更详细的Alt描述",
                    element=f"img[{i}]"
                ))
            
            # 检查图片文件名
            src = img.get('src', '')
            if src and not self.is_descriptive_filename(src):
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="image_filename_not_descriptive",
                    severity="info",
                    message=f"图片文件名不够描述性: {src}",
                    suggestion="使用描述性的图片文件名",
                    element=f"img[{i}]"
                ))
        
        return issues
    
    def check_internal_links(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查内部链接"""
        issues = []
        
        internal_links = page_data.internal_links
        
        # 检查内部链接数量
        if len(internal_links) == 0:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_internal_links",
                severity="info",
                message="页面缺少内部链接",
                suggestion="添加相关页面的内部链接"
            ))
        elif len(internal_links) > 100:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="too_many_internal_links",
                severity="warning",
                message=f"页面内部链接过多 ({len(internal_links)}个)",
                suggestion="减少内部链接数量，保持页面简洁"
            ))
        
        # 检查链接锚文本
        for link in soup.find_all('a', href=True):
            anchor_text = link.get_text().strip()
            if anchor_text and not self.is_descriptive_anchor_text(anchor_text):
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="anchor_text_not_descriptive",
                    severity="info",
                    message=f"链接锚文本不够描述性: {anchor_text}",
                    suggestion="使用描述性的链接锚文本",
                    element="a"
                ))
        
        return issues
    
    def check_external_links(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查外部链接"""
        issues = []
        
        external_links = page_data.external_links
        
        # 检查外部链接是否使用nofollow
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if self.is_external_link(href, page_data.url):
                rel = link.get('rel', [])
                if 'nofollow' not in rel:
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="external_link_no_nofollow",
                        severity="info",
                        message=f"外部链接未使用nofollow: {href}",
                        suggestion="为外部链接添加rel='nofollow'属性",
                        element="a"
                    ))
        
        return issues
    
    def check_content_quality(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查内容质量"""
        issues = []
        
        # 检查内容长度
        if page_data.content_length < self.min_content_length:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="content_too_short",
                severity="warning",
                message=f"页面内容过短 ({page_data.content_length}字符)",
                suggestion=f"建议内容长度至少{self.min_content_length}字符",
                element="body"
            ))
        
        # 检查关键词密度
        content = soup.get_text().lower()
        keyword_density = self.calculate_keyword_density(content, page_data.title, page_data.url)
        
        if keyword_density < self.keyword_density_min:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="keyword_density_too_low",
                severity="info",
                message=f"关键词密度过低 ({keyword_density:.2f}%)",
                suggestion=f"建议关键词密度在{self.keyword_density_min}-{self.keyword_density_max}%之间",
                element="body"
            ))
        elif keyword_density > self.keyword_density_max:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="keyword_density_too_high",
                severity="warning",
                message=f"关键词密度过高 ({keyword_density:.2f}%)",
                suggestion=f"建议关键词密度在{self.keyword_density_min}-{self.keyword_density_max}%之间",
                element="body"
            ))
        
        # 检查内容可读性
        readability_score = self.calculate_readability(content)
        if readability_score < 60:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="content_readability_low",
                severity="info",
                message=f"内容可读性较低 ({readability_score:.1f})",
                suggestion="简化句子结构，提高内容可读性",
                element="body"
            ))
        
        return issues
    
    def check_page_speed(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查页面速度"""
        issues = []
        
        # 检查页面加载时间
        if page_data.load_time > 3.0:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="page_slow",
                severity="warning",
                message=f"页面加载时间过长 ({page_data.load_time:.2f}秒)",
                suggestion="优化页面加载速度，建议控制在3秒以内",
                element="page"
            ))
        
        # 检查图片优化
        large_images = self.find_large_images(soup)
        for img in large_images:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="image_too_large",
                severity="info",
                message=f"图片文件可能过大: {img.get('src', 'Unknown')}",
                suggestion="压缩图片文件大小",
                element="img"
            ))
        
        return issues
    
    def check_mobile_optimization(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查移动端优化"""
        issues = []
        
        # 检查viewport标签
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_viewport",
                severity="critical",
                message="页面缺少viewport标签",
                suggestion="添加<meta name='viewport' content='width=device-width, initial-scale=1'>标签",
                element="meta"
            ))
        
        # 检查触摸目标大小
        small_buttons = self.find_small_buttons(soup)
        for button in small_buttons:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="button_too_small",
                severity="warning",
                message="按钮或链接过小，不适合触摸操作",
                suggestion="增加按钮和链接的尺寸",
                element="button/a"
            ))
        
        return issues
    
    def check_structured_data(self, page_data, soup: BeautifulSoup, total_pages: int = None) -> List[SEOIssue]:
        """检查结构化数据"""
        issues = []
        
        # 检查JSON-LD结构化数据
        json_ld = soup.find_all('script', type='application/ld+json')
        if not json_ld:
            # 根据网站页面数量决定提示信息
            if total_pages and total_pages <= 5:
                message = "页面缺少结构化数据（对单页网站至关重要）"
            else:
                message = "页面缺少结构化数据"
            
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_structured_data",
                severity="critical",
                message=message,
                suggestion="添加JSON-LD格式的结构化数据，包括Website、Organization、Product/Service等类型",
                element="script"
            ))
        else:
            # 检查结构化数据类型
            structured_data_types = []
            for script in json_ld:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        data_type = data.get('@type', '')
                        structured_data_types.append(data_type)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                data_type = item.get('@type', '')
                                structured_data_types.append(data_type)
                except:
                    pass
            
            # 检查是否包含推荐的结构化数据类型
            recommended_types = ['WebSite', 'Organization', 'LocalBusiness', 'Product', 'Service', 'FAQPage', 'Review']
            found_types = [t for t in structured_data_types if t in recommended_types]
            
            if not found_types:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="structured_data_type_missing",
                    severity="warning",
                    message="结构化数据类型不够全面",
                    suggestion="添加WebSite、Organization、Product/Service等推荐的结构化数据类型",
                    element="script"
                ))
            
            # 检查单页网站特有的结构化数据
            if 'WebSite' not in structured_data_types:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="no_website_schema",
                    severity="warning",
                    message="单页网站缺少WebSite结构化数据",
                    suggestion="添加WebSite类型的结构化数据标明网站性质",
                    element="script"
                ))
        
        return issues
    
    def check_url_structure(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查URL结构"""
        issues = []
        url = page_data.url
        
        # 检查URL长度
        if len(url) > 100:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="url_too_long",
                severity="warning",
                message=f"URL过长 ({len(url)}字符)",
                suggestion="缩短URL长度，建议控制在100字符以内",
                element="url"
            ))
        
        # 检查URL是否包含关键词
        url_path = urlparse(url).path.lower()
        if not self.contains_keywords(url_path):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="url_no_keywords",
                severity="info",
                message="URL未包含关键词",
                suggestion="在URL中添加相关关键词",
                element="url"
            ))
        
        return issues
    
    def check_single_page_navigation(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查单页网站的导航和锚点链接"""
        issues = []
        
        # 检查锚点链接
        anchor_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        
        if len(anchor_links) < 3:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="insufficient_anchor_navigation",
                severity="warning",
                message="单页网站锚点导航不足",
                suggestion="添加更多锚点链接进行页面内导航，提升用户体验",
                element="navigation"
            ))
        
        # 检查导航菜单
        nav_elements = soup.find_all(['nav', 'ul', 'ol'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['nav', 'menu', 'navigation']
        ))
        
        if not nav_elements:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_navigation_menu",
                severity="warning",
                message="单页网站缺少导航菜单",
                suggestion="添加清晰的导航菜单，帮助用户快速跳转到不同章节",
                element="navigation"
            ))
        
        # 检查回到顶部按钮（更全面的检测）
        back_to_top_found = self._check_back_to_top_button(soup)
        
        if not back_to_top_found:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_back_to_top",
                severity="info",
                message="单页网站缺少回到顶部按钮",
                suggestion="添加回到顶部按钮，提升长页面用户体验",
                element="navigation"
            ))
        
        return issues
    
    def check_call_to_action(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查行动号召按钮"""
        issues = []
        
        # 检查行动号召按钮
        cta_elements = soup.find_all(['button', 'a'], text=lambda x: x and any(
            keyword in x.lower() for keyword in [
                '立即', '马上', '现在', '点击', '购买', '联系', '咨询', '下载', '注册', '订阅',
                'now', 'click', 'buy', 'contact', 'download', 'register', 'subscribe', 'get started'
            ]
        ))
        
        if len(cta_elements) < 2:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="insufficient_cta_buttons",
                severity="warning",
                message="单页网站行动号召按钮不足",
                suggestion="添加更多醒目的行动号召按钮，引导用户转化",
                element="cta"
            ))
        
        # 检查联系表单
        contact_forms = soup.find_all('form')
        if not contact_forms:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_contact_form",
                severity="info",
                message="单页网站缺少联系表单",
                suggestion="添加联系表单，方便用户咨询和转化",
                element="form"
            ))
        
        return issues
    
    def check_content_sections(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查单页网站内容章节结构"""
        issues = []
        
        # 检查内容章节
        sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in [
                'section', 'chapter', 'part', 'block', 'content', 'main',
                '服务', '产品', '特点', '案例', '定价', '联系', '关于'
            ]
        ))
        
        if len(sections) < 4:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="insufficient_content_sections",
                severity="warning",
                message="单页网站内容章节不足",
                suggestion="添加更多内容章节，如服务介绍、产品特点、客户案例、定价信息等",
                element="content"
            ))
        
        # 检查H2标签数量（单页网站应该有多个H2）
        h2_count = len(page_data.h2_tags)
        if h2_count < 3:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="insufficient_h2_sections",
                severity="warning",
                message="单页网站H2标签不足",
                suggestion="添加更多H2标签划分内容章节，建议至少3-5个",
                element="h2"
            ))
        
        return issues
    
    def check_hidden_content(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查隐藏内容（单页网站常见问题）"""
        issues = []
        
        # 检查CSS隐藏的内容
        hidden_elements = soup.find_all(attrs={'style': lambda x: x and any(
            style in x.lower() for style in ['display:none', 'visibility:hidden', 'opacity:0']
        )})
        
        if len(hidden_elements) > 5:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="too_many_hidden_elements",
                severity="warning",
                message="页面隐藏元素过多，可能被误判为隐藏内容",
                suggestion="减少隐藏元素，确保主要内容对搜索引擎可见",
                element="hidden content"
            ))
        
        # 检查折叠内容
        collapsible_elements = soup.find_all(['details', 'summary'])
        if collapsible_elements:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="collapsible_content_detected",
                severity="info",
                message="检测到折叠内容，确保初始状态可见",
                suggestion="确保折叠内容在初始状态部分可见，避免被搜索引擎误判",
                element="collapsible content"
            ))
        
        return issues
    
    def check_breadcrumb_navigation(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查面包屑导航"""
        issues = []
        
        # 检查面包屑导航元素
        breadcrumb_selectors = [
            'nav[aria-label*="breadcrumb"]',
            'nav[aria-label*="Breadcrumb"]',
            '.breadcrumb',
            '.breadcrumbs',
            '[role="navigation"][aria-label*="breadcrumb"]',
            'ol[class*="breadcrumb"]',
            'ul[class*="breadcrumb"]'
        ]
        
        breadcrumb_found = False
        for selector in breadcrumb_selectors:
            if soup.select(selector):
                breadcrumb_found = True
                break
        
        if not breadcrumb_found:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_breadcrumb_navigation",
                severity="info",
                message="页面缺少面包屑导航",
                suggestion="添加面包屑导航帮助用户了解页面位置和网站结构",
                element="breadcrumb"
            ))
        else:
            # 检查面包屑导航结构
            breadcrumb_links = soup.select('nav[aria-label*="breadcrumb"] a, .breadcrumb a')
            if len(breadcrumb_links) < 2:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="insufficient_breadcrumb_links",
                    severity="warning",
                    message="面包屑导航链接不足",
                    suggestion="确保面包屑导航包含至少2个链接，形成完整的导航路径",
                    element="breadcrumb"
                ))
        
        return issues
    
    def check_canonical_tag(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查Canonical标签"""
        issues = []
        
        # 检查canonical标签
        canonical = soup.find('link', rel='canonical')
        if not canonical:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_canonical_tag",
                severity="warning",
                message="页面缺少canonical标签",
                suggestion="添加canonical标签避免重复内容问题",
                element="canonical"
            ))
        else:
            canonical_url = canonical.get('href', '')
            if canonical_url:
                # 检查canonical URL是否指向当前页面
                if canonical_url != page_data.url and not canonical_url.startswith(page_data.url):
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="canonical_url_mismatch",
                        severity="warning",
                        message=f"Canonical URL指向其他页面: {canonical_url}",
                        suggestion="确保canonical URL指向当前页面或正确的规范页面",
                        element="canonical"
                    ))
        
        # 检查是否有多个canonical标签
        canonical_tags = soup.find_all('link', rel='canonical')
        if len(canonical_tags) > 1:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="multiple_canonical_tags",
                severity="critical",
                message="页面包含多个canonical标签",
                suggestion="每个页面只能有一个canonical标签",
                element="canonical"
            ))
        
        return issues
    
    def check_social_sharing(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查社交分享功能"""
        issues = []
        
        # 检查Open Graph标签
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        if not og_tags:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_open_graph_tags",
                severity="info",
                message="页面缺少Open Graph标签",
                suggestion="添加Open Graph标签提升社交分享效果",
                element="og tags"
            ))
        else:
            # 检查必需的OG标签
            required_og_tags = ['og:title', 'og:description', 'og:image']
            found_og_tags = [tag.get('property', '') for tag in og_tags]
            
            for required_tag in required_og_tags:
                if required_tag not in found_og_tags:
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type=f"missing_{required_tag.replace(':', '_')}",
                        severity="warning",
                        message=f"缺少{required_tag}标签",
                        suggestion=f"添加{required_tag}标签提升社交分享效果",
                        element="og tags"
                    ))
        
        # 检查Twitter Card标签
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        if not twitter_tags:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_twitter_cards",
                severity="info",
                message="页面缺少Twitter Card标签",
                suggestion="添加Twitter Card标签提升Twitter分享效果",
                element="twitter cards"
            ))
        
        # 检查社交分享按钮
        social_buttons = soup.find_all(['a', 'button'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in [
                'share', 'facebook', 'twitter', 'linkedin', 'wechat', 'weibo',
                'social', '分享', '微博', '微信'
            ]
        ))
        
        if len(social_buttons) < 2:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="insufficient_social_buttons",
                severity="info",
                message="社交分享按钮不足",
                suggestion="添加更多社交分享按钮，增加内容曝光和流量",
                element="social buttons"
            ))
        
        return issues
    
    def check_media_seo(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查视频和图片SEO"""
        issues = []
        
        # 检查视频元素
        videos = soup.find_all(['video', 'iframe'])
        for i, video in enumerate(videos):
            # 检查视频标题
            video_title = video.get('title', '')
            if not video_title:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="video_no_title",
                    severity="warning",
                    message=f"视频缺少标题属性",
                    suggestion="为视频添加title属性提升可访问性和SEO",
                    element=f"video[{i}]"
                ))
            
            # 检查视频描述
            video_description = video.find('p', class_=lambda x: x and 'description' in x.lower())
            if not video_description:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="video_no_description",
                    severity="info",
                    message=f"视频缺少文字描述",
                    suggestion="为视频添加文字描述，提升SEO和用户体验",
                    element=f"video[{i}]"
                ))
        
        # 检查图片SEO增强
        for i, img in enumerate(page_data.images):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # 检查图片标题
            img_title = img.get('title', '')
            if not img_title and alt:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="image_no_title",
                    severity="info",
                    message=f"图片缺少title属性: {src}",
                    suggestion="为重要图片添加title属性",
                    element=f"img[{i}]"
                ))
            
            # 检查图片说明文字
            img_caption = soup.find('img', src=src)
            if img_caption:
                caption_element = img_caption.find_next(['figcaption', 'p', 'div'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['caption', 'description', '说明', '描述']
                ))
                if not caption_element and len(alt) > 50:
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="image_no_caption",
                        severity="info",
                        message=f"重要图片缺少说明文字: {src}",
                        suggestion="为重要图片添加说明文字，提升图片搜索排名",
                        element=f"img[{i}]"
                    ))
        
        return issues
    
    def check_accessibility(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查网站可访问性"""
        issues = []
        
        # 检查图片Alt属性（已在图片检查中实现，这里做补充检查）
        images_without_alt = soup.find_all('img', alt=False)
        if len(images_without_alt) > 0:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="accessibility_images_no_alt",
                severity="warning",
                message=f"有{len(images_without_alt)}个图片缺少Alt属性",
                suggestion="为所有图片添加Alt属性，提升可访问性",
                element="accessibility"
            ))
        
        # 检查表单标签（只检查主要表单，排除搜索框等简单表单）
        forms = soup.find_all('form')
        for i, form in enumerate(forms):
            inputs = form.find_all(['input', 'textarea', 'select'])
            labels = form.find_all('label')
            
            # 跳过搜索框等简单表单（通常只有1个输入框且没有复杂交互）
            if len(inputs) <= 1 and len(labels) == 0:
                # 检查是否是搜索框
                is_search_form = False
                for inp in inputs:
                    input_type = inp.get('type', 'text')
                    placeholder = inp.get('placeholder', '').lower()
                    name = inp.get('name', '').lower()
                    if (input_type == 'search' or 
                        'search' in placeholder or 
                        'search' in name or
                        'query' in name):
                        is_search_form = True
                        break
                
                if is_search_form:
                    continue
            
            # 只对复杂表单（多个输入元素或明确需要标签的表单）检查标签
            if len(inputs) > 1 and len(labels) == 0:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="form_no_labels",
                    severity="warning",
                    message=f"复杂表单缺少标签元素",
                    suggestion="为表单输入元素添加label标签，提升可访问性",
                    element=f"form[{i}]"
                ))
        
        # 检查颜色对比度（基础检查）
        elements_with_color = soup.find_all(attrs={'style': lambda x: x and ('color:' in x or 'background:' in x)})
        if len(elements_with_color) > 0:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="color_contrast_check_needed",
                severity="info",
                message="页面包含内联颜色样式，建议检查对比度",
                suggestion="确保文字和背景颜色对比度符合WCAG标准（至少4.5:1）",
                element="accessibility"
            ))
        
        # 检查视频字幕
        videos = soup.find_all(['video', 'iframe'])
        for i, video in enumerate(videos):
            # 检查是否有字幕轨道
            tracks = video.find_all('track', kind='captions')
            if not tracks:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="video_no_captions",
                    severity="warning",
                    message=f"视频缺少字幕轨道",
                    suggestion="为视频添加字幕轨道，提升可访问性",
                    element=f"video[{i}]"
                ))
        
        # 检查语言声明
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_language_declaration",
                severity="critical",
                message="HTML标签缺少语言声明",
                suggestion="为html标签添加lang属性，如<html lang='zh-CN'>",
                element="html"
            ))
        
        return issues
    
    def check_eeat_elements(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查EEAT（经验、专业、权威、可信）相关元素"""
        issues = []
        
        # 注意：作者信息检查已移至全站级别检查，这里不再检查单个页面的作者信息
        # 因为整个网站只需要有一个页面包含作者信息即可
        
        # 检查JSON-LD结构化数据
        issues.extend(self.check_json_ld_structure(page_data, soup))
        
        # 检查发布时间
        date_selectors = [
            'time', '.date', '.publish-date', '.post-date',
            '[datetime]', '[itemprop="datePublished"]'
        ]
        
        date_found = False
        for selector in date_selectors:
            if soup.select(selector):
                date_found = True
                break
        
        if not date_found:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_publication_date",
                severity="info",
                message="页面缺少发布时间信息",
                suggestion="添加发布时间提升内容的权威性和新鲜度",
                element="publication date"
            ))
        
        # 联系信息检查已移至网站级别检查
        
        # 检查关于我们/公司信息
        about_selectors = [
            '.about', '.company-info', '.organization', '.about-us',
            '[itemprop="organization"]', '.business-info'
        ]
        
        about_found = False
        for selector in about_selectors:
            if soup.select(selector):
                about_found = True
                break
        
        if not about_found:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_about_info",
                severity="info",
                message="页面缺少关于我们信息",
                suggestion="添加关于我们或公司信息提升专业性和可信度",
                element="about"
            ))
        
        # 检查证书/资质信息（仅对特定页面类型）
        if self._should_page_have_credentials(page_data, soup):
            credential_selectors = [
                '.certificate', '.credential', '.license', '.certification',
                '.award', '.recognition', '.badge'
            ]
            
            credential_found = False
            for selector in credential_selectors:
                if soup.select(selector):
                    credential_found = True
                    break
            
            if not credential_found:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="no_credentials",
                    severity="info",
                    message="页面缺少证书或资质信息",
                    suggestion="展示相关证书、资质或奖项提升专业权威性",
                    element="credentials"
                ))
        
        return issues
    
    def check_content_freshness(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查内容新鲜度"""
        issues = []
        
        # 智能判断页面是否需要时间信息
        needs_date_info = self._should_page_have_date_info(page_data, soup)
        
        # 只有需要时间信息的页面才检查
        if needs_date_info:
            # 检查最后更新时间
            last_modified_selectors = [
                'meta[http-equiv="last-modified"]',
                '[itemprop="dateModified"]',
                '.last-updated',
                '.modified-date'
            ]
            
            last_modified_found = False
            for selector in last_modified_selectors:
                if soup.select(selector):
                    last_modified_found = True
                    break
            
            if not last_modified_found:
                issues.append(SEOIssue(
                    page_url=page_data.url,
                    issue_type="no_last_modified",
                    severity="info",
                    message="页面缺少最后更新时间信息",
                    suggestion="添加最后更新时间信息，特别是对于需要保持新鲜的内容",
                    element="last modified"
                ))
        
        # 检查版权年份（判断内容是否过时）
        copyright_elements = soup.find_all(text=lambda text: text and '©' in text or 'copyright' in text.lower())
        current_year = datetime.now().year
        
        for copyright_text in copyright_elements:
            # 提取年份
            import re
            years = re.findall(r'\b(20\d{2})\b', str(copyright_text))
            if years:
                latest_year = max([int(year) for year in years])
                if latest_year < current_year - 2:
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="outdated_copyright",
                        severity="warning",
                        message=f"版权信息可能过时（最新年份: {latest_year}）",
                        suggestion="更新版权年份信息，保持内容新鲜度",
                        element="copyright"
                    ))
                break
        
        # 检查是否有"最新"、"新"等时间相关关键词
        time_indicators = ['最新', '新', '2024', '2025', 'recent', 'latest', 'new', 'updated']
        page_text = soup.get_text().lower()
        
        has_time_indicators = any(indicator in page_text for indicator in time_indicators)
        if not has_time_indicators:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_time_indicators",
                severity="info",
                message="页面缺少时间相关指示词",
                suggestion="在适当位置添加时间相关词汇，如'最新'、'2024'等，提升内容新鲜度感知",
                element="content freshness"
            ))
        
        return issues
    
    # 辅助方法
    def contains_keywords(self, text: str) -> bool:
        """检查文本是否包含关键词"""
        # 扩展的关键词列表，适合单页网站
        keywords = [
            # 中文关键词
            '工具', '计算器', '转换器', '生成器', '检查器', '分析器', '服务', '产品', '解决方案',
            '在线', '免费', '专业', '高效', '快速', '简单', '易用', '智能', '自动化',
            # 英文关键词
            'tool', 'calculator', 'converter', 'generator', 'checker', 'analyzer', 
            'service', 'product', 'solution', 'online', 'free', 'professional', 
            'efficient', 'fast', 'simple', 'easy', 'smart', 'automatic',
            # 单页网站特有
            '单页', '一站式', 'all-in-one', 'complete', 'comprehensive'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def is_duplicate_title(self, title: str) -> bool:
        """检查标题是否重复"""
        # 这里可以添加重复检测逻辑
        # 简化版本：返回False
        return False
    
    def is_descriptive_filename(self, src: str) -> bool:
        """检查文件名是否描述性"""
        filename = src.split('/')[-1].split('.')[0]
        # 检查文件名是否包含描述性词汇
        descriptive_words = ['image', 'photo', 'picture', 'img', '图片', '照片']
        return any(word in filename.lower() for word in descriptive_words)
    
    def is_descriptive_anchor_text(self, anchor_text: str) -> bool:
        """检查锚文本是否描述性"""
        # 检查锚文本长度和内容
        if len(anchor_text) < 3:
            return False
        if anchor_text.lower() in ['点击这里', '点击', '更多', 'click here', 'more', 'read more']:
            return False
        return True
    
    def is_external_link(self, href: str, base_url: str) -> bool:
        """检查是否为外部链接"""
        try:
            link_domain = urlparse(href).netloc
            base_domain = urlparse(base_url).netloc
            return link_domain != base_domain and link_domain != ''
        except:
            return False
    
    def analyze_heading_structure(self, soup: BeautifulSoup) -> List[str]:
        """分析H标签结构"""
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append(tag.name)
        return headings
    
    def is_valid_heading_structure(self, structure: List[str]) -> bool:
        """检查H标签结构是否有效"""
        if not structure:
            return True
        
        # 检查是否按层次使用
        prev_level = 0
        for heading in structure:
            level = int(heading[1])
            if level > prev_level + 1:
                return False
            prev_level = level
        
        return True
    
    def calculate_keyword_density(self, content: str, page_title: str, page_url: str = "") -> float:
        """基于页面标题计算关键词密度"""
        if not page_title or not content:
            return 0.0
        
        # 从页面标题中提取核心关键词
        keywords = self._extract_keywords_from_title(page_title)
        
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        # 如果内容太少，不进行密度检查
        if total_words < 50:
            return 0.0
        
        keyword_count = 0
        for keyword in keywords:
            keyword_count += content.lower().count(keyword.lower())
        
        density = (keyword_count / total_words) * 100
        
        # 如果密度异常高（>50%），可能是内容太少或关键词重复过多
        if density > 50:
            return 0.0  # 返回0表示不进行密度检查
        
        return density
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """从页面标题中提取核心关键词"""
        if not title:
            return []
        
        import re
        
        # 移除HTML标签
        title = re.sub(r'<[^>]+>', '', title)
        
        # 处理常见的标题格式，提取核心部分
        # 1. 移除网站名称（通常在分隔符后面）
        separators = [' - ', ' | ', ' _ ', ' – ', ' — ', ' :: ', ' :: ', ' | ', ' - ', ' | ']
        for sep in separators:
            if sep in title:
                # 取分隔符前面的部分作为核心标题
                title = title.split(sep)[0].strip()
                break
        
        # 2. 移除常见的网站名称后缀
        site_suffixes = [
            'zuhelper', 'zuhelper.com', '在线工具', '工具集合', '专业工具',
            'tool', 'tools', 'online', 'free', 'generator', 'calculator'
        ]
        
        for suffix in site_suffixes:
            if title.lower().endswith(suffix.lower()):
                title = title[:-len(suffix)].strip()
                break
        
        # 3. 移除常见的停用词和符号
        stop_words = [
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        ]
        
        # 移除标点符号和特殊字符
        title = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', title)
        
        # 分词
        words = title.lower().split()
        
        # 过滤停用词和短词
        keywords = []
        for word in words:
            word = word.strip()
            if (len(word) >= 2 and  # 至少2个字符
                word not in stop_words and  # 不是停用词
                not word.isdigit() and  # 不是纯数字
                word not in keywords):  # 不重复
                keywords.append(word)
        
        # 如果提取的关键词太少，添加一些通用关键词
        if len(keywords) < 2:
            keywords.extend(['工具', '在线', '免费'])
        
        return keywords[:5]  # 最多返回5个关键词
    
    def _get_relevant_keywords(self, page_url: str, content: str) -> List[str]:
        """根据页面类型获取相关关键词"""
        url_lower = page_url.lower()
        content_lower = content.lower()
        
        # 工具页面关键词
        if any(keyword in url_lower for keyword in ['tool', 'calculator', 'converter', 'generator', '工具', '计算', '转换']):
            return ['工具', '计算器', '转换器', '生成器', '在线', '免费', 'tool', 'calculator', 'converter', 'generator', 'online', 'free']
        
        # 文本处理页面
        if any(keyword in url_lower for keyword in ['text', 'text-processing', '文本', '处理']):
            return ['文本', '处理', '转换', '格式化', 'text', 'processing', 'convert', 'format']
        
        # 图像处理页面
        if any(keyword in url_lower for keyword in ['image', 'image-processing', '图片', '图像']):
            return ['图片', '图像', '处理', '压缩', '转换', 'image', 'processing', 'compress', 'convert']
        
        # 编程开发页面
        if any(keyword in url_lower for keyword in ['programming', 'development', '编程', '开发']):
            return ['编程', '开发', '代码', '程序', 'programming', 'development', 'code', 'program']
        
        # 网络工具页面
        if any(keyword in url_lower for keyword in ['network', 'web', '网络', '网站']):
            return ['网络', '网站', '工具', '检测', 'network', 'web', 'tool', 'check']
        
        # 生活工具页面
        if any(keyword in url_lower for keyword in ['life', 'lifestyle', '生活', '日常']):
            return ['生活', '日常', '工具', '计算', 'life', 'lifestyle', 'tool', 'calculate']
        
        # 默认关键词（通用）
        return ['工具', '在线', '免费', 'tool', 'online', 'free']
    
    
    def calculate_readability(self, content: str) -> float:
        """计算内容可读性分数"""
        # 简化的Flesch Reading Ease计算
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        syllables = self.count_syllables(content)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease公式
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))
    
    def count_syllables(self, text: str) -> int:
        """计算音节数（简化版本）"""
        vowels = 'aeiouy'
        text = text.lower()
        syllable_count = 0
        prev_was_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # 处理以'e'结尾的单词
        if text.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def find_large_images(self, soup: BeautifulSoup) -> List[Dict]:
        """查找可能过大的图片"""
        large_images = []
        for img in soup.find_all('img'):
            width = img.get('width')
            height = img.get('height')
            
            # 检查图片尺寸
            if width and height:
                try:
                    w = int(width)
                    h = int(height)
                    if w > 1920 or h > 1080:
                        large_images.append(img)
                except ValueError:
                    pass
        
        return large_images
    
    def find_small_buttons(self, soup: BeautifulSoup) -> List[Dict]:
        """查找过小的按钮或链接"""
        small_buttons = []
        for element in soup.find_all(['button', 'a']):
            style = element.get('style', '')
            # 检查CSS样式中的尺寸
            if 'width' in style or 'height' in style:
                # 这里可以添加更复杂的CSS解析
                pass
            else:
                # 检查文本长度，过短的可能是小按钮
                text = element.get_text().strip()
                if len(text) < 3 and element.name == 'a':
                    small_buttons.append(element)
        
        return small_buttons
    
    def extract_keywords_from_content(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        # 简单的关键词提取
        words = content.lower().split()
        word_freq = {}
        
        # 过滤停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        for word in words:
            # 清理单词
            word = re.sub(r'[^\w]', '', word)
            if len(word) > 2 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的前10个词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def check_duplicate_content(self, page_data, all_pages_data: List) -> List[SEOIssue]:
        """检查重复内容"""
        issues = []
        current_content = page_data.content_length
        
        for other_page in all_pages_data:
            if other_page.url != page_data.url:
                # 简单的内容相似度检查
                similarity = self.calculate_content_similarity(page_data, other_page)
                if similarity > 0.8:  # 80%相似度阈值
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="duplicate_content",
                        severity="warning",
                        message=f"页面内容与 {other_page.url} 高度相似 ({similarity:.1%})",
                        suggestion="创建独特的内容，避免重复",
                        element="body"
                    ))
        
        return issues
    
    def calculate_content_similarity(self, page1, page2) -> float:
        """计算两个页面的内容相似度"""
        # 简化的相似度计算
        content1 = page1.content_length
        content2 = page2.content_length
        
        if content1 == 0 or content2 == 0:
            return 0.0
        
        # 基于内容长度的简单相似度
        length_diff = abs(content1 - content2)
        max_length = max(content1, content2)
        
        return 1.0 - (length_diff / max_length)
    
    def check_broken_links(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查损坏的链接"""
        issues = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                # 检查URL格式
                if not self.is_valid_url_format(href):
                    issues.append(SEOIssue(
                        page_url=page_data.url,
                        issue_type="broken_link",
                        severity="warning",
                        message=f"格式错误的链接: {href}",
                        suggestion="检查链接格式是否正确",
                        element="a"
                    ))
                else:
                    # 这里可以添加实际的HTTP状态检查
                    # 由于性能考虑，暂时只检查格式
                    pass
        
        return issues
    
    def is_valid_url_format(self, url: str) -> bool:
        """检查URL格式是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def check_ssl_certificate(self, page_data) -> List[SEOIssue]:
        """检查SSL证书"""
        issues = []
        url = page_data.url
        
        if not url.startswith('https://'):
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_https",
                severity="critical",
                message="网站未使用HTTPS协议",
                suggestion="启用SSL证书，使用HTTPS协议",
                element="protocol"
            ))
        
        return issues
    
    def check_robots_txt(self, base_url: str) -> List[SEOIssue]:
        """检查robots.txt文件"""
        issues = []
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 404:
                issues.append(SEOIssue(
                    page_url=base_url,
                    issue_type="no_robots_txt",
                    severity="info",
                    message="网站缺少robots.txt文件",
                    suggestion="创建robots.txt文件指导搜索引擎爬取",
                    element="robots.txt"
                ))
        except:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="robots_txt_error",
                severity="warning",
                message="无法访问robots.txt文件",
                suggestion="检查robots.txt文件是否存在且可访问",
                element="robots.txt"
            ))
        
        return issues
    
    def check_sitemap(self, base_url: str) -> List[SEOIssue]:
        """检查网站地图"""
        issues = []
        
        try:
            sitemap_urls = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemap_index.xml'),
                urljoin(base_url, '/sitemaps.xml')
            ]
            
            sitemap_found = False
            for sitemap_url in sitemap_urls:
                response = requests.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    sitemap_found = True
                    break
            
            if not sitemap_found:
                issues.append(SEOIssue(
                    page_url=base_url,
                    issue_type="no_sitemap",
                    severity="info",
                    message="网站缺少XML网站地图",
                    suggestion="创建XML网站地图帮助搜索引擎发现页面",
                    element="sitemap.xml"
                ))
        except:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="sitemap_error",
                severity="warning",
                message="无法检查网站地图",
                suggestion="确保网站地图文件存在且可访问",
                element="sitemap.xml"
            ))
        
        return issues
    
    def generate_seo_score(self, issues: List[SEOIssue]) -> float:
        """根据问题生成SEO评分"""
        base_score = 100.0
        
        for issue in issues:
            if issue.severity == 'critical':
                base_score -= 15
            elif issue.severity == 'warning':
                base_score -= 8
            elif issue.severity == 'info':
                base_score -= 3
        
        return max(0.0, base_score)
    
    def get_seo_grade(self, score: float) -> str:
        """根据评分获取SEO等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_priority_issues(self, issues: List[SEOIssue]) -> List[SEOIssue]:
        """获取优先处理的问题"""
        priority_order = ['critical', 'warning', 'info']
        return sorted(issues, key=lambda x: priority_order.index(x.severity))
    
    def check_website_global_seo(self, base_url: str, all_pages_data: List, max_pages: int = None) -> List[SEOIssue]:
        """检查网站级别的全局SEO问题"""
        issues = []
        
        # 1. 检查robots.txt
        issues.extend(self.check_robots_txt(base_url))
        
        # 2. 检查sitemap.xml
        issues.extend(self.check_sitemap(base_url))
        
        # 3. 检查网站联系信息（全站检查）
        issues.extend(self.check_website_contact_info(base_url, all_pages_data, max_pages))
        
        # 4. 检查favicon
        issues.extend(self.check_favicon(base_url))
        
        # 5. 检查全局导航结构
        issues.extend(self.check_global_navigation(base_url, all_pages_data))
        
        return issues
    
    def check_website_contact_info(self, base_url: str, all_pages_data: List, max_pages: int = None) -> List[SEOIssue]:
        """检查网站联系信息和作者信息（全站检查）"""
        issues = []
        
        # 检查是否已遍历全站（达到最大页数限制）
        if max_pages and len(all_pages_data) >= max_pages:
            # 如果达到最大页数限制，说明可能还有页面未检查
            # 此时不进行联系信息检查，因为可能遗漏了包含联系信息的页面
            return issues
        
        # 检查所有已采集的页面是否有联系信息
        contact_found = False
        author_found = False
        
        for page in all_pages_data:
            if self._check_contact_info_in_page(page):
                contact_found = True
            if self._check_author_info_in_page(page):
                author_found = True
            
            # 如果都找到了，可以提前退出
            if contact_found and author_found:
                break
        
        # 检查联系信息
        if not contact_found:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="no_website_contact_info",
                severity="info",
                message="网站缺少联系信息",
                suggestion="在网站任意页面添加联系信息提升网站可信度",
                element="contact"
            ))
        
        # 检查作者信息
        if not author_found:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="no_website_author_info",
                severity="warning",
                message="网站缺少作者信息",
                suggestion="在网站任意页面添加作者信息提升内容的专业性和可信度",
                element="author"
            ))
        
        # 检查JSON-LD结构化数据中的作者和组织信息
        issues.extend(self.check_website_json_ld_info(base_url, all_pages_data))
        
        return issues
    
    def _check_contact_info_in_page(self, page_data) -> bool:
        """检查单个页面是否有联系信息"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_data.html, 'html.parser')
        
        contact_selectors = [
            'a[href^="mailto:"]', 'a[href^="tel:"]', '.contact', '.contact-info',
            '.address', '[itemprop="telephone"]', '[itemprop="email"]'
        ]
        
        for selector in contact_selectors:
            if soup.select(selector):
                return True
        return False
    
    def _check_author_info_in_page(self, page_data) -> bool:
        """检查单个页面是否有作者信息"""
        from bs4 import BeautifulSoup
        import json
        soup = BeautifulSoup(page_data.html, 'html.parser')
        
        # 1. 检查传统HTML元素中的作者信息
        author_selectors = [
            '.author', '.byline', '.author-info', '[rel="author"]',
            '.post-author', '.article-author', '[itemprop="author"]',
            '.about', '.about-us', '.team', '.staff'
        ]
        
        for selector in author_selectors:
            if soup.select(selector):
                return True
        
        # 2. 检查JSON-LD结构化数据中的作者信息
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if self._check_author_in_json_ld(data):
                    return True
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return False
    
    def _check_author_in_json_ld(self, data) -> bool:
        """检查JSON-LD数据中是否包含作者信息"""
        if isinstance(data, dict):
            # 检查直接的作者字段
            author_fields = ['author', 'creator', 'copyrightHolder', 'publisher']
            for field in author_fields:
                if field in data and data[field]:
                    return True
            
            # 检查@graph数组中的作者信息
            if '@graph' in data and isinstance(data['@graph'], list):
                for item in data['@graph']:
                    if isinstance(item, dict):
                        if item.get('@type') == 'Organization':
                            return True
                        if any(field in item for field in author_fields):
                            return True
            
            # 递归检查嵌套对象
            for value in data.values():
                if isinstance(value, (dict, list)):
                    if self._check_author_in_json_ld(value):
                        return True
        
        elif isinstance(data, list):
            for item in data:
                if self._check_author_in_json_ld(item):
                    return True
        
        return False
    
    def check_json_ld_structure(self, page_data, soup: BeautifulSoup) -> List[SEOIssue]:
        """检查JSON-LD结构化数据"""
        issues = []
        import json
        
        # 查找所有JSON-LD脚本
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        if not json_ld_scripts:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_json_ld",
                severity="warning",
                message="页面缺少JSON-LD结构化数据",
                suggestion="添加JSON-LD结构化数据提升搜索引擎理解",
                element="json-ld"
            ))
            return issues
        
        # 解析JSON-LD数据
        json_ld_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    json_ld_data.extend(data)
                else:
                    json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        if not json_ld_data:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="invalid_json_ld",
                severity="warning",
                message="JSON-LD数据格式无效",
                suggestion="检查JSON-LD语法是否正确",
                element="json-ld"
            ))
            return issues
        
        # 检查基础信息
        issues.extend(self._check_json_ld_basic_info(page_data, json_ld_data))
        
        # 检查内容页面信息
        issues.extend(self._check_json_ld_content_info(page_data, json_ld_data))
        
        return issues
    
    def _check_json_ld_basic_info(self, page_data, json_ld_data: List) -> List[SEOIssue]:
        """检查JSON-LD基础信息"""
        issues = []
        
        # 检查是否有WebPage类型
        has_webpage = False
        for data in json_ld_data:
            if isinstance(data, dict) and data.get('@type') == 'WebPage':
                has_webpage = True
                break
        
        if not has_webpage:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_webpage_type",
                severity="info",
                message="JSON-LD缺少WebPage类型",
                suggestion="添加@type为WebPage的基础页面信息",
                element="json-ld"
            ))
        
        # 检查基础字段
        required_fields = ['name', 'url', 'inLanguage']
        for data in json_ld_data:
            if isinstance(data, dict) and data.get('@type') == 'WebPage':
                for field in required_fields:
                    if field not in data or not data[field]:
                        issues.append(SEOIssue(
                            page_url=page_data.url,
                            issue_type=f"missing_json_ld_{field}",
                            severity="info",
                            message=f"JSON-LD缺少{field}字段",
                            suggestion=f"在WebPage类型中添加{field}字段",
                            element="json-ld"
                        ))
                break
        
        return issues
    
    def _check_json_ld_content_info(self, page_data, json_ld_data: List) -> List[SEOIssue]:
        """检查JSON-LD内容页面信息"""
        issues = []
        
        # 检查内容页面字段
        content_fields = ['headline', 'description', 'datePublished', 'dateModified']
        has_content_info = False
        
        for data in json_ld_data:
            if isinstance(data, dict) and data.get('@type') in ['WebPage', 'Article', 'BlogPosting']:
                has_content_info = True
                for field in content_fields:
                    if field not in data or not data[field]:
                        issues.append(SEOIssue(
                            page_url=page_data.url,
                            issue_type=f"missing_json_ld_{field}",
                            severity="info",
                            message=f"JSON-LD缺少{field}字段",
                            suggestion=f"添加{field}字段提升内容结构化",
                            element="json-ld"
                        ))
                break
        
        if not has_content_info:
            issues.append(SEOIssue(
                page_url=page_data.url,
                issue_type="no_content_json_ld",
                severity="info",
                message="JSON-LD缺少内容页面信息",
                suggestion="添加Article或BlogPosting类型的结构化数据",
                element="json-ld"
            ))
        
        return issues
    
    def check_website_json_ld_info(self, base_url: str, all_pages_data: List) -> List[SEOIssue]:
        """检查网站JSON-LD结构化数据中的作者和组织信息"""
        issues = []
        import json
        from bs4 import BeautifulSoup
        
        # 检查所有页面是否有JSON-LD的作者和组织信息
        has_author_info = False
        has_organization_info = False
        has_social_links = False
        
        for page in all_pages_data:
            soup = BeautifulSoup(page.html, 'html.parser')
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        json_ld_data = data
                    else:
                        json_ld_data = [data]
                    
                    for item in json_ld_data:
                        if isinstance(item, dict):
                            # 检查作者信息
                            if not has_author_info:
                                author_fields = ['author', 'creator', 'copyrightHolder', 'publisher']
                                if any(field in item for field in author_fields):
                                    has_author_info = True
                            
                            # 检查组织信息
                            if not has_organization_info:
                                if item.get('@type') == 'Organization':
                                    has_organization_info = True
                            
                            # 检查社交链接
                            if not has_social_links:
                                if 'sameAs' in item and isinstance(item['sameAs'], list) and len(item['sameAs']) > 0:
                                    has_social_links = True
                            
                            # 如果都找到了，可以提前退出
                            if has_author_info and has_organization_info and has_social_links:
                                break
                    
                    if has_author_info and has_organization_info and has_social_links:
                        break
                        
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            if has_author_info and has_organization_info and has_social_links:
                break
        
        # 生成检查结果
        if not has_author_info:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="no_json_ld_author",
                severity="warning",
                message="网站JSON-LD缺少作者信息",
                suggestion="在JSON-LD结构化数据中添加author、creator或publisher字段",
                element="json-ld"
            ))
        
        if not has_organization_info:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="no_json_ld_organization",
                severity="warning",
                message="网站JSON-LD缺少组织信息",
                suggestion="添加@type为Organization的结构化数据",
                element="json-ld"
            ))
        
        if not has_social_links:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="no_json_ld_social_links",
                severity="info",
                message="网站JSON-LD缺少社交媒体链接",
                suggestion="在Organization类型中添加sameAs字段包含社交媒体链接",
                element="json-ld"
            ))
        
        return issues
    
    def check_favicon(self, base_url: str) -> List[SEOIssue]:
        """检查网站favicon"""
        issues = []
        
        try:
            favicon_urls = [
                urljoin(base_url, '/favicon.ico'),
                urljoin(base_url, '/favicon.png'),
                urljoin(base_url, '/apple-touch-icon.png')
            ]
            
            favicon_found = False
            for favicon_url in favicon_urls:
                response = requests.head(favicon_url, timeout=10)
                if response.status_code == 200:
                    favicon_found = True
                    break
            
            if not favicon_found:
                issues.append(SEOIssue(
                    page_url=base_url,
                    issue_type="no_favicon",
                    severity="info",
                    message="网站缺少favicon图标",
                    suggestion="添加favicon.ico文件提升网站专业度",
                    element="favicon"
                ))
        except:
            pass
        
        return issues
    
    def check_global_navigation(self, base_url: str, all_pages_data: List) -> List[SEOIssue]:
        """检查全局导航结构"""
        issues = []
        
        # 检查是否有足够的页面形成导航结构
        if len(all_pages_data) < 3:
            issues.append(SEOIssue(
                page_url=base_url,
                issue_type="insufficient_pages",
                severity="info",
                message="网站页面数量较少",
                suggestion="增加更多页面内容提升网站丰富度",
                element="navigation"
            ))
        
        return issues
    
    def _should_page_have_date_info(self, page_data, soup: BeautifulSoup) -> bool:
        """智能判断页面是否需要时间信息"""
        
        # 1. 检查页面内容特征
        content_indicators = self._analyze_content_indicators(page_data, soup)
        
        # 2. 检查页面结构特征
        structure_indicators = self._analyze_structure_indicators(soup)
        
        # 3. 检查页面功能特征
        functionality_indicators = self._analyze_functionality_indicators(page_data, soup)
        
        # 综合判断
        return self._make_date_info_decision(content_indicators, structure_indicators, functionality_indicators)
    
    def _analyze_content_indicators(self, page_data, soup: BeautifulSoup) -> Dict[str, bool]:
        """分析内容特征"""
        indicators = {
            'has_news_content': False,
            'has_blog_content': False,
            'has_tutorial_content': False,
            'has_static_content': False,
            'has_tool_content': False
        }
        
        # 检查新闻相关内容
        news_keywords = ['news', 'update', 'announcement', '新闻', '更新', '公告']
        if any(keyword in page_data.title.lower() for keyword in news_keywords if page_data.title):
            indicators['has_news_content'] = True
        
        # 检查博客相关内容
        blog_elements = soup.find_all(['article', '.post', '.blog-post', '.entry'])
        if blog_elements:
            indicators['has_blog_content'] = True
        
        # 检查教程/文档内容
        tutorial_keywords = ['tutorial', 'guide', 'how-to', '教程', '指南', '如何']
        if any(keyword in page_data.title.lower() for keyword in tutorial_keywords if page_data.title):
            indicators['has_tutorial_content'] = True
        
        # 检查静态内容
        static_keywords = ['about', 'contact', 'privacy', 'terms', '关于', '联系', '隐私', '条款']
        if any(keyword in page_data.url.lower() for keyword in static_keywords):
            indicators['has_static_content'] = True
        
        # 检查工具内容
        tool_indicators = [
            'form', 'input', 'button[type="submit"]', '.calculator', '.converter',
            'input[type="number"]', 'input[type="text"]'
        ]
        if any(soup.select(indicator) for indicator in tool_indicators):
            indicators['has_tool_content'] = True
        
        return indicators
    
    def _analyze_structure_indicators(self, soup: BeautifulSoup) -> Dict[str, bool]:
        """分析页面结构特征"""
        indicators = {
            'has_article_structure': False,
            'has_form_structure': False,
            'has_simple_structure': False
        }
        
        # 检查文章结构
        if soup.find('article') or soup.find('.post') or soup.find('.entry'):
            indicators['has_article_structure'] = True
        
        # 检查表单结构
        if soup.find('form'):
            indicators['has_form_structure'] = True
        
        # 检查简单结构（只有基本HTML元素）
        complex_elements = soup.find_all(['article', 'section', 'aside', 'nav'])
        if len(complex_elements) < 2:
            indicators['has_simple_structure'] = True
        
        return indicators
    
    def _analyze_functionality_indicators(self, page_data, soup: BeautifulSoup) -> Dict[str, bool]:
        """分析页面功能特征"""
        indicators = {
            'is_interactive': False,
            'is_informational': False,
            'is_navigational': False
        }
        
        # 检查交互性
        interactive_elements = soup.find_all(['form', 'button', 'input', 'select'])
        if len(interactive_elements) > 2:
            indicators['is_interactive'] = True
        
        # 检查信息性内容
        text_content = soup.get_text()
        if len(text_content) > 1000:  # 内容较长
            indicators['is_informational'] = True
        
        # 检查导航性
        nav_elements = soup.find_all('nav') or soup.find_all('.navigation')
        if nav_elements:
            indicators['is_navigational'] = True
        
        return indicators
    
    def _make_date_info_decision(self, content_indicators: Dict, structure_indicators: Dict, functionality_indicators: Dict) -> bool:
        """综合判断是否需要时间信息"""
        
        # 明确需要时间信息的情况
        if (content_indicators['has_news_content'] or 
            content_indicators['has_blog_content'] or 
            content_indicators['has_tutorial_content']):
            return True
        
        # 明确不需要时间信息的情况
        if (content_indicators['has_static_content'] or 
            content_indicators['has_tool_content'] or
            functionality_indicators['is_interactive']):
            return False
        
        # 根据内容长度和结构判断
        if (functionality_indicators['is_informational'] and 
            structure_indicators['has_article_structure']):
            return True
        
        # 默认情况：简单页面不需要时间信息
        if structure_indicators['has_simple_structure']:
            return False
        
        # 其他情况默认需要时间信息
        return True
    
    def _is_single_page_website(self, page_data, total_pages: int = None) -> bool:
        """判断是否为单页网站"""
        
        # 1. 如果明确知道页面总数且为1，则为单页网站
        if total_pages == 1:
            return True
        
        # 2. 如果页面总数很少（≤3），且当前页面是首页，可能是单页网站
        if total_pages and total_pages <= 3:
            # 检查是否是首页
            url = page_data.url
            if (url.endswith('/') or 
                url.count('/') <= 3 or  # URL层级很少
                'index' in url.lower() or
                url == url.split('/')[0] + '//' + url.split('/')[2] + '/'):
                return True
        
        # 3. 检查页面内容特征
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_data.html, 'html.parser')
        
        # 检查是否有单页网站的特征
        single_page_indicators = [
            # 锚点导航
            len(soup.find_all('a', href=lambda x: x and x.startswith('#'))) >= 3,
            # 多个内容章节
            len(soup.find_all(['section', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['section', 'chapter', 'part', 'step']
            ))) >= 3,
            # 长页面内容
            len(soup.get_text()) > 2000,
            # 包含单页网站常见元素
            any(soup.find_all(text=lambda x: x and keyword in x.lower()) for keyword in [
                '一站式', 'all-in-one', 'complete', 'comprehensive', '单页'
            ])
        ]
        
        # 如果满足多个单页网站特征，则认为是单页网站
        if sum(single_page_indicators) >= 2:
            return True
        
        return False
    
    def _should_page_have_credentials(self, page_data, soup: BeautifulSoup) -> bool:
        """智能判断页面是否需要证书/资质信息"""
        
        url = page_data.url.lower()
        title = page_data.title.lower() if page_data.title else ""
        
        # 明确需要证书/资质的页面类型
        professional_keywords = [
            'service', 'services', 'consulting', 'consultation', 'professional',
            'expert', 'specialist', 'advisor', 'therapy', 'treatment',
            'legal', 'medical', 'financial', 'investment', 'insurance',
            '服务', '咨询', '专业', '专家', '顾问', '治疗', '法律', '医疗', '金融'
        ]
        
        # 检查URL和标题是否包含专业服务关键词
        if any(keyword in url or keyword in title for keyword in professional_keywords):
            return True
        
        # 检查页面内容是否涉及专业服务
        content_text = soup.get_text().lower()
        professional_content_keywords = [
            'certified', 'licensed', 'qualified', 'accredited', 'approved',
            '认证', '许可', '资质', '资格', '授权'
        ]
        
        if any(keyword in content_text for keyword in professional_content_keywords):
            return True
        
        # 检查是否是团队/关于我们页面
        about_keywords = ['about', 'team', 'staff', 'about-us', '关于', '团队', '员工']
        if any(keyword in url or keyword in title for keyword in about_keywords):
            return True
        
        # 检查是否是公司介绍页面
        company_keywords = ['company', 'organization', 'business', 'firm', '公司', '企业', '机构']
        if any(keyword in url or keyword in title for keyword in company_keywords):
            return True
        
        # 明确不需要证书/资质的页面类型
        tool_keywords = ['tool', 'calculator', 'converter', 'generator', 'checker', '工具', '计算', '转换', '生成']
        if any(keyword in url or keyword in title for keyword in tool_keywords):
            return False
        
        blog_keywords = ['blog', 'article', 'post', 'news', '博客', '文章', '新闻']
        if any(keyword in url or keyword in title for keyword in blog_keywords):
            return False
        
        # 检查页面内容长度和复杂度
        text_content = soup.get_text()
        if len(text_content) < 500:  # 内容很少的页面
            return False
        
        # 检查是否有表单或交互元素（工具页面特征）
        interactive_elements = soup.find_all(['form', 'input', 'button', 'select'])
        if len(interactive_elements) > 3:  # 交互元素很多，可能是工具页面
            return False
        
        # 默认情况：内容丰富的页面可能需要证书/资质信息
        return len(text_content) > 1000
    
    def _check_back_to_top_button(self, soup: BeautifulSoup) -> bool:
        """全面检查回到顶部按钮"""
        
        # 1. 检查文本内容
        text_keywords = [
            '回到顶部', '返回顶部', 'top', 'back to top', 'scroll to top',
            'go to top', 'scroll up', '回到顶部', '返回顶部'
        ]
        
        # 检查链接和按钮的文本内容
        text_elements = soup.find_all(['a', 'button'], text=lambda x: x and any(
            keyword in x.lower() for keyword in text_keywords
        ))
        if text_elements:
            return True
        
        # 2. 检查图标和符号
        icon_keywords = ['↑', '∧', '▲', '⌃', '^', 'top', 'up']
        icon_elements = soup.find_all(['a', 'button', 'span', 'div'], text=lambda x: x and any(
            keyword in x for keyword in icon_keywords
        ))
        if icon_elements:
            return True
        
        # 3. 检查类名和ID
        class_id_selectors = [
            '.back-to-top', '.back-to-top-btn', '.scroll-to-top', '.go-to-top',
            '#back-to-top', '#scroll-to-top', '#go-to-top',
            '.scroll-top', '.top-button', '.up-button'
        ]
        
        for selector in class_id_selectors:
            if soup.select(selector):
                return True
        
        # 4. 检查href属性指向页面顶部
        top_links = soup.find_all('a', href=lambda x: x and (
            x == '#' or x == '#top' or x == '#header' or x.startswith('#top')
        ))
        if top_links:
            return True
        
        # 5. 检查onclick事件
        onclick_elements = soup.find_all(attrs={'onclick': lambda x: x and any(
            keyword in x.lower() for keyword in [
                'scroll', 'top', 'scrolltop', 'scrollto', 'scrollto(0,0)',
                'window.scroll', 'document.body.scrolltop'
            ]
        )})
        if onclick_elements:
            return True
        
        # 6. 检查data属性
        data_elements = soup.find_all(attrs={'data-action': lambda x: x and any(
            keyword in x.lower() for keyword in ['scroll', 'top', 'back']
        )})
        if data_elements:
            return True
        
        return False

    def get_issue_summary(self, issues: List[SEOIssue]) -> Dict[str, int]:
        """获取问题摘要"""
        summary = {'critical': 0, 'warning': 0, 'info': 0}
        
        for issue in issues:
            summary[issue.severity] += 1
        
        return summary