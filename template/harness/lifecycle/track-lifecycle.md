# Track 生命周期

本文件定义 Track 状态机、命令、`active-track.md` 格式，以及多 Track 互斥规则。

## 状态机

```text
（无 active track）
  |
  | track.py open <name>
  v
active track
  |
  | proposal.md 人工定稿
  | track.py next-stage
  v
spec.md
  |
  | spec.md 人工定稿
  | track.py next-stage
  v
design.md
  |
  | design.md 人工定稿
  | track.py next-stage
  v
tasks.md
  |
  | tasks.md 人工定稿
  | 编码 + finish-task 循环
  v
acceptance.md / learnings.md
  |
  | acceptance.md 人工定稿
  | track.py close
  v
closed

任意阶段发现上游问题：
track.py revise-stage <stage> --confirmed-by <人名>
  -> 清空该阶段及下游定稿戳
  -> 从该阶段重新 review
```

## 命令清单

| 命令 | 作用 | 关键检查 |
| --- | --- | --- |
| `track.py open <name>` | 创建新 track 并标记为 active；默认铺 `proposal.md` 和 `notes.md` | init-status 已完成 + 当前无 active track |
| `track.py next-stage` | 铺出下一档文档 | 上一档已有非空 `approved-by`；archive 档要求全部 task Done |
| `track.py revise-stage <stage> --confirmed-by <人名>` | 重审某档文档 | 清空该档及下游定稿戳；正文保留为草稿 |
| `track.py finish-task [--task T1] [--message ...]` | 完成当前任务 | tasks 已定稿 + implementation map 检查 + 验证通过 → 更新 tasks.md 状态；默认不提交 git |
| `track.py finish-task --task T1 --commit --confirmed-by <人名>` | 人工确认后提交当前任务 | 在 finish-task 通过后执行 `git add -A`、`git commit`、`git push` |
| `track.py close` | 关闭当前 track | acceptance 已人工定稿 + learnings 非空 + 全部 task Done + implementation map 检查 + 最终 verify 通过 |
| `track.py close --abort [--reason ...]` | 放弃当前 track | 跳过验收，写入 `aborted.md` |
| `track.py knowledge-status [--track <slug>]` | 只读扫描待沉淀知识 | 输出 learnings 中疑似 pending 条目，不修改状态 |
| `track.py pre-merge-check` | 合并 / push / 删除分支前检查 | 无 active track 才通过 |
| `track.py status` | 查看当前状态 | 显示 active track、阶段状态、当前任务和任务进度 |

## 阶段定稿规则

- `open` 默认只创建 `proposal.md` 和 `notes.md`，不创建 spec/design/tasks。
- 每一档文档必须由人工 review 后填写：
  - `approved-by: <人名>`
  - `approved-at: <时间>`
- `next-stage` 只在上一档已定稿时铺出下一档。
- `proposal -> spec -> design -> tasks -> coding` 不能跳级。
- 已定稿文档不允许直接修改；需要修改时必须先运行 `revise-stage`。
- `revise-stage` 会清空目标档及下游档位的定稿戳，防止下游文档继续假装有效。

## 互斥规则

- 同时仅允许 1 个 active track。
- 关闭当前 track（`close` 或 `close --abort`）后才能 open 下一个。
- 不允许手动 `mkdir specs/tracks/<X>/`；必须通过 `track.py open <name>`。
- 编辑 `specs/tracks/<X>/` 时，X 必须等于 active track。

## active-track.md 格式

该文件位于 `harness/state/active-track.md`，是本地状态，已在 `.gitignore` 排除。多人协作时各自维护，不进 git。

```markdown
# Active Track

## 元数据

- 状态：active
- Track 路径：specs/tracks/2026-05-14-user-profile-cache-port/
- Track slug：2026-05-14-user-profile-cache-port
- Base 分支：main
- 启动时间：2026-05-14T16:30:00
- 当前任务：T2

## 历史

- 2026-05-14T16:30:00 open
- 2026-05-14T17:15:00 next-stage spec
- 2026-05-14T18:20:00 finish T1
```

