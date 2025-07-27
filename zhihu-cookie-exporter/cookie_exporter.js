// 知乎Cookie导出器 - 开发者工具脚本
// 使用方法：
// 1. 打开知乎网站并登录
// 2. 按F12打开开发者工具
// 3. 切换到Console标签
// 4. 复制粘贴下面的代码并回车
// 5. 自动下载cookies.json文件

(function() {
    console.log('🍪 开始导出知乎Cookie...');
    
    // 获取所有cookie
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [name, value] = cookie.trim().split('=');
        if (name && value) {
            acc[name] = value;
        }
        return acc;
    }, {});
    
    // 过滤知乎相关的cookie
    const zhihuCookies = {};
    const importantNames = [
        'z_c0', '_xsrf', 'd_c0', 'SESSIONID', 'JOID', 'osd',
        '__zse_ck', 'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49',
        'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49',
        'BEC', 'HMACCOUNT', 'tst', 'q_c1', '_zap', '_ga',
        'edu_user_uuid', '__snaker__id'
    ];
    
    for (const [name, value] of Object.entries(cookies)) {
        // 检查是否是知乎相关的cookie
        if (importantNames.includes(name) || 
            name.includes('zhihu') || 
            name.includes('_zse')) {
            zhihuCookies[name] = value;
        }
    }
    
    console.log('📋 找到的知乎Cookie:', zhihuCookies);
    console.log(`✅ 共找到 ${Object.keys(zhihuCookies).length} 个Cookie`);
    
    if (Object.keys(zhihuCookies).length === 0) {
        console.log('❌ 未找到知乎Cookie，请确保已登录知乎');
        return;
    }
    
    // 创建JSON文件并下载
    const jsonContent = JSON.stringify(zhihuCookies, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cookies.json';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('💾 Cookie文件已下载: cookies.json');
    console.log('📝 请将下载的文件放到知乎PDF下载器目录中');
    
    // 显示使用说明
    console.log('\n📖 使用说明:');
    console.log('1. 将下载的cookies.json文件放到知乎PDF下载器目录');
    console.log('2. 运行GUI程序或命令行工具');
    console.log('3. 程序会自动使用最新的cookie');
    console.log('4. 如果cookie过期，重复此步骤即可');
    
    // 显示Cookie详情
    console.log('\n🔍 Cookie详情:');
    for (const [name, value] of Object.entries(zhihuCookies)) {
        console.log(`  ${name}: ${value.substring(0, 20)}${value.length > 20 ? '...' : ''}`);
    }
    
})(); 