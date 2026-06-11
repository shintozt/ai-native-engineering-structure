# Context 读取地图

本文件是 AI 进入工程后的上下文调度表。它不解释 `context/` 的设计思想，设计思想见 `context/README.md`；它只回答一个问题：当前工作场景下，AI 应该先读哪些上下文，发现缺口后写回哪里。

## 初始化新服务时必读

按顺序建立上下文，不跳层：

1. `business/business-map.md`
2. `domain/ubiquitous-language.md`
3. `domain/business-rules.md`
4. `domain/core-capability-design.md`
5. `architecture/layered-architecture.md`
6. `architecture/runtime-dataflow.md`
7. `architecture/implementation-module-map.md`
8. `architecture/blueprint/directory-blueprint.md`
9. `architecture/blueprint/layering-rules.md`
10. `architecture/blueprint/dependency-rules.md`
11. `architecture/blueprint/class-design-rules.md`
12. `engineering/README.md`
13. `engineering/scaffolds/README.md`
14. `operations/build-and-test.md`
15. `operations/cpp-coding-style.md`
16. `operations/observability.md`

初始化结束前，以上文件必须替换占位内容，并同步更新相关 `catalog.md`。

## 开发新需求前必读

每个 Track 进入 Spec / Design 前，至少读取：

1. `business/business-map.md`
2. `domain/ubiquitous-language.md`
3. `domain/business-rules.md`
4. `domain/core-capability-design.md`
5. `architecture/layered-architecture.md`
6. `architecture/runtime-dataflow.md`
7. `architecture/implementation-module-map.md`
8. `architecture/blueprint/layering-rules.md`
9. `architecture/blueprint/dependency-rules.md`
10. `architecture/blueprint/class-design-rules.md`
11. `operations/build-and-test.md`
12. `operations/cpp-coding-style.md`

如果需求涉及已有知识、历史决策或代码脚手架，再按触发条件补读对应目录。

## 触发条件读取

| 触发条件 | 必读上下文 | 写回位置 |
| --- | --- | --- |
| 修改业务范围、用户、上下游 | `business/business-map.md` | `business/business-map.md`、`business/catalog.md` |
| 修改领域术语或核心规则 | `domain/ubiquitous-language.md`、`domain/business-rules.md` | `domain/`、`domain/catalog.md` |
| 修改 domain 能力域、数据主线、public 入口 | `domain/core-capability-design.md`、`architecture/blueprint/domain-capability-design-rules.md` | `domain/core-capability-design.md`、`domain/catalog.md` |
| 修改分层、依赖方向、目录结构 | `architecture/layered-architecture.md`、`architecture/blueprint/`、`architecture/implementation-module-map.md` | `architecture/`、`architecture/catalog.md` |
| 新增 public 类型或类拆分 | `architecture/blueprint/class-design-rules.md`、`architecture/implementation-module-map.md` | `architecture/implementation-module-map.md`、当前 Track `design.md` |
| 引入外部依赖或 SDK | `architecture/blueprint/dependency-rules.md`、`decisions/catalog.md` | `decisions/ADR-xxx.md`、`architecture/catalog.md` |
| 需要复制代码模式或模块骨架 | `engineering/scaffolds/README.md`、相关 scaffold | `engineering/scaffolds/`、`engineering/catalog.md` |
| 修改构建、测试、格式化、CI | `operations/build-and-test.md`、`operations/cpp-coding-style.md` | `operations/`、`operations/catalog.md` |
| 修改日志、指标、健康检查 | `operations/observability.md`、`operations/log-analysis-guide.md` | `operations/observability.md`、`operations/log-analysis-guide.md`、`operations/catalog.md` |
| 发现性能风险或做性能专项 | `operations/performance-risk-analysis.md` | `operations/performance-risk-analysis.md`、`operations/catalog.md` |
| 出现重要方案取舍 | `decisions/catalog.md` | `decisions/ADR-xxx.md` |
| 产生可复用经验或 AI 犯错记录 | `learnings/README.md`、`learnings/catalog.md` | `learnings/TK-xxx.md`、`learnings/catalog.md` |

## Catalog 入口

| 目录 | Catalog | 用途 |
| --- | --- | --- |
| `business/` | `business/catalog.md` | 业务上下文索引 |
| `domain/` | `domain/catalog.md` | 领域规则索引 |
| `architecture/` | `architecture/catalog.md` | 架构和蓝图索引 |
| `engineering/` | `engineering/catalog.md` | 脚手架和实现模式索引 |
| `operations/` | `operations/catalog.md` | 构建、验证、观测索引 |
| `decisions/` | `decisions/catalog.md` | ADR 索引 |
| `learnings/` | `learnings/catalog.md` | TK 知识条目索引 |

## 写回规则

- 改了长期上下文，必须同步更新对应 `catalog.md`。
- 新增 ADR，必须更新 `decisions/catalog.md`。
- 新增 TK 知识条目，必须更新 `learnings/catalog.md`。
- Track 中引用过 TK 条目，归档时必须更新该条目的 `last_referenced`。
- 只属于一次性讨论的问题，不写入 `context/`；先放当前 Track 的 `notes.md`。
- 无证据、无适用场景、无失效条件的内容，不升级为长期知识。
