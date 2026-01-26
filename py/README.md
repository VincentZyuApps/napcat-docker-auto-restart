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
sudo visudo

# 在文件末尾添加（把 zyu 换成你的用户名）：
zyu ALL=(ALL) NOPASSWD: /usr/bin/docker
```

或者把用户加入 docker 组（这样不需要 sudo）：
```bash
sudo usermod -aG docker zyu
# 重新登录后生效
```

### 3. 查看容器名

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
pip install -r requirements.txt
```

### 6. 启动监控

```bash
cd src
python main.py
```
