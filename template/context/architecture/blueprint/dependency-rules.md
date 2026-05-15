# 依赖规则

## 默认依赖方向

```text
app/use_cases   ──> ports, domain, common
app/wiring      ──> app/use_cases, adapter, infra, ports, common  （唯一 include 具体实现的层）
app/bootstrap   ──> app/wiring, observer, common
adapter         ──> ports, infra, domain, common
infra           ──> 外部 SDK, common
ports           ──> domain, common
domain          ──> ports（DIP）, common
observer        ──> common
common          ──> 标准库 + 经允许的基础工具库
```

## 依赖倒置（DIP）

`domain` 可以 `#include` `ports/` 接口头文件，这是依赖倒置原则的体现：

- 传统方向：高层直接依赖低层（domain 直接 new RedisClient）—— 禁止。
- 倒置方向：高层依赖抽象（domain 持有 `ICacheReader` 接口引用，由 adapter 实现）—— 允许。

`domain → ports` 是必要依赖，**不算"domain 依赖外部世界"**。被禁止的是 `domain → adapter / infra`。

## Wiring / Composition Root

`app/wiring/` 是整个工程**唯一**可以 `#include` 具体 adapter 和 infra 类的地方。

职责：

- 实例化具体 adapter（如 `RedisCacheAdapter`）和 infra 客户端（如 `RedisClient`）。
- 把它们装配成 use_case 的构造参数。
- 不应该有单元测试（纯粘合代码）。

反例：

- `app/use_cases/sync_external_state.cpp` 中 `new RedisClient()` → 应由 wiring 装配后注入。
- `domain/some_service.cpp` 中 `#include "adapter/kafka/..."` → 永远禁止。

## 禁止依赖

- `domain` 依赖 `adapter`、`infra`、`app`、`observer`、外部 SDK。
- `ports` 依赖 `adapter`、`infra`、`app`、外部 SDK。
- `adapter` 绕过 `ports` 直接被 `domain` 引用。
- `infra` 依赖 `ports`、`domain`、`adapter`、`app`。
- `infra` 写业务规则。
- `observer` 影响业务决策（只观察，不改变状态）。
- `app/use_cases` 直接 `#include` 具体 adapter 或 infra（必须通过 wiring 注入）。

## 循环依赖

- 禁止模块之间的循环依赖。
- 如果 A 和 B 互相需要对方的概念，把共享类型提取到 `common/` 或 `domain/shared/`。
- 检查方式：`harness/scripts/verify/check-layer-boundaries-template.sh` 应包含循环依赖检测；工具暂未支持时通过 ADR 暂时豁免，并写明清理计划。

## 外部依赖原则

新增外部依赖前必须**在 `spec.md` 或 ADR 中显式回答**以下 5 个问题：

1. 为什么标准库或现有依赖不够。
2. 依赖是否进入热路径，性能影响如何。
3. 如何 mock 或 fake（必须有 hermetic 单测路径）。
4. 如何降级和观测（外部服务失败时的行为）。
5. 许可证、部署、版本升级风险是什么。

**未回答 5 个问题的引入提案不通过设计评审门禁**（见 `harness/lifecycle/gates.md#门禁-2`）。
