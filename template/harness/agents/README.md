# Agent 分工

AI Agent 必须分工明确。做事的 Agent 和评判的 Agent 分离。

| 分工 | 职责 | 产物 | 禁止事项 |
| --- | --- | --- | --- |
| Planner | 澄清需求，逐阶段生成 Proposal / Spec / Design / Tasks | 需求契约和任务计划 | 不直接改代码，不代替人工定稿 |
| Generator | 按已确认 Tasks 实现代码和测试 | 源码、测试、局部文档 | 不扩大需求范围 |
| Evaluator | 检查实现是否逐条满足 Spec | Spec 合规检查报告 | 不提出未确认的新需求 |
| Reviewer | 从缺陷、风险、架构、测试角度 Review | Review findings | 不以风格偏好替代证据 |
| Maintainer | 归档 Track、更新 context、ADR、脚手架 | 知识沉淀和索引更新 | 不把未经验证的知识升级为 proven |
