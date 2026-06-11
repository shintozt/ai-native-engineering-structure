# Tasks：需求名称

> 本档是 Track 的"分步实现"。design 必须先有 `approved-by` 才允许编辑本档。tasks 没有 `approved-by` 之前禁止 Generator 编码。

## 定稿戳

- approved-by:
- approved-at:

## 执行状态机

状态只能是：Todo / Doing / Done。

## 任务列表

### Task 1：任务名称

- 目标：
- 依赖：
- 状态：Todo
- 修改文件：
- 对应 Spec：
- 命中 INV：
- implementation module map 影响：（需更新 / 不影响。若不影响，写明原因；纯文档任务也要写）
- public API 面积确认：（新增 public 类型数量、调用方、是否存在聚合入口；无新增 public 类型写"无"）
- 关键接口骨架（<= 20 行，新公开类型必填）：

```text
（贴 <= 20 行接口骨架；纯重构 / 纯文档可写"无"并说明原因）
```

- 关键测试用例清单（非 trivial 任务至少 3 条边界场景）：
  - 测试 1：
  - 测试 2：
  - 测试 3：
- 验证方式：
- 完成证据：（task 完成后补，列出测试输出 / 验证命令 / 人工确认后的 commit 引用）

### Task 2：任务名称

- 目标：
- 依赖：
- 状态：Todo
- 修改文件：
- 对应 Spec：
- 命中 INV：
- implementation module map 影响：
- public API 面积确认：
- 关键接口骨架（<= 20 行，新公开类型必填）：

```text
```

- 关键测试用例清单：
  - 测试 1：
  - 测试 2：
  - 测试 3：
- 验证方式：
- 完成证据：

## 变更摘要

- 总文件数：
- 关键变更：
- 测试结果：
- Spec-Plan 偏差：
- 遗留问题：

## 知识引用

| 知识 ID | 标题 | 使用位置 |
| --- | --- | --- |

## 定稿要求

- [ ] 每个 Task 都标了"对应 Spec"和"命中 INV"。
- [ ] 每个 Task 都标了 implementation module map 影响；结构影响文件变更要更新 map 或说明不影响原因。
- [ ] 每个新增 public 类型都说明了调用方和是否需要聚合入口。
- [ ] 每个含新公开类型的 Task 都给出非占位的接口骨架。
- [ ] 每个非 trivial Task 至少有 3 条边界测试用例。
- [ ] 每个 Task 给出可运行的验证方式。
- 全部勾选后，在"定稿戳"补 `approved-by` / `approved-at`，再让 Generator 开始编码。
