# Lifecycle 目录

本目录保存 Harness 生命周期中跨角色、跨工具的全局控制说明。

状态文件不放在这里。需要被脚本读取或写入的运行状态统一放在 `harness/state/`。

只服务单个 Agent 的检查清单不在本目录拆分，直接内联在 `harness/agents/` 对应角色文档中，避免多跳引用。

| 文件 | 用途 |
| --- | --- |
| `track-lifecycle.md` | Track 状态机、命令、互斥规则 |
| `gates.md` | Spec、Design、验证、Review、归档门禁 |

## 引用与触发关系

`track-lifecycle.md` 是 Track 流程的必读规则，不是脚本配置文件。它通过以下路径生效：

- `AGENTS.md` 必读顺序直接引用，AI 每次进入工程和处理需求前都必须读取。
- `specs/tracks/README.md` 引用，用于说明 Track 目录创建、状态机、互斥规则和任务推进方式。
- `harness/README.md` 引用，用于在人类阅读控制流程图时定位 Track 生命周期规则。
- `harness/scripts/lifecycle/track.py` 是它的机械化执行入口，负责 `open`、`next-stage`、`revise-stage`、`finish-task`、`close`、`pre-merge-check`、`status`。
- `harness/scripts/hooks/harness_gate.py` 使用 `harness/state/active-track.md` 执行编辑前门禁，阻断无 active track、跨 track 编辑、未定稿阶段编辑和 proposal/spec/design/tasks 未定稿时的代码编辑。
- `harness/scripts/lifecycle/check-init-readiness.py` 会检查 `AGENTS.md` 是否包含本文件，防止初始化时遗漏必读规则。

`gates.md` 是门禁总览，也不是脚本配置文件。它通过以下路径生效：

- `AGENTS.md` 必读顺序直接引用，AI 进入需求流程前必须读取。
- `context/architecture/blueprint/layering-rules.md` 和 `dependency-rules.md` 引用其中的设计评审、验证门禁，作为架构例外和外部依赖引入的评审依据。
- 具体门禁动作由 `harness_gate.py`、`track.py`、`verify/` 脚本和 `harness/agents/` 中的 Evaluator / Reviewer / Maintainer 分工共同执行。
