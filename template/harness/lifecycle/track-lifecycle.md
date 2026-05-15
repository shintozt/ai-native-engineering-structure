# Track 生命周期

本文件定义 Track 状态机、命令、`active-track.md` 格式，以及多 Track 互斥规则。

## 状态机

```text
        ┌──────────────────────────┐
        │   （无 active track）      │
        └────────────┬─────────────┘
                     │
              track.py open <name>
                     │
                     ▼
        ┌──────────────────────────┐
        │       active             │  ← 唯一可写状态
        │ (1 个 track 内多个 task)  │
        └────────────┬─────────────┘
                     │
                ┌────┴───────┐
                │            │
   track.py    track.py     track.py
   finish-task  close       close --abort
   (在 track 内推进)
                │            │
                ▼            ▼
        ┌─────────────┐ ┌─────────────┐
        │   closed    │ │  aborted    │
        │ (含完整归档) │ │ (含 aborted.md) │
        └─────────────┘ └─────────────┘
```

## 命令清单

| 命令 | 作用 | 关键检查 |
| --- | --- | --- |
| `track.py open <name>` | 创建新 track 并标记为 active | init-status 已完成 + 当前无 active track |
| `track.py finish-task [--task T1] [--message ...]` | 完成当前任务 | 验证通过 → commit + push → 更新 tasks.md 状态 |
| `track.py close` | 关闭当前 track | acceptance.md + learnings.md 非空 + 全部 task Done + 最终 verify 通过 |
| `track.py close --abort [--reason ...]` | 放弃当前 track | 跳过验收，写入 `aborted.md` |
| `track.py status` | 查看当前状态 | 显示 active track、当前任务、任务进度 |

## 互斥规则（硬约束）

- **同时仅允许 1 个 active track**。已有 active 时 `open` 会被阻断。
- **关闭后才能 open 下一个**。`close` 或 `close --abort` 都会释放锁。
- **不允许手动 mkdir `specs/tracks/<X>/`**。`harness_gate.py pre-edit` 会阻断非 active track 的编辑。

## active-track.md 格式

该文件位于 `harness/state/active-track.md`，是**本地状态**，已在 `.gitignore` 排除。多人协作时各自维护，不进 git。

由 `track.py open` 自动创建，格式如下：

```markdown
# Active Track

本文件是当前 active track 的本地指针，已在 `.gitignore` 中排除。
多人协作时各自维护，不共享。

## 元数据

- 状态：active
- Track 路径：specs/tracks/2026-05-14-user-profile-cache-port/
- Track slug：2026-05-14-user-profile-cache-port
- Base 分支：main
- 启动时间：2026-05-14T16:30:00
- 当前任务：T2

## 历史

- 2026-05-14T16:30:00 open
- 2026-05-14T17:15:00 finish T1
```

字段说明：

- `状态`：`active` / `empty`。`empty` 表示无 active track，可以 open。
- `Track 路径`：相对项目根的路径。
- `Track slug`：包含日期前缀的唯一标识。
- `Base 分支`：open track 前所在分支，close 后合并提示会使用它。
- `当前任务`：当前指向的 task id（如 `T1`），由 `finish-task` 自动推进。
- `历史`：每次 open / finish / close / abort 追加一行。

## Task 验证与提交

`finish-task` 严格按以下顺序执行：

1. 读 `active-track.md`，确认状态 = active。
2. 若 `--task` 指定，对照 `tasks.md`；否则取第一个未 Done 的 task。
3. 跑 `bash harness/scripts/verify/verify-template.sh`。
4. 跑 `bash harness/scripts/verify/check-layer-boundaries-template.sh`。
5. 任一失败 → **阻断 commit，保留工作区**。
6. 全通过后，先更新 `tasks.md` 中该 task 的 `状态` 为 `Done`。
7. 再提交本次代码和 `tasks.md` 状态变更：
   - `git add -A`
   - `git commit -m "feat(<slug>): <T-id> <task-name>"`
   - `git push -u origin HEAD`
8. 更新 `active-track.md` 的"当前任务"指向下一个未 Done 的 task。

## Commit Message 约定

格式：`feat(<track-slug>): <T-id> <task-name>`

示例：

```text
feat(2026-05-14-user-profile-cache-port): T1 抽离外部缓存端口
feat(2026-05-14-user-profile-cache-port): T2 实现内存 Fake
feat(2026-05-14-user-profile-cache-port): T3 重构用例注入接口
```

可用 `--message` 覆盖默认 task name 部分：

```bash
python3 -B harness/scripts/lifecycle/track.py finish-task --task T2 --message "内存 Fake + 边界测试"
# 生成：feat(<slug>): T2 内存 Fake + 边界测试
```

## 分支策略

`open` 默认 `git checkout -b track/<name>`。每个 track 一个独立分支，便于：

- 多 track 并行准备（虽然同时仅 1 个 active，但可以预留下一批分支）
- 失败时干净回滚（`git checkout <base-branch> && git branch -D track/<name>`）
- `close` 后选择性 merge 到 open 前的 base 分支

跳过分支：`track.py open <name> --no-branch`。

## 关闭后合并

`close` 命令本身**不 merge 到 main**，避免误操作。close 后会提示：

```text
可选下一步：git checkout <base-branch> && git merge --no-ff track/<name>
```

由人决定是否合并、什么时候合并。

## 与门禁的关系

`harness_gate.py pre-edit` 扩展了以下检查（详见脚本）：

- 编辑 `specs/tracks/<X>/` 时，X 必须等于 active track 路径；否则阻断。
- 无 active track 时编辑 `specs/tracks/` 下任何子目录都阻断；必须先 `track.py open`。
- 业务代码（`src/` 等）编辑仍受 spec.md 非空检查约束（既有行为）。

## 常见情况

| 情况 | 处理 |
| --- | --- |
| 想暂停当前 track 处理紧急 bug | 先 close 当前 track 或 close --abort，再 open 新 track |
| Track 跑到一半发现方向错 | `close --abort --reason "..."` 放弃，保留分支供事后回顾 |
| 验证失败但要提交 WIP | 不允许。本设计要求每个 commit 都通过验证；WIP 可以暂存（`git stash`）|
| 团队成员手动改了 active-track.md | 不要这样做；若必须，对齐"## 元数据"段格式 |

## 错误恢复

active-track.md 损坏或丢失：

- 文件不存在 → `track.py status` 显示"无 active track"
- 文件存在但格式错乱 → 删除文件，从无 active 状态重新 open

被中断的 finish-task：

- commit 已发生但 push 失败 → 手动 `git push -u origin HEAD`
- commit 未发生（验证失败）→ 工作区保留，修复后重跑 finish-task
- tasks.md 已标 Done 但 commit 未发生 → 罕见，需手动修正 tasks.md
