# NapCat Docker 自动重启监控 (Python)

## 使用步骤

### 1. 配置免密 SSH

**Linux/macOS:**
```bash
# 生成密钥（如果没有）
ssh-keygen -t rsa

# 复制公钥到 Docker 宿主机
ssh-copy-id zyu@192.168.31.233
```

**Windows PowerShell:**
```powershell
# 生成密钥（如果没有）
ssh-keygen -t rsa

# 复制公钥到 Docker 宿主机（Windows 没有 ssh-copy-id，手动复制）
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh zyu@192.168.31.233 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 2. 配置 sudo 免密码（Docker 宿主机上执行）

```bash
# 在 Docker 宿主机上，让用户执行 docker 命令时不需要 sudo 密码
# 默认用 vi 编辑，如果想用 nano：sudo EDITOR=nano visudo
sudo visudo

# 在文件末尾添加（把 zyu 换成你的用户名）：
zyu ALL=(ALL) NOPASSWD: /usr/bin/docker
```

或者把用户加入 docker 组（这样不需要 sudo）：
```bash
sudo usermod -aG docker zyu
# 重新登录后生效
```

### 3. 配置 NapCat 容器快速登录（Docker 宿主机上执行）

NapCat 容器需要配置 `ACCOUNT` 环境变量才能实现自动快速登录，否则每次重启都要扫码。

**方法一：手动重建容器**

```bash
# 1. 查看现有容器的配置（记下端口映射、挂载等信息）
docker inspect napcat-dev

# 2. 停止并删除旧容器（数据在 volume 里不会丢）
docker stop napcat-dev
docker rm napcat-dev

# 3. 重新创建容器，添加 ACCOUNT 环境变量
docker run -d \
  -e ACCOUNT=你的QQ号 \
  -p 3000:3000 \
  -p 6099:6099 \
  -v napcat-qq-data:/app/.config/QQ \
  -v napcat-config:/app/napcat/config \
  --name napcat-dev \
  --restart=always \
  mlikiowa/napcat-docker:latest
```

**方法二：使用 1Panel 面板**

> [1Panel](https://1panel.cn/) 是一个现代化的 Linux 服务器运维管理面板

1. 打开 1Panel 首页
2. 左侧菜单 → 容器 → 上方 容器
3. 找到 napcat 容器 → 点击「更多」→「编辑」
4. 往下翻找到「环境变量」
5. 添加：`ACCOUNT=你的QQ号`
6. 点击「保存」，等待 1Panel 自动重建容器

### 4. 查看容器名

```bash
ssh zyu@192.168.31.233
sudo docker ps -a | grep napcat
```

### 4. 创建配置文件

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml，填入容器名、IP、端口、token
```

### 5. 安装依赖

```bash
python -m venv venv
# or use uv. https://gitee.com/wangnov/uv-custom/releases
# uv venv --python 3.12
pip install -r requirements.txt
# uv pip install -r requirements.txt
```

### 6. 启动监控

```bash
cd src
python main.py
# uv run main.py
```
