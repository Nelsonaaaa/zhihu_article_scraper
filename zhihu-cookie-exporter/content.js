// 知乎Cookie导出器 - 内容脚本
// 在知乎页面中运行，提供额外的功能

console.log('🍪 知乎Cookie导出器已加载');

// 监听来自扩展的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'getPageInfo') {
        // 获取页面信息
        const pageInfo = {
            url: window.location.href,
            title: document.title,
            isLoggedIn: checkLoginStatus()
        };
        sendResponse(pageInfo);
    }
});

// 检查登录状态
function checkLoginStatus() {
    // 检查是否存在登录相关的元素
    const loginIndicators = [
        document.querySelector('.AppHeader-profileEntry'), // 用户头像
        document.querySelector('[data-za-detail-view-path-module="UserItem"]'), // 用户信息
        document.querySelector('.AppHeader-userInfo'), // 用户信息
        document.querySelector('[data-za-detail-view-path-module="UserAvatar"]') // 用户头像
    ];
    
    return loginIndicators.some(indicator => indicator !== null);
}

// 添加页面内提示
function addPageNotification(message, type = 'info') {
    // 移除已存在的通知
    const existingNotification = document.getElementById('zhihu-cookie-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.id = 'zhihu-cookie-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        font-family: 'Microsoft YaHei', Arial, sans-serif;
        font-size: 14px;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// 监听页面变化，检测登录状态
let lastLoginStatus = checkLoginStatus();
setInterval(() => {
    const currentLoginStatus = checkLoginStatus();
    if (currentLoginStatus !== lastLoginStatus) {
        lastLoginStatus = currentLoginStatus;
        if (currentLoginStatus) {
            addPageNotification('检测到登录状态，可以导出Cookie', 'success');
        } else {
            addPageNotification('登录状态已失效，请重新登录', 'error');
        }
    }
}, 5000);

// 页面加载完成后显示提示
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (checkLoginStatus()) {
            addPageNotification('知乎Cookie导出器已就绪，点击扩展图标导出Cookie', 'info');
        }
    });
} else {
    if (checkLoginStatus()) {
        addPageNotification('知乎Cookie导出器已就绪，点击扩展图标导出Cookie', 'info');
    }
} 