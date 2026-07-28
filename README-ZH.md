# V8 Agent OS Site

这是 **V8 Agent OS** 的中英双语公开站点仓库。

这个仓库存在的目的，是让陌生观众很快产生一个明确感受：**V8 Agent OS 不是又一个聊得聪明、做事却总让你重讲项目、忍受工具噪音、最后还看不清内部发生了什么的 Agent。**

站点需要在很短时间里讲清五件事：

1. V8 会让你**少重讲**。
2. V8 会把**工具噪音压下去**。
3. V8 让长任务**可见、可审批、可接管**。
4. V8 能把成功过的屏幕操作慢慢收口成**更可复用的执行**。
5. V8 用**受治理画布、可复用工作区素材、精确本机编辑和交付 QA**承载创意工作，而不是把媒体散落在提示词和目录里。

## 这个站点应该做到什么

- 用观众能立刻复述的话解释产品
- 保持安装入口直接、低摩擦
- 把 GitHub、文档和安装入口统一指回 [`v8-agent-os`](https://github.com/justForever17/v8-agent-os) 主仓
- 保持中英双语页面结构与语气一致
- 只描述主仓已落地能力；新功能截图未准备好时保留明确占位，不使用过时截图冒充当前界面

## 这个站点绝不能像什么

- 维护手册
- 内部架构汇报
- 分仓迁移说明
- 试图靠功能清单压过竞品的对比页

## 预览版安装入口

公开桌面入口是主仓 [GitHub Releases](https://github.com/justForever17/v8-agent-os/releases) 中的 Windows Desktop Preview。当前仍是 unsigned preview，不代表已签名 stable 或自动更新承诺。Phone 使用独立的 Android Preview APK，并在桌面控制台中配对。

主仓 `bootstrap.ps1` / `bootstrap.sh` 是依赖安装与服务启动脚本，默认启动 Engine + Admin，不是 Electron 桌面安装器。源码树的完整桌面预览入口是：

```powershell
.\v8os.cmd preview --rebuild
```

发布前可做一条简单叙事校验：

```bash
python scripts/audit_public_narrative.py
```

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
- 主仓 GitHub Releases、`v8os preview` 与 bootstrap 的真实职责边界
- 当前从统一主仓对外暴露的文档页面

## 支持 V8 Agent OS

如果这个项目帮你的团队少重讲、少折腾，并且更放心地把长任务交给 Agent，欢迎在这里支持后续开发：

[https://afdian.com/a/justForever17](https://afdian.com/a/justforever17)
