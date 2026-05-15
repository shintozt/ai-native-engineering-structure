# 工程目录蓝图

## 推荐代码目录

```text
src/
  domain/
  ports/
  adapter/
  infra/
  app/
    use_cases/    # 业务用例（注入 port 接口）
    wiring/       # DI 装配（唯一 include 具体实现）
    bootstrap/    # 入口、配置、生命周期
  observer/
  common/
tests/
  unit/{domain,ports,adapter,infra,app,observer,common}/
  integration/    # 接真实 infra 的集成测
  e2e/            # 端到端测试
```

## 各层职责

| 目录 | 职责 | 允许依赖 |
| --- | --- | --- |
| `domain/` | 纯业务模型、规则、算法 | `ports/`（DIP）、`common/`、标准库 |
| `ports/` | 领域需要的外部能力接口 | `domain/`、`common/` |
| `adapter/` | 协议、DTO、消息、文件与领域模型转换 | `domain/`、`ports/`、`infra/`、`common/` |
| `infra/` | 真实外部依赖客户端和 SDK 封装 | 外部 SDK、`common/` |
| `app/use_cases/` | 业务用例编排 | `domain/`、`ports/`、`common/` |
| `app/wiring/` | DI 装配（唯一 include 具体实现） | `app/use_cases/`、`adapter/`、`infra/`、`ports/`、`common/` |
| `app/bootstrap/` | 入口、配置、生命周期 | `app/wiring/`、`observer/`、`common/` |
| `observer/` | 日志、指标、debug、health | `common/`；通过 app 主动推送（如 metrics 注册）获取数据，不直接 `#include` app 内部类 |
| `common/` | 基础类型、配置、通用工具 | 标准库 + 经允许的基础工具库（见 `dependency-rules.md#外部依赖原则`） |

## app 内部组织

`app/` 是唯一可同时引用其他层的"枢纽"。为避免变成巨型脚本，按职责拆分。

| 子目录 | 职责 | 测试 |
| --- | --- | --- |
| `use_cases/` | 业务用例编排，构造时注入 port 接口 | 单测注入 fake，独立可测 |
| `wiring/` | 实例化具体 adapter / infra，装配 use_case | 不测（纯粘合代码） |
| `bootstrap/` | main、配置加载、信号处理、shutdown hook | 集成测或 e2e |

### 何时三分，何时合并

| 信号 | 拆 `wiring/` | 拆 `bootstrap/` |
| --- | --- | --- |
| 用例 ≥ 3 个 | ✅ | — |
| 外部依赖 ≥ 2 种 | ✅ | — |
| 多个入口（gRPC + HTTP / batch + online） | — | ✅ |
| 复杂启动顺序（健康检查、warmup、迁移） | — | ✅ |
| 都不满足 | 合并到 `app/main.cpp` | 合并到 `app/main.cpp` |

**最小可接受变体**（小服务）：

```text
src/app/
  use_cases/
  main.cpp        # wiring + bootstrap 合并
```

## tests/ 分层

| 目录 | 范围 | 依赖 |
| --- | --- | --- |
| `tests/unit/` | 单层单测，按 src 镜像 | 全部 mock/fake |
| `tests/integration/` | 多层联调 | 真实 adapter/infra 或 testcontainer |
| `tests/e2e/` | 端到端，从入口到出口 | 真实环境或完整 docker-compose |

**单测必须 hermetic**（不依赖真实外部服务）。如果一个测试无法 hermetic，应迁移到 `integration/` 或 `e2e/`。

## 文件命名约定

固化以下约定，避免同仓库内不一致。选定的约定写入 `context/operations/build-and-test.md`。

| 类型 | 约定 | 示例 |
| --- | --- | --- |
| Port 接口 | `i_<name>.h` 或 `<name>_port.h`（项目内选一种） | `i_event_subscriber.h` |
| Adapter 实现 | `<source>_<name>_adapter.h` | `kafka_event_subscriber.h` |
| Infra 客户端 | `<sdk>_client.h` | `kafka_client.h` |
| Use case | `<verb>_<noun>_use_case.h` 或 `<noun>_<verb>.h` | `sync_external_state_use_case.h` |
| 单元测试 | `test_<name>.cpp` 或 `<name>_test.cpp`（项目内选一种） | `test_kline_policy.cpp` |
| 集成测试 | `it_<scenario>.cpp` | `it_external_cache_sync.cpp` |

## 第一批 README 文件

每个 `src/` 子目录建议有一份 `README.md`，只写：

- 本层职责（一句话）
- 允许依赖
- 禁止事项

不写长篇业务手册。
