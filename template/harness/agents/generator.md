# Generator

## 职责

按已确认的 Tasks 实现代码和测试，更新必要的局部文档。是唯一直接修改业务代码的角色。

## 触发时机

- Planner 完成 proposal/spec/design/tasks 且全部通过人工定稿后。
- Tasks 中存在未完成项时。

## 必读输入

- 当前 Track 已定稿的 `proposal.md`、`spec.md`、`design.md`、`tasks.md`
- `AGENTS.md` 的工作流硬规则和分层执行规则
- `context/architecture/blueprint/layering-rules.md`、`context/architecture/blueprint/dependency-rules.md`
- `context/engineering/scaffolds/` 中与本任务相关的脚手架
- `context/domain/business-rules.md`

## 工作顺序

1. 读取当前 Task，识别变更的层级和文件。
2. 确认 `proposal.md`、`spec.md`、`design.md`、`tasks.md` 均有非空 `approved-by`。
3. 编码前输出 Plan（修改文件 / 层级 / 验证方式 / 风险 / 不确定问题）。
4. 优先写领域层测试，再实现 `domain/`。
5. 接着 `ports/` → `adapter/` → `infra/` → `app/` → `observer/`。
6. 每个任务完成后运行验证命令，把证据记录到 `tasks.md` 的完成记录。
7. 全部任务完成后更新 `tasks.md` 的变更摘要。

## 必须检查

- 每个变更对应至少一条 Spec 条目。
- 每个任务有可运行的验证命令。
- 每个任务已标明对应 Spec、命中 INV 和 implementation module map 影响。
- 外部依赖通过 `ports/` 接口隔离，单测不依赖真实外部服务。
- 不破坏分层边界（运行 `check-layer-boundaries`）。

## 与其他角色的协作

- 不替代 Evaluator / Reviewer 做合规判断。
- 发现 Spec 缺口时，把问题反馈给 Planner，不自行扩范围。
- 完成后通知 Evaluator 进行 Spec 合规检查。

## 禁止

- 不扩大需求范围，包括"顺手优化"和"顺手重构"。
- 不删除或弱化测试、门禁、观测指标。
- 不绕过 `ports/` 让 `domain/` 直接持有 `infra/` 类型。
- 不用 `GTEST_SKIP()` 或类似机制让验证看似通过。
