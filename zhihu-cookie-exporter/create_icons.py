#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎Cookie导出器 - 图标生成脚本
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """创建指定尺寸的图标"""
    # 创建透明背景
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 计算边距和字体大小
    margin = size // 8
    font_size = size // 3
    
    # 绘制圆形背景（知乎蓝色）
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill=(0, 132, 255, 255))
    
    # 绘制Cookie图标（白色）
    cookie_color = (255, 255, 255, 255)
    
    # 绘制Cookie主体（圆形）
    cookie_margin = size // 4
    cookie_bbox = [cookie_margin, cookie_margin, size - cookie_margin, size - cookie_margin]
    draw.ellipse(cookie_bbox, fill=cookie_color)
    
    # 绘制Cookie上的巧克力豆
    dot_size = size // 12
    dot_positions = [
        (size // 3, size // 3),
        (2 * size // 3, size // 3),
        (size // 2, size // 2),
        (size // 3, 2 * size // 3),
        (2 * size // 3, 2 * size // 3)
    ]
    
    for pos in dot_positions:
        dot_bbox = [pos[0] - dot_size//2, pos[1] - dot_size//2, 
                   pos[0] + dot_size//2, pos[1] + dot_size//2]
        draw.ellipse(dot_bbox, fill=(139, 69, 19, 255))  # 棕色巧克力豆
    
    # 保存图标
    img.save(output_path, 'PNG')
    print(f"✅ 创建图标: {output_path}")

def main():
    """主函数"""
    # 确保icons目录存在
    icons_dir = "icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # 创建不同尺寸的图标
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f"icon{size}.png")
        create_icon(size, output_path)
    
    print("🎉 所有图标创建完成！")

if __name__ == "__main__":
    main() 