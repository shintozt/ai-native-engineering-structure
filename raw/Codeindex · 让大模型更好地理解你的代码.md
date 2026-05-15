
原创 跨端技术团队 大淘宝技术

 _2026年4月20日 17:13_ _浙江_

![图片](https://mmbiz.qpic.cn/mmbiz_gif/33P2FdAnju9cLcib00YV66gYq2V6Fhm7YTHlzZdFwfnCtxyBCvgiaicG65n8du0mUYunHZIaBKohjsBxA4sgrPSjQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=0)

  

  

  

本文介绍了一款专为解决大模型在处理大型代码仓库时面临的上下文理解难题而设计的工具Codeindex。针对代码量大、分支多及依赖关系复杂等痛点，Codeindex 提供了代码语义化索引、检索以及函数依赖图生成能力。其核心技术亮点包括：利用增量索引与摘要生成技术提升大模型对代码意图的理解，采用分层架构与图数据库（KuzuDB/Postgres）精准构建函数上下游依赖关系。该工具通过 OpenAPI 和 SDK 两种形式，支持 CodeWiz 代码检索、AICR 智能代码审查及 CodeWiki 自动生成文档等应用场景，旨在帮助开发者更高效地构建基于代码的 AI 应用。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXThopqZpL00ibwWAU5Pk8seQ6mU83eJCNLnHey19ibT0ENW8YGSA0BwHuQ/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=1)

前⾔

  

在⽇常开发⼯作中你有没有这样的想法：

1. 想⾃⼰实现⼀个 Agent 助⼿来回答关于代码的⼀些问题，但是代码仓库过⼤，都塞给⼤模型也不太现实...
    
2. 想对仓库代码做分析，但还要考虑不同仓库不同分⽀的⽂件变化...
    
3. 想识别函数的上下游依赖，使⼤模型更准确地理解代码，还要单独实现函数依赖的上下游能⼒...
    
      
    

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp0PcLP4XaHFvZmPmJeTQIF5qdcz81EQb6fjGicojkdx1vj8v8UXUg0vOGzibpNdCA2AklrXR6ZeJmOhanwGVOV5x2v4MmcrjVh94/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=2)

  

现在，你可以使⽤ Codeindex 来帮助你解决这些问题：

1. 增量语义化索引&检索你的代码仓库，召回相关的代码⽚段
    
2. 增量⽣成代码⽚段&⽂件级别的代码摘要
    
3. 根据函数声明&调⽤⽣成函数依赖关系图，可获取函数依赖的上下游函数
    

下⾯就来介绍下 Codeindex ⽀持的能⼒以及可以实现的场景。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXTXKZWKec4l37w6NC4la1sV53zcZqqMO9wnqskOicSVEFvXiboFHlhWDbg/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=3)

介绍

Codeindex 是⼀个代码语义化索引、检索和函数依赖图⽣成⼯具，并⽀持增量索引。借助 codeindex，你可以对你的⼤型代码仓库进⾏索引，通过语义化描述检索代码仓库中的相关代码⽚段，此外你还可以获取这段代码或者其对应⽂件的语义化摘要，从⽽帮助⼤模型更好地理解代码意图。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp1oiajiaU4z9Z1f4g5rKSfbK0Upnrf28xmp23aRiaH6AKPOZkXoP09WPicd3M1Licq7U9TZKtT5uHk1t1lZfyFBqicd4hiaheNWdJc2us/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=4)

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXTPXlMC7M5h83yzCia08ia5SksCneXXPkicCvWGTgaIStFe0XPAOzaOvLlg/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=5)

整体架构

  

Codeindex 提供 SDK 与 OpenAPI 两种服务，OpenAPI 依赖 Node.js SDK 实现，⼆者均提供如下能⼒：

1. 建⽴索引：根据仓库及分⽀对代码建⽴语义化索引，并存储⽂件哈希值信息，⼆次索引可复⽤，实现增量索引。
    
2. 查询索引进度：因索引过程中涉及⽂本模型及向量模型的调⽤，⼤型项⽬的索引时间较⻓，可通过该能⼒实时查询索引进度。
    
3. 语义化检索：索引完成之后可通过⼀段语义化描述检索代码仓库中相关的代码⽚段及其语义化摘要。
    
4. 查询⽂件摘要：可查询单个⽂件的语义化摘要，可⽤于 Codewiki 等应⽤。
    
5. 查询函数声明：可查询⽂件中声明的函数⽚段。
    
