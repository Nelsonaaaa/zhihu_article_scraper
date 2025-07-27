# 知乎文章爬取PDF生成器

一个Python工具，用于爬取知乎文章并生成保持原文图文顺序的PDF文件。

## 功能特点

- ✅ **保持知乎原文图文顺序** - 图片和文字按原文顺序排列
- ✅ **支持复杂排版** - 段落内图片、列表内图片等
- ✅ **Cookie认证** - 支持登录状态，避免反爬限制
- ✅ **图片本地化** - 自动下载并优化图片
- ✅ **中文支持** - 完整的中文字体和排版支持
- ✅ **富文本处理** - 保持原文格式和样式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 准备Cookie文件

从浏览器导出知乎的Cookie，保存为 `cookies.json` 文件。

### 2. 运行爬虫

```bash
python main.py "https://www.zhihu.com/question/123456/answer/789012"
```

### 3. 测试图文顺序

```bash
python test_order.py "https://www.zhihu.com/question/123456/answer/789012"
```

## 项目结构

```
zhihu_scraper/
├── main.py              # 主程序入口
├── scraper.py           # 知乎爬虫模块
├── pdf_generator.py     # PDF生成模块
├── utils.py             # 工具函数
├── test_order.py        # 图文顺序测试脚本
├── config.py            # 配置文件
├── requirements.txt     # 依赖包
├── cookies.json         # Cookie文件
├── downloads/           # 下载目录
│   └── images/          # 图片存储
└── README.md           # 说明文档
```

## 核心改进

### 图文顺序优化

**问题**: 之前的版本中，PDF生成的图文顺序与知乎原文不一致。

**解决方案**:
1. **按节点顺序处理**: 直接遍历知乎原文的HTML节点，保持原有顺序
2. **图片位置保持**: 图片在HTML中保持原有位置，不单独提取
3. **复杂场景支持**: 支持段落内图片、列表内图片等复杂排版

**技术实现**:
- `scraper.py`: 修改 `process_content` 方法，按节点顺序处理
- `pdf_generator.py`: 使用BeautifulSoup解析HTML，递归遍历保持顺序
- `utils.py`: 改进 `flatten_rich_text` 函数，保持HTML结构

## 输出文件

生成的PDF文件命名格式：
```
知乎文章_{标题}_{时间戳}.pdf
```

## 注意事项

1. 需要有效的知乎Cookie才能访问某些内容
2. 图片下载可能需要较长时间
3. 生成的PDF文件较大，包含所有图片

## 开发状态

- ✅ v0.1.0 - MVP基础版本
- ✅ v0.2.0 - 样式优化版本（包含图文顺序优化）
- 🔄 v0.3.0 - 功能完善版本（开发中）

## 许可证

MIT License 