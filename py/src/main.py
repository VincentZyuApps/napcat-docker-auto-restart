"""
NapCat Docker 自动重启监控主程序

功能：
- 定时检测 NapCat 容器的在线状态
- 如果检测到离线，自动通过 SSH 重启容器
"""
import asyncio
import sys

from config import load_config, AppConfig, ContainerConfig
from monitor import check_container_status, restart_container, log


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
    log(f"启动监控，检测间隔: {config.check_interval_ms}ms")
    log(f"容器心跳错开间隔: {config.stagger_interval_ms}ms")
    log(f"监控容器数量: {len(config.containers)}")
    
    for c in config.containers:
        status_str = "启用" if c.enabled else "禁用"
        log(f"  - {c.name} ({status_str}) @ {c.ssh_host}:{c.ws_port}")
    
    print("-" * 50)
    
    while True:
        # 依次检测每个容器，错开间隔
        # 过滤掉未启用的容器
        enabled_containers = [c for c in config.containers if c.enabled]
        
        for i, container in enumerate(enabled_containers):
            await monitor_container(container)
            # 如果不是最后一个容器，等待错开间隔
            if i < len(enabled_containers) - 1:
                await asyncio.sleep(config.stagger_interval_ms / 1000)
        
        print("-" * 50)
        
        # 等待下一次检测周期
        await asyncio.sleep(config.check_interval_ms / 1000)


def main():
    """主函数"""
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
        print()  # 换行，让输出更整洁
        log("收到退出信号，监控已停止", "WARN")


if __name__ == "__main__":
    main()
