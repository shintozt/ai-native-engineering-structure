# <服务名称>

本服务用于 `<业务目标>`，面向 `<用户 / 调用方>`，核心职责是 `<一句话说明服务做什么>`。

本文件是项目 README 的初始占位骨架。复制母版后，AI 在初始化阶段把所有 `<...>` 占位和 TODO 替换为真实业务内容；初始化完成后，本文件就是面向人类的最终 README，无需另存。

## 当前阶段

- 阶段：初始化 / 第一个 Track / 开发中 / 已上线
- 技术栈：C++17 + CMake + GoogleTest
- AI 入口：`AGENTS.md`
- 初始化状态：`harness/state/init-status.md`

## 快速入口

| 文件 / 目录 | 用途 |
| --- | --- |
| `AGENTS.md` | AI Agent 入口规则 |
| `CLAUDE.md` | Claude Code 转接入口 |
| `.claude/settings.json` | Claude Code Hooks 配置 |
| `.codex/config.toml` | Codex Hooks 配置 |
| `.claude/agents/` | Claude Code 角色 wrapper，引用 `harness/agents/` |
| `.codex/agents/` | Codex 角色 wrapper，引用 `harness/agents/` |
| `constitution.md` | 项目不可违背原则 |
| `harness/sop/01-新服务初始化SOP.md` | 新服务初始化操作手册 |
| `harness/state/init-status.md` | 初始化状态门禁 |
| `context/INDEX.md` | 长期上下文索引 |
| `specs/tracks/` | 需求 Track |
| `harness/scripts/` | 门禁和验证脚本 |

## 服务范围

### 包含

- TODO：填写本服务包含的职责。

### 不包含

- TODO：填写本服务明确不做的内容。

## 上下游

| 类型 | 系统 / 角色 | 交互方式 | 备注 |
| --- | --- | --- | --- |
| 上游 | TODO | TODO | TODO |
| 下游 | TODO | TODO | TODO |
| 外部支撑 | TODO | TODO | TODO |

## 核心能力

- TODO：核心能力 1。
- TODO：核心能力 2。
- TODO：核心能力 3。

## 构建与验证

初始化阶段必须替换为真实命令；如果暂时无法确定，必须写清原因和待确认人。

```bash
bash harness/scripts/verify/verify-template.sh
bash harness/scripts/verify/check-layer-boundaries-template.sh
bash harness/scripts/verify/check-cpp-style-template.sh
```

## 工作方式

- AI 工作入口是 `AGENTS.md`，不是本 README。
- 初始化未完成前，不创建需求 Track，不修改业务代码。
- 第一个需求进入 `specs/tracks/<需求名>/`。
- 每个需求必须经过 Spec、Design、Tasks、验证、Review、归档。
