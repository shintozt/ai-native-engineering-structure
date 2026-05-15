# State 目录

本目录保存 Harness 的运行状态。状态文件会被脚本读取或写入，用来判断当前工程是否允许进入下一步。

| 文件 | 类型 | 维护者 | 说明 |
| --- | --- | --- | --- |
| `init-status.md` | 可提交状态 | AI 初始化 + 人工确认 | 记录新服务初始化是否完成 |
| `active-track.md` | 本地状态 | `track.py` 自动维护 | 当前 active track 指针，已在 `.gitignore` 中排除 |

## 规则

- `init-status.md` 可以提交，因为它表示项目是否完成初始化。
- `active-track.md` 不提交，因为它是每个开发者本地的当前工作指针。
- 流程说明和门禁不放在本目录，统一放入 `harness/lifecycle/`。
- Review、验证、归档等角色内检查项直接放入 `harness/agents/` 对应角色文档。
