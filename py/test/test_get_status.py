import asyncio
import websockets
import json

async def get_bot_status():
    # 你的服务器地址和 Token
    uri = "ws://192.168.31.233:3000?access_token=test"
    
    try:
        # 1. 建立连接
        async with websockets.connect(uri) as websocket:
            print(f"已连接到: {uri}")

            # 2. 接收连接成功的第一个生命周期消息 (lifecycle)
            init_msg = await websocket.recv()
            print(f"收到初始信号: {init_msg}")

            # 3. 构造请求数据 (Action)
            payload = {
                "action": "get_status",
                "params": {},
                "echo": "123"
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
                data = result.get("data", {})
                online = data.get("online")
                good = data.get("good")
                
                print(f"\n========== 状态检测结果 ==========")
                print(f"在线状态 (online): {online}")
                print(f"运行正常 (good):   {good}")
                
                if online:
                    print("\n✅ Bot 当前在线！")
                else:
                    print("\n❌ Bot 已离线！可能被顶下线了")
                    
                if not good:
                    print("⚠️  Bot 状态异常！")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"连接被关闭: {e}")
        print("❌ 可能 Bot 已离线，无法建立连接")
    except ConnectionRefusedError:
        print("❌ 连接被拒绝，NapCat 服务可能未运行")
    except Exception as e:
        print(f"连接或通信发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(get_bot_status())
