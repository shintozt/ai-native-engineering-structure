# Specs 目录

需求必须先进入 `specs/tracks/<需求名>/`，再进入编码。

## 复杂度分级

| 复杂度 | 适用场景 | 最小文件集 | 说明 |
| --- | --- | --- | --- |
| 微小 | 文案、注释、非行为性文档、小范围测试命名修正 | `tasks.md`、`acceptance.md`、`notes.md` | 不改业务行为，不触碰热路径 |
| 小 | 单点 bug、adapter/infra mock、小型观测指标、错误处理补齐 | `proposal.md`、`spec.md`、`tasks.md`、`acceptance.md`、`notes.md` | 可跳过完整 Design，但必须说明验证方式 |
| 中 | 新增模块、小型 app 编排、外部依赖适配、业务规则局部变化 | `proposal.md`、`spec.md`、`design.md`、`tasks.md`、`acceptance.md`、`notes.md` | 默认流程 |
| 大 | 核心业务规则、协议变更、缓存一致性、并发模型、数据正确性边界 | 完整 Track + ADR + 评审记录 | 必须工程主导，AI 只执行明确任务 |

## 模板

- `templates/proposal-template.md`
- `templates/spec-template.md`
- `templates/design-template.md`
- `templates/tasks-template.md`
- `templates/acceptance-template.md`
- `templates/notes-template.md`
- `templates/learnings-template.md`

## 模板使用时机

| 文件 | 何时启用 | 何时定稿 |
| --- | --- | --- |
| `proposal.md` | Track 启动第一时间填写 | 进入 Spec 前确认 |
| `spec.md` | Proposal 确认后填写 | 进入 Design 前确认（关闭所有 Blocking 问题） |
| `design.md` | Spec 确认后填写（中等及以上复杂度必填） | 进入 Tasks 前确认 |
| `tasks.md` | Design 确认后填写 | 编码前确认 |
| `notes.md` | Track 启动即维护 | 归档前由 Maintainer 处理 |
| `acceptance.md` | 所有任务完成、验证通过后填写 | 人工 Review 通过即定稿 |
| `learnings.md` | 归档前补充 | 从 `notes.md` 提取已验证经验，归档时定稿 |

完整 Track 内部规则见 `specs/tracks/README.md`。
