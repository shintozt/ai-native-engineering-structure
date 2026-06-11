# SOP 目录

本目录保存项目可执行的操作手册。每份 SOP 用编号 + 名称命名，便于按阶段引用。

## 当前 SOP

| 编号 | 文件 | 触发时机 |
| --- | --- | --- |
| 01 | `01-新服务初始化SOP.md` | 复制母版后第一次执行；让一个空工程项目化到可创建 Track 的状态 |
| 02 | `02-domain-clarification-sop.md` | 用户选择先澄清或生成具体项目 domain 设计时；可选，不修改初始化强制流程 |
| 03 | `03-domain-special-verification-sop.md` | 项目准备开启 domain 功能正确性和性能专项验证时；可选，需要先设计测试内容 |

## 编号约定

- 编号按阶段顺序递增，不按重要性排序。
- 后续若新增需求开发 SOP 或归档 SOP，按 `02-`、`03-` 编号。
- 已有但不需独立成 SOP 的流程（如代码 Review、验证、归档）由 `harness/agents/` 下的角色定义承载，无须在本目录重复造一份 SOP。

## 维护规则

- SOP 内容只在本目录修改。`harness/agents/` 和 `harness/lifecycle/` 引用 SOP 时不复制正文。
- 新增 SOP 必须更新本 README 的"当前 SOP"表。
