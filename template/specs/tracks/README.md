# Tracks 目录

每个需求创建一个子目录，**必须通过 `python3 -B harness/scripts/lifecycle/track.py open <name>` 创建**，不允许手动 `mkdir`：

```text
specs/tracks/<YYYY-MM-DD-需求名>/
  proposal.md
  notes.md
  spec.md
  design.md
  tasks.md
  acceptance.md
  learnings.md
```

`open` 默认只创建 `proposal.md` 和 `notes.md`。`spec.md`、`design.md`、`tasks.md` 必须在上一档人工定稿后，通过 `track.py next-stage` 顺序生成。`acceptance.md` / `learnings.md` 在全部 task Done 后生成。

## Track 状态机

| 状态 | 含义 | 触发条件 |
| --- | --- | --- |
| active | 进行中（**同时仅允许 1 个**） | `track.py open` |
| closed | 已归档（acceptance + learnings + 全部 task Done + 验证通过） | `track.py close` |
| aborted | 已放弃（保留分支和 `aborted.md`） | `track.py close --abort` |

状态机和命令见 `harness/lifecycle/track-lifecycle.md`；当前 active track 本地指针见 `harness/state/active-track.md`。

## 互斥规则

- 同时仅允许 1 个 active track。已有 active 时 `open` 会被 `harness_gate.py` 阻断。
- 当 active track 存在时，`harness_gate.py pre-edit` 阻断对其他 track 目录的编辑。
- 关闭当前 track 后才能 open 下一个。

## 模板使用时机

| 文件 | 何时启用 | 何时定稿 |
| --- | --- | --- |
| `proposal.md` | Track 启动第一时间填写 | 进入 Spec 前确认 |
| `spec.md` | Proposal 确认后填写 | 进入 Design 前确认（关闭所有 Blocking 问题） |
| `design.md` | Spec 确认后填写（中等及以上复杂度必填） | 进入 Tasks 前确认 |
| `tasks.md` | Design 确认后填写 | 编码前确认 |
| `notes.md` | Track 启动即维护 | 归档前由 Maintainer 处理（提取知识、关闭遗留问题） |
| `acceptance.md` | 所有任务完成、验证通过后填写 | 人工 Review 通过即定稿 |
| `learnings.md` | 归档前补充 | 从 `notes.md` 提取已验证经验，归档时定稿 |

复杂度分级和最小文件集见 `specs/README.md`。

## 任务推进

每个 task 完成必须通过：

```bash
python3 -B harness/scripts/lifecycle/track.py finish-task [--task T1] [--message "..."]
```

该命令会自动：
1. 检查 `tasks.md` 已定稿。
2. 检查 implementation module map 影响是否已处理。
3. 跑 `verify-template.sh` 和 `check-layer-boundaries-template.sh`。
4. 通过后更新 `tasks.md` 中该 task 的状态为 `Done`。
5. 推进 active-track.md 的当前任务指针。
6. 如果是最后一个 task，自动铺出 `acceptance.md` / `learnings.md`。

**验证失败时阻断状态推进，工作区保留供修复**。

默认不执行 git commit / push。只有人工确认后，才允许运行：

```bash
python3 -B harness/scripts/lifecycle/track.py finish-task --task T1 --commit --confirmed-by <人名>
```

## 归档要求

- `notes.md` 中的待沉淀知识必须由 Maintainer 处理：升级为 `context/learnings/TK-xxx.md` 或确认无需沉淀。
- 引用过的知识条目必须在对应 `TK-xxx.md` 元数据中更新 `last_referenced` 字段；归档时由 Maintainer 按 `harness/agents/maintainer.md` 中的归档检查清单核对。
- 全部 task Done + acceptance + learnings 完成后，运行 `track.py close`。
