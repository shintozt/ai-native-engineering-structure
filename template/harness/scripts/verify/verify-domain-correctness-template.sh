#!/usr/bin/env bash
# Domain correctness 专项验证占位脚本。启用前必须替换为真实测试命令。
set -euo pipefail

summary="build/domain-special/correctness.json"
mkdir -p "$(dirname "$summary")"

cat > "$summary" <<'JSON'
{
  "suite": "domain-correctness",
  "status": "failed",
  "duration_ms": 0,
  "summary": "template placeholder; replace with project domain correctness tests",
  "tests_total": 0,
  "tests_failed": 0
}
JSON

echo "WHAT: verify-domain-correctness-template.sh 尚未项目化。"
echo "WHY: 母版不知道真实 domain 正确性用例，不能证明核心语义。"
echo "HOW: 按 harness/sop/03-domain-special-verification-sop.md 替换为真实 correctness 验证。"
exit 1
