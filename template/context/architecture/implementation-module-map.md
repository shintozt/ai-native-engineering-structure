# 实现模块映射

本文记录当前实现文件与正式业务能力设计之间的映射。它是"当前实现快照"，不是目标架构设计，也不能替代 `context/domain/core-capability-design.md`。

复制母版后，首次生成代码目录时必须填充本文；后续如果业务源码、public 头文件、协议、构建入口或目录结构变化，必须更新本文，或在 Track task / acceptance 中说明不影响原因。

## 元数据

- status: draft
- owner:
- updated-at:
- source-track:

## 维护规则

需要更新本文的情况：

- 新增、删除或移动 `src/` / `include/` 下的业务模块。
- 新增、删除或修改 public 头文件。
- 修改 `api/`、`proto/` 等外部协议文件。
- 修改 `CMakeLists.txt`、构建入口或目录组织。
- domain 能力设计与当前实现产生偏差。

不需要更新本文的情况：

- 只修改内部函数实现，不改变模块职责或 public 面积。
- 只修改测试断言，不改变被测模块边界。
- 只修改文档，且不影响实现结构。

## 能力域到实现模块

| 能力域 ID | 能力域名称 | 主要 public 入口 | 主要实现文件 / 目录 | 测试文件 / 目录 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| CAP-001 |  |  |  |  | draft |

## 分层映射

| 层级 | 目录 / 文件 | 职责 | 不应依赖 |
| --- | --- | --- | --- |
| domain |  |  | infra / adapter 具体实现 |
| ports |  |  | infra 具体实现 |
| adapter |  |  | domain internal helper |
| infra |  |  | domain internal helper |
| app |  |  | infra 细节直接散落 |
| observer |  |  | 业务状态写入 |

## public API 面积

| public 类型 / 函数 | 所属能力域 | 调用方 | 为什么 public | 替代方案 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 与正式设计的偏差

| 偏差 ID | 正式设计 | 当前实现 | 风险 | 处理计划 |
| --- | --- | --- | --- | --- |
| DEV-001 |  |  |  |  |

## 最近更新记录

| 时间 | Track | 更新内容 | 更新人 |
| --- | --- | --- | --- |
|  |  |  |  |
