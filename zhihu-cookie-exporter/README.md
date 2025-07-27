# 知乎Cookie导出器 - 浏览器扩展

一个简单易用的Chrome扩展，用于一键导出知乎Cookie，配合知乎PDF下载器使用。

## 功能特点

- 🍪 **一键导出**: 点击扩展图标即可导出知乎Cookie
- 📁 **自动下载**: 自动生成`cookies.json`文件并下载到本地
- 🔍 **智能检测**: 自动检测登录状态和Cookie有效性
- 🎨 **美观界面**: 现代化的UI设计，用户体验友好
- 🔒 **安全可靠**: 只获取必要的Cookie，不上传任何数据

## 安装方法

### 方法一：开发者模式安装（推荐）

1. **下载扩展文件**
   - 下载整个`zhihu-cookie-exporter`文件夹
   - 确保包含所有文件：`manifest.json`、`popup.html`、`popup.js`等

2. **打开Chrome扩展管理页面**
   - 在Chrome地址栏输入：`chrome://extensions/`
   - 或者点击菜单 → 更多工具 → 扩展程序

3. **启用开发者模式**
   - 在页面右上角打开"开发者模式"开关

4. **加载扩展**
   - 点击"加载已解压的扩展程序"
   - 选择`zhihu-cookie-exporter`文件夹
   - 扩展安装成功！

### 方法二：打包安装

1. **打包扩展**
   ```bash
   # 在扩展目录中运行
   zip -r zhihu-cookie-exporter.zip . -x "*.git*" "*.DS_Store*"
   ```

2. **安装打包文件**
   - 将`.zip`文件拖拽到`chrome://extensions/`页面
   - 或者双击`.zip`文件安装

## 使用方法

### 基本使用

1. **登录知乎**
   - 打开知乎网站并登录你的账号
   - 确保登录状态正常

2. **导出Cookie**
   - 点击浏览器工具栏中的扩展图标
   - 在弹出的界面中点击"导出Cookie"
   - 文件会自动下载到默认下载目录

3. **使用Cookie**
   - 将下载的`cookies.json`文件放到知乎PDF下载器目录
   - 重新运行PDF下载器即可

### 高级功能

- **检查Cookie状态**: 点击"检查Cookie状态"可以查看当前Cookie情况
- **自动检测**: 扩展会自动检测登录状态变化
- **页面提示**: 在知乎页面会显示操作提示

## 文件说明

```
zhihu-cookie-exporter/
├── manifest.json          # 扩展配置文件
├── popup.html            # 弹出界面
├── popup.js              # 弹出界面逻辑
├── background.js         # 后台服务脚本
├── content.js            # 内容脚本
├── create_icons.py       # 图标生成脚本
├── icons/                # 图标文件
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # 使用说明
```

## 技术特性

### 支持的Cookie
扩展会自动识别并导出以下重要的知乎Cookie：
- `z_c0` - 用户认证Cookie
- `_xsrf` - CSRF保护
- `d_c0` - 设备标识
- `SESSIONID` - 会话ID
- `JOID` / `osd` - 用户标识
- `__zse_ck` - 安全Cookie
- 其他知乎相关Cookie

### 安全考虑
- ✅ 只获取知乎域名下的Cookie
- ✅ 不上传任何数据到服务器
- ✅ 本地处理，保护用户隐私
- ✅ 只导出必要的Cookie字段

## 故障排除

### 常见问题

**Q: 扩展无法安装？**
A: 确保Chrome版本支持Manifest V3，并已启用开发者模式。

**Q: 导出失败？**
A: 检查是否已登录知乎，确保在知乎页面操作。

**Q: Cookie无效？**
A: Cookie可能已过期，请重新登录知乎后再次导出。

**Q: 下载的文件格式错误？**
A: 确保扩展有下载权限，检查浏览器下载设置。

### 调试方法

1. **查看扩展日志**
   - 打开`chrome://extensions/`
   - 点击扩展的"详情"
   - 点击"检查视图"查看控制台

2. **检查权限**
   - 确保扩展有cookies和downloads权限
   - 检查host_permissions是否包含知乎域名

## 更新日志

### v1.0.0 (2025-07-27)
- ✨ 初始版本发布
- 🍪 支持一键导出知乎Cookie
- 🔍 自动检测登录状态
- 🎨 现代化UI设计
- 📱 响应式界面

## 许可证

本项目仅供学习和个人使用，请遵守知乎的服务条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个扩展！

---

**注意**: 请合理使用Cookie，遵守相关网站的服务条款和法律法规。 