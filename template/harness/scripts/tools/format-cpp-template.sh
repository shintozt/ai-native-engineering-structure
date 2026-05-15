#!/usr/bin/env bash
# C++ 批量格式化脚本。复制母版后，可按项目目录和文件后缀调整。
#
# 用途：批量修复 C++ 文件格式。
# 何时运行：本地开发或 AI 生成代码后，不建议在 CI 中自动改写。
# 项目化要求：按真实项目调整目录范围和文件后缀。
set -euo pipefail

files="$(
    find src tests -type f \( -name '*.h' -o -name '*.hpp' -o -name '*.cc' -o -name '*.cpp' -o -name '*.cxx' \) 2>/dev/null | sort
)"

if [ -z "$files" ]; then
    echo "未发现 C++ 源文件，跳过格式化。"
    exit 0
fi

if ! command -v clang-format >/dev/null 2>&1; then
    echo "WHAT: 未找到 clang-format。"
    echo "WHY: C++ 项目要求使用根目录 .clang-format 统一格式。"
    echo "HOW: 请安装 clang-format，或在项目 SOP 中说明替代格式化工具。"
    exit 1
fi

echo "$files" | xargs clang-format -i
