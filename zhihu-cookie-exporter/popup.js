// 知乎Cookie导出器 - 弹出界面逻辑
document.addEventListener('DOMContentLoaded', function() {
    const exportBtn = document.getElementById('exportBtn');
    const checkBtn = document.getElementById('checkBtn');
    const statusText = document.getElementById('statusText');
    const statusDiv = document.getElementById('status');
    const cookieCount = document.getElementById('cookieCount');
    
    // 页面加载时检查Cookie状态
    checkCookieStatus();
    
    // 导出Cookie按钮点击事件
    exportBtn.addEventListener('click', function() {
        exportCookies();
    });
    
    // 检查Cookie状态按钮点击事件
    checkBtn.addEventListener('click', function() {
        checkCookieStatus();
    });
    
    // 检查Cookie状态
    function checkCookieStatus() {
        setStatus('正在检查Cookie状态...', 'loading');
        exportBtn.disabled = true;
        checkBtn.disabled = true;
        
        chrome.cookies.getAll({domain: "zhihu.com"}, function(cookies) {
            if (chrome.runtime.lastError) {
                setStatus('检查失败: ' + chrome.runtime.lastError.message, 'error');
                exportBtn.disabled = false;
                checkBtn.disabled = false;
                return;
            }
            
            // 过滤重要的知乎Cookie
            const importantCookies = filterImportantCookies(cookies);
            
            if (importantCookies.length === 0) {
                setStatus('未找到知乎Cookie，请先登录知乎', 'error');
                cookieCount.textContent = '';
            } else {
                setStatus('找到知乎Cookie，可以导出', 'success');
                cookieCount.textContent = `找到 ${importantCookies.length} 个Cookie`;
            }
            
            exportBtn.disabled = false;
            checkBtn.disabled = false;
        });
    }
    
    // 导出Cookie
    function exportCookies() {
        setStatus('正在导出Cookie...', 'loading');
        exportBtn.disabled = true;
        checkBtn.disabled = true;
        
        chrome.cookies.getAll({domain: "zhihu.com"}, function(cookies) {
            if (chrome.runtime.lastError) {
                setStatus('导出失败: ' + chrome.runtime.lastError.message, 'error');
                exportBtn.disabled = false;
                checkBtn.disabled = false;
                return;
            }
            
            // 过滤并格式化Cookie
            const cookieData = formatCookiesForExport(cookies);
            
            if (Object.keys(cookieData).length === 0) {
                setStatus('未找到有效的知乎Cookie', 'error');
                exportBtn.disabled = false;
                checkBtn.disabled = false;
                return;
            }
            
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
                    setStatus('下载失败: ' + chrome.runtime.lastError.message, 'error');
                } else {
                    setStatus('Cookie导出成功！', 'success');
                    cookieCount.textContent = `已导出 ${Object.keys(cookieData).length} 个Cookie`;
                }
                
                URL.revokeObjectURL(url);
                exportBtn.disabled = false;
                checkBtn.disabled = false;
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
    
    // 格式化Cookie用于导出
    function formatCookiesForExport(cookies) {
        const cookieData = {};
        const importantCookies = filterImportantCookies(cookies);
        
        importantCookies.forEach(cookie => {
            cookieData[cookie.name] = cookie.value;
        });
        
        return cookieData;
    }
    
    // 设置状态显示
    function setStatus(message, type = 'normal') {
        statusText.innerHTML = message;
        statusDiv.className = 'status';
        
        if (type === 'loading') {
            statusText.innerHTML = '<span class="loading"></span> ' + message;
        } else if (type === 'success') {
            statusDiv.classList.add('success');
        } else if (type === 'error') {
            statusDiv.classList.add('error');
        }
    }
}); 