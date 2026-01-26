const WebSocket = require('ws');

// 配置信息
const url = 'ws://192.168.31.233:3000?access_token=test';

// 创建连接
const ws = new WebSocket(url);

ws.on('open', function open() {
    console.log('✅ 已连接到 NapCat 服务器');

    // 构造请求包
    const requestData = {
        action: 'get_login_info',
        params: {},
        echo: 'node_test_123' // 自定义 echo 方便匹配
    };

    console.log('🚀 正在发送请求...');
    ws.send(JSON.stringify(requestData));
});

ws.on('message', function message(data) {
    // data 是 Buffer 类型，需要转成字符串再解析
    const response = JSON.parse(data.toString());

    // 区分系统事件和 API 响应
    if (response.echo === 'node_test_123') {
        console.log('--- 收到 API 响应 ---');
        console.log(JSON.stringify(response, null, 2));

        if (response.status === 'ok') {
            const { nickname, user_id } = response.data;
            console.log(`\n机器人在线: ${nickname} (${user_id})`);
        }
        
        // 测试完毕后可以手动关闭连接，否则会一直保持监听
        ws.close();
    } else {
        // 这里会收到类似 lifecycle 或者心跳之类的消息
        console.log('📩 收到系统事件:', response.post_type || 'unknown');
    }
});

ws.on('error', function error(err) {
    console.error('❌ 连接错误:', err.message);
});

ws.on('close', () => {
    console.log('🔌 连接已关闭');
});