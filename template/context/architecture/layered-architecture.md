# 分层架构

> 本文是项目化产物，记录本服务**实际采用**的分层方案和项目化调整。
> **通用分层规则源**在 `context/architecture/blueprint/layering-rules.md` 和 `context/architecture/blueprint/dependency-rules.md`。如本文与 blueprint 出现冲突，以 blueprint 为准；本文只记录"对默认规则的项目化偏离及原因"。

## 默认分层

```text
domain -> ports -> adapter / infra -> app -> observer
```

## 原则

- 领域模型不认识外部 SDK。
- 外部依赖通过端口进入应用。
- 适配器做转换，基础设施做真实 I/O。
- 应用层组织用例，避免写复杂业务规则。

## 项目化调整

| 调整 | 原因 | 风险 | ADR |
| --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | 待填写 |
