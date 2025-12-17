#!/bin/bash
# 发布到 PyPI 的脚本

set -e

echo "🧹 清理旧构建..."
rm -rf dist/ build/ *.egg-info

echo "📦 构建包..."
python -m build

echo "🚀 上传到 PyPI..."
# 首次使用需要配置 token，或使用: twine upload dist/* -u __token__ -p <your-token>
twine upload dist/*

echo "✅ 完成！"
