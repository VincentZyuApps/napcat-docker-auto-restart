import asyncio
import websockets
import json

async def get_bot_login_info():
    # 你的服务器地址和 Token
    uri = "ws://192.168.31.233:3000?access_token=test"
    
    try:
        # 1. 建立连接
        async with websockets.connect(uri) as websocket:
            print(f"已连接到: {uri}")

            # 2. 接收连接成功的第一个生命周期消息 (lifecycle)
            # 就像你在 log 里看到的那个 meta_event
            init_msg = await websocket.recv()
            print(f"收到初始信号: {init_msg}")

            # 3. 构造请求数据 (Action)
            payload = {
                "action": "get_login_info",
                "params": {},
                "echo": "123"  # 用于追踪请求的 ID
            }

            # 4. 发送请求
            print(f"正在发送 Action: {payload['action']}...")
            await websocket.send(json.dumps(payload))

            # 5. 等待并接收响应
            response = await websocket.recv()
            result = json.loads(response)

            # 6. 解析并美化输出
            print("\n--- 获取成功 ---")
            print(json.dumps(result, indent=4, ensure_ascii=False))
            
            if result.get("status") == "ok":
                user_data = result.get("data", {})
                print(f"\n机器人昵称: {user_data.get('nickname')}")
                print(f"机器人 QQ: {user_data.get('user_id')}")

    except Exception as e:
        print(f"连接或通信发生错误: {e}")

if __name__ == "__main__":
    # 运行异步任务
    asyncio.run(get_bot_login_info())