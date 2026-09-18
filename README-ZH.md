# V8 Agent OS 产品门户

**让一个人，也能做成更大的事。** 这里是 [V8 Agent OS](https://github.com/justForever17/v8-agent-os) 的中英双语产品门户，围绕研究、开发与创作展示个人 AI 工作系统。

[访问官网](https://v8agentos.top/zh/) · [English](README.md) · [共创社区](https://github.com/justForever17/v8-agent-os/discussions) · [下载预览版](https://github.com/justForever17/v8-agent-os/releases/tag/v8-os-v2026.09.17.3)

## 本地预览

需要 Python 3.12 或更高版本，无前端框架与运行时 CDN 依赖。

```powershell
python scripts/build_site.py
python scripts/audit_public_narrative.py
python scripts/test_media.py
python -m http.server 8789 --directory dist
```

打开 `http://127.0.0.1:8789/zh/`，英文入口为 `/`。

## 内容维护

| 文件 | 职责 |
| --- | --- |
| `content/zh.json` / `content/en.json` | 中英文案 |
| `templates/index.html` | 共用页面结构 |
| `assets/styles.css` / `assets/site.js` | 视觉与渐进增强交互 |
| `assets/media.json` | 场景与 Phone 实拍、控制台与星图、scene-atlas/scene-camera、terminal/pairing/recovery 细节、影片与字幕 |
| `scripts/build_site.py` | 生成根目录双语页面与 `_headers`，组装仅含公开文件的 `dist` |

修改源文件后重新构建，不手工修改生成页面。`python scripts/build_site.py --check` 可检查生成物是否同步。根目录页面继续兼容现有 Cloudflare Pages Git 部署；配置构建时使用 `python scripts/build_site.py`，输出目录选 `dist`。

素材未配置时展示有明确标注的概念图和“影片即将上线”。截图填写 `assets/media/` 下的本地路径；影片、海报与字幕也可使用 R2 的永久公共 HTTPS 链接，不能包含凭据、查询参数或片段。构建自动把媒体来源加入 CSP。R2 仍需设置相应 CORS，才能支持跨域视频与字幕。大视频不进入 Git 仓库。

当前选用三张 Web 工作台与三张控制台实拍，来自 2026-09-13 本机开发构建，分别展示资料修改、网页预览、画布素材连接与版本迭代、模型连接、项目工作区和插件配置，不作为固定发布安装包的验收证据。画布图用于说明工作过程，其中生成内容仅作内部配色参考。

记忆星图与 Web 终端章节另选用四张对应 `v8-os-v2026.09.16.1` 的组件验收画面。星图使用隔离环境中的示例数据，终端展示合成负载回放，页面图注保留这些区别。这些素材不代表真实用户数据、生产规模指标或干净安装验收。仅选定图片进入公开站点，来源清单与运行证据留在站点仓库之外。

新增五张 9 月 17 日已审阅图片：场景参考图集、相机控制、去敏 Admin 配对入口、Android 14 真机连接和首条回复恢复。Phone 来自运行生产代码的 `validation917` 验证应用，不是正式发行 APK 实拍；恢复图为 Engine 持久化的合成 503 案例，不表示云模型回复成功。图片原字节及遮盖保留；几何预览只表达创作方向，不是生成成片。

下载明确指向已核实发布的 `v8-os-v2026.09.17.3`，避免 GitHub `/latest` 忽略预发布而跳到旧版。该版本的 11 个产品文件及校验清单包含桌面、Android Phone、Linux x64 Server 和独立 TUI 包。后续更新先核实发布，再修改 `scripts/build_site.py` 的 `RELEASE_TAG`、重新构建并同步 README 下载链接；新发布不改变旧图来源。

门户支持键盘切换场景、移动导航、原生 FAQ、截图放大、系统减少动态效果偏好和手动暂停动效。没有 JavaScript 时仍能阅读正文、查看全部场景并使用主要导航。Preview、模型配置与第三方费用说明保留在下载附近。

## 浏览器验收

```powershell
pip install -r scripts/requirements-test.txt
python -m playwright install chromium
python scripts/test_browser.py
```

检查桌面/手机、中英切换、场景、FAQ、无 JavaScript、减少动态效果，以及隔离媒体传输夹具下的真实视频解码、字幕、失败提示和截图放大。实际 R2 对象需补充后另行验证。

CI 校验生成物并只上传 `dist`。内部素材指南、行动计划与验收截图保存在本仓库之外，不属于网站发布内容。

## 资源说明

产品图标取自桌面端 `apps/v8-agent-os-shell/assets/icon.png`，光轨为门户原创插画。图标或分享封面变更后，运行 `python scripts/render_social.py`（使用 Playwright 测试依赖），再重新构建。Manrope 字体自托管，许可见 `assets/fonts/OFL.txt`。产品源码、安装包和产品文档统一指向 V8 Agent OS 主仓。
