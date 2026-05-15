# tests 目录

复制母版后，在这里建立真实测试。

推荐结构：

```text
tests/
  domain/
  ports/
  adapter/
  infra/
  app/
  observer/
  common/
```

默认单测不得依赖真实外部服务。真实 Redis、Kafka、Mongo、HTTP 等依赖应归类为集成测试，并在验证脚本中明确区分。
