# 门禁

## 门禁 1：Spec 评审

通过标准：

- 业务行为清楚。
- 验收标准可测试。
- 非目标明确。
- Blocking 问题已关闭或转为 Non-blocking。

自动检查方式：

- `harness/scripts/hooks/harness_gate.py pre-edit` 检查代码类编辑前是否存在当前 Track 的 `spec.md`。

人工检查方式：

- 业务负责人确认验收标准可执行。
- 研发负责人确认边界和风险可控。

## 门禁 2：设计评审

通过标准：

- 设计覆盖 Spec。
- 分层影响清楚。
- 端口、适配器、基础设施边界清楚。
- 回滚、降级、异常流程清楚。
- 测试方案可执行。

自动检查方式：

- 可通过 Evaluator Agent 检查 Design 是否覆盖 Spec。

人工检查方式：

- 技术负责人确认接口、流程、风险缓解均合理。

## 门禁 3：计划评审

通过标准：

- 每个任务原子化。
- 每项任务有验证方式。
- 修改文件明确。
- 不确定问题已列出。

## 门禁 4：验证

通过标准：

- 构建通过。
- 测试数大于 0。
- passed == total。
- 分层边界通过。
- 高风险业务用例通过。

自动检查方式：

- `bash harness/scripts/verify/verify-template.sh`
- `bash harness/scripts/verify/check-layer-boundaries-template.sh`

## 门禁 5：AI 自审

通过标准：

- AI 已逐条对照 Spec 检查实现。
- AI 已列出修改文件、验证证据、残余风险。
- AI 已确认没有引入 Spec 外范围。
- AI 已检查是否需要更新 `context/`、脚手架、门禁或 ADR。

## 门禁 6：人工 Review

通过标准：

- 人工确认业务语义正确。
- 人工确认架构边界合理。
- 人工确认测试证据可信。
- 人工确认知识沉淀去向。

## 门禁 7：归档

通过标准：

- `acceptance.md` 已记录。
- `learnings.md` 已记录。
- `context/` 已更新。
- 必要 ADR 已补充。
- `notes.md` 中的知识已处理。
