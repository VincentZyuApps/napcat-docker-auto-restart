package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"napcat-docker-auto-restart/config"
	"napcat-docker-auto-restart/monitor"
)

func main() {
	fmt.Println("==================================================")
	fmt.Println("  NapCat Docker 自动重启监控 (Go版)")
	fmt.Println("==================================================")

	cfg, err := config.LoadConfig()
	if err != nil {
		monitor.Log(fmt.Sprintf("加载配置失败: %v", err), "ERROR")
		os.Exit(1)
	}

	monitor.Log(fmt.Sprintf("启动监控，检测间隔: %dms", cfg.CheckIntervalMS), "INFO")
	monitor.Log(fmt.Sprintf("容器心跳错开间隔: %dms", cfg.StaggerIntervalMS), "INFO")
	monitor.Log(fmt.Sprintf("容器总数: %d", len(cfg.Containers)), "INFO")

	for _, c := range cfg.Containers {
		statusStr := "启用"
		if !c.Enabled {
			statusStr = "禁用"
		}
		monitor.Log(fmt.Sprintf("  - %s (%s) @ %s:%d", c.Name, statusStr, c.SSHHost, c.WSPort), "INFO")
	}

	fmt.Println("--------------------------------------------------")

	// 捕获退出信号
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// 运行监控循环
	ticker := time.NewTicker(time.Duration(cfg.CheckIntervalMS) * time.Millisecond)
	defer ticker.Stop()

	runMonitor := func() {
		enabledContainers := []config.ContainerConfig{}
		for _, c := range cfg.Containers {
			if c.Enabled {
				enabledContainers = append(enabledContainers, c)
			}
		}

		for i, container := range enabledContainers {
			isOnline, errMsg := monitor.CheckContainerStatus(container)
			if isOnline {
				monitor.Log(fmt.Sprintf("[%s] 在线 ✓", container.Name), "SUCCESS")
			} else {
				monitor.Log(fmt.Sprintf("[%s] 离线! 原因: %s", container.Name, errMsg), "ERROR")

				if container.AutoRestart {
					monitor.Log(fmt.Sprintf("[%s] 正在尝试重启...", container.Name), "WARN")
					success, msg := monitor.RestartContainer(container)
					if success {
						monitor.Log(fmt.Sprintf("[%s] %s", container.Name, msg), "SUCCESS")
					} else {
						monitor.Log(fmt.Sprintf("[%s] %s", container.Name, msg), "ERROR")
					}
				}
			}

			if i < len(enabledContainers)-1 {
				time.Sleep(time.Duration(cfg.StaggerIntervalMS) * time.Millisecond)
			}
		}
		fmt.Println("--------------------------------------------------")
	}

	// 立即运行一次
	runMonitor()

	for {
		select {
		case <-sigChan:
			fmt.Println()
			monitor.Log("收到退出信号，监控已停止", "WARN")
			return
		case <-ticker.C:
			runMonitor()
		}
	}
}
