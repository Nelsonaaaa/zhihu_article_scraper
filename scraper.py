import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
from utils import *
from bs4 import NavigableString

# 添加USER_AGENT常量
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class ZhihuScraper:
    def __init__(self, cookies=None):
        self.cookies = cookies or {}
        self.session = requests.Session()
        self.driver = None
        self.setup_session()
    
    def setup_session(self):
        """设置会话和请求头"""
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        
        # 添加cookies
        for name, value in self.cookies.items():
            self.session.cookies.set(name, value)
    
    def init_driver(self):
        """初始化Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--log-level=3')  # 只显示致命错误
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'--user-agent={USER_AGENT}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 添加cookies到driver
        self.driver.get("https://www.zhihu.com")
        for name, value in self.cookies.items():
            # 设置cookie时指定domain和path，确保cookie正确设置
            cookie_dict = {
                'name': name, 
                'value': value,
                'domain': '.zhihu.com',  # 知乎的cookie domain
                'path': '/'
            }
            try:
                self.driver.add_cookie(cookie_dict)
                print(f"✅ Cookie设置成功: {name}")
            except Exception as e:
                print(f"⚠️ Cookie设置失败 {name}: {e}")
    
    def extract_article_content(self, url):
        """提取知乎文章内容"""
        try:
            # 使用Selenium获取动态内容
            if not self.driver:
                self.init_driver()
            
            self.driver.get(url)
            time.sleep(3)  # 等待页面加载
            
            # 等待内容加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "RichText"))
            )
            
            # 滚动页面以加载懒加载的图片
            self.scroll_page()
            
            # 等待图片加载
            time.sleep(2)
            
            # 获取页面源码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 调试：检查页面中的图片
            all_images = soup.find_all('img')
            print(f"🔍 页面中共找到 {len(all_images)} 个图片元素")
            for i, img in enumerate(all_images[:10]):  # 显示前10个
                src = img.get('src', 'No src')
                data_src = img.get('data-src', 'No data-src')
                print(f"  图片{i+1}: src={src} | data-src={data_src}")
            
            # 提取文章信息
            article_data = self.parse_article(soup, url)
            
            return article_data
            
        except Exception as e:
            print(f"提取文章内容失败: {e}")
            return None
    
    def scroll_page(self):
        """滚动页面以加载懒加载内容"""
        try:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 滚动到页面顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except Exception as e:
            print(f"滚动页面失败: {e}")
    
    def parse_article(self, soup, url):
        """解析文章内容"""
        article_data = {
            'url': url,
            'title': '',
            'author': '',
            'content': '',
            'images': [],
            'timestamp': get_timestamp()
        }
        
        try:
            print("🔍 开始解析文章内容...")
            
            # 提取标题 - 尝试多种选择器
            title_selectors = [
                'h1.QuestionHeader-title',
                '.QuestionHeader h1',
                '.QuestionHeader-title',
                'h1[data-zop-itemid]',
                '.ContentItem-title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    article_data['title'] = title_elem.get_text(strip=True)
                    print(f"✅ 找到标题: {article_data['title']}")
                    break
            
            # 提取作者信息 - 尝试多种选择器
            author_selectors = [
                '.UserLink',
                '.AnswerItem-authorInfo .UserLink',
                '.ContentItem-meta .UserLink',
                '.AuthorInfo-name',
                '.AnswerItem-authorInfo .AuthorInfo-name'
            ]
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    article_data['author'] = author_elem.get_text(strip=True)
                    print(f"✅ 找到作者: {article_data['author']}")
                    break
            
            # 提取文章内容 - 尝试多种选择器
            content_selectors = [
                '.RichText',
                '.AnswerItem-content .RichText',
                '.ContentItem-content .RichText',
                '.AnswerItem-content',
                '.ContentItem-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    print(f"✅ 找到内容区域: {selector}")
                    article_data['content'], article_data['images'] = self.process_content(content_elem)
                    break
            
            # 如果没有找到内容，尝试更宽泛的选择器
            if not article_data['content']:
                print("⚠️ 未找到内容，尝试备用方法...")
                # 查找所有包含文本的div
                content_divs = soup.find_all('div', class_=lambda x: x and 'RichText' in x)
                if content_divs:
                    content_elem = content_divs[0]
                    article_data['content'], article_data['images'] = self.process_content(content_elem)
            
            print(f"📊 解析结果: 标题={len(article_data['title'])}字符, 作者={len(article_data['author'])}字符, 内容={len(article_data['content'])}字符")
            
        except Exception as e:
            print(f"❌ 解析文章失败: {e}")
        
        return article_data
    
    def clean_rich_text(self, element):
        """递归清理知乎富文本，合并span/a/svg等为纯文本"""
        result = ""
        for child in element.children:
            if isinstance(child, NavigableString):
                result += str(child)
            elif child.name in ['span', 'a', 'b', 'strong', 'em']:
                # 递归处理，保留文本
                result += self.clean_rich_text(child)
            elif child.name == 'svg':
                # svg一般是icon，直接用空格或特殊符号代替
                result += " "
            else:
                # 其他标签递归处理
                result += self.clean_rich_text(child)
        return result

    def process_content(self, content_elem):
        """递归处理知乎内容，保持图文顺序，收集所有有效图片"""
        content_html = ""
        images = []
        
        def walk(node):
            nonlocal images
            if getattr(node, 'name', None) == 'img':
                src = node.get('src', '')
                # 只处理有效图片
                if src and src.startswith('http'):
                    img_data = self.process_image(node)
                    if img_data:
                        images.append(img_data)
                        # 在HTML中插入base64图片
                        content_type = img_data['content_type']
                        base64_data = img_data['base64_data']
                        return f'<img src="data:{content_type};base64,{base64_data}" alt="{img_data["alt"]}" class="zhihu-image" />'
                return ''  # 忽略无效图片
            elif getattr(node, 'name', None) is not None:
                # 递归处理子节点
                inner = ''.join([walk(child) for child in node.children])
                if node.name in ['p', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    return f'<{node.name}>{inner}</{node.name}>'
                elif node.name in ['ul', 'ol']:
                    return f'<{node.name}>{inner}</{node.name}>'
                elif node.name == 'br':
                    return '<br>'
                else:
                    return inner
            else:
                # 文本节点
                return str(node)

        content_html = walk(content_elem)
        print(f"✅ 内容处理完成: {len(content_html)}字符, {len(images)}张图片")
        print(f"🔍 图片顺序: {[img['filename'] for img in images]}")
        return content_html, images
    
    def process_paragraph_content(self, p_elem):
        """处理段落内容，保持其中的图片顺序"""
        content = ""
        for child in p_elem.children:
            if child.name is None:  # 文本节点
                content += str(child)
            elif child.name == 'img':
                # 处理段落中的图片
                img_data = self.process_image(child)
                if img_data:
                    # 在段落中插入base64图片
                    content_type = img_data['content_type']
                    base64_data = img_data['base64_data']
                    content += f'<img src="data:{content_type};base64,{base64_data}" alt="{img_data["alt"]}" class="zhihu-image" />'
            else:
                # 其他元素递归处理
                content += self.clean_rich_text(child)
        return content
    
    def process_list_content(self, list_elem):
        """处理列表内容，保持其中的图片顺序"""
        content = ""
        for li in list_elem.find_all('li', recursive=False):
            li_content = ""
            for child in li.children:
                if child.name is None:  # 文本节点
                    li_content += str(child)
                elif child.name == 'img':
                    # 处理列表项中的图片
                    img_data = self.process_image(child)
                    if img_data:
                        content_type = img_data['content_type']
                        base64_data = img_data['base64_data']
                        li_content += f'<img src="data:{content_type};base64,{base64_data}" alt="{img_data["alt"]}" class="zhihu-image" />'
                else:
                    # 其他元素递归处理
                    li_content += self.clean_rich_text(child)
            if li_content.strip():
                content += f"<li>{li_content.strip()}</li>"
        return content
    
    def process_image(self, img_elem):
        """处理图片元素，直接获取base64数据"""
        try:
            # 尝试多种图片属性
            src = None
            for attr in ['src', 'data-src', 'data-original', 'data-actualsrc']:
                src = img_elem.get(attr)
                if src:
                    print(f"🔍 找到图片源: {attr} = {src}")
                    break
            
            if not src:
                print("⚠️ 未找到图片源")
                return None
            
            # 处理相对URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://www.zhihu.com' + src
            elif not src.startswith('http'):
                src = 'https://www.zhihu.com' + src
            
            print(f"🔍 处理后的图片URL: {src}")
            
            # 直接下载图片到内存
            img_data = self.download_image_to_memory(src)
            if img_data:
                return {
                    'original_url': src,
                    'base64_data': img_data['base64'],
                    'content_type': img_data['content_type'],
                    'filename': img_data['filename'],
                    'alt': img_elem.get('alt', '')
                }
            
        except Exception as e:
            print(f"❌ 处理图片失败: {e}")
        
        return None
    
    def download_image_to_memory(self, url):
        """下载图片到内存，返回base64数据"""
        try:
            print(f"📥 开始下载图片到内存: {url}")
            
            # 添加图片请求头
            headers = {
                'User-Agent': USER_AGENT,
                'Referer': 'https://www.zhihu.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', 'image/jpeg')
            if not content_type.startswith('image/'):
                print(f"⚠️ 非图片内容: {content_type}")
                return None
            
            # 获取图片数据
            image_data = response.content
            
            # 转换为base64
            import base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # 生成文件名（用于调试）
            filename = generate_filename_from_url(url)
            
            print(f"✅ 图片下载到内存成功: {filename} ({len(image_data)} bytes)")
            
            return {
                'base64': base64_data,
                'content_type': content_type,
                'filename': filename
            }
            
        except Exception as e:
            print(f"❌ 下载图片到内存失败 {url}: {e}")
            return None 
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit() 