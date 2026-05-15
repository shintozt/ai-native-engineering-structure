# 新服务初始化 SOP

本文说明复制母版后，如何把一个空工程项目化到“可以启动第一个需求 Track”的状态。

适用场景：

- 新建一个业务服务。
- 已有业务建模文档，但还没有工程代码。
- 希望 AI 后续能按 Harness 流程编写代码。

完成本 SOP 前，不创建需求 Track，不进入业务代码实现。

## 0. 完成证据分级

初始化不允许只靠“我觉得已经写清楚了”来打勾。每一项完成标准必须落到以下三类证据之一：

| 类型 | 含义 | 记录方式 |
| --- | --- | --- |
| 自动验证 | 脚本可直接判断，例如文件存在、非空、无占位符、门禁行为正确 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` 输出 |
| 半自动证据 | 脚本能证明结构存在，但语义需要人读，例如上下游表格、核心流程、风险表 | 文件路径 + 段落名 |
| 人工确认 | 只能由人判断，例如业务边界是否合理、术语是否准确、架构取舍是否符合团队预期 | `harness/state/init-status.md` 记录确认人和日期 |

初始化完成前必须至少运行：

```bash
python3 -B harness/scripts/lifecycle/check-init-readiness.py
python3 -B harness/scripts/hooks/harness_gate.py prompt
```

如果 `check-init-readiness.py` 有 FAIL 项，不得把 `harness/state/init-status.md` 改为 `已完成`。

## 1. 输入材料

开始前准备：

- 业务建模文档或需求背景。
- 技术栈选择，例如 C++17 / CMake / GoogleTest。
- 服务名称。
- 预期上游、下游、外部依赖。
- 构建和测试命令的初步方案。
- Git 仓库和分支/提交策略。

如果这些材料不完整，先把未知项写入 `context/business/business-map.md` 的“风险和未知”表格。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 输入材料已落盘 | 半自动证据 | 人读 `context/business/business-map.md` | 业务目标、上下游、范围、风险未知不为空 | `context/business/business-map.md` |
| 未知项已记录 | 半自动证据 | 人读风险表 | 无法确认的问题不留在聊天里 | `context/business/business-map.md` |

## 2. 复制母版

将 `ai-native-engineering-structure/template/` 复制为新服务根目录。

复制后第一天必须保留这些入口：

```text
README.md
AGENTS.md
CLAUDE.md
constitution.md
.clang-format
.claude/
.codex/
context/
specs/
harness/
harness/scripts/
harness/scripts/hooks/
harness/scripts/lifecycle/
harness/scripts/verify/
harness/scripts/tools/
src/
tests/
```

不要在第一天删除 `harness/`、`context/`、`specs/`。这些是 AI 工作所需的控制系统。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 入口文件和目录存在 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 必要入口存在且关键文件非空 | 脚本输出 |
| 初始化状态未完成 | 自动验证 | `python3 -B harness/scripts/hooks/harness_gate.py prompt` | 输出初始化提醒 | 终端输出 |

## 2.1 初始化 Git 仓库

目标：让 Track 生命周期命令可以创建分支、提交变更，并在完成 task 时留下可追溯记录。

如果新服务目录还不是 Git 仓库，先执行：

```bash
git init -b main
```

如果团队要求远端分支，请在第一个 Track 进入编码前配置 remote。`track.py finish-task` 会自动提交，并尝试 `git push -u origin HEAD`；没有 remote 时会保留本地 commit 并提示人工处理。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| Git 仓库已初始化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `git rev-parse --is-inside-work-tree` 返回 true | 脚本输出 |
| 分支/提交策略已理解 | 人工确认 | 人读本节和 `harness/scripts/lifecycle/track.py` | 知道 task 完成会触发 commit，push 失败需人工处理 | `harness/state/init-status.md` |

## 3. 接入 AI 工具控制

目标：让 Claude Code、Codex 等工具在会话启动、编辑前、结束前自动触发 Harness 门禁，不只依赖模型记忆。

母版默认提供：

| 工具 | 配置文件 | 作用 |
| --- | --- | --- |
| Claude Code | `.claude/settings.json` | 配置 `SessionStart`、`PreToolUse`、`Stop` Hooks |
| Codex | `.codex/config.toml` | 配置 `SessionStart`、`PreToolUse`、`Stop` Hooks |
| Claude Code | `.claude/agents/*.md` | 角色 wrapper，指向 `harness/agents/*.md` |
| Codex | `.codex/agents/*.toml` | 角色 wrapper，指向 `harness/agents/*.md` |

这些配置统一调用：

```bash
python3 -B harness/scripts/hooks/harness_gate.py prompt
python3 -B harness/scripts/hooks/harness_gate.py pre-edit
python3 -B harness/scripts/hooks/harness_gate.py stop
```

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| Claude Code Hook 已接入 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `.claude/settings.json` 存在且引用 `harness/scripts/hooks/harness_gate.py` | 脚本输出 |
| Codex Hook 已接入 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `.codex/config.toml` 存在且引用 `harness/scripts/hooks/harness_gate.py` | 脚本输出 |
| Claude Code 角色 wrapper 已接入 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `.claude/agents/*.md` 均引用对应 `harness/agents/*.md` | 脚本输出 |
| Codex 角色 wrapper 已接入 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `.codex/agents/*.toml` 均引用对应 `harness/agents/*.md` | 脚本输出 |
| 控制边界已理解 | 人工确认 | 人读本节 | Hooks 是护栏，不替代 CI / PR 门禁 | `harness/state/init-status.md` |

## 4. 初始化状态门禁

复制母版后，先检查：

```text
harness/state/init-status.md
```

默认状态必须是：

```text
未完成
```

初始化未完成时，AI 只能做以下事情：

- 原地修改 `README.md` 占位为真实业务信息。
- 项目化 `AGENTS.md`、`constitution.md`。
- 保持 `CLAUDE.md` 只转接 `AGENTS.md`。
- 填写 `context/`。
- 项目化 `harness/scripts/`。
- 更新 `harness/state/init-status.md`。

初始化未完成时，AI 禁止：

- 创建 `specs/tracks/<需求名>/`。
- 修改 `src/` 业务代码。
- 声称可以进入编码。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| Track 创建会被阻断 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | “初始化未完成时阻断创建 Track”为 PASS | 脚本输出 |
| 业务代码编辑会被阻断 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | “初始化未完成时阻断业务代码编辑”为 PASS | 脚本输出 |
| README 初始化编辑被允许 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | README 白名单检查为 PASS | 脚本输出 |

## 5. 修改 README.md 为项目说明

目标：让人类在 1 分钟内知道这个服务是什么。`README.md` 不作为 AI 工作规则来源，AI 规则以 `AGENTS.md`、`harness/`、`context/` 和 `specs/` 为准。

母版的 `README.md` 已经是项目级 README 的占位骨架。本节是把骨架原地修改为真实项目说明，不另存为新文件。

执行方式：

1. 读取 `README.md`（已是占位骨架）。
2. 读取用户提供的业务建模文档、服务名称、上下游、技术栈和构建测试约束。
3. 用真实项目信息替换骨架中的占位内容。
4. 保存到原文件。

必须替换的占位：

| 位置 | 占位 | 改成什么 |
| --- | --- | --- |
| 标题 | `<服务名称>` | 服务名称 |
| 第一段 | `<业务目标>` 等 | 服务一句话定位 |
| 当前阶段 | `初始化 / 第一个 Track / ...` | 当前阶段 |
| 快速入口 | （保留） | 保留 `AGENTS.md`、`context/INDEX.md`、`specs/tracks/` |
| 服务范围 | TODO | 包含和不包含 |
| 上下游 | TODO | 上游、下游、外部支撑 |
| 构建与验证 | （保留示例） | 真实命令或保留待项目化说明 |

格式以 `README.md` 自身为准；本 SOP 不复制第二份 README 模板，避免漂移。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| README 无占位符 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 无 `<...>`、TODO、待填写、占位 | 脚本输出 |
| README 不再是骨架占位 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 不包含"项目 README 的初始占位"等模板自我说明 | 脚本输出 |
| README 包含人类入口段落 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 当前阶段、快速入口、服务范围、上下游存在 | 脚本输出 |
| 服务定位正确 | 人工确认 | 人读 `README.md` | 一句话定位、包含范围、不包含范围符合业务 | `harness/state/init-status.md` |

## 6. 修改 AGENTS.md

目标：让 AI 知道进入本项目后必须读什么、不能做什么、怎么验证。

必须改：

| 位置 | 改成什么 |
| --- | --- |
| 文件开头 | 项目名称和一句话职责 |
| 必读顺序 | 保留通用入口，补业务关键 context |
| 工作流硬规则 | 保留；如项目有特殊规则，追加 |
| 分层执行规则 | 引用 `context/architecture/blueprint/`，不要复制完整分层原则 |
| 常用命令 | 替换为真实构建、测试、格式化、门禁命令 |
| 人工确认点 | 作为 `constitution.md` 的操作化触发清单，补业务高风险点 |

业务关键路径示例（按真实业务定义）：

```markdown
- 修改核心业务计算或数据语义（如本服务对外承诺的关键算法、聚合规则、时间窗口）。
- 修改对外存储或消费协议（数据库 Schema、消息格式、缓存主键、对外响应字段）。
- 修改业务时间或顺序边界（窗口、分段、幂等键、水位线）。
- 修改并发模型、锁粒度、异步生命周期。
- 引入新的强外部依赖（新服务、新中间件、新 SDK）。
```

如团队沉淀了具体业务示例，可在真实项目中新增 `examples/<业务>/` 并在本节补充链接；母版不预设业务案例。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| AGENTS 不依赖 README | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 必读顺序中没有 `README.md` | 脚本输出 |
| AGENTS 包含初始化、门禁、Track 生命周期和 C++ 入口 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 包含初始化 SOP、`harness/lifecycle/gates.md`、`harness/lifecycle/track-lifecycle.md`、`context/INDEX.md`、C++ 规范入口 | 脚本输出 |
| 不重复宪法原则 | 半自动证据 | 人读 `AGENTS.md` | 只引用 `constitution.md`，不复制原则全文 | `AGENTS.md` |
| 人工确认点符合业务风险 | 人工确认 | 人读 `AGENTS.md` | 高风险变更会停下来确认 | `harness/state/init-status.md` |

## 7. 修改 CLAUDE.md

目标：让 Claude Code 使用同一套入口，不产生第二套规则。

推荐保持轻量，不复制 `AGENTS.md` 内容。

建议内容：

```markdown
# CLAUDE.md

Claude Code 进入本工程后，先读取并遵守 `AGENTS.md`。本文件只做入口转接，不重复 `AGENTS.md` 内容；如出现差异，以 `AGENTS.md` 为准。
```

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| CLAUDE 只转接 AGENTS | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 包含 `AGENTS.md`，且没有二级规则章节 | 脚本输出 |
| 没有漂移规则 | 人工确认 | 人读 `CLAUDE.md` | 没有复制一份会和 AGENTS 漂移的规则 | `CLAUDE.md` |

## 8. 修改 constitution.md

目标：写清项目不可违背的业务和工程原则。

必须改：

| 段落 | 要写什么 |
| --- | --- |
| 业务正确性优先 | 本业务最重要的正确性是什么 |
| 领域纯净 | 哪些外部类型不能进入领域层 |
| 外部依赖可替换 | 哪些外部服务必须通过端口隔离 |
| 验证优先 | 哪些验证是最低门槛 |
| AI 执行边界 | AI 可自主改、必须确认、禁止改的范围 |

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 包含 AI 执行边界 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 存在 `## AI 执行边界` | 脚本输出 |
| 无明显占位符 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 无 `<...>`、TODO、待填写、占位 | 脚本输出 |
| 原则符合业务 | 人工确认 | 人读 `constitution.md` | 3-5 条原则确实约束本服务 | `harness/state/init-status.md` |

## 9. 填写 context/business/

目标：让 AI 知道这个服务在业务系统里的位置。

必须填写：

- 业务目标。
- 核心用户或调用方。
- 成功后业务变化。
- 上游。
- 下游。
- 外部支撑系统。
- 包含范围。
- 不包含范围。
- 核心流程。
- 风险和未知。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| business-map 已填写 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 文件非空且无明显占位符 | 脚本输出 |
| 上下游和范围可读 | 半自动证据 | 人读 `context/business/business-map.md` | 上游、下游、外部支撑、包含、不包含均可定位 | `context/business/business-map.md` |
| 业务边界合理 | 人工确认 | 人读业务地图 | 不包含范围没有遗漏关键职责 | `harness/state/init-status.md` |

## 10. 填写 context/domain/

目标：建立领域语言和业务规则。

必须更新：

- `context/domain/ubiquitous-language.md`
- `context/domain/business-rules.md`
- `context/domain/catalog.md`

填写方法：

1. 从业务文档抽取术语。
2. 每个术语写定义和反例。
3. 每条业务规则写验证方式。
4. 更新 `catalog.md`。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 领域文档已填写 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 三个文件非空且无明显占位符 | 脚本输出 |
| 术语和规则可检索 | 半自动证据 | 人读 `catalog.md` | catalog 能索引术语和业务规则 | `context/domain/catalog.md` |
| 术语和规则准确 | 人工确认 | 业务负责人或开发负责人确认 | 定义、反例、验证方式符合真实业务 | `harness/state/init-status.md` |

## 11. 填写 context/architecture/

目标：让 AI 知道服务的分层、数据流和依赖边界。

必须更新：

- `context/architecture/layered-architecture.md`
- `context/architecture/runtime-dataflow.md`
- `context/architecture/catalog.md`

必须说明：

- 代码分层。
- 主数据流。
- 异常数据流。
- 幂等和重试。
- 外部依赖通过哪些端口进入。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 架构文档已填写 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 三个文件非空且无明显占位符 | 脚本输出 |
| 数据流和分层可读 | 半自动证据 | 人读 architecture 文档 | 主流程、异常流程、外部依赖入口可定位 | `context/architecture/` |
| 分层边界合理 | 人工确认 | 技术负责人确认 | 外部依赖不会直接穿透 `domain/` | `harness/state/init-status.md` |

## 12. 填写 context/engineering/

目标：让 AI 知道业务代码应该按什么脚手架和实现模式落地。

必须更新：

- `context/engineering/README.md`
- `context/engineering/catalog.md`
- `context/engineering/scaffolds/README.md`

必须确认：

- 当前服务是否沿用母版提供的 C++17 脚手架。
- 是否需要新增或删除某类脚手架。
- 脚手架是否能被 AI 复制改造，而不是只有概念说明。
- 可复用代码模式应先从真实需求沉淀，再升级为脚手架。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| engineering 入口已填写 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | README、catalog、scaffolds README 非空且无明显占位符 | 脚本输出 |
| 脚手架边界可读 | 半自动证据 | 人读 `context/engineering/` | 清楚说明哪些模式可复制、哪些需要真实需求后再沉淀 | `context/engineering/` |
| 脚手架符合服务代码组织 | 人工确认 | 开发负责人确认 | 与 `context/architecture/blueprint/`、`src/`、`tests/` 一致 | `harness/state/init-status.md` |

## 13. 填写 context/operations/

目标：让 AI 和 CI 知道怎么构建、测试、格式化、排查。

必须更新：

- `context/operations/build-and-test.md`
- `context/operations/cpp-coding-style.md`
- `context/operations/observability.md`
- `context/operations/catalog.md`

C++17 项目必须确认：

- `.clang-format` 为 `Standard: c++17`。
- 构建命令开启 C++17。
- 格式化命令可运行。

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 运维文档已填写 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 四个文件非空且无明显占位符 | 脚本输出 |
| C++17 规则可见 | 半自动证据 | 人读 `.clang-format` 和 `cpp-coding-style.md` | 明确 C++17、命名、格式化、错误输出 | `.clang-format`、`context/operations/cpp-coding-style.md` |
| 命令符合团队环境 | 人工确认 | 开发负责人确认 | 构建、测试、格式化命令能在本机或 CI 落地 | `harness/state/init-status.md` |

## 14. 项目化 harness/scripts/

目标：让验证脚本从“占位失败”变成真实可运行。

必须项目化：

| 分组 | 脚本 | 动作 |
| --- | --- | --- |
| Hook 自动调用 | `hooks/harness_gate.py` | 确认代码目录、Track 识别规则、代码类文件识别 |
| 生命周期命令 | `lifecycle/check-init-readiness.py` | 必要时补项目特有初始化检查 |
| 生命周期命令 | `lifecycle/track.py` | 确认验证命令、分支命名、commit / push 策略 |
| CI / 交付验证 | `verify/verify-template.sh` | 替换为真实构建、测试、测试数断言、分层检查 |
| CI / 交付验证 | `verify/check-layer-boundaries-template.sh` | 按真实语言和目录实现分层检查 |
| CI / 交付验证 | `verify/check-cpp-style-template.sh` | 确认目录、后缀、clang-format 版本 |
| 人工辅助工具 | `tools/format-cpp-template.sh` | 确认目录和后缀 |

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| verify 脚本已项目化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `verify-template.sh` 不再包含“尚未项目化” | 脚本输出 |
| 分层检查已项目化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `check-layer-boundaries-template.sh` 不再包含“尚未项目化” | 脚本输出 |
| 验证命令可执行 | 半自动证据 | 运行项目化后的验证命令 | 输出 WHAT / WHY / HOW 或真实测试结果 | 终端输出 |
| 测试数断言合理 | 人工确认 | 人读 `verify-template.sh` | 没有测试或 skipped-only 测试会失败 | `harness/state/init-status.md` |

## 15. 初始化完成检查

全部满足后，才允许创建第一个 Track。

必须先运行：

```bash
python3 -B harness/scripts/lifecycle/check-init-readiness.py
python3 -B harness/scripts/hooks/harness_gate.py prompt
```

完成证据：

| 检查项 | 类型 | 验证方式 | 通过标准 | 证据位置 |
| --- | --- | --- | --- | --- |
| 自动检查通过 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 所有自动检查为 PASS | 终端输出 |
| 初始化状态记录完整 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | `init-status` 记录自动检查和人工确认字段 | 脚本输出 |
| 人工确认完成 | 人工确认 | 人在 `harness/state/init-status.md` 记录 | 有确认人、日期、结论 | `harness/state/init-status.md` |
| 状态改为已完成 | 人工确认 | 人读 `harness/state/init-status.md` | 只有自动检查和人工确认都完成后才改为 `已完成` | `harness/state/init-status.md` |

通过本清单后，AI 才可以创建第一个 Track。第一个 Track 的 Spec / Design / Tasks 被确认后，AI 才可以按 `tasks.md` 进入编码。
