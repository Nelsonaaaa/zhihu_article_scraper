// 知乎Cookie导出器 - 后台服务脚本
chrome.runtime.onInstalled.addListener(function() {
    console.log('知乎Cookie导出器已安装');
});

// 监听扩展图标点击事件
chrome.action.onClicked.addListener(function(tab) {
    // 检查当前页面是否是知乎
    if (tab.url && tab.url.includes('zhihu.com')) {
        // 如果当前在知乎页面，直接导出Cookie
        exportCookiesFromTab(tab);
    } else {
        // 如果不在知乎页面，打开弹出窗口
        chrome.action.setPopup({ popup: 'popup.html' });
    }
});

// 从指定标签页导出Cookie
function exportCookiesFromTab(tab) {
    chrome.cookies.getAll({domain: "zhihu.com"}, function(cookies) {
        if (chrome.runtime.lastError) {
            console.error('获取Cookie失败:', chrome.runtime.lastError);
            return;
        }
        
        // 过滤重要的知乎Cookie
        const importantCookies = filterImportantCookies(cookies);
        
        if (importantCookies.length === 0) {
            // 显示通知
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: '知乎Cookie导出器',
                message: '未找到知乎Cookie，请先登录知乎'
            });
            return;
        }
        
        // 格式化Cookie数据
        const cookieData = {};
        importantCookies.forEach(cookie => {
            cookieData[cookie.name] = cookie.value;
        });
        
        // 创建JSON文件并下载
        const jsonContent = JSON.stringify(cookieData, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        chrome.downloads.download({
            url: url,
            filename: 'cookies.json',
            saveAs: false
        }, function(downloadId) {
            if (chrome.runtime.lastError) {
                console.error('下载失败:', chrome.runtime.lastError);
            } else {
                // 显示成功通知
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon48.png',
                    title: '知乎Cookie导出器',
                    message: `成功导出 ${Object.keys(cookieData).length} 个Cookie`
                });
            }
            
            URL.revokeObjectURL(url);
        });
    });
}

// 过滤重要的知乎Cookie
function filterImportantCookies(cookies) {
    const importantNames = [
        'z_c0', '_xsrf', 'd_c0', 'SESSIONID', 'JOID', 'osd',
        '__zse_ck', 'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49',
        'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49',
        'BEC', 'HMACCOUNT', 'tst', 'q_c1', '_zap', '_ga',
        'edu_user_uuid', '__snaker__id'
    ];
    
    return cookies.filter(cookie => 
        importantNames.includes(cookie.name) || 
        cookie.name.includes('zhihu') ||
        cookie.name.includes('_zse')
    );
}

// 监听来自弹出窗口的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'exportCookies') {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                exportCookiesFromTab(tabs[0]);
            }
        });
        sendResponse({success: true});
    }
}); 