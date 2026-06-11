#!/usr/bin/env bash
# Domain performance 专项验证占位脚本。启用前必须替换为真实 benchmark 命令。
set -euo pipefail

summary="build/domain-special/performance.json"
mkdir -p "$(dirname "$summary")"

cat > "$summary" <<'JSON'
{
  "suite": "domain-performance",
  "status": "failed",
  "duration_ms": 0,
  "summary": "template placeholder; replace with project domain performance benchmarks",
  "metrics": {}
}
JSON

echo "WHAT: verify-domain-performance-template.sh 尚未项目化。"
echo "WHY: 母版不知道真实 domain 性能场景，不能证明性能风险。"
echo "HOW: 按 harness/sop/03-domain-special-verification-sop.md 替换为真实 performance benchmark。"
exit 1
