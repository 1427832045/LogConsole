#!/usr/bin/env bash
# LogConsole 启动脚本

set -e

echo "🚀 启动 LogConsole..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."

    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
if ! python -c "import PyQt5" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -e .
fi

# 启动应用
echo "✅ 启动成功"
python -m logconsole.main
