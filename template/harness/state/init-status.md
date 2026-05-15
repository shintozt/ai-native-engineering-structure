# 初始化状态

本文件用于告诉 AI：当前工程是否已经完成新服务项目化。

复制母版后，默认状态必须是 `未完成`。只有完成 `harness/sop/01-新服务初始化SOP.md` 的全部检查项后，才允许改为 `已完成`。

## 状态

未完成

## 初始化证据清单

| 检查项 | 类型 | 证据 | 结果 |
| --- | --- | --- | --- |
| `README.md` 已替换占位为真实业务信息 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| Git 仓库已初始化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| `AGENTS.md` 必读顺序不依赖 `README.md` | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| `CLAUDE.md` 只转接到 `AGENTS.md` | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| `constitution.md` 已写入业务原则和 AI 执行边界 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| `context/business/` 已填写 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| `context/domain/` 已填写 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| `context/architecture/` 已填写 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| `context/engineering/` 已填写 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| `context/operations/` 已填写 | 自动验证 + 人工确认 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` + 人工确认 | 未验证 |
| Claude Code / Codex Hooks 和角色 wrapper 已接入 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| `harness/scripts/verify/verify-template.sh` 已项目化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| `harness/scripts/verify/check-layer-boundaries-template.sh` 已项目化 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |
| 第一个 Track 创建前初始化门禁有效 | 自动验证 | `python3 -B harness/scripts/lifecycle/check-init-readiness.py` | 未验证 |

## 最近一次自动检查

- 命令：`python3 -B harness/scripts/lifecycle/check-init-readiness.py`
- 结果：未运行 / 通过 / 未通过
- 时间：待填写
- 关键失败项：待填写

## 人工确认

- 确认人：待填写
- 确认日期：待填写
- 确认结论：待填写
- 需要人工确认的范围：
  - 业务边界、上下游和不包含范围是否正确。
  - 领域术语和业务规则是否符合真实业务。
  - 架构分层、端口隔离和外部依赖边界是否合理。
  - 工程脚手架是否符合本服务的代码组织方式。
  - 构建、测试、格式化命令是否符合团队实际环境。

## 备注

- 初始化未完成时，AI 只能修改入口文档、`context/`、`harness/` 和 `harness/scripts/`，不得创建需求 Track 或修改业务代码。
- `README.md` 是给人类阅读的项目说明，不作为 AI 工作规则来源。
- 初始化完成后，将“状态”改为 `已完成`，并在本文件记录确认人和日期。
