# Infra 模块脚手架

## 适用场景

真实数据库、消息队列、HTTP/gRPC、文件系统、第三方 SDK 客户端。

## 不适用场景

- 业务规则。
- DTO 到领域模型转换。

## 复制后必须替换

- 外部服务名称。
- 配置项。
- 超时和重试策略。
- 错误映射。

## 不允许变化

- 不允许被 `domain/` 直接依赖。
- 不允许吞掉错误。

## 最小结构

```text
src/infra/<dependency>/
  <dependency>_client.h
  <dependency>_client.cpp
tests/infra/
  test_<dependency>_client.cpp
```

## 验证方式

默认单测使用 fake server 或接口替身；真实外部依赖测试必须标记为集成测试。