## Task 验证与提交

`finish-task` 默认只做验证与任务状态推进，不执行 git commit / push。严格按以下顺序执行：

1. 读 `active-track.md`，确认状态 = active。
2. 确认 `tasks.md` 已有非空 `approved-by`。
3. 若 `--task` 指定，对照 `tasks.md`；否则取第一个未 Done 的 task。
4. 检查当前工作区结构影响文件变更是否已更新 `context/architecture/implementation-module-map.md`，或在当前 task 写明不影响原因。
5. 跑 `bash harness/scripts/verify/verify-template.sh`。
6. 跑 `bash harness/scripts/verify/check-layer-boundaries-template.sh`。
7. 任一失败 -> 阻断状态推进与 git 操作，保留工作区。
8. 全通过后，更新 `tasks.md` 中该 task 的 `状态` 为 `Done`。
9. 更新 `active-track.md` 的"当前任务"指向下一个未 Done 的 task。
10. 如果已是最后一个 task，自动铺出 `acceptance.md` / `learnings.md`。
11. 输出工作区摘要，等待人工确认是否提交。

只有显式传入 `--commit --confirmed-by <人名>` 时，才允许提交：

```bash
python3 -B harness/scripts/lifecycle/track.py finish-task --task T1 --commit --confirmed-by shentuchentao
```

## implementation module map 影响判断

`finish-task` 使用当前工作区 diff 判断结构影响文件；`close` 使用当前分支相对 base 分支的 diff 作为最终兜底。

结构影响文件包括：

- `src/`
- `include/`
- `api/`
- `proto/`
- `cmake/`
- `CMakeLists.txt` 等构建入口

命中后必须满足以下任一条件：

- 已修改 `context/architecture/implementation-module-map.md`。
- 当前 task 或 acceptance 中写明 `implementation module map 影响：不影响`，并说明原因。

## 合并前检查

`git merge` / `git push` / 删除本地或远端分支前，必须先运行：

```bash
python3 -B harness/scripts/lifecycle/track.py pre-merge-check
```

通过标准：

- 当前无 active track；或 active-track.md 状态为 `empty`。
- 如果存在 active track，必须先运行 `track.py close` 或 `track.py close --abort`。

## 与门禁的关系

`harness_gate.py pre-edit` 会做以下检查：

- 新服务初始化未完成时，不能创建需求 Track 或修改业务代码。
- 编辑 `specs/tracks/<X>/` 时，X 必须等于 active track。
- 编辑 `spec.md` 前必须先定稿 `proposal.md`。
- 编辑 `design.md` 前必须先定稿 `spec.md`。
- 编辑 `tasks.md` 前必须先定稿 `design.md`。
- 编辑业务代码前必须定稿 `proposal.md`、`spec.md`、`design.md`、`tasks.md`。
- 直接修改已定稿阶段文档会被阻断；必须先运行 `revise-stage`。

## 常见情况

| 情况 | 处理 |
| --- | --- |
| 想暂停当前 track 处理紧急需求 | 先 close 当前 track 或 close --abort，再 open 新 track |
| Track 跑到一半发现方向错 | `close --abort --reason "..."` 放弃，保留分支供事后回顾 |
| 已定稿 spec 需要改 | `track.py revise-stage spec --confirmed-by <人名>`，再从 spec 重新 review |
| 验证失败但想提交 WIP | 不允许。WIP 可本地保留或人工决定其它处理方式 |
| 需要兼容旧流程一次性铺文档 | `track.py open <name> --legacy-all`，仅迁移旧项目时使用 |

## 错误恢复

active-track.md 损坏或丢失：

- 文件不存在 -> `track.py status` 显示"无 active track"。
- 文件存在但格式错乱 -> 人工检查后删除文件，从无 active 状态重新 open。

被中断的 finish-task：

- 验证失败 -> 工作区保留，修复后重跑 finish-task。
- tasks.md 已标 Done 但未提交 -> 这是允许状态；人工确认后再决定是否 commit。
- commit 成功但 push 失败 -> 手动 `git push -u origin HEAD` 或检查 remote 配置。
