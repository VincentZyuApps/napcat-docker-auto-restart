"""
NapCat 容器状态监控模块
"""
import asyncio
import json
import subprocess
from datetime import datetime
from typing import Optional, Tuple

import websockets

from config import ContainerConfig


async def check_container_status(container: ContainerConfig, timeout: float = 5.0) -> Tuple[bool, Optional[str]]:
    """
    检查单个容器的在线状态
    
    Args:
        container: 容器配置
        timeout: 超时时间（秒）
    
    Returns:
        (is_online, error_message)
        - is_online: True 表示在线，False 表示离线
        - error_message: 错误信息，如果在线则为 None
    """
    uri = f"ws://{container.ssh_host}:{container.ws_port}?access_token={container.token}"
    
    try:
        async with asyncio.timeout(timeout):
            async with websockets.connect(uri) as websocket:
                # 接收初始 lifecycle 消息
                await websocket.recv()
                
                # 发送 get_status 请求
                payload = {
                    "action": "get_status",
                    "params": {},
                    "echo": "status_check"
                }
                await websocket.send(json.dumps(payload))
                
                # 接收响应
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("status") == "ok":
                    data = result.get("data", {})
                    online = data.get("online", False)
                    
                    if online:
                        return True, None
                    else:
                        return False, "Bot 已离线（可能被顶下线）"
                else:
                    return False, f"API 返回错误: {result.get('message', 'unknown')}"
                    
    except asyncio.TimeoutError:
        return False, "连接超时"
    except websockets.exceptions.ConnectionClosedError as e:
        return False, f"连接被关闭: {e}"
    except ConnectionRefusedError:
        return False, "连接被拒绝，NapCat 服务可能未运行"
    except Exception as e:
        return False, f"未知错误: {e}"


def restart_container(container: ContainerConfig) -> Tuple[bool, str]:
    """
    通过 SSH 重启容器
    
    Args:
        container: 容器配置
    
    Returns:
        (success, message)
    """
    ssh_cmd = f"ssh {container.ssh_user}@{container.ssh_host} 'sudo docker restart {container.name}'"
    
    try:
        result = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, f"容器 {container.name} 重启成功"
        else:
            return False, f"重启失败: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "SSH 命令超时"
    except Exception as e:
        return False, f"执行 SSH 命令失败: {e}"


def log(message: str, level: str = "INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_icons = {
        "INFO": "ℹ️ ",
        "WARN": "⚠️ ",
        "ERROR": "❌",
        "SUCCESS": "✅",
    }
    icon = level_icons.get(level, "")
    print(f"[{timestamp}] {icon} {message}")
