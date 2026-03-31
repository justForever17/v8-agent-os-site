# V8 Agent OS Site

这是 **V8 Agent OS** 的中英双语公开站点仓库。

这个仓库存在的目的，是让陌生观众很快产生一个明确感受：**V8 Agent OS 不是又一个聊得聪明、做事却总让你重讲项目、忍受工具噪音、最后还看不清内部发生了什么的 Agent。**

站点需要在很短时间里讲清四件事：

1. V8 会让你**少重讲**。
2. V8 会把**工具噪音压下去**。
3. V8 让长任务**可见、可审批、可接管**。
4. V8 能把成功过的屏幕操作慢慢收口成**更可复用的执行**。

## 这个站点应该做到什么

- 用观众能立刻复述的话解释产品
- 保持安装入口直接、低摩擦
- 把 GitHub、文档和安装入口统一指回 [`v8-agent-os`](https://github.com/justForever17/v8-agent-os) 主仓
- 保持中英双语页面结构与语气一致

## 这个站点绝不能像什么

- 维护手册
- 内部架构汇报
- 分仓迁移说明
- 试图靠功能清单压过 OpenClaw 的对比页

## 安装入口

公开安装口径刻意收成最简单的一种：

- Windows

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/justForever17/v8-agent-os/main/bootstrap.ps1 | iex"
```

- Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/justForever17/v8-agent-os/main/bootstrap.sh | bash
```

这些命令会从主仓根目录拉脚本，安装所需依赖，并拉起 Admin + Engine。Web 端仍继续独立分发。

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
| `index.html` | 英文落地页 |
| `zh/index.html` | 中文落地页 |
| `assets/` | 共享样式、脚本和品牌资源 |

## 对齐对象

- [`v8-agent-os`](https://github.com/justForever17/v8-agent-os) 主仓的公开产品叙事
- 主仓根目录里的 bootstrap 脚本
- 当前从统一主仓对外暴露的文档页面

## 支持 V8 Agent OS

如果这个项目帮你的团队少重讲、少折腾，并且更放心地把长任务交给 Agent，欢迎在这里支持后续开发：

[https://afdian.com/a/justForever17](https://afdian.com/a/justforever17)
