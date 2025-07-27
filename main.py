import argparse
import json
from scraper import ZhihuScraper
from utils import create_directories, extract_question_answer_ids
from pdf_generator import PDFGenerator

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

def main():
    parser = argparse.ArgumentParser(description='知乎文章爬取PDF生成器')
    parser.add_argument('url', help='知乎文章URL')
    parser.add_argument('--cookies', '-c', help='cookies文件路径')
    parser.add_argument('--output', '-o', help='输出PDF文件路径')
    
    args = parser.parse_args()
    
    # 创建必要目录
    create_directories()
    
    # 验证URL格式
    question_id, answer_id = extract_question_answer_ids(args.url)
    if not question_id or not answer_id:
        print("❌ 无效的知乎文章URL格式")
        return
    
    # 加载cookies
    cookies = {}
    if args.cookies:
        cookies = load_cookies_from_json(args.cookies)
        if not cookies:
            print("⚠️  警告: 未能加载cookies，将以游客身份访问")
    else:
        print("⚠️  警告: 未提供cookies文件，将以游客身份访问")
    
    # 创建爬虫实例
    scraper = ZhihuScraper(cookies)
    
    try:
        print(f"🚀 开始爬取文章: {args.url}")
        print(f" 问题ID: {question_id}, 回答ID: {answer_id}")
        
        # 提取文章内容
        article_data = scraper.extract_article_content(args.url)
        
        if article_data:
            print(f"✅ 文章标题: {article_data['title']}")
            print(f"✅ 作者: {article_data['author']}")
            print(f"✅ 图片数量: {len(article_data['images'])}")
            print(f"✅ 内容长度: {len(article_data['content'])} 字符")
            
            # 保存文章数据
            output_file = f"article_data_{article_data['timestamp']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 文章数据已保存到: {output_file}")
            
            # 生成PDF
            pdf_generator = PDFGenerator()
            pdf_path = pdf_generator.generate_pdf(article_data, args.output)
            
            if pdf_path:
                print(f"✅ PDF生成完成: {pdf_path}")
            else:
                print("❌ PDF生成失败")
            
        else:
            print("❌ 提取文章内容失败")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 