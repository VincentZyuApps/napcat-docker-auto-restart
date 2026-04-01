![napcat-docker-auto-restart](https://socialify.git.ci/VincentZyu233/napcat-docker-auto-restart/image?custom_language=Go&description=1&font=Inter&forks=1&issues=1&language=1&logo=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2Fc%2Fc3%2FPython-logo-notext.svg%2F120px-Python-logo-notext.svg.png&name=1&owner=1&pattern=Charlie+Brown&pulls=1&stargazers=1&theme=Auto)

# NapCat Docker Auto Restart 监控工具 捏 🐱

[![Build & Release](https://github.com/VincentZyuApps/napcat-docker-auto-restart/actions/workflows/build.yml/badge.svg)](https://github.com/VincentZyuApps/napcat-docker-auto-restart/actions/workflows/build.yml)

自动检测 NapCat Docker 容器中的账号在线状态，并在检测到离线时自动通过 SSH 重启容器的轻量级工具。

> **使用场景**：如果你跟我一样，在 Linux 机器上挂着 NapCat Docker，希望它在线状态更稳，那么你就是本项目的受众之一 (●'◡'●)

---

## ✨ 核心特性

- **多版本可选**：
  - **Go 版本 (推荐)**：高性能、跨平台单文件，解压即用，资源分配极低。
  - **Python 版本**：适合开发者调试或对源码有定制需求的场景。
- **智能策略**：
  - 支持配置多个容器，每个容器可独立开启/关闭。
  - **心跳错位**：支持设置多个容器间的检测错开时间，避免瞬间打满宿主机资源。
- **全平台支持**：提供 Windows, Linux, macOS (x64 & ARM64) 的预编译版本。
- **自动恢复**：通过 WebSocket 实时获取 Bot 运行状态，非在线即触发 SSH 执行 `docker restart`。

---

## 🛠️ 技术栈

### Python 版本依赖

| 依赖库 | 版本 | 说明 |
|:---|:---|:---|
| [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/) | 3.8+ | 编程语言 |
| [![WebSockets](https://img.shields.io/badge/WebSockets-16.0-333333?style=flat-square)](https://github.com/python-websockets/websockets) | 16.0 | WebSocket 通信 |
| [![PyYAML](https://img.shields.io/badge/PyYAML-6.0.3-CC0200?style=flat-square)](https://pyyaml.org/) | 6.0.3 | YAML 配置解析 |
| [![Requests](https://img.shields.io/badge/Requests-2.32.5-3776AB?style=flat-square)](https://requests.readthedocs.io/) | 2.32.5 | HTTP 请求库 |

---

## 🚀 快速开始

### 1. 下载
前往 [Releases](https://github.com/VincentZyuApps/napcat-docker-auto-restart/releases) 页面下载对应系统的二进制文件。

### 2. ⚠️ 配置 SSH 免密登录（必须！）

**重要提示**：本工具通过 SSH 远程重启容器，**必须配置免密登录**，否则会卡在密码输入提示导致超时失败。

**注意事项**：
- 确认**运行本程序的用户**（如 `root` 或普通用户）
- 该用户需要能免密 SSH 到**远程服务器的目标用户**（配置文件中的 `ssh_user`）

#### Windows 11 PowerShell → Linux 免密登录

```powershell
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519

# 2. 复制公钥到远程服务器
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh user@remote_host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 3. 测试免密登录
ssh user@remote_host "echo '连接成功'"
```

#### Linux → Linux 免密登录

```bash
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -N ""

# 2. 复制公钥到远程服务器
ssh-copy-id user@remote_host

# 3. 测试免密登录
ssh user@remote_host "echo '连接成功'"
```

**特别提醒**：如果程序以 `root` 用户运行（如通过 systemd 或 MCSManager），需要为 `root` 用户配置免密登录：

```bash
sudo su - root
ssh-keygen -t ed25519 -N ""
ssh-copy-id user@remote_host
```

### 3. 配置 (`config.yaml`)
不管是 Python 还是 Go 版本，都使用统一的 YAML 配置文件。你可以参考各目录下的 `config.example.yaml`。

```yaml
check_interval_ms: 10000     # 总检测频率
stagger_interval_ms: 500      # 容器间错开时间

containers:
  - enabled: true             # 是否启用
    name: napcat-dev          # Docker 容器名
    ssh_user: zyu             # SSH 登录用户名
    ssh_host: 192.168.31.233  # 服务器 IP
    ws_port: 3000             # NapCat 的 WS 端口
    token: your_token         # Access Token
    auto_restart: true        # 离线是否自动重启
    use_sudo: false           # 是否使用 sudo（Python 版本）
```

**配置说明**：
- `use_sudo`: 仅 Python 版本使用。如果 SSH 用户不在 docker 组，需设为 `true` 并配置 sudo 免密（见下方）

#### 配置 sudo 免密（可选，仅 Python 版本需要）

如果 `use_sudo: true`，需在 Docker 宿主机上配置：

```bash
sudo visudo
# 添加（把 zyu 换成你的用户名）：
zyu ALL=(ALL) NOPASSWD: /usr/bin/docker
```

或者将用户加入 docker 组（推荐）：
```bash
sudo usermod -aG docker zyu
# 重新登录后生效，然后设置 use_sudo: false
```

### 4. 运行

#### **Go 版本 (推荐)**
```bash
# 直接运行编译好的产物即可
./napcat-monitor-linux-amd64-v1.0.0
```

#### **Python 版本**
```bash
cd py
pip install -r requirements.txt
python src/main.py
```

---

## 🛠️ 进阶技巧：配合 NapCat 自动登录

为了保证重启后能自动登录，**强烈建议**在 Docker 容器中配置 `ACCOUNT` 环境变量。

**方法一：命令行重启容器**
```bash
docker run -d \
  -e ACCOUNT=你的QQ号 \
  -p 3000:3000 \
  -v napcat-config:/app/napcat/config \
  --name napcat-dev \
  mlikiowa/napcat-docker:latest
```

**方法二：1Panel 面板**
1. 进入容器详情 -> 编辑。
2. 在环境变量中添加 `ACCOUNT=你的QQ号`。
3. 保存并由面板自动重建容器。

---

## 📂 项目结构
- `go/`: Go 实现的主程序，包含 `build.py` 跨平台打包脚本。
- `py/`: Python 实现的主程序，方便二次开发。
- `js/`: 最初用于探索 WebSocket 接口逻辑的测试脚本。
- `.github/`: 全自动化构建流水线。

---

## 💡 开发背景
1. 最开始想用 Python 快速撸个 Demo，搞定稳定的业务逻辑。
2. 逻辑验证通过后，用 Go 重写了一个更高性能、发布更简单的版本。
3. JS 的部分最初是想用 `wscat` 测试，后来单纯好奇前端流程也顺手揉了一份捏。

---

> ⚠️ **注意**：本项目目前暂无 License，仅供个人学习和技术交流使用捏。
