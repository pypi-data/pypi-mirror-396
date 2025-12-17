#!/bin/bash

# WS-Robot 打包和上传脚本
# 使用方法: ./build_and_upload.sh [test|prod]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印彩色消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
UPLOAD_TYPE=${1:-"test"}

if [ "$UPLOAD_TYPE" != "test" ] && [ "$UPLOAD_TYPE" != "prod" ]; then
    print_error "Invalid argument. Use 'test' or 'prod'"
    echo "Usage: $0 [test|prod]"
    exit 1
fi

print_info "Starting build and upload process (Mode: $UPLOAD_TYPE)"

# 检查是否安装了必要的工具
print_info "Checking required tools..."
if ! command -v python &> /dev/null; then
    print_error "Python is not installed"
    exit 1
fi

if ! python -m pip show build &> /dev/null; then
    print_warn "build package not found, installing..."
    python -m pip install --upgrade build
fi

if ! python -m pip show twine &> /dev/null; then
    print_warn "twine package not found, installing..."
    python -m pip install --upgrade twine
fi

# 清理旧的构建文件
print_info "Cleaning old build files..."
rm -rf build/ dist/ *.egg-info ws_robot.egg-info

# 构建包
print_info "Building package..."
python -m build

# 检查构建结果
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    print_error "Build failed - dist directory is empty"
    exit 1
fi

print_info "Build completed successfully"
ls -lh dist/

# 检查包
print_info "Checking package with twine..."
python -m twine check dist/*

# 上传
if [ "$UPLOAD_TYPE" == "test" ]; then
    print_info "Uploading to TestPyPI..."
    echo ""
    print_warn "You will be prompted for credentials:"
    print_warn "  Username: __token__"
    print_warn "  Password: your TestPyPI API token"
    echo ""
    python -m twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_info "Upload to TestPyPI successful!"
        echo ""
        print_info "To install from TestPyPI, run:"
        echo "  pip install --index-url https://test.pypi.org/simple/ ws-robot"
    fi
else
    print_warn "You are about to upload to PyPI (production)"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Upload cancelled"
        exit 0
    fi
    
    print_info "Uploading to PyPI..."
    echo ""
    print_warn "You will be prompted for credentials:"
    print_warn "  Username: __token__"
    print_warn "  Password: your PyPI API token"
    echo ""
    python -m twine upload dist/*
    
    if [ $? -eq 0 ]; then
        print_info "Upload to PyPI successful!"
        echo ""
        print_info "To install from PyPI, run:"
        echo "  pip install ws-robot"
    fi
fi

print_info "Done!"