6. 查询函数 Deps：查询某个函数的上下游函数依赖，可⽤于 AI CR 等场景，辅助⼤模型判断代码变更是否合理。
    
      
    

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/DthwRd8vvp0VPwdy8DEicrYF80oy0CLZa0vAQDhghxD3ANfWjvwic5EEgQ3YYnzO8vSc53e1ebcicTKo81cGQ7p4qIia6T08ic6AylbBeL9z51G8/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=6)

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXTEckyrs2AEMfbYLRp4wWezyVM5XiaEeDC8UW37DXUNVNazPXhxt8LB0w/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=7)

部分细节解析

  

▐  语义化摘要

  

语义化摘要依赖代码 Chunk 拆分的结果，在分块过程中会使⽤如下策略：  

1. codeChunker：codeChunker 利⽤ Tree-sitter 解析器⽣成 AST，并基于语法结构进⾏分块：

2. 若 Class 内代码超出 chunk token 上限，会对内部的函数体省略，保持 Class 的整体代码结构完整
    
3. 对 Class 内部的函数成员⼆次处理，单独进⾏ Chunk 拆分。
    

4. basicChunker：basicChunker是⼀个简单的基于⾏的分块器，适⽤于纯⽂本和 Markdown ⽂件，会按照 Chunk token 上限进⾏拆分。

Chunk 拆分完成之后会⽣成语义化代码摘要，代码⽚段会按照如下结构发送给⼤模型，最外层为 document 标签，表示单个⽂件，path 属性为⽂件路径；内部的 code 标签为当前⽂件内拆分的代码⽚段，start_line 与end_line 分别表示代码⽚段的开始⾏号和结束⾏号。

  

```
<document path="lib/utils.js">
```

  

我们会将上述信息发送给⼤模型让其做摘要，返回结果为如下结构的 JSON 对象

```
[
```

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp0gRicFvDu6ehTPCE3HibfPaqicdLOeVgrje4dTbCE56lO0onnwvKvZ9Qc758KOXj7PAvbic5IMAWJEMXS6pg6zSqSeG436V2ZliaibU/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=8)

  

▐  函数依赖图

  

代码依赖图可以⽤在 AI CR 等场景中，它可以查询函数依赖的上下游，从⽽为⼤模型提供更完备的上下⽂信息。

由于涉及到多种编程语⾔以及数据库语法差异，函数依赖图部分整体采⽤分层架构设计：

1. Parser 适配层，所有语⾔的依赖图解析均通过拓展该层的⽅式实现，对外暴露 API ⼀致，内部采⽤ tree-sitter 对代码进⾏解析，分析其内部的函数依赖。
    
2. GraphDB 适配层，由于涉及到 SDK 与 openapi，故需要考虑本地与线上两种存储介质，所以对 KuzuDB 与 Postgres 数据库对外暴露接⼝标准化，⽆缝切换存储介质。
    

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp3KiawicWkKJzmHq0s7pczDAnUViaAicTlvqNA3SlCQj9w7UaxRMjmtw99QstIe9aCfVejwR5fHPfAb0ia4mO7vibUkQDpcZzXFcJibMs/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=9)

函数依赖图⽣成时序图

  

> 总结一下上面的时序图，SDK 内部会查询文件内部声明了哪些函数、函数内部有没有嵌套声明函数、函数内部调用了哪些函数、被调用的函数是来自内部声明还是外部引用。获取到这些信息之后可以合并为图数据结构存储在图数据库中。

  

图数据存储⽅⾯，嵌⼊式图数据库采⽤ KuzuDB，线上使⽤ Postgres Age 插件，⼆者均设计了如下表结构⽤于存储图数据结构：

1. Files:节点表，存储代码库中每个⽂件的基本信息。
    
2. Functions: 节点表，存储代码中定义的函数信息。
    
3. Contains: 关系表，表示⽂件与函数之间的包含关系 (Files -> Functions)。
    
4. FunctionCalls: 关系表，记录函数之间的调⽤关系 (Functions -> Functions)。
    
5. FileCalls: 关系表，记录⽂件直接调⽤函数的关系 (Files -> Functions)。
    
6. Imports: 关系表，表示⽂件之间的导⼊/导出关系 (Files -> Files)。
    
7. Exports: 关系表，表示⽂件导出函数的关系 (Files -> Functions)。
    
8. FunctionContains: 关系表，表示函数内部定义了其他函数的关系（嵌套函数），(Functions -> Functions)。
    

  

