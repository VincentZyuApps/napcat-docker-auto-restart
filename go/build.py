import os
import subprocess
import shutil
import re

def get_version():
    """从 version.toml 提取版本号"""
    version_file = "version.toml"
    if not os.path.exists(version_file):
        return "unknown"
    
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'version = "(.*)"', content)
        if match:
            return match.group(1)
    return "unknown"

def build():
    # 获取版本号
    version = get_version()
    print(f"📦 正在为版本 {version} 构建...")

    # 创建输出目录
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # 编译目标配置: (OS, ARCH, 扩展名)
    targets = [
        ("windows", "amd64", ".exe"),
        ("linux", "amd64", ""),
    ]

    for goos, goarch, suffix in targets:
        binary_name = f"napcat-monitor-{goos}-{goarch}-{version}{suffix}"
        output_path = os.path.join(dist_dir, binary_name)
        
        print(f"🚀 正在构建 {goos}/{goarch} -> {binary_name}...")
        
        # 设置环境变量并运行 go build
        env = os.environ.copy()
        env["GOOS"] = goos
        env["GOARCH"] = goarch
        
        cmd = [
            "go", "build",
            "-o", output_path,
            "main.go"
        ]
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 构建成功: {output_path}")
            else:
                print(f"❌ 构建失败: {result.stderr}")
        except Exception as e:
            print(f"💥 发生错误: {e}")

    print("\n✨ 所有构建任务已完成！产物保存在 dist 文件夹中。")

if __name__ == "__main__":
    # 确保在脚本所在目录运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build()
