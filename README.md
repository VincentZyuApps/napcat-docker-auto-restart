# NapCat Docker Auto Restart

NapCat Docker 容器在线状态监控与自动重启工具。

定时检测 NapCat 容器的在线状态，如果检测到离线（如被顶下线），自动通过 SSH 重启容器。

## 项目结构

```
napcat-docker-auto-restart/
├── go/          # Go 实现（TODO）
├── py/          # Python 实现
└── js/          # JavaScript/Node.js 实现
```

## 功能

- ✅ 定时检测容器在线状态（通过 WebSocket `get_status` 接口）
- ✅ 支持多容器监控
- ✅ 离线时自动通过 SSH 重启容器
- ✅ 配置文件管理

## 快速开始

### Python 版本

```bash
cd py
cp config.example.yaml config.yaml
# 编辑 config.yaml
pip install -r requirements.txt
python src/main.py
```

### JavaScript 版本

```bash
cd js
cp config.example.yaml config.yaml
# 编辑 config.yaml
npm install
npm start
```

## 配置说明

参考 `config.example.yaml`：

```yaml
check_interval: 10  # 检测间隔（秒）

containers:
  - name: napcat-dev           # 容器名称
    ssh_user: zyu              # SSH 用户名
    ssh_host: 192.168.31.233   # SSH 主机 IP
    ws_port: 3000              # WebSocket 端口
    token: test                # access_token
    auto_restart: true         # 是否自动重启
```

## 前置要求

- 配置好免密 SSH 登录到 Docker 宿主机
- Docker 宿主机上有 sudo 权限执行 `docker restart`
