# 分层规则

## 基本规则

- 业务规则优先放在 `domain/`。
- `domain/` 不访问数据库、网络、文件系统、消息队列、系统时间。
- 外部能力先在 `ports/` 建接口，再由 `infra/` 实现。
- `adapter/` 不承载业务规则。任何业务判定都应在 `domain/`；adapter 唯一允许的判断是"如何把外部数据格式映射成领域对象"。
- `app/` 负责编排，不承载核心算法。
- `observer/` 只能观察，不改变业务状态。

## ports vs adapter 边界判定

`ports/` 和 `adapter/` 都靠近外部世界，但职责不同。下面三条规则用于判定一段代码应该归到哪里。

### 三层本质

| 层 | 是什么 | 懂什么 | 不懂什么 |
| --- | --- | --- | --- |
| port | 接口（abstract class / interface） | 领域语言：`loadOrder(orderId) -> OrderSnapshot` | 任何外部技术细节 |
| adapter | 实现某个 port 的具体类 | 翻译规则：Kafka byte[] 哪几个字段对应 Tick | SDK 实例化、连接管理、重试策略 |
| infra | 真实 SDK 的薄封装 | 协议原语：`Kafka.poll() -> raw_msg` | 业务对象、映射规则 |

### 判定规则 1：测试时 mock 什么

- 测 `app/` 用例 → mock port（用 in-memory fake 实现接口）。
- 测 `adapter/` → mock infra（如 mock KafkaClient）。
- 测 `domain/` → 不需要 mock。

如果一段代码不清楚测试时该 mock 什么，说明它在跨层。

### 判定规则 2：依赖方向

```text
domain  ←── ports（接口被 domain 引用）
              ↑
            adapter（实现 port，使用 infra）
              ↓
            infra（依赖外部 SDK）
```

port 只能被 `domain/` 和 `app/` 引用，不能被 `infra/` 引用。这是单向依赖的硬约束。

### 判定规则 3：领域语义浓度

- port 签名里不能出现 `topic`、`offset`、`key`、`message_id`、`http_status`、`connection` 这类外部技术名词。
- adapter 同时出现领域名词和技术名词（这是它的"翻译"职责）。
- infra 只出现技术名词。

### 三个最常见的边界穿越反例

1. **adapter 偷偷写业务规则** → 应挪到 `domain/`。  
   反例：`KafkaEventSubscriber` 内写"如果 price < bid 则方向是 SELL"。这是 `domain/TickClassifier` 的事。

2. **port 暴露技术细节** → 不是好 port。  
   反例：`interface EventSubscriber { subscribe(topic: string, partition: int) }`。应改为 `subscribe(channel: ChannelName)`，由 adapter 决定 channel 怎么映射到 topic / partition。

3. **infra 认识领域对象** → 层级错位。  
   反例：`KafkaClient.publishTickClassified(tick: TickClassified)`。infra 不应认识 `TickClassified`。

### 参考示例：消费 TickClassified 事件

```text
domain/
  tick_classified.h               # 领域对象

ports/
  event_subscriber.h              # interface { subscribe(handler); commit_watermark(); }
                                  # 完全不提 Kafka

adapter/kafka/
  tick_classified_decoder.h       # byte[] → TickClassified（纯翻译）
  kafka_event_subscriber.h        # implements EventSubscriber：
                                  #   用 infra/KafkaClient 拉 raw msg
                                  #   用 Decoder 翻译
                                  #   回调上层 handler(TickClassified)

infra/kafka/
  kafka_client.h                  # 薄包装：poll() / commit(offset) / close()
                                  # 完全不认识 TickClassified
```

## 代码审查重点

每条问题如果答"是"，按"修复方向"处理。

| 检查问题 | 修复方向 |
| --- | --- |
| 领域层是否被外部 SDK 类型污染？ | 抽接口到 `ports/`，由 `adapter/` 持有 SDK 类型 |
| 适配层是否偷偷写了业务规则？ | 把规则挪到 `domain/`，adapter 只做翻译 |
| 基础设施层是否绕过端口直接被领域使用？ | 在 `ports/` 加接口，由 `adapter/` 实现并经 wiring 注入 |
| 应用层是否变成巨型流程脚本？ | 按 `directory-blueprint.md#app-内部组织` 拆 use_cases / wiring / bootstrap |
| 测试是否需要真实外部服务才能证明行为？ | 改为通过 port 注入 fake；如必须真实，迁移到 `tests/integration/`（见 `harness/lifecycle/gates.md#门禁-4`） |

## 允许例外

例外必须写入 ADR 并经技术负责人 review：

- 性能原因导致端口抽象成本过高。
- 第三方 SDK 类型本身就是业务协议的一部分。
- 旧系统迁移期存在临时桥接层。

### ADR 必须包含

- 失效条件（什么时候这条例外不再适用）。
- 清理计划（谁、何时、用什么方式消除该例外）。
- `Status: approved-by: <人名>` 字段。
- 关联的 Track 或 PR 链接。

未经 review 的例外不通过设计评审门禁（见 `harness/lifecycle/gates.md#门禁-2`）。
