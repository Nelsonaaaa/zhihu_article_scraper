import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import black, gray, HexColor
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PIL import Image as PILImage
import io

class PDFGenerator:
    def __init__(self):
        self.styles = self.create_styles()
    
    def create_styles(self):
        """创建PDF样式，支持中文"""
        styles = getSampleStyleSheet()
        
        # 注册中文字体
        try:
            # 尝试使用系统中文字体
            pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            chinese_font = 'SimSun'
        except:
            # 使用Unicode字体作为备选
            chinese_font = 'STSong-Light'
        
        # 标题样式
        styles.add(ParagraphStyle(
            name='ZhihuTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black,
            fontName=chinese_font,
            leading=22
        ))
        
        # 作者样式
        styles.add(ParagraphStyle(
            name='ZhihuAuthor',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=gray,
            fontName=chinese_font,
            leading=14
        ))
        
        # 正文样式
        styles.add(ParagraphStyle(
            name='ZhihuContent',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            textColor=black,
            fontName=chinese_font,
            leading=16,
            firstLineIndent=22  # 首行缩进
        ))
        
        # 图片说明样式
        styles.add(ParagraphStyle(
            name='ZhihuImageCaption',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=gray,
            fontName=chinese_font,
            leading=12
        ))
        
        return styles
    
    def clean_html_tags(self, text):
        """清理HTML标签，保留基本格式"""
        # 处理特殊HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&ldquo;', '"')
        text = text.replace('&rdquo;', '"')
        text = text.replace('&hellip;', '...')
        
        # 移除HTML标签，但保留换行
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def extract_images_from_content(self, content, images):
        """从内容中提取图片位置信息，保持知乎原文的图文顺序"""
        print(f"🔍 开始处理内容，图片数量: {len(images)}")
        
        # 使用BeautifulSoup解析HTML，保持原有结构
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        content_parts = []
        image_index = 0
        
        # 递归遍历所有节点，保持顺序
        def process_node(node):
            nonlocal image_index
            if node is None:
                return []
            
            if node.name is None:  # 文本节点
                text = str(node).strip()
                if text:
                    return [('text', text)]
                return []
            elif node.name == 'img':
                # 处理图片节点 - 直接按顺序分配图片
                if image_index < len(images):
                    img_data = images[image_index]
                    image_index += 1
                    print(f"✅ 分配图片 {image_index}: {img_data['filename']}")
                    return [('image', img_data)]
                else:
                    print(f"⚠️ 图片数量不足，跳过图片节点")
                    return []
            elif node.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']:
                # 处理块级元素
                parts = []
                for child in node.children:
                    child_parts = process_node(child)
                    if child_parts:
                        parts.extend(child_parts)
                if parts:
                    # 将内容包装在对应标签中
                    content_text = '\n'.join([part[1] for part in parts if part[0] == 'text'])
                    if content_text.strip():
                        return [('text', f"<{node.name}>{content_text.strip()}</{node.name}>")]
                return []
            elif node.name in ['ul', 'ol']:
                # 处理列表
                list_items = []
                for li in node.find_all('li', recursive=False):
                    li_parts = []
                    for child in li.children:
                        child_parts = process_node(child)
                        if child_parts:
                            li_parts.extend(child_parts)
                    li_text = '\n'.join([part[1] for part in li_parts if part[0] == 'text'])
                    if li_text.strip():
                        list_items.append(f"<li>{li_text.strip()}</li>")
                if list_items:
                    return [('text', f"<{node.name}>{''.join(list_items)}</{node.name}>")]
                return []
            elif node.name == 'br':
                return [('text', '\n')]
            else:
                # 处理其他元素
                parts = []
                for child in node.children:
                    child_parts = process_node(child)
                    if child_parts:
                        parts.extend(child_parts)
                return parts
        
        # 处理根节点
        for child in soup.children:
            try:
                child_parts = process_node(child)
                if child_parts is not None:
                    content_parts.extend(child_parts)
                else:
                    print(f"⚠️ process_node返回None: {child}")
            except Exception as e:
                print(f"❌ 处理节点失败: {e}, 节点: {child}")
                continue
        
        # 合并连续的文本部分
        merged_parts = []
        current_text = ""
        
        for part_type, part_content in content_parts:
            if part_type == 'text':
                current_text += part_content + "\n"
            else:  # image
                # 先添加累积的文本
                if current_text.strip():
                    merged_parts.append(('text', current_text.strip()))
                    current_text = ""
                # 再添加图片
                merged_parts.append((part_type, part_content))
        
        # 添加最后的文本
        if current_text.strip():
            merged_parts.append(('text', current_text.strip()))
        
        print(f"🔍 内容部分: {len(merged_parts)} 个")
        for i, (part_type, part_content) in enumerate(merged_parts):
            if part_type == 'image':
                print(f"  图片{i+1}: {part_content['filename']}")
            else:
                print(f"  文本{i+1}: {len(part_content)} 字符")
        
        return merged_parts
    
    def extract_image_id(self, url):
        """从图片URL中提取唯一标识"""
        pattern = r'v2-([a-f0-9]+)_'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    
    def convert_image_format(self, image_path):
        """转换图片格式为PDF支持的格式"""
        try:
            # 打开图片
            with PILImage.open(image_path) as img:
                # 转换为RGB模式（如果是RGBA或其他模式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 生成新的文件名
                base_name = os.path.splitext(image_path)[0]
                new_path = f"{base_name}_converted.jpg"
                
                # 保存为JPEG格式
                img.save(new_path, 'JPEG', quality=85, optimize=True)
                
                print(f"✅ 图片格式转换成功: {new_path}")
                return new_path
                
        except Exception as e:
            print(f"❌ 图片格式转换失败: {e}")
            return None
    
    def process_image_for_pdf(self, img_data):
        """处理图片，确保格式兼容PDF"""
        try:
            # 处理base64图片数据
            if 'base64_data' in img_data:
                import base64
                import io
                from PIL import Image
                
                # 解码base64数据
                image_bytes = base64.b64decode(img_data['base64_data'])
                
                # 使用PIL打开图片
                with Image.open(io.BytesIO(image_bytes)) as img:
                    # 转换为RGB模式（如果是RGBA或其他模式）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # 创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 保存为临时JPEG文件
                    temp_path = f"temp_{img_data['filename']}.jpg"
                    img.save(temp_path, 'JPEG', quality=85, optimize=True)
                    
                    print(f"✅ 图片格式转换成功: {temp_path}")
                    return temp_path
            
            # 兼容旧版本（本地文件）
            original_path = img_data.get('local_path')
            if original_path and os.path.exists(original_path):
                # 检查文件大小
                file_size = os.path.getsize(original_path)
                if file_size == 0:
                    print(f"❌ 图片文件为空: {original_path}")
                    return None
                
                # 获取文件扩展名
                file_ext = os.path.splitext(original_path)[1].lower()
                
                # 如果是WebP格式，需要转换
                if file_ext in ['.webp', '.avif']:
                    print(f"🔄 转换WebP图片: {original_path}")
                    converted_path = self.convert_image_format(original_path)
                    if converted_path:
                        return converted_path
                    else:
                        return None
                
                # 其他格式直接使用
                return original_path
            
            return None
            
        except Exception as e:
            print(f"❌ 处理图片失败: {e}")
            return None

    def generate_pdf(self, article_data, output_path=None):
        """生成PDF文件"""
        try:
            print("🔄 开始生成PDF...")
            
            # 设置输出路径
            if not output_path:
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_data['title'])[:50]
                output_path = f"知乎文章_{safe_title}_{article_data['timestamp']}.pdf"
            
            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # 构建PDF内容
            story = []
            
            # 添加标题
            title_text = article_data['title']
            title = Paragraph(title_text, self.styles['ZhihuTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 添加作者信息
            if article_data['author']:
                author_text = f"作者：{article_data['author']}"
                author = Paragraph(author_text, self.styles['ZhihuAuthor'])
                story.append(author)
                story.append(Spacer(1, 10))
            
            # 添加元信息
            meta_text = f"来源：知乎 | 时间：{article_data['timestamp']}"
            meta = Paragraph(meta_text, self.styles['ZhihuAuthor'])
            story.append(meta)
            story.append(Spacer(1, 30))
            
            # 处理内容
            content_parts = self.extract_images_from_content(article_data['content'], article_data['images'])
            
            for i, (part_type, part_content) in enumerate(content_parts):
                print(f"🔍 处理第{i+1}部分: {part_type}")
                
                if part_type == 'text':
                    # 处理文本内容
                    if part_content.strip():
                        # 分段处理
                        paragraphs = part_content.split('\n')
                        for para in paragraphs:
                            if para.strip():
                                try:
                                    p = Paragraph(para.strip(), self.styles['ZhihuContent'])
                                    story.append(p)
                                    story.append(Spacer(1, 6))
                                except Exception as e:
                                    print(f"❌ 处理段落失败: {e}")
                                    p = Paragraph(para.strip(), self.styles['Normal'])
                                    story.append(p)
                                    story.append(Spacer(1, 6))
                elif part_type == 'image':
                    # 处理图片
                    try:
                        # 处理图片格式
                        processed_path = self.process_image_for_pdf(part_content)
                        
                        if processed_path and os.path.exists(processed_path):
                            # 检查文件大小
                            file_size = os.path.getsize(processed_path)
                            print(f"🔍 处理后的图片文件大小: {file_size} bytes")
                            
                            if file_size > 0:
                                # 使用PIL获取图片尺寸
                                with PILImage.open(processed_path) as pil_img:
                                    img_width, img_height = pil_img.size
                                
                                # 计算合适的显示尺寸
                                max_width = 4 * inch
                                max_height = 3 * inch
                                
                                # 保持宽高比
                                ratio = min(max_width / img_width, max_height / img_height)
                                display_width = img_width * ratio
                                display_height = img_height * ratio
                                
                                # 添加图片
                                img = Image(processed_path, width=display_width, height=display_height)
                                story.append(img)
                                story.append(Spacer(1, 10))
                                
                                # 添加图片说明（如果有）
                                if part_content.get('alt'):
                                    caption = Paragraph(part_content['alt'], self.styles['ZhihuImageCaption'])
                                    story.append(caption)
                                    story.append(Spacer(1, 10))
                                
                                print(f"✅ 成功添加图片: {part_content['filename']} ({display_width:.1f}x{display_height:.1f})")
                            else:
                                print(f"⚠️ 处理后的图片文件为空: {processed_path}")
                        else:
                            print(f"❌ 图片处理失败: {part_content['filename']}")
                    except Exception as e:
                        print(f"❌ 处理图片失败: {e}")
                        import traceback
                        traceback.print_exc()
            
            # 生成PDF
            doc.build(story)
            
            print(f"✅ PDF生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None 