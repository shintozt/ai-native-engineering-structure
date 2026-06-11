# 领域知识包

本目录用于跨项目迁移领域知识。知识包只作为候选输入或候选输出，不能跳过当前项目 Track 审核直接成为正式规则。

## 目录

| 目录 | 含义 |
| --- | --- |
| `incoming/` | 外部项目导入、等待当前项目审核的候选知识 |
| `outgoing/` | 本项目准备给其他项目参考的候选知识 |

## 状态

- candidate：刚导入，未审核。
- reviewed：已阅读并初步评估。
- accepted：目标项目 Track 已确认可裁剪采用。
- rejected：不适配目标项目。

accepted 也不自动生效。只有裁剪后写入 `context/domain/`、`context/architecture/` 或 Track 文档，才成为当前项目规则。
