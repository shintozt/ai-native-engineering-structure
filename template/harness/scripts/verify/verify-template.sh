#!/usr/bin/env bash
# 复制到真实项目后，替换为项目的构建、测试和验证命令。
# 如果使用 GoogleTest 默认摘要，可解析 total/passed；若开启 --gtest_brief=1，需改写解析逻辑。
#
# 用途：统一完成前验证入口。
# 何时运行：声称完成前、人工验收前、CI 中。
# 项目化要求：替换构建命令、测试命令、测试数断言、分层检查和格式检查。
set -euo pipefail

echo "WHAT: verify-template.sh 尚未项目化。"
echo "WHY: 母版不知道真实技术栈，不能证明构建和测试通过。"
echo "HOW: 请替换 harness/scripts/verify/verify-template.sh 中的构建、测试、测试数断言和分层检查命令。"
exit 1
