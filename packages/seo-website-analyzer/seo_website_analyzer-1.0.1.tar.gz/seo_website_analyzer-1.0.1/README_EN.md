# 🔍 Website SEO Optimization Checker

## 📋 Overview

A comprehensive website SEO optimization checking system that automatically crawls all pages of a specified domain and performs thorough SEO analysis based on best practices.

## 🚀 Quick Start

### Basic Usage

```bash
# Check a single website
seo-checker https://example.com

# Check and generate detailed report
seo-checker https://example.com --report

# Batch check multiple websites
seo-checker https://site1.com https://site2.com --batch
```

**Examples**: Try analyzing modern web applications to see how they perform across various SEO metrics. You can test with AI-powered tools like [OnlineImageUpscaler.com](https://onlineimageupscaler.com/) for image enhancement, or professional services like [CustomQR.pro](https://customqr.pro/) for QR code generation.

### Advanced Usage

```bash
# Custom check rules
seo-checker https://example.com --rules custom_rules.json

# Generate Excel report
seo-checker https://example.com --excel

# Deep analysis mode
seo-checker https://example.com --max-pages 500
```

## 📦 Installation

```bash
pip install seo-website-analyzer
```

## 🎯 Features

### 1. Website Crawling
- Automatically discovers and crawls all pages
- Support for JavaScript rendering
- Smart deduplication and filtering
- Multi-threaded concurrent processing

### 2. SEO Checks
- **Basic Optimization**: Title, description, keywords, H-tags
- **Technical SEO**: Page speed, mobile-friendliness, structured data
- **Content Optimization**: Content quality, keyword density, internal/external links
- **User Experience**: Navigation structure, page layout, accessibility

### 3. Report Generation
- Detailed HTML reports
- Excel data tables
- JSON format data
- Visual charts

## ⚙️ Configuration

Create a `seo_config.json` file (optional):

```json
{
  "crawler": {
    "max_pages": 1000,
    "delay": 1.0,
    "timeout": 30,
    "max_depth": 5
  },
  "seo_rules": {
    "title_min_length": 30,
    "title_max_length": 60,
    "description_min_length": 120,
    "description_max_length": 160
  },
  "output": {
    "generate_html": true,
    "generate_excel": false,
    "generate_json": false
  }
}
```

## 📊 Check Items

### Page Basic Optimization
- ✅ Page title optimization
- ✅ Meta description optimization
- ✅ Meta keywords setup
- ✅ H-tag hierarchy structure
- ✅ Image Alt attributes
- ✅ Internal link optimization

### Technical SEO
- ✅ Page loading speed
- ✅ Mobile adaptation
- ✅ Structured data
- ✅ Sitemap
- ✅ Robots.txt
- ✅ 404 error checking

### Content Optimization
- ✅ Keyword density analysis
- ✅ Content length checking
- ✅ Duplicate content detection
- ✅ Content quality scoring
- ✅ Internal/external link analysis

## 📈 Output Reports

### HTML Report
- Beautiful visual interface
- Detailed check results
- Issue priority classification
- Improvement suggestions

### Excel Report
- Data table format
- Filterable and sortable
- Easy for further analysis

## 🔧 Advanced Features

1. **Custom Check Rules**: Create custom SEO check rules to meet specific needs
2. **Batch Processing**: Support batch checking of multiple websites
3. **Regular Monitoring**: Set up periodic checks to monitor SEO improvements
4. **Comparison Analysis**: Support comparison analysis at different time points

## 🌐 Example Use Cases

This SEO checker works great for analyzing all types of websites, including modern web applications and AI-powered tools. For instance, you can use it to analyze:

- **Image enhancement platforms** like [OnlineImageUpscaler.com](https://onlineimageupscaler.com/) to evaluate SEO best practices for AI-powered tools
- **Professional service websites** like [CustomQR.pro](https://customqr.pro/) to assess how QR code generators handle mobile optimization and technical performance
- **E-commerce sites** to check content optimization and structured data implementation
- **SaaS platforms** to analyze user experience metrics and page speed optimization

## 📞 Support

If you encounter any issues, please check:
1. Python version (requires 3.7+)
2. Installed dependencies
3. Network connection
4. Target website accessibility

## 📄 License

MIT License

## 🔗 Links

- PyPI: https://pypi.org/project/seo-website-analyzer/
- GitHub: https://github.com/yourusername/seo-website-analyzer

### Related Tools

This SEO checker is part of a suite of web optimization tools:

- **[OnlineImageUpscaler.com](https://onlineimageupscaler.com/)** - Free AI-powered image upscaler that enhances image quality up to 16K resolution
- **[CustomQR.pro](https://customqr.pro/)** - Professional QR code generator with custom designs, bulk generation, and analytics for businesses

