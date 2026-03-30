# V8 Agent OS Site

> 这是 **V8 Agent OS 的公开站点仓库**。

## 这是让人决定“我愿不愿意认真试试它”的地方

如果说 Web、Admin、Engine 负责把机器造出来，那么这个仓库负责让人愿意相信它。

很多 Agent 产品很容易演示，却很难让人真正信服。  
**这个仓库存在的意义，就是把 V8 Agent OS 讲清楚：** 它不是又一个聊天壳，而是一套围绕 memory、automation、MCP、skills、OpenClaw 插件生态与多节点协作搭起来的 runtime-first Agent OS。

## 为什么站点要单独拆成一个仓库

因为产品表达值得拥有自己的发布节奏。

这个仓库负责：

- 中英双语产品页
- runtime 故事线
- 安装入口
- 页内文档阅读器
- Web / Admin / Engine / Site 四个仓库的公共导航

单独拆出来之后，产品表达可以持续演进，而不必拖着运行时代码一起改动。

## 这个站点真正要讲的是什么

| 大多数人拿到的东西 | V8 Agent OS 想交付的东西 |
| --- | --- |
| 一个会聊天的页面 | 一套 runtime-first 的 Agent operating surface |
| 会话一关就忘 | 能持续留下来的长期记忆 |
| 工具越装越乱 | MCP 与 skills 定向暴露、控制 token 成本 |
| 插件很多但系统很散 | OpenClaw 生态广度 + 更稳的 runtime 纪律 |

OpenClaw 给你的是外部连接能力。  
**V8 Agent OS 给你的是更像系统的内部骨架。**

## 站点内容从哪里来

- 安装脚本来自官方 [`v8-agent-os`](https://github.com/justForever17/v8-agent-os) 主仓根目录
- 公共文档来自当前对外暴露的 V8 Agent OS markdown 真相源
- 顶部 GitHub 入口统一指向 V8 Agent OS 主仓

这样既能保证站点轻量，也能保证读者看到的是最新公开内容。

## 部署到 Cloudflare Pages

1. 把这个仓库连接到 Cloudflare Pages。
2. 使用下面的设置：
   - Framework preset：`None`
   - Build command：留空
   - Build output directory：`/`
3. 部署即可。

## 本地预览

用任意静态文件服务器都可以。

```bash
python -m http.server 8789
```

然后打开：

```text
http://127.0.0.1:8789/
```

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `index.html` | 英文产品页 |
| `zh/index.html` | 中文产品页 |
| `assets/` | 共享样式、脚本和品牌资源 |

## 继续了解

- [English README](./README.md)
- [V8 Agent OS Web](https://github.com/justForever17/v8-agent-os-web)
- [V8 Agent OS Admin](https://github.com/justForever17/v8-agent-os-admin)
- [V8 Agent OS Engine](https://github.com/justForever17/v8-agent-os-engine)

---

## 赞助 V8 Agent OS

> **支持 V8 Agent OS 继续变强**
>
> 如果它让你的团队拥有了更稳的记忆、更顺的自动化和更像正式软件的 Agent 体验，欢迎在这里支持后续开发：
>
> [https://afdian.com/a/justforever17](https://afdian.com/a/justforever17)

---

> “We become what we behold. We shape our tools, and thereafter our tools shape us.”
>
> “我们眼之所见重塑了我们；我们塑造了工具，此后工具塑造了我们。”
>
> — Marshall McLuhan
