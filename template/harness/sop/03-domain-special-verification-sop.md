# Domain 专项验证 SOP

本 SOP 用于为高风险 domain 能力建立专项正确性和性能验证。它是可选流程，默认不启用；只有当项目已经有稳定 public domain 入口，且普通单测无法覆盖关键语义或性能风险时才执行。

## 触发场景

- domain 层包含状态机、合流、去重、时间窗、重采样、计费、权限、资金、库存等高风险规则。
- 普通单测能覆盖局部函数，但无法证明端到端业务语义。
- 性能风险已经进入 `context/operations/performance-risk-analysis.md`。
- 需求频繁修改核心规则，需要长期回归样本。

## 初始化步骤

1. 在 `harness/verification/domain-special-verification.json` 中确认 `enabled=false`。
2. 设计专项 correctness 场景，放入 `harness/verification/domain-special/`。
3. 设计专项 performance benchmark，放入 `harness/verification/domain-special/`。
4. 将占位脚本项目化：
   - `harness/scripts/verify/verify-domain-correctness-template.sh`
   - `harness/scripts/verify/verify-domain-performance-template.sh`
5. 产出运行日志：
   - `harness/verification-runs/domain-correctness.md`
   - `harness/verification-runs/domain-performance.md`
6. 人工确认后，把 `enabled` 改为 `true`，并填写 `enabled_by` / `enabled_at`。

## 正确性验证要求

| 项 | 要求 |
| --- | --- |
| 输入 | 使用稳定 fixture 或可复现实例 |
| 输出 | 生成 summary JSON，包含 suite、status、tests_total、tests_failed、summary |
| 覆盖 | 至少覆盖核心业务不变式、异常输入、边界条件 |
| 失败 | 任何失败返回非 0，不允许只写日志不阻断 |

## 性能验证要求

| 项 | 要求 |
| --- | --- |
| 输入 | 明确样本规模、冷热状态、并发模型 |
| 输出 | 生成 summary JSON，包含 suite、status、metrics、duration_ms、summary |
| 阈值 | 初期可只记录，不设硬阈值；有 3 次以上稳定样本后再讨论阈值 |
| 归档 | 每次专项运行追加到 `harness/verification-runs/` |

## 启用原则

- 没有稳定 public domain 入口时，不启用。
- 没有真实专项用例时，不启用。
- 没有人工确认的阈值时，不把 performance 作为硬阻断。
- 专项验证失败时，必须先判断是业务语义变化、测试数据过期，还是实现回归。
