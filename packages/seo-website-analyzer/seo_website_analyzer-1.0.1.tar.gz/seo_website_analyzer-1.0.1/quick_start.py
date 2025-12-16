#!/usr/bin/env python3
"""
快速开始脚本 - 一键运行SEO检查
"""

import sys
import os
import argparse

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SEO优化检查 - 快速开始')
    parser.add_argument('url', help='要检查的网站URL')
    parser.add_argument('--test', action='store_true', help='运行测试模式')
    parser.add_argument('--report', action='store_true', help='生成详细报告')
    parser.add_argument('--excel', action='store_true', help='生成Excel报告')
    parser.add_argument('--max-pages', type=int, default=100, help='最大采集页面数 (默认: 100)')
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试
        print("🧪 运行系统测试...")
        os.system("python test_simple.py")
        return
    
    # 运行SEO检查
    print(f"🔍 开始检查网站: {args.url}")
    
    # 构建命令
    cmd = f"python seo_checker.py {args.url} --max-pages {args.max_pages}"
    
    if args.report:
        cmd += " --report"
    
    if args.excel:
        cmd += " --excel"
    
    print(f"执行命令: {cmd}")
    os.system(cmd)

if __name__ == "__main__":
    main()
