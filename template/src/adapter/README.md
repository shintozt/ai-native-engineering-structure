# adapter

外部协议、DTO、消息、文件格式与领域模型之间的转换。

允许依赖：

- `domain/`
- `ports/`
- `common/`

禁止：

- 直接连接真实外部服务。
- 承载复杂业务规则。
- 让外部 SDK 类型穿透到 `domain/`。
