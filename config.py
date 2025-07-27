# 配置文件
import os

# 知乎配置
ZHIHU_BASE_URL = "https://www.zhihu.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 文件路径配置
DOWNLOAD_DIR = "downloads"
IMAGES_DIR = os.path.join(DOWNLOAD_DIR, "images")
TEMP_DIR = "temp"

# 请求配置
REQUEST_TIMEOUT = 30
RETRY_TIMES = 3
DELAY_BETWEEN_REQUESTS = 2

# 图片配置
MAX_IMAGE_SIZE = 2048  # 最大图片尺寸
IMAGE_QUALITY = 85     # 图片质量 