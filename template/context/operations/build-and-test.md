# 构建与测试

## 构建命令

```bash
# TODO: 替换为真实构建命令
```

## 测试命令

```bash
# TODO: 替换为真实测试命令
```

## C++ 格式化

如果项目使用 C++，提交或声明完成前必须运行：

```bash
bash harness/scripts/verify/check-cpp-style-template.sh
```

需要批量修复格式时运行：

```bash
bash harness/scripts/tools/format-cpp-template.sh
```

## 错误输出格式

脚本失败时优先使用三段式：

```text
WHAT: 发生了什么
WHY: 为什么这会阻断
HOW: 如何修复或下一步怎么查
```
