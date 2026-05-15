# 经验知识

每条知识使用 `TK-xxx.md` 文件保存，并登记到 `catalog.md`。

## 成熟度

| 状态 | 含义 | 升级条件 |
| --- | --- | --- |
| draft | 来自一次观察或推测 | 至少一个真实需求验证 |
| verified | 已在真实需求中验证 | 多次复用且结果稳定 |
| proven | 已成为团队稳定规则 | 有反例处理和失效条件 |

## 条目模板

```markdown
# TK-xxx：知识标题

| 字段 | 内容 |
| --- | --- |
| type | rule / pitfall / pattern / checklist / case |
| layer | team / tech / biz / project |
| maturity | draft / verified / proven |
| tags |  |
| source |  |
| owner |  |
| applicable_phases | proposal / spec / design / coding / testing / review / archive |
| created_at | YYYY-MM-DD |
| last_referenced |  |

## 适用场景

## 做法

## 示例

## 证据

## 失效条件
```
