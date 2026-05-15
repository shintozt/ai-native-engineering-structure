# Harness Scripts 目录

本目录放 Harness 机械化门禁和验证脚本。脚本按**触发方式**分组，而不是按语言或文件名平铺。

复制母版后，所有带 `template` 的脚本都必须项目化；不能长期保留“占位即失败”的状态。

根目录默认不提供 `scripts/`。如果真实项目需要 CI、部署、运维或本地开发脚本，应在初始化或具体需求中单独生成根目录 `scripts/`，并在 `context/operations/` 记录用途。

## 目录结构

| 目录 | 触发方式 | 放什么 |
| --- | --- | --- |
| `hooks/` | Claude Code / Codex Hook 自动调用 | 会话启动、编辑前、结束前门禁 |
| `lifecycle/` | AI 或人按 SOP / Track 生命周期主动执行 | 初始化检查、Track open / finish-task / close / status |
| `verify/` | `track.py`、AI 完成定义、CI / PR 调用 | 构建、测试、分层、格式等交付验证 |
| `tools/` | AI 或人手动执行 | 格式化、批量修复等非门禁工具 |

## 脚本清单

### hooks/

| 脚本 | 触发来源 | 何时运行 | 复制后必须确认 |
| --- | --- | --- | --- |
| `hooks/harness_gate.py` | `.claude/settings.json`、`.codex/config.toml` | `prompt` / `pre-edit` / `stop` | 代码目录、Track 识别、代码类文件识别 |

### lifecycle/

| 脚本 | 触发来源 | 何时运行 | 复制后必须确认 |
| --- | --- | --- | --- |
| `lifecycle/check-init-readiness.py` | `AGENTS.md`、初始化 SOP、人工复核 | 新服务初始化完成前 | 可直接使用；必要时补项目特有检查 |
| `lifecycle/track.py` | `AGENTS.md`、Track 生命周期文档 | open / finish-task / close / status | 分支命名、验证命令、commit / push 策略 |

### verify/

| 脚本 | 触发来源 | 何时运行 | 复制后必须项目化的内容 |
| --- | --- | --- | --- |
| `verify/verify-template.sh` | `track.py finish-task`、AI 完成定义、CI | 声称完成前、CI、人工验收前 | 构建命令、测试命令、测试数断言、分层检查 |
| `verify/check-layer-boundaries-template.sh` | `verify-template.sh`、CI 可单独调用 | verify 中调用，也可单独运行 | 语言 import/include 规则、目录边界 |
| `verify/check-cpp-style-template.sh` | `verify-template.sh`、CI 可单独调用 | C++ 代码完成前、CI | C++ 文件后缀、目录范围、clang-format 版本 |

### tools/

| 脚本 | 触发来源 | 何时运行 | 复制后必须确认 |
| --- | --- | --- | --- |
| `tools/format-cpp-template.sh` | AI 或研发人员手动运行 | 需要批量修复 C++ 格式时 | C++ 文件后缀、目录范围 |

## 推荐调用顺序

```bash
python3 -B harness/scripts/hooks/harness_gate.py prompt
python3 -B harness/scripts/lifecycle/check-init-readiness.py
python3 -B harness/scripts/hooks/harness_gate.py pre-edit
bash harness/scripts/verify/verify-template.sh
python3 -B harness/scripts/hooks/harness_gate.py stop
```

对于 C++ 项目，`verify-template.sh` 应包含：

```bash
bash harness/scripts/verify/check-cpp-style-template.sh
bash harness/scripts/verify/check-layer-boundaries-template.sh
```

## 项目化检查

复制到真实项目后的第一天，必须完成：

- [ ] `check-init-readiness.py` 自动检查通过。
- [ ] `verify-template.sh` 能运行真实构建。
- [ ] `verify-template.sh` 能运行真实测试。
- [ ] 测试数为 0 或 skipped-only 时会失败。
- [ ] `check-layer-boundaries-template.sh` 能检查真实分层规则。
- [ ] C++ 项目可以运行 `check-cpp-style-template.sh`。
- [ ] `harness_gate.py pre-edit` 在无当前 Track spec 时会阻断代码类编辑。

## 输出格式

脚本失败时优先使用三段式：

```text
WHAT: 发生了什么
WHY: 为什么这会阻断
HOW: 如何修复或下一步怎么查
```
