# Domain 设计生成规则

本文件约束 AI 在生成具体项目 domain 设计前应如何澄清、评审和沉淀。它是跨项目方法论，不描述任何项目的固定业务模块。

## 适用场景

以下场景建议先执行本规则，再生成具体 domain 设计：

- 项目初始化后，用户希望先讨论 domain 层的整体职责。
- 已有 domain 代码出现多个能力互相独立、app 层组合负担过重、public helper 过多等问题。
- 后续需求需要新增核心领域能力，但现有上下文没有说明能力域、数据主线和 app/domain 边界。
- 目标项目准备导入其他项目提炼出的可迁移领域知识包。

不适用场景：

- 只修改单个已确认规则的文案或测试。
- 已有明确 context 能覆盖本次需求，且不涉及 domain 总体边界变化。
- 用户明确要求跳过 domain 澄清，并接受后续另开 Track 修正设计风险。

## 总原则

1. 先澄清业务能力，再讨论类、文件和目录。
2. 先覆盖完整运行场景，再讨论局部实现步骤。
3. 先明确 app/domain 边界，再定义 domain public 入口。
4. 外部可复用知识只能作为候选输入，不能直接变成目标项目规则。
5. 具体 domain 设计必须经过 Track 生命周期和人工确认。

## Spec 澄清清单

生成具体 domain 设计前，spec 至少要澄清以下问题。

### 能力域

- 项目需要哪些主要业务能力支撑完整运行。
- 每个能力域对用户或业务流程提供什么稳定能力。
- 哪些只是内部技术步骤，不能提升为同级主模块。
- 哪些能力需要跨实时、历史、预热、查询等场景复用。

### 运行场景

- 外部请求如何进入 domain。
- 历史、恢复或预热路径如何恢复或构造 domain 状态。
- 查询路径如何读取、拼接或投影 domain 数据。
- 换日、恢复、回放、补齐、重试等生命周期场景是否存在。

### app/domain 边界

- app 层只负责接入、路由、生命周期、端口调用和简单编排。
- domain 层负责业务规则、状态推进、数据主线和派生规则。
- 若 app 必须按固定顺序组合多个 domain helper，说明 domain public 入口过细，需要重新设计聚合入口。

### 数据主线

- 输入领域对象是什么。
- 规范事实层是什么。
- 派生结果是什么。
- 关键状态存在于哪个 context。
- 哪些规则会改变正式领域状态，哪些只是查询视图或候选材料。

### 外部依赖

- 外部协议、数据库、缓存、消息队列、系统时间等能力是否需要 ports 隔离。
- domain 是否只依赖纯值对象和端口抽象。
- 是否存在直接把 infra 细节写进 domain 的风险。

## Design 输出要求

| 内容 | 要求 |
| --- | --- |
| 能力域总览 | 用业务能力描述主模块，而不是目录或 helper 名称 |
| 模块关系图 | 能看出主能力、内部能力、调用方向、app 边界 |
| 数据主线 | 能说明输入、规范事实层、派生输出、状态位置 |
| public 入口 | 说明调用方、业务语义、为什么不更粗或更细 |
| 上下文状态 | 说明状态所有者、生命周期和重建方式 |
| 知识复用处理 | 说明 incoming 处理结果和 outgoing 是否需要提炼 |
| 重审规则 | 说明靠前文档变更后下游确认状态如何处理 |

domain design 确认后，与 architecture 文档的职责关系如下：

| 文档 | 职责 |
| --- | --- |
| `context/domain/core-capability-design.md` | 正式 domain 能力设计 |
| `context/architecture/layered-architecture.md` | 稳定分层和依赖规则 |
| `context/architecture/runtime-dataflow.md` | 能力级运行数据流 |
| `context/architecture/implementation-module-map.md` | 当前实现快照和与正式能力域的偏差 |

## 靠前文档修改后的重审规则

若 proposal、spec 或 design 被修改，且下游文档已经生成或确认，则必须重审。

| 修改位置 | 必须处理 |
| --- | --- |
| proposal | 清空或标记 spec、design、tasks、acceptance、learnings 的确认状态 |
| spec | 清空或标记 design、tasks、acceptance、learnings 的确认状态 |
| design | 清空或标记 tasks、acceptance、learnings 的确认状态 |
| tasks | 不得继续执行旧任务；需要重新确认 tasks |

推荐使用 `track.py revise-stage <stage> --confirmed-by <人名>` 完成状态清理。

## 可迁移领域知识包

领域知识跨项目复用必须经过候选知识包机制。

### incoming

incoming 表示外部项目导入、等待当前项目审核的候选知识。

- candidate：刚导入，未审核。
- reviewed：已阅读并初步评估。
- accepted：目标项目 Track 已确认可裁剪采用。
- rejected：不适配目标项目。

accepted 也不自动生效。只有裁剪后写入目标项目正式 context，才成为目标项目规则。

### outgoing

outgoing 表示本项目准备给其他项目参考的候选知识。

允许生成 outgoing 的时机：

- domain 澄清 Track 关闭后，从已确认的正式 context、acceptance、learnings 中提炼。
- 业务 Track 关闭后，learnings 中出现可迁移领域模型、能力域、数据主线或边界规则。
- 用户明确要求导出可复用领域知识。

outgoing 不是当前项目新增正式规则。其他项目使用 outgoing 时，必须先把它作为 incoming 导入，并重新审核、裁剪。
