# Adapter 模块脚手架

## 适用场景

外部协议、DTO、消息、文件格式与领域模型之间的转换。

## 不适用场景

- 真实网络连接。
- 复杂业务规则。
- 持久化状态管理。

## 复制后必须替换

- 协议 / DTO 名称。
- 转换规则。
- 错误映射。
- fake/mock。

## 不允许变化

- 不允许直接依赖真实外部服务。
- 不允许让外部 SDK 类型穿透到 `domain/`。

## 最小结构

```text
src/adapter/<dependency>/
  <dependency>_adapter.h
  <dependency>_adapter.cpp
tests/adapter/
  test_<dependency>_adapter.cpp
```

## 验证方式

Adapter 单测必须使用 fake/mock 输入，不能依赖真实外部服务。
