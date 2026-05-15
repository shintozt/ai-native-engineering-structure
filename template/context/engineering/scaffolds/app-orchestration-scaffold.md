# App 编排脚手架

## 适用场景

把领域规则、端口、适配器、基础设施组合为一个用例。

## 不适用场景

- 写核心业务算法。
- 直接解析外部协议。

## 复制后必须替换

- 用例名称。
- 输入输出。
- 依赖端口。
- 异常流程。

## 不允许变化

- 不允许把 app 写成巨型脚本。
- 不允许绕过端口直接访问外部 SDK。

## 最小结构

```text
src/app/<use_case>/
  <use_case>_service.h
  <use_case>_service.cpp
tests/app/
  test_<use_case>_service.cpp
```
