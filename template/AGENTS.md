# AGENTS.md

本文件是 AI Agent 进入工程后的入口地图。复制母版后，必须按真实项目更新。

## 必读顺序

1. `constitution.md`
2. `harness/sop/01-新服务初始化SOP.md`
3. `harness/lifecycle/gates.md`
4. `harness/lifecycle/track-lifecycle.md`
5. `context/INDEX.md`
6. `context/architecture/blueprint/directory-blueprint.md`
7. `context/architecture/blueprint/layering-rules.md`
8. `context/architecture/blueprint/dependency-rules.md`
9. C++ 项目还必须读取 `context/operations/cpp-coding-style.md`
10. 当前需求的 `specs/tracks/<需求名>/spec.md`
11. 当前需求的 `specs/tracks/<需求名>/design.md`

## 工作流硬规则

- 必须遵守 `constitution.md` 中的项目原则和 AI 执行边界；本文件只规定执行方式，不重复宪法全文。
- 新服务初始化未完成时，先执行 `harness/sop/01-新服务初始化SOP.md`，不得创建需求 Track 或修改业务代码。
- `README.md` 是给人类阅读的项目说明，不作为 AI 工作规则来源；AI 只在初始化阶段原地修改 `README.md` 占位骨架，初始化完成后不再修改。
- 启动新 Track 必须通过 `python3 -B harness/scripts/lifecycle/track.py open <name>`，不允许手动 `mkdir specs/tracks/`。
- 完成 task 必须通过 `python3 -B harness/scripts/lifecycle/track.py finish-task` 触发验证 + commit + push，不允许手动 `git commit` 业务代码。
- 同时只允许 1 个 active track。关闭当前 track（`track.py close` 或 `--abort`）后才能 open 下一个。
- 没有确认过的 Spec，不允许编码。
- Blocking 问题未关闭，不允许编码。
- 编码前必须输出计划，列出修改文件、影响层级、验证方式和风险点。
- 任何实现都必须能追溯到 Spec。
- 需求外重构必须单独提出。
- 完成前必须运行验证命令，并说明结果。
- C++ 文件提交或声明完成前必须运行 clang-format。
- 发现业务规则缺口时，优先补 `context/` 或 Spec，不靠聊天记忆。
- 需求结束后必须更新 Track 和知识沉淀。
- 所有说明性文档必须使用中文；路径、命令、API、类名、字段名等技术标识可保留英文。

## 分层执行规则

分层规则以 `context/architecture/blueprint/layering-rules.md` 和 `context/architecture/blueprint/dependency-rules.md` 为准。AI 执行时必须：

- 编码前判断变更落在哪一层，并在计划中写明。
- 涉及外部依赖时，先确认是否需要通过 `ports/` 隔离。
- 完成前运行分层检查命令，或说明无法运行的原因。
- 如需临时违反分层规则，必须先写 ADR 并等待人工确认。

## 常用命令

复制母版后必须替换：

```bash
bash harness/scripts/verify/verify-template.sh
bash harness/scripts/verify/check-layer-boundaries-template.sh
python3 -B harness/scripts/lifecycle/check-init-readiness.py
python3 -B harness/scripts/hooks/harness_gate.py prompt
python3 -B harness/scripts/hooks/harness_gate.py pre-edit
python3 -B harness/scripts/hooks/harness_gate.py stop
bash harness/scripts/verify/check-cpp-style-template.sh
```

## 人工确认点

以下是 `constitution.md` 中 AI 执行边界的操作化触发清单。出现任一情况必须停下来请人确认：

- 修改外部协议、存储格式、缓存主键、对外响应。
- 修改核心业务规则。
- 修改并发模型、锁粒度、异步生命周期。
- 引入新依赖、新线程、新队列、新后台任务。
- 删除或弱化测试、门禁、观测指标。

## 完成定义

一个需求只有同时满足以下条件才算完成：

- 代码满足 Spec。
- 相关测试通过。
- 分层边界检查通过。
- 风险点已说明。
- Track 已更新。
- 可复用规则已沉淀到 `context/`、`context/engineering/scaffolds/` 或 `harness/`。
