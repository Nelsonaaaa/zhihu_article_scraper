import os
import re
import time
import hashlib
from urllib.parse import urlparse, urljoin
import requests
from PIL import Image
import io
import json
from bs4 import NavigableString, Tag

def create_directories():
    """创建必要的目录"""
    directories = ['downloads', 'downloads/images', 'temp', 'templates', 'styles']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clean_filename(filename):
    """清理文件名，移除非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def generate_filename_from_url(url, extension='.jpg'):
    """从URL生成文件名"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or '.' not in filename:
        filename = hashlib.md5(url.encode()).hexdigest()[:8] + extension
    return clean_filename(filename)

def download_image(url, save_path, headers=None):
    """下载图片"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 保存图片
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        # 优化图片大小
        optimize_image(save_path)
        
        return True
    except Exception as e:
        print(f"下载图片失败 {url}: {e}")
        return False

def optimize_image(image_path):
    """优化图片大小和质量"""
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整图片大小
            if max(img.size) > 2048:
                img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            
            # 保存优化后的图片
            img.save(image_path, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        print(f"优化图片失败 {image_path}: {e}")

def extract_question_answer_ids(url):
    """从知乎URL中提取问题ID和回答ID"""
    pattern = r'/question/(\d+)/answer/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def get_timestamp():
    """获取当前时间戳，格式：2025-07-26（只保留日期）"""
    return time.strftime("%Y-%m-%d")

def load_cookies_from_json(cookie_file):
    """从JSON文件加载cookies"""
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        if isinstance(cookies, dict):
            print(f"✅ 成功加载 {len(cookies)} 个cookies")
            return cookies
        else:
            print("❌ cookies文件格式错误，应该是JSON对象格式")
            return {}
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return {}
    except Exception as e:
        print(f"❌ 加载cookies失败: {e}")
        return {} 

def flatten_rich_text(element):
    """
    递归处理知乎富文本，保持图文顺序和段落结构。
    保留图片标签和基本HTML结构，清理不必要的嵌套标签。
    """
    if isinstance(element, NavigableString):
        return str(element)
    elif isinstance(element, Tag):
        if element.name == 'img':
            # 保留图片标签，保持原有属性
            attrs = []
            for attr in ['src', 'data-src', 'data-original', 'data-actualsrc', 'alt', 'class']:
                if element.has_attr(attr):
                    attrs.append(f'{attr}="{element[attr]}"')
            return f'<img {" ".join(attrs)} />'
        elif element.name in ['br']:
            return '<br>'
        elif element.name in ['p', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # 段落/列表/引用/标题，递归处理内容并保持标签结构
            inner_content = ''.join([flatten_rich_text(child) for child in element.children])
            if inner_content.strip():
                return f'<{element.name}>{inner_content.strip()}</{element.name}>'
            return ''
        elif element.name in ['ul', 'ol']:
            # 列表，保持结构
            list_items = []
            for li in element.find_all('li', recursive=False):
                li_content = ''.join([flatten_rich_text(child) for child in li.children])
                if li_content.strip():
                    list_items.append(f'<li>{li_content.strip()}</li>')
            if list_items:
                return f'<{element.name}>{"".join(list_items)}</{element.name}>'
            return ''
        elif element.name in ['span', 'a', 'b', 'strong', 'em', 'u', 'sup', 'sub']:
            # 内联标签，递归处理内容，保持标签结构
            inner_content = ''.join([flatten_rich_text(child) for child in element.children])
            if inner_content.strip():
                return f'<{element.name}>{inner_content.strip()}</{element.name}>'
            return inner_content
        elif element.name == 'svg':
            # svg一般是icon，用空格代替
            return " "
        elif element.name == 'div':
            # div标签，只处理内容，不保留div标签
            return ''.join([flatten_rich_text(child) for child in element.children])
        else:
            # 其他标签递归处理
            return ''.join([flatten_rich_text(child) for child in element.children])
    return str(element)

def process_content(self, content_elem):
    """
    处理知乎内容，保留图片和段落结构，热门词不换行
    """
    content_html = ""
    images = []
    try:
        print("🔍 开始处理内容...")
        # 递归处理整个内容区域
        content_html = flatten_rich_text(content_elem)
        # 提取图片
        for img in content_elem.find_all('img'):
            img_data = self.process_image(img)
            if img_data:
                images.append(img_data)
        print(f"✅ 内容处理完成: {len(content_html)}字符, {len(images)}张图片")
    except Exception as e:
        print(f"❌ 处理内容失败: {e}")
    return content_html, images 