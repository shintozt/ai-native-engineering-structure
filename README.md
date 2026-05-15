# AI Native 工程结构母版

本仓库用于沉淀一套可复制的新服务工程母版。人类使用本仓库时，只需要理解三类目录的关系：原始材料、方法论、可复制模板。

```text
raw/      原始案例材料
wiki/     从案例中提炼的方法论
template/ 可复制到真实服务的新工程母版
```

## 目录结构

```text
ai-native-engineering-structure/
  README.md
  raw/
  wiki/
  template/
```

| 目录 | 用途 | 人类应该怎么用 |
| --- | --- | --- |
| `raw/` | 保存外部文章、公众号实践、案例原文 | 只作为证据来源，不复制到业务项目 |
| `wiki/` | 保存团队方法论和设计依据 | 用来理解为什么这样设计模板，维护模板前先看这里 |
| `template/` | 新服务工程母版 | 复制到真实服务目录，再让 AI 执行初始化 |

## template 结构

`template/` 是真正会被复制到业务项目中的内容。

```text
template/
  README.md
  AGENTS.md
  CLAUDE.md
  constitution.md
  .clang-format
  .claude/
  .codex/
  context/
  harness/
  specs/
  src/
  tests/
```

| 路径 | 用途 |
| --- | --- |
| `README.md` | 复制后由 AI 改写成真实项目 README，给人类阅读 |
| `AGENTS.md` | AI 进入项目后的入口规则 |
| `CLAUDE.md` | Claude Code 转接到 `AGENTS.md` |
| `constitution.md` | 项目原则和 AI 执行边界 |
| `.claude/`、`.codex/` | 工具 Hook 和 Agent wrapper |
| `context/` | 业务、领域、架构、工程、运维、知识沉淀 |
| `harness/` | SOP、门禁、脚本、Agent 分工、Dry Run |
| `specs/` | 需求 Track 和模板 |
| `src/`、`tests/` | C++17 服务代码和测试骨架 |

## 人类如何使用

### 1. 创建新服务

复制 `template/` 到目标服务目录：

```bash
cp -r ai-native-engineering-structure/template /path/to/<新服务名>
cd /path/to/<新服务名>
git init -b main
```

然后把下面这类指令交给 AI：

```text
请先按 AGENTS.md 和 harness/sop/01-新服务初始化SOP.md 执行新服务初始化。
业务建模文档在：<业务文档路径>
服务名称是：<服务名称>
技术栈要求：C++17 + CMake + GoogleTest
初始化完成前不要创建需求 Track，也不要写业务代码。
```

### 2. 增加新需求

初始化完成并通过人工确认后，把下面这类指令交给 AI：

```text
我现在要开发一个新需求：<一句话需求目标>。
请先读取 AGENTS.md，按当前工程 SOP 启动需求 Track。
在 Spec / Design / Tasks 确认前不要编码。
```

如果一个业务目标较大，让 AI 先拆成多个 Track；每个 Track 独立走 Spec、Design、Tasks、编码、验证、Review、归档闭环。

### 3. 维护方法论

有新的外部实践或真实项目经验时，建议按这个顺序维护：

```text
补充 raw/
  -> 提炼或修正 wiki/
  -> 调整 template/
  -> 用真实小需求验证
```

不要直接把某篇文章的做法塞进 `template/`。模板只承载已经被团队理解、验证、愿意长期执行的结构。

## 适用边界

这套模板默认面向新服务开发，尤其适合没有沉重存量包袱、希望从第一天就建立上下文、契约、验证和 Review 机制的 C++17 服务。

如果是改造大型历史系统，不建议直接整套套用，应先抽取一个新模块或新服务试运行。
