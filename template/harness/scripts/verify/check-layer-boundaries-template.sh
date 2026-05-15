#!/usr/bin/env bash
# 复制到真实项目后，按语言和目录规则补充分层检查。
#
# 用途：机械化检查 context/architecture/blueprint 中定义的依赖方向。
# 何时运行：verify-template.sh 中调用，也可单独运行。
# 项目化要求：按真实语言的 import/include 语法和目录结构实现检查。
set -euo pipefail

echo "WHAT: check-layer-boundaries-template.sh 尚未项目化。"
echo "WHY: 母版不知道真实 import/include 规则，不能证明分层边界。"
echo "HOW: 请按 context/architecture/blueprint/dependency-rules.md 编写项目分层检查。"
exit 1
