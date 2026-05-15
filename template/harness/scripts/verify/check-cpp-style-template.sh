#!/usr/bin/env bash
# C++ 格式检查脚本。复制母版后，可按项目目录和 clang-format 版本调整。
#
# 用途：检查 C++ 文件是否符合根目录 .clang-format。
# 何时运行：C++ 代码完成前、verify-template.sh 中、CI 中。
# 项目化要求：按真实项目调整目录范围、文件后缀和 clang-format 版本要求。
set -euo pipefail

files="$(
    find src tests -type f \( -name '*.h' -o -name '*.hpp' -o -name '*.cc' -o -name '*.cpp' -o -name '*.cxx' \) 2>/dev/null | sort
)"

if [ -z "$files" ]; then
    echo "未发现 C++ 源文件，跳过 clang-format 检查。"
    exit 0
fi

if ! command -v clang-format >/dev/null 2>&1; then
    echo "WHAT: 未找到 clang-format。"
    echo "WHY: C++ 项目要求使用根目录 .clang-format 统一格式。"
    echo "HOW: 请安装 clang-format，或在项目 SOP 中说明替代格式化工具。"
    exit 1
fi

echo "$files" | xargs clang-format --dry-run --Werror
