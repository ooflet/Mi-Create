# Mi Create macOS Launcher v2.1

**An all-in-one launcher for the Mi Create project on macOS.**
<br>
**一个为 Mi Create 项目在 macOS 上设计的一体化启动器。**

---

## 🚀 Quick Start / 快速开始

1.  **Grant Permission / 赋予权限**
    ```bash
    chmod +x Mi-Create-Launcher.sh
    ```
2.  **Run Launcher / 运行启动器**
    ```bash
    ./Mi-Create-Launcher.sh
    ```

> **Note / 提示:**
> The script will automatically handle all environment checks, dependency installations, and virtual environment setup on the first run. Subsequent launches will be much faster.
> 脚本将在首次运行时自动处理所有环境检查、依赖安装和虚拟环境设置。后续启动将非常快速。

---

## ✨ Key Features / 主要功能

| Feature / 功能 | Description / 描述 |
| :--- | :--- |
| 🔍 **Auto-Detection** / 自动检测 | Verifies macOS & Python compatibility. / 验证 macOS 和 Python 兼容性。 |
| 📦 **Smart Install** / 智能安装 | Installs all required dependencies automatically. / 自动安装所有必需的依赖。 |
| 🔧 **Venv-Managed** / 虚拟环境 | Creates and manages a local Python virtual environment. / 创建并管理本地 Python 虚拟环境。|
| ⚡ **Fast Launch** / 快速启动 | Uses a cache marker to skip installation on subsequent runs. / 使用缓存标记跳过后续运行的安装步骤。|
| 🧹 **Auto-Cleanup** / 自动清理 | Removes old virtual environments on first run. / 首次运行时自动清理旧的虚拟环境。|

---

## 🛠️ Advanced Usage / 高级用法

### **Force Reinstall / 强制重新安装**
If you encounter issues, you can force a complete reinstallation of the environment.
<br>
如果遇到问题，可以强制重新安装整个环境。
```bash
# This removes the setup marker, triggering a fresh install on the next run.
# 这会删除安装标记，在下次运行时触发全新安装。
rm .mi-create-setup-complete && ./Mi-Create-Launcher.sh
```

### **Full Cleanup / 完全清理**
To remove both the virtual environment and the setup marker.
<br>
用于删除虚拟环境和安装标记。
```bash
# This deletes the venv folder and the setup marker.
# 这会删除 venv 文件夹和安装标记。
rm -rf venv-mac .mi-create-setup-complete && ./Mi-Create-Launcher.sh
```

---

## 📋 Requirements / 系统要求

- **OS / 操作系统**: macOS 10.15+ (Catalina or later)
- **Python**: Version 3.8+
- **Disk Space / 磁盘空间**: ~200MB

---

## 🔍 Troubleshooting / 故障排除

- **"Permission denied" error / "权限不足" 错误:**
  - Run `chmod +x Mi-Create-Launcher.sh` to make the script executable.
  - 运行 `chmod +x Mi-Create-Launcher.sh` 使脚本可执行。

- **Incompatible Python Version / Python 版本不兼容:**
  - Ensure Python 3.8 or newer is installed. Use Homebrew (`brew install python`) or download from [python.org](https://www.python.org/downloads/).
  - 确保已安装 Python 3.8 或更高版本。使用 Homebrew (`brew install python`) 或从 [python.org](https://www.python.org/downloads/) 下载。

- **Application exits unexpectedly / 应用意外退出:**
  - Check for other running instances of Mi Create.
  - Review terminal output for specific error messages.
  - Try forcing a reinstall (see "Advanced Usage").
  - 检查是否有其他 Mi Create 实例正在运行。
  - 查看终端输出以获取具体的错误信息。
  - 尝试强制重新安装 (见“高级用法”)。
