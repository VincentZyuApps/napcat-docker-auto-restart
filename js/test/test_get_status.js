const WebSocket = require('ws');

// 1. 配置
const CONFIG = {
    url: 'ws://192.168.31.233:3000?access_token=test',
    action: 'get_status',
    echo: 'status_check_001'
};

const ws = new WebSocket(CONFIG.url);

// 2. 监听连接打开
ws.on('open', () => {
    console.log(`✅ 已建立 WebSocket 连接: ${CONFIG.url}`);
    
    // 构造 OneBot 标准请求包
    const payload = {
        action: CONFIG.action,
        params: {},
        echo: CONFIG.echo
    };

    console.log(`🚀 正在请求接口: ${CONFIG.action}...`);
    ws.send(JSON.stringify(payload));
});

// 3. 监听消息返回
ws.on('message', (rawData) => {
    try {
        const response = JSON.parse(rawData.toString());

        // 排除掉 lifecycle 等 meta_event，只处理我们发送的那个请求的响应
        if (response.echo === CONFIG.echo) {
            console.log('\n--- 收到状态响应 ---');
            console.log(JSON.stringify(response, null, 2));

            if (response.status === 'ok') {
                const { online, good } = response.data;

                console.log('\n========== 状态检测结果 ==========');
                console.log(`在线状态 (online): ${online ? '🟢 在线' : '🔴 离线'}`);
                console.log(`运行正常 (good):   ${good ? '✅ 是' : '⚠️ 否'}`);

                if (online && good) {
                    console.log('\n✨ Bot 运行完美！');
                } else {
                    console.log('\n🚨 请检查 Bot 运行环境或登录状态！');
                }
            }
            
            // 查完就走，关闭连接
            ws.close();
        } else if (response.post_type === 'meta_event') {
            // 这里可以打印心跳或连接信息，不想看可以注掉
            console.log(`[系统事件] ${response.meta_event_type}: ${response.sub_type || ''}`);
        }
    } catch (err) {
        console.error('解析消息失败:', err);
    }
});

// 4. 异常处理
ws.on('error', (err) => {
    if (err.message.includes('ECONNREFUSED')) {
        console.error('❌ 连接被拒绝：NapCat 服务可能没启动，或者 IP/端口填错了。');
    } else {
        console.error('❌ 发生错误:', err.message);
    }
});

ws.on('close', () => {
    console.log('\n🔌 连接已断开');
});