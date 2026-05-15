# C++ 编码规范

本规范来自团队 C++ 文档的可复用部分。复制母版后，如果项目使用不同 C++ 标准或命名体系，应在本文件中明确覆盖。

## 1. 基础格式

- 文件编码：UTF-8，无 BOM。
- 换行符：LF。
- 缩进：4 个空格，禁止 Tab。
- 格式化：所有 C++ 源码必须使用项目根目录 `.clang-format`。
- 控制流：`if / else / for / while` 即使只有一行，也必须使用 `{}`。
- 提交或声明完成前，必须对改动过的 C++ 文件运行 `clang-format -i path/to/file.cpp`，或运行项目封装脚本。

## 2. C++ 标准

- 默认使用 C++17。
- 禁止使用未被项目确认的更高版本特性。
- 如项目决定升级到 C++20 或更高版本，必须同步更新 `.clang-format`、构建脚本、AI 入口说明和相关 ADR。

## 3. 命名规范

| 对象 | 规则 | 示例 |
| --- | --- | --- |
| 类型：class / struct / enum | `snake_case_t`，以 `_t` 结尾 | `session_impl_t` |
| 函数 | `snake_case` | `load_today_ticks` |
| 类成员变量 | `m_` 前缀，单词下划线分隔 | `m_guide_count` |
| 结构体 public 成员 | 不加 `m_` | `max_seq_no` |
| 静态变量 | `s_` 前缀 | `s_instance` |
| 全局变量 | `g_` 前缀，头文件只允许 `extern` 声明 | `g_config` |
| 枚举值 | `kPascalCase` | `kChannelModePool` |
| 命名空间 | 小写或 `snake_case` | `order_flow` |

已有项目如存在历史例外，必须写入本文件或 ADR，不允许让 AI 自行推断。

## 4. 头文件和 include

- 禁用 `#pragma once`。
- 必须使用 `#ifndef / #define / #endif` include guard。
- include guard 可使用结尾带 `_H_` 或 `_H` 的形式。

示例：

```cpp
#ifndef _PROJECT_MODULE_FILE_H_
#define _PROJECT_MODULE_FILE_H_

// declarations

#endif
```

- 能用前置声明解决的依赖，优先前置声明。
- 头文件禁止定义全局变量。
- include 顺序以 `.clang-format` 输出为准。

## 5. 构造、初始化和函数签名

- 单参数构造函数必须 `explicit`。
- 成员变量在声明处使用 `{}` 初始化。
- 不修改成员状态的成员函数必须标注 `const`。
- 不抛异常的函数应标注 `noexcept`。
- 基类虚函数标注 `virtual`。
- 派生类重写函数标注 `override`。
- 不再允许继承的类标注 `final`。
- 禁止在虚函数中使用默认参数。

## 6. 注释规范

- 修改已有文件时，必须跟随原文件注释风格。
- 新文件默认使用 `// ` 单行注释。
- 只注释关键逻辑、线程安全性、生命周期、非显而易见行为。
- 不写“赋值给变量”这类空泛注释。
- 新增 public API 时，应说明语义、约束、错误行为和线程安全影响。

## 7. AI 生成代码禁忌

- 不允许凭记忆编造 API；引用已有 API 前必须搜索源码验证。
- 不允许为了通过测试改变业务语义。
- 不允许跳过 clang-format。
- 不允许把外部 SDK 类型穿透到 `domain/`。
- 不允许默认单测依赖真实外部服务。

## 8. 验证命令

格式化单个文件：

```bash
clang-format -i path/to/file.h path/to/file.cpp
```

检查全部 C++ 文件：

```bash
bash harness/scripts/verify/check-cpp-style-template.sh
```

批量格式化全部 C++ 文件：

```bash
bash harness/scripts/tools/format-cpp-template.sh
```
