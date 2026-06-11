# Domain 澄清 SOP

本 SOP 用于在新服务初始化后，先澄清 domain 层整体职责、能力域、数据主线和 app/domain 边界。它是可选流程；只有当当前项目缺少正式 domain 设计，或新增需求会改变 domain 总体边界时才执行。

## 触发场景

- 新服务初始化后，用户希望先定义 domain 设计，再进入具体需求编码。
- 已有设计让 app 层组合过多 domain helper，public API 面积过大。
- 新需求涉及核心领域能力，但 `context/domain/core-capability-design.md` 无法支撑。
- 需要导入其他项目的候选领域知识包。

## 执行方式

1. 确认当前无 active Track；如有，先 close 或 abort。
2. 运行 `python3 -B harness/scripts/lifecycle/track.py open domain-clarification`。
3. 只在 `proposal.md` 写清楚为什么要澄清 domain、期望结果和不做什么。
4. proposal 人工定稿后，运行 `track.py next-stage` 生成 spec。
5. spec 澄清能力域、运行场景、app/domain 边界、数据主线、外部端口和知识复用。
6. spec 人工定稿后，运行 `track.py next-stage` 生成 design。
7. design 输出正式 domain 能力设计草案，并明确写入位置。
8. design 人工定稿后，生成 tasks，把确认后的设计写入：
   - `context/domain/core-capability-design.md`
   - 必要时更新 `context/architecture/runtime-dataflow.md`
   - 必要时更新 `context/architecture/implementation-module-map.md`
   - 必要时更新 `context/domain/knowledge-packages/`
9. 验证、验收、沉淀后 close Track。

## 输出要求

- `context/domain/core-capability-design.md` 不再是占位。
- 能力域、数据主线、状态所有权、外部端口和错误降级规则清楚。
- app 层不需要按固定顺序组合多个 domain 内部步骤来完成一个业务用例。
- 相关 catalog 已更新。

## 常见错误

- 直接按目录名定义能力域，而不是按业务能力定义。
- proposal 阶段写入大段业务规则和 API 细节。
- 直接复制外部项目知识，没有经过 incoming / accepted / 正式写入流程。
- spec 修改后继续执行旧 design / tasks，没有重审。
