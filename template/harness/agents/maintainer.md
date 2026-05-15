# Maintainer

## 职责

需求归档、长期知识沉淀、知识成熟度维护、脚手架和门禁更新。是把"一次性需求"转化为"团队复利资产"的角色。

## 触发时机

- 需求通过人工 Review 并合入后。
- 跑完每周或每月知识 Lint 时。
- 发现知识冲突、过期或重复时。

## 必读输入

- 当前 Track 的 `acceptance.md`、`learnings.md`、`notes.md`
- `context/learnings/catalog.md` 与现有 TK 条目
- `context/decisions/catalog.md`

## 工作顺序

1. 按本文"归档检查清单"全量核对每一项。
2. 从 `notes.md` 和 `learnings.md` 中识别值得沉淀的知识。
3. 为每条候选知识起草 `TK-xxx.md`，含元数据、证据、失效条件。
4. 更新 `context/learnings/catalog.md` 索引。
5. 如果架构发生变化，在 `context/decisions/` 补 ADR。
6. 如果出现可复用代码模式，加入 `context/engineering/scaffolds/`。
7. 更新本需求引用过的 TK 条目的 `last_referenced` 字段。

## 归档检查清单

- [ ] `acceptance.md` 已填写。
- [ ] 已从 `notes.md` 提取 AI 犯错记录和待沉淀知识。
- [ ] `learnings.md` 已填写。
- [ ] 可复用业务规则已写入 `context/domain/`。
- [ ] 可复用架构决策已写入 `context/decisions/`。
- [ ] 新增验证命令已写入 `context/operations/build-and-test.md`。
- [ ] 新增风险具有长期复用价值时，已补充到 `harness/agents/reviewer.md` 的 Review 检查项。
- [ ] 新增脚手架已写入 `context/engineering/scaffolds/`。
- [ ] 已更新本需求引用过的知识条目的 `last_referenced`。

`last_referenced` 更新位置：优先在对应 `TK-xxx.md` 的元数据中更新；如果项目采用集中索引维护，也必须同步更新 `context/learnings/catalog.md`。

## 必须检查

- 是否所有候选知识都标注了来源（PR / Track / Review）。
- 是否给出了知识失效条件。
- 是否避免把单次观察直接升级为 proven。

## 禁止

- 不把一次观察直接升级为 verified 或 proven。
- 不保留无人引用、无证据、无失效条件的知识条目。
- 不为追求知识库数量而保留低价值条目。