借助上述的图数据表可以查询函数的多级依赖。可以⽣成类似下⾯的关系图

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp2GkjMtoFZBsPuS1NPVZcibwBjo7CjVaDhibTNiaqfBupHmCSYWxvdjzsicmHZficQpxnMqM98n7ibpUnwlnx3IHv9mLSylZpwcK6YOM/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=10)

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXTka17Qxq5b6yibxwJfmZt0s3qOjBIBiaFsA57MJgCNxFmgdOovIvM2n8Q/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=11)

应⽤

  

CodeWiz 集成

CodeWiz 基于 codeindex 的索引/检索能⼒实现了代码库索引功能，并为⼤模型提供检索⼯具，可在 Chat 过程中获取上下⽂，从⽽更好地为⽤户解决问题。

  

AI CR Agent

AI CR 是聚焦中后台场景、具有智能上下⽂分析能⼒的 Agent 应⽤，其内部依赖了 Codeindex 来获取函数依赖的上下游信息，以帮助⼤模型更好地判断当前变更是否对已有功能产⽣影响。

  

CodeWiki

CodeWiki 可根据仓库中的代码基于 Qwen ⼤模型 ⽣成 wiki ⽂档。

Codeindex 索引过程中会⽣成代码⽚段以及全⽂语义化摘要，将⽂件路径及其摘要发送给⼤模型可以帮助⼤模型更准确地输出 Wiki 结构，Codewiki 前置会先⽣成对应仓库的 Codeindex 索引，后续会基于其拆分的代码⽚段以及语义化摘要⽣成⽂档。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/DthwRd8vvp2KGjmvVPkhSwbickFo7CBR87dRQcFTO2AQbY13oSH2zhCQ3wpxWTSPGFoCF15ibngZTk5jXkJ72ibIgXGbQkzojO95Hp8OeicL2vM/640?from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=12)

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicZrWZ3a7SNVtibcNht0QoXTXbr9C0h0U8pnMsI1R3X2LmiaKiaH4INcq7Sk2dMca2S3bBxS3twu0vHA/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=13)

总结

  

总结⼀下，Codeindex 是⼀个代码语义化索引&检索⼯具，并且可以⽣成代码⽚段/⽂件级别的语义化摘要和函数依赖图，你可以使⽤这些能⼒来构建你的 AI 应⽤。⽬前 Codeindex 同时提供了 OpenAPI 和 SDK 两种⽅式，OpenAPI 中已经配置好了 SDK，只需要传⼊你的仓库信息就可以为你的仓库⽣成索引。

  

![图片](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8X1wEorjS3bDLnHiar4vtV5ibBdQV0nVXicyxBznmwreAKcTzDlbYsiaB2vC1ygO11TMiaYgGbicqjOUDg/640?wx_fmt=other&wxfrom=5&wx_lazy=1&wx_co=1&tp=wxpic#imgIndex=42)

团队介绍

  

本文作者崇野，来自淘天集团-跨端技术团队。本团队服务于淘宝基础用户产品，是淘宝重要的业务线之一。团队以前端、Weex、Native端的技术解决方案框架和研发模式不断完善自己，持续探索端智能等创新，打造极致的体验和工程技术，保障多端设备的适配和稳定运行，致力于让亿级规模的交付能够更丝滑、更稳定。

  

  

  

**¤** **拓展阅读** **¤**

  

[3DXR技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=2565944923443904512#wechat_redirect) | [终端技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1533906991218294785#wechat_redirect) | [音视频技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1592015847500414978#wechat_redirect)

[服务端技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1539610690070642689#wechat_redirect) | [技术质量](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=2565883875634397185#wechat_redirect) | [数据算法](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1522425612282494977#wechat_redirect)

  

![](http://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8t5nZGhAatCrc4e2iaDfAaoInribRKxc7MOqdTGygfcLqSDxhj0trCHVEh94Sjl7zuWYzwouYtJ0VQ/300?wx_fmt=png&wxfrom=19)

**大淘宝技术**

大淘宝技术官方账号

918篇原创内容

公众号

  

  

阅读 7508

​

**留言**

写留言

[](javacript:;)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8t5nZGhAatCrc4e2iaDfAaoInribRKxc7MOqdTGygfcLqSDxhj0trCHVEh94Sjl7zuWYzwouYtJ0VQ/300?wx_fmt=png&wxfrom=18)

大淘宝技术
