import sys
import os
import shutil
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from scraper import ZhihuScraper
from pdf_generator import PDFGenerator
from utils import load_cookies_from_json, create_directories

CONFIG_FILE = 'gui_config.json'
RECENT_FILE = 'recent.json'
MAX_RECENT = 10

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_recent():
    if os.path.exists(RECENT_FILE):
        try:
            with open(RECENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_recent(recent):
    try:
        with open(RECENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(recent, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_recent_record(title, pdf_path, timestamp):
    recent = load_recent()
    # 去重（同路径只保留最新）
    recent = [r for r in recent if r['pdf_path'] != pdf_path]
    recent.insert(0, {'title': title, 'pdf_path': pdf_path, 'timestamp': timestamp})
    if len(recent) > MAX_RECENT:
        recent = recent[:MAX_RECENT]
    save_recent(recent)

class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str, str, str)  # pdf_path, title, timestamp
    error = pyqtSignal(str)

    def __init__(self, url, cookie_path, save_dir, parent=None):
        super().__init__(parent)
        self.url = url
        self.cookie_path = cookie_path
        self.save_dir = save_dir

    def run(self):
        try:
            self.progress.emit("正在初始化...")
            create_directories()
            cookies = load_cookies_from_json(self.cookie_path)
            self.progress.emit("正在登录知乎...")
            scraper = ZhihuScraper(cookies)
            self.progress.emit("正在爬取文章...")
            article_data = scraper.extract_article_content(self.url)
            if not article_data:
                self.error.emit("文章内容提取失败！")
                return
            self.progress.emit("正在生成PDF...")
            pdf_gen = PDFGenerator()
            safe_title = article_data['title'][:30] if article_data['title'] else 'zhihu_article'
            output_name = f"知乎文章_{safe_title}_{article_data['timestamp']}.pdf"
            output_path = os.path.join(self.save_dir, output_name)
            pdf_path = pdf_gen.generate_pdf(article_data, output_path)
            scraper.close()
            # 清理临时文件
            self.progress.emit("正在清理临时文件...")
            self.cleanup_temp()
            if pdf_path:
                self.finished.emit(pdf_path, article_data['title'], article_data['timestamp'])
            else:
                self.error.emit("PDF生成失败！")
        except Exception as e:
            self.error.emit(f"发生错误: {e}")

    def cleanup_temp(self):
        # 删除临时图片文件
        for f in os.listdir('.'):
            if f.startswith('temp_') and f.endswith('.jpg'):
                try:
                    os.remove(f)
                except Exception:
                    pass
        # 删除所有article_data_*.json
        for f in os.listdir('.'):
            if f.startswith('article_data_') and f.endswith('.json'):
                try:
                    os.remove(f)
                except Exception:
                    pass
        # 删除temp/等其他临时目录
        if os.path.exists('temp'):
            shutil.rmtree('temp', ignore_errors=True)

class ZhihuPDFGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('知乎文章PDF下载器')
        self.resize(600, 500)  # 增大默认尺寸
        self.config = load_config()
        self.init_ui()
        self.download_thread = None
        self.load_recent_list()

    def init_ui(self):
        layout = QVBoxLayout()
        # 链接输入
        url_layout = QHBoxLayout()
        url_label = QLabel('知乎文章链接:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://www.zhihu.com/question/...')
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        # cookie选择
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel('Cookie文件:')
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText('请选择cookies.json')
        self.cookie_btn = QPushButton('选择')
        self.cookie_btn.clicked.connect(self.choose_cookie)
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_input)
        cookie_layout.addWidget(self.cookie_btn)
        # 恢复上次选择的cookie文件
        last_cookie = self.config.get('cookie_file', '')
        if last_cookie and os.path.exists(last_cookie):
            self.cookie_input.setText(last_cookie)
        # 保存目录选择
        save_layout = QHBoxLayout()
        save_label = QLabel('保存目录:')
        self.save_input = QLineEdit()
        self.save_input.setPlaceholderText('请选择PDF保存目录')
        self.save_btn = QPushButton('选择')
        self.save_btn.clicked.connect(self.choose_save_dir)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_input)
        save_layout.addWidget(self.save_btn)
        # 恢复上次保存目录
        last_dir = self.config.get('save_dir', '')
        if last_dir:
            self.save_input.setText(last_dir)
        # 下载按钮
        self.download_btn = QPushButton('下载PDF')
        self.download_btn.clicked.connect(self.start_download)
        # 进度条/状态
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        # 最近记录栏
        recent_label = QLabel('最近解析记录:')
        self.recent_list = QListWidget()
        self.recent_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.recent_list.itemDoubleClicked.connect(self.open_pdf)
        self.recent_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recent_list.customContextMenuRequested.connect(self.show_recent_menu)
        # 布局
        layout.addLayout(url_layout)
        layout.addLayout(cookie_layout)
        layout.addLayout(save_layout)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(recent_label)
        layout.addWidget(self.recent_list)
        self.setLayout(layout)

    def choose_cookie(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择Cookie文件', '.', 'JSON Files (*.json)')
        if file_path:
            self.cookie_input.setText(file_path)
            # 保存选择
            self.config['cookie_file'] = file_path
            save_config(self.config)

    def choose_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择PDF保存目录', '.')
        if dir_path:
            self.save_input.setText(dir_path)
            self.config['save_dir'] = dir_path
            save_config(self.config)

    def start_download(self):
        url = self.url_input.text().strip()
        cookie_path = self.cookie_input.text().strip()
        save_dir = self.save_input.text().strip()
        if not url or not url.startswith('http'):
            QMessageBox.warning(self, '输入错误', '请输入有效的知乎文章链接！')
            return
        if not cookie_path or not os.path.exists(cookie_path):
            QMessageBox.warning(self, '输入错误', '请选择有效的Cookie文件！')
            return
        if not save_dir or not os.path.isdir(save_dir):
            QMessageBox.warning(self, '输入错误', '请选择有效的PDF保存目录！')
            return
        self.download_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText('开始下载...')
        self.download_thread = DownloadThread(url, cookie_path, save_dir)
        self.download_thread.progress.connect(self.on_progress)
        self.download_thread.finished.connect(self.on_finished)
        self.download_thread.error.connect(self.on_error)
        self.download_thread.start()

    def on_progress(self, msg):
        self.status_label.setText(msg)

    def on_finished(self, pdf_path, title, timestamp):
        self.progress_bar.hide()
        self.download_btn.setEnabled(True)
        self.status_label.setText(f'下载完成！PDF已保存: {pdf_path}')
        add_recent_record(title, pdf_path, timestamp)
        self.load_recent_list()
        QMessageBox.information(self, '下载完成', f'PDF已保存到：\n{pdf_path}')

    def on_error(self, msg):
        self.progress_bar.hide()
        self.download_btn.setEnabled(True)
        self.status_label.setText(msg)
        QMessageBox.critical(self, '出错了', msg)

    def load_recent_list(self):
        self.recent_list.clear()
        recent = load_recent()
        for rec in recent:
            # 只显示文件名
            filename = os.path.basename(rec['pdf_path'])
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, rec['pdf_path'])
            item.setToolTip(rec['pdf_path'])  # 完整路径作为提示
            item.setTextAlignment(Qt.AlignLeft)
            self.recent_list.addItem(item)

    def open_pdf(self, item):
        pdf_path = item.data(Qt.UserRole)
        if os.path.exists(pdf_path):
            try:
                if sys.platform.startswith('win'):
                    os.startfile(pdf_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', pdf_path])
                else:
                    subprocess.call(['xdg-open', pdf_path])
            except Exception as e:
                QMessageBox.warning(self, '无法打开', f'无法打开PDF文件：{e}')
        else:
            QMessageBox.warning(self, '文件不存在', 'PDF文件已被删除或移动！')

    def show_recent_menu(self, pos):
        item = self.recent_list.itemAt(pos)
        if item:
            from PyQt5.QtWidgets import QMenu
            menu = QMenu()
            open_action = menu.addAction('打开PDF')
            show_in_folder_action = menu.addAction('在文件夹中显示')
            menu.addSeparator()
            del_action = menu.addAction('删除该记录')
            action = menu.exec_(self.recent_list.mapToGlobal(pos))
            if action == open_action:
                self.open_pdf(item)
            elif action == show_in_folder_action:
                self.show_in_folder(item)
            elif action == del_action:
                self.delete_recent(item)

    def show_in_folder(self, item):
        pdf_path = item.data(Qt.UserRole)
        if os.path.exists(pdf_path):
            try:
                if sys.platform.startswith('win'):
                    subprocess.run(['explorer', '/select,', pdf_path])
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', '-R', pdf_path])
                else:
                    subprocess.run(['xdg-open', os.path.dirname(pdf_path)])
            except Exception as e:
                QMessageBox.warning(self, '无法显示', f'无法在文件夹中显示：{e}')
        else:
            QMessageBox.warning(self, '文件不存在', 'PDF文件已被删除或移动！')

    def delete_recent(self, item):
        pdf_path = item.data(Qt.UserRole)
        recent = load_recent()
        recent = [r for r in recent if r['pdf_path'] != pdf_path]
        save_recent(recent)
        self.load_recent_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ZhihuPDFGUI()
    gui.show()
    sys.exit(app.exec_()) 