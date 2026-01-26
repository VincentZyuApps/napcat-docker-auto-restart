"""
NapCat Docker 自动重启监控主程序

功能：
- 定时检测 NapCat 容器的在线状态
- 如果检测到离线，自动通过 SSH 重启容器
"""
import asyncio
import signal
import sys

from config import load_config, AppConfig, ContainerConfig
from monitor import check_container_status, restart_container, log


# 全局退出标志
running = True


def signal_handler(signum, frame):
    """处理退出信号"""
    global running
    log("收到退出信号，正在停止...", "WARN")
    running = False


async def monitor_container(container: ContainerConfig):
    """
    监控单个容器
    
    Args:
        container: 容器配置
    """
    is_online, error = await check_container_status(container)
    
    if is_online:
        log(f"[{container.name}] 在线 ✓", "SUCCESS")
    else:
        log(f"[{container.name}] 离线! 原因: {error}", "ERROR")
        
        if container.auto_restart:
            log(f"[{container.name}] 正在尝试重启...", "WARN")
            success, msg = restart_container(container)
            
            if success:
                log(f"[{container.name}] {msg}", "SUCCESS")
            else:
                log(f"[{container.name}] {msg}", "ERROR")


async def run_monitor(config: AppConfig):
    """
    运行监控循环
    
    Args:
        config: 应用配置
    """
    global running
    
    log(f"启动监控，检测间隔: {config.check_interval} 秒")
    log(f"监控容器数量: {len(config.containers)}")
    
    for c in config.containers:
        log(f"  - {c.name} @ {c.ssh_host}:{c.ws_port}")
    
    print("-" * 50)
    
    while running:
        # 并发检测所有容器
        tasks = [monitor_container(c) for c in config.containers]
        await asyncio.gather(*tasks)
        
        print("-" * 50)
        
        # 等待下一次检测
        for _ in range(config.check_interval):
            if not running:
                break
            await asyncio.sleep(1)


def main():
    """主函数"""
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("  NapCat Docker 自动重启监控")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    
    if not config.containers:
        log("配置文件中没有容器配置!", "ERROR")
        sys.exit(1)
    
    # 运行监控
    try:
        asyncio.run(run_monitor(config))
    except KeyboardInterrupt:
        pass
    
    log("监控已停止", "INFO")


if __name__ == "__main__":
    main()
