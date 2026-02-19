package monitor

import (
	"encoding/json"
	"fmt"
	"net/url"
	"os/exec"
	"strings"
	"time"

	"napcat-docker-auto-restart/config"

	"github.com/gorilla/websocket"
)

func Log(message string, level string) {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	var icon string
	switch level {
	case "INFO":
		icon = "ℹ️ "
	case "WARN":
		icon = "⚠️ "
	case "ERROR":
		icon = "❌"
	case "SUCCESS":
		icon = "✅"
	default:
		icon = ""
	}
	fmt.Printf("[%s] %s %s\n", timestamp, icon, message)
}

func CheckContainerStatus(container config.ContainerConfig) (bool, string) {
	u := url.URL{
		Scheme:   "ws",
		Host:     fmt.Sprintf("%s:%d", container.SSHHost, container.WSPort),
		Path:     "/",
		RawQuery: "access_token=" + container.Token,
	}

	dialer := websocket.Dialer{
		HandshakeTimeout: 5 * time.Second,
	}

	c, _, err := dialer.Dial(u.String(), nil)
	if err != nil {
		if strings.Contains(err.Error(), "refused") {
			return false, "连接被拒绝，NapCat 服务可能未运行"
		}
		return false, fmt.Sprintf("连接错误: %v", err)
	}
	defer c.Close()

	// 接收初始 lifecycle 消息
	_, _, err = c.ReadMessage()
	if err != nil {
		return false, fmt.Sprintf("读取生命周期消息失败: %v", err)
	}

	// 发送 get_status 请求
	payload := map[string]interface{}{
		"action": "get_status",
		"params": map[string]interface{}{},
		"echo":   "status_check",
	}
	err = c.WriteJSON(payload)
	if err != nil {
		return false, fmt.Sprintf("发送状态请求失败: %v", err)
	}

	// 接收响应
	_, message, err := c.ReadMessage()
	if err != nil {
		return false, fmt.Sprintf("接收响应失败: %v", err)
	}

	var result struct {
		Status string `json:"status"`
		Data   struct {
			Online bool `json:"online"`
		} `json:"data"`
		Message string `json:"message"`
	}

	if err := json.Unmarshal(message, &result); err != nil {
		return false, fmt.Sprintf("解析响应失败: %v", err)
	}

	if result.Status == "ok" {
		if result.Data.Online {
			return true, ""
		}
		return false, "Bot 已离线（可能被顶下线）"
	}

	return false, fmt.Sprintf("API 返回错误: %s", result.Message)
}

func RestartContainer(container config.ContainerConfig) (bool, string) {
	dockerCmd := "/usr/bin/docker"
	if container.UseSudo {
		dockerCmd = "/usr/bin/sudo /usr/bin/docker"
	}

	sshCmd := fmt.Sprintf("ssh %s@%s \"%s restart %s\"", container.SSHUser, container.SSHHost, dockerCmd, container.Name)
	_ = sshCmd // Keep for reference or remove

	var cmd *exec.Cmd
	// On Windows, use powershell or cmd to run the ssh command
	// But it's better to just run 'ssh' directly if it's in PATH

	// Better way to execute combined command:
	cmd = exec.Command("ssh", fmt.Sprintf("%s@%s", container.SSHUser, container.SSHHost), fmt.Sprintf("%s restart %s", dockerCmd, container.Name))

	output, err := cmd.CombinedOutput()
	if err != nil {
		return false, fmt.Sprintf("重启失败: %s (%v)", string(output), err)
	}

	return true, fmt.Sprintf("容器 %s 重启成功", container.Name)
}
