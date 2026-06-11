# 运行日志分析手册

本文面向 AI Agent、开发和 SRE，说明如何阅读本服务的运行日志。复制母版后，必须用真实日志格式、字段和指标替换占位内容。

## 日志格式

生产运行时日志建议使用结构化输出，一行一条事件。每条日志只承载必要定位字段，跨模块分析应按字段串联，不要求单条日志包含完整上下文。

必填字段建议：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `logtime` | string | 日志时间 |
| `level` | string | `DEBUG` / `INFO` / `WARN` / `ERROR` / `FATAL` |
| `traceId` | string | 请求链路 id；无链路时填固定占位 |
| `threadName` | string | 逻辑线程名 |
| `component` | string | 稳定组件名 |
| `content` | string | 简短事件摘要 |

## Level 语义

| level | 影响范围 | 分析含义 |
| --- | --- | --- |
| DEBUG | 默认不输出的排查细节 | 只在人工开启 debug 时使用 |
| INFO | 正常生命周期和成功摘要 | 启动、关闭、请求成功摘要 |
| WARN | 单个请求、单条数据、局部容量或可恢复降级 | 用户级或局部失败 |
| ERROR | 组件级能力异常，影响一批请求或一类能力 | 外部依赖失败、组件不可用 |
| FATAL | 服务无法启动或必须退出 | 配置非法、关键资源不可用 |

## 组件命名

`component` 应使用稳定小写短名。复制母版后补充真实组件：

| component | 说明 |
| --- | --- |
| app | 应用生命周期 |
| api | 对外请求入口 |
| domain | 领域规则和状态推进 |
| adapter | 外部依赖适配 |
| observer | 日志、指标、追踪 |

## TraceId 串联

分析单个用户请求：

1. 先按 `traceId` 检索。
2. 再按 `component` 区分入口、domain、adapter 和 observer。
3. 如果请求触发外部回源，继续看同一 `traceId` 下的 adapter 日志。
4. 如果没有 traceId，结合时间、方法、业务主键和线程名缩小范围。

## 指标与日志联合排查

建议先用指标判断影响面，再用日志定位具体事件。

| 问题类型 | 先看指标 | 再看日志 |
| --- | --- | --- |
| 请求失败 | 请求总量、失败原因、延迟分布 | `component=api`、`level=WARN/ERROR` |
| 外部依赖异常 | dependency failure、调用耗时 | `component=adapter` |
| 队列积压 | queue depth、overflow total | `component=domain/app` |
| 性能退化 | latency histogram、处理耗时 | 同一 traceId 的阶段耗时 |
| 服务无法启动 | 进程状态、健康检查 | `level=FATAL` |

## AI Agent 使用建议

AI 分析生产问题时应先用指标确定影响面：哪个方法、组件、依赖或原因异常；再按日志的 `level` 和 `component` 缩小范围，最后按 `traceId` 串联上下文。需要更多业务上下文时，应结合 `context/domain/core-capability-design.md`、`context/architecture/implementation-module-map.md` 和对应 Track 文档阅读。
