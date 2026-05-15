# Harness 目录

本目录保存工程控制系统。根目录只保留本导航文件，具体规则和工具按职责放入子目录。

工具接入配置位于工程根目录：

- `.claude/settings.json`：Claude Code Hooks。
- `.codex/config.toml`：Codex Hooks。
- `.claude/agents/`：Claude Code 角色 wrapper。
- `.codex/agents/`：Codex 角色 wrapper。

Hooks 配置都调用 `harness/scripts/hooks/harness_gate.py`，把 SOP 变成会话启动、编辑前、结束前的机械化护栏。角色 wrapper 统一指向 `harness/agents/*.md`，避免 Claude Code 和 Codex 各维护一套角色说明。

## 控制流程图

```mermaid
flowchart TD
  A["人类复制 template 到新服务"] --> B["AI 读取 AGENTS.md"]
  B --> C["执行新服务初始化 SOP"]
  C --> D["填写 README 与 context"]
  D --> E["项目化 harness/scripts/verify"]
  E --> F{"check-init-readiness.py 通过？"}
  F -- "否" --> C
  F -- "是" --> G["init-status.md 标记为已完成"]

  G --> H["Planner 提出 Track 拆分"]
  H --> I{"人工确认 Track？"}
  I -- "否" --> H
  I -- "是" --> J["track.py open <track-name>"]

  J --> K["Proposal / Spec / Design / Tasks"]
  K --> L{"Blocking 问题已关闭？"}
  L -- "否" --> K
  L -- "是" --> M["Generator 编码与测试"]

  M --> N["verify-template.sh / 分层检查 / C++ 风格检查"]
  N --> O{"验证通过？"}
  O -- "否" --> M
  O -- "是" --> P["Evaluator 做 Spec 合规检查"]
  P --> Q["Reviewer 做代码 Review"]
  Q --> R{"人工验收通过？"}
  R -- "否" --> M
  R -- "是" --> S["track.py finish-task / close"]

  S --> T["归档、learnings、ADR、scaffolds 回写"]
  T --> U{"还有下一个 Track？"}
  U -- "是" --> J
  U -- "否" --> V["阶段复盘，必要时修正模板"]

  X["SessionStart Hook"] -.提醒.-> B
  Y["PreToolUse Hook"] -.阻断越界编辑.-> M
  Z["Stop Hook"] -.提醒验证与归档.-> N
```

这张图只表达控制流。业务服务的目录蓝图、分层规则和代码脚手架不放在 `harness/`，它们属于项目上下文。

| 目录 | 用途 |
| --- | --- |
| `sop/` | 可执行操作手册 |
| `state/` | 初始化状态、active track 等脚本读写的运行状态 |
| `lifecycle/` | Track 生命周期和全局门禁 |
| `scripts/` | 按触发方式分组的 Harness 脚本：hooks / lifecycle / verify / tools |
| `agents/` | Agent 分工 |
| `dry-runs/` | 真实需求试运行日志 |

## 关键文件

- `state/init-status.md` — 工程初始化状态门禁。复制母版后默认 `未完成`，初始化未完成时阻断 Track 创建和业务代码编辑。
- `state/active-track.md` — 当前 active track 本地指针（已 `.gitignore`，由 `track.py` 维护）。同时仅允许 1 个 active track。
- `lifecycle/track-lifecycle.md` — Track 状态机、命令、active-track.md 格式、互斥规则。
- `sop/01-新服务初始化SOP.md` — 新服务初始化操作手册（15 节，每节带完成证据三类型）。
- `scripts/hooks/harness_gate.py` — 工具 Hook 调用的门禁脚本（SessionStart / PreToolUse / Stop 三阶段，含 active-track 锁）。
- `scripts/lifecycle/check-init-readiness.py` — 初始化完成度自动检查（README/AGENTS/CLAUDE/constitution/context/scripts/Hooks/门禁行为）。
- `scripts/lifecycle/track.py` — Track 生命周期命令（open / finish-task / close / status）。每完成一个 task 自动触发验证 + commit + push。
- `scripts/verify/` — CI / PR / 完成前验证入口。
- `scripts/tools/` — 手动修复和本地辅助工具。
- `agents/*.md` — 5 个角色定义（planner / generator / evaluator / reviewer / maintainer），工具无关；Claude Code 和 Codex 都通过 `.claude/agents/` 和 `.codex/agents/` 下的 wrapper 触发。

业务服务的目录蓝图、分层规则和代码脚手架不放在 `harness/`。它们属于项目上下文：

- `context/architecture/blueprint/` — 业务服务目录、分层、依赖边界。
- `context/engineering/scaffolds/` — AI 可复制改造的代码脚手架。

常用入口：

```bash
python3 -B harness/scripts/lifecycle/check-init-readiness.py
python3 -B harness/scripts/hooks/harness_gate.py prompt
bash harness/scripts/verify/verify-template.sh
```

初始化状态见 `harness/state/init-status.md`。初始化未完成前，不创建需求 Track，不修改业务代码。
