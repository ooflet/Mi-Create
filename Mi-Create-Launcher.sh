#!/bin/bash

# ==================================================================================================
# Mi Create All-in-One Launcher v2.1
#
# Features:
# - Auto environment detection
# - Auto dependency installation
# - Auto application launch
# - Supports any version of the Mi Create project
#
# Usage:
# 1. Copy this file to the Mi Create project root directory.
# 2. Run: ./Mi-Create-Launcher.sh
# 3. Enjoy!
#
# ---
#
# Mi Create 一体化启动器 v2.1
#
# 功能:
# - 自动检测环境
# - 自动安装依赖
# - 自动启动应用
# - 支持任意版本的 Mi Create 项目
#
# 使用方法:
# 1. 将此文件复制到 Mi Create 项目根目录
# 2. 运行: ./Mi-Create-Launcher.sh
# 3. 享受！
# ==================================================================================================

set -e

# --------------------------------------------------------------------------------------------------
# Style & Color Definitions / 颜色和样式定义
# --------------------------------------------------------------------------------------------------
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[1;33m'
C_BLUE='\033[0;34m'
C_PURPLE='\033[0;35m'
C_CYAN='\033[0;36m'
C_WHITE='\033[1;37m'
C_BOLD='\033[1m'
C_UNDERLINE='\033[4m'
C_NC='\033[0m' # No Color

# --------------------------------------------------------------------------------------------------
# Global Variables / 全局变量
# --------------------------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Mi Create"
MIN_PYTHON_VERSION="3.8"
VENV_DIR="venv-mac"
MAIN_SCRIPT="src/main.py"
SETUP_COMPLETE_FILE="mi-create-setup-complete.txt"

# --------------------------------------------------------------------------------------------------
# Logging Functions / 日志函数
# --------------------------------------------------------------------------------------------------
# Arguments: $1: Message
log_info() { echo -e "${C_BLUE}ℹ [INFO]${C_NC} $1"; }
log_success() { echo -e "${C_GREEN}✔ [SUCCESS]${C_NC} $1"; }
log_warning() { echo -e "${C_YELLOW}⚠ [WARNING]${C_NC} $1"; }
log_error() { echo -e "${C_RED}✖ [ERROR]${C_NC} $1"; }
log_header() { echo -e "\n${C_PURPLE}${C_BOLD}═══ $1 ═══${C_NC}"; }
log_step() { echo -e "${C_CYAN}»${C_NC} $1"; }

# --------------------------------------------------------------------------------------------------
# UI & Banners / 界面与横幅
# --------------------------------------------------------------------------------------------------
show_banner() {
    clear
    echo -e "${C_CYAN}${C_BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                      🚀 Welcome to Mi Create Launcher 🚀                     ║"
    echo "║                  One script to solve all your setup needs.                   ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${C_NC}"
    echo -e "${C_WHITE}✨ Auto Environment Detection   📦 Smart Dependency Installation   🎯 One-Click App Launch${C_NC}"
    echo -e "${C_PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_NC}"
    echo
}

# --------------------------------------------------------------------------------------------------
# Core Logic Functions / 核心逻辑函数
# --------------------------------------------------------------------------------------------------

# Check if this is the first time the script is run.
# 检查是否首次运行
is_first_run() {
    [[ ! -f "$SETUP_COMPLETE_FILE" ]]
}

# Create a marker file to indicate that the setup is complete.
# 创建安装完成标记
create_setup_marker() {
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat > "$SETUP_COMPLETE_FILE" << EOF
# Mi Create Setup Completion Marker
# Delete this file to trigger a fresh installation.
# ---
# Mi Create 安装完成标记
# 删除此文件可重新安装环境

Setup-Time: $timestamp
Python-Version: $python_version
Virtual-Env: $VENV_DIR
Launcher-Version: 2.1
EOF

    log_success "Setup marker created. / 安装完成标记已创建。"
}

# Check system environment compatibility.
# 检查系统环境
check_system() {
    log_header "System Environment Check / 系统环境检查"
    
    # Check OS / 检查操作系统
    log_step "Checking Operating System..."
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This launcher is designed for macOS. / 此启动器专为 macOS 设计。"
        exit 1
    fi
    log_success "macOS detected. / 已检测到 macOS 系统。"
    
    # Check Python / 检查Python
    log_step "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not found. / 未找到 Python 3。"
        echo -e "${C_YELLOW}Please install Python 3.8+ / 请安装 Python 3.8+:${C_NC}"
        echo -e "  • Official Website / 官方网站: ${C_UNDERLINE}https://www.python.org/downloads/${C_NC}"
        echo -e "  • Homebrew: ${C_BLUE}brew install python${C_NC}"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_success "Python $python_version found. / 已找到 Python $python_version。"
    
    # Check Python version / 检查Python版本
    log_step "Verifying Python version..."
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_error "Python version is too old. Version 3.8+ is required. / Python 版本过低，需要 3.8+。"
        exit 1
    fi
    log_success "Python version is compatible. / Python 版本兼容。"
    
    # Check project structure / 检查项目结构
    log_step "Verifying project structure..."
    cd "$SCRIPT_DIR"
    if [[ ! -f "$MAIN_SCRIPT" ]]; then
        log_error "Could not find '$MAIN_SCRIPT'. Please run this script from the project root. / 未找到 '$MAIN_SCRIPT'，请确保在项目根目录运行此脚本。"
        exit 1
    fi
    log_success "Project structure is valid. / 项目结构完整。"
}

# Set up the Python virtual environment.
# 设置虚拟环境
setup_venv() {
    log_header "Virtual Environment Setup / 虚拟环境设置"

    if is_first_run; then
        if [[ -d "$VENV_DIR" ]]; then
            log_warning "Old virtual environment detected. Cleaning up... / 检测到旧虚拟环境，正在清理..."
            rm -rf "$VENV_DIR"
            log_success "Cleaned up old virtual environment. / 旧虚拟环境已清理。"
        fi

        log_step "Creating new virtual environment... / 正在创建新的虚拟环境..."
        python3 -m venv "$VENV_DIR"
        log_success "New virtual environment created at '$VENV_DIR'. / 新虚拟环境已创建在 '$VENV_DIR'。"
    else
        if [[ ! -d "$VENV_DIR" ]]; then
            log_error "Virtual environment is missing. Delete '$SETUP_COMPLETE_FILE' to reinstall. / 虚拟环境丢失，请删除 '$SETUP_COMPLETE_FILE' 后重新安装。"
            exit 1
        fi
        log_success "Using existing virtual environment. / 使用现有虚拟环境。"
    fi

    # Activate virtual environment / 激活虚拟环境
    log_step "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_error "Failed to activate virtual environment. / 虚拟环境激活失败。"
        exit 1
    fi
    log_success "Virtual environment activated. / 虚拟环境已激活。"

    # Upgrade pip only on first run / 只在首次运行时升级pip
    if is_first_run; then
        log_step "Upgrading pip..."
        python -m pip install --upgrade pip --quiet
        log_success "pip has been upgraded. / pip 已升级。"
    else
        log_success "Skipping pip upgrade (not first run). / 跳过 pip 升级（非首次运行）。"
    fi
}

# Install dependencies, with smart caching.
# 安装依赖 - 智能缓存版本
install_dependencies() {
    log_header "Dependency Management / 依赖管理"

    if ! is_first_run; then
        log_info "Setup marker found. Performing quick dependency check... / 检测到安装标记，执行快速依赖检查..."
        
        local key_imports=("PyQt6" "Cocoa" "Quartz")
        local verification_failed=false

        for import_name in "${key_imports[@]}"; do
            if python -c "import $import_name" 2>/dev/null; then
                log_success "  ✔ $import_name is installed. / 已安装。"
            else
                log_warning "  ✖ $import_name is missing. / 缺失。"
                verification_failed=true
            fi
        done

        if [[ "$verification_failed" == "false" ]]; then
            log_success "All key dependencies are present. Skipping installation. / 所有关键依赖均存在，跳过安装。"
            return 0
        else
            log_warning "Dependency check failed. Re-installing... / 依赖检查失败，将重新安装..."
            rm -f "$SETUP_COMPLETE_FILE" # Force re-installation / 强制重新安装
        fi
    fi

    log_info "Performing full dependency installation... / 执行完整依赖安装..."
    
    if [[ -f "requirements.txt" ]]; then
        log_step "Installing base dependencies from requirements.txt... / 从 requirements.txt 安装基础依赖..."
        python -m pip install -r requirements.txt --quiet
        log_success "Base dependencies installed. / 基础依赖已安装。"
    else
        log_error "requirements.txt not found. / 未找到 requirements.txt 文件。"
        exit 1
    fi

    log_step "Installing macOS-specific dependencies... / 安装 macOS 特定依赖..."
    python -m pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz --quiet
    log_success "macOS dependencies installed. / macOS 依赖已安装。"

    # Final verification / 最终验证
    log_info "Verifying final installation... / 验证最终安装结果..."
    local key_imports=("PyQt6" "Cocoa" "Quartz")
    for import_name in "${key_imports[@]}"; do
        if python -c "import $import_name" 2>/dev/null; then
            log_success "  ✔ $import_name successfully verified. / 验证成功。"
        else
            log_error "  ✖ Verification failed for $import_name. / 验证失败。"
            exit 1
        fi
    done

    create_setup_marker
}

# Launch the main application.
# 启动应用程序
launch_app() {
    log_header "Launching Application / 启动应用程序"
    
    log_info "Starting $PROJECT_NAME..."
    log_warning "On first launch, you may need to select a language. / 首次启动可能需要选择语言。"
    echo
    
    python "$MAIN_SCRIPT"
    
    echo
    log_success "$PROJECT_NAME has exited. / $PROJECT_NAME 已退出。"
}

# --------------------------------------------------------------------------------------------------
# Main Execution Logic / 主执行逻辑
# --------------------------------------------------------------------------------------------------
main() {
    show_banner

    if is_first_run; then
        log_info "First run detected. Executing full installation process... / 检测到首次运行，将执行完整安装流程..."
    else
        log_info "Setup marker detected. Using quick launch mode... / 检测到安装标记，将使用快速启动模式..."
        echo -e "${C_CYAN}💡 TIP: To re-install, just delete the ${C_BOLD}$SETUP_COMPLETE_FILE${C_NC}${C_CYAN} file.${C_NC}"
        echo -e "${C_CYAN}💡 提示：要重新安装，只需删除 ${C_BOLD}$SETUP_COMPLETE_FILE${C_NC}${C_CYAN} 文件。${C_NC}"
    fi

    check_system
    setup_venv
    install_dependencies
    launch_app

    echo
    log_header "🎉 All Done! / 全部完成！ 🎉"
    if is_first_run; then
        echo -e "${C_GREEN}First-time setup complete! Subsequent launches will be much faster.${C_NC}"
        echo -e "${C_GREEN}首次安装完成！下次启动将更快速。${C_NC}"
    fi
    echo -e "${C_WHITE}To run again / 再次运行: ${C_BOLD}./Mi-Create-Launcher.sh${C_NC}"
    echo -e "${C_YELLOW}To reinstall / 重新安装: ${C_BOLD}rm $SETUP_COMPLETE_FILE && ./Mi-Create-Launcher.sh${C_NC}"
    echo
}

# --------------------------------------------------------------------------------------------------
# Error Handling / 错误处理
# --------------------------------------------------------------------------------------------------
handle_error() {
    local exit_code=$1
    echo
    log_error "An error occurred during execution (Exit Code: $exit_code). / 启动过程中发生错误 (退出码: $exit_code)。"
    log_warning "Please check the error messages above and try again. / 请检查上方的错误信息并重试。"
    exit $exit_code
}

trap 'handle_error $?' ERR

# --------------------------------------------------------------------------------------------------
# Run the main function / 执行主函数
# --------------------------------------------------------------------------------------------------
main "$@"
