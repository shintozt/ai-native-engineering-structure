# Domain 模块脚手架

## 适用场景

纯业务规则、实体、值对象、算法。

## 不适用场景

- 访问数据库、网络、文件系统、消息队列。
- 依赖外部 SDK 类型。

## 复制后必须替换

- 模块名。
- 领域术语。
- 业务规则。
- 测试用例。

## 允许变化

- 文件名。
- 领域对象数量。
- 测试 fixture。

## 不允许变化

- 引入外部 I/O。
- 把错误路径留给 app 层猜测。

## 最小结构

```text
src/domain/<module>/
  <entity>.h
  <entity>.cpp
tests/domain/<module>/
  test_<entity>.cpp
```

## 验证方式

```bash
# 复制后替换为真实测试命令，例如：
ctest --test-dir build --output-on-failure
```
