# V8 Agent OS Site

这是 V8 Agent OS 的公开站点仓库。

它专门用于 Cloudflare Pages，负责：

- 产品介绍页
- 页内文档阅读器
- 安装入口
- 三个产品仓库的导航入口

## 这个仓库负责什么

这个仓库只放静态站点本身。

它**不会**复制三端的主代码。

站点会直接读取：

- `v8-agent-os-engine` 里的安装脚本
- `v8-agent-os-engine` 和 `v8-agent-os-web` 里的公开文档
- 三个公开仓库的链接

这样站点本身保持轻量，但读者看到的文档和安装命令仍然可以跟随公开仓库更新。

## 部署到 Cloudflare Pages

1. 把这个目录单独上传成一个 GitHub 仓库。
2. 在 Cloudflare Pages 里连接这个仓库。
3. 使用下面的设置：
   - Framework preset：`None`
   - Build command：留空
   - Build output directory：`/`
4. 部署即可。

## 本地预览

用任意静态文件服务器都可以。

例如：

```bash
python -m http.server 8789
```

然后打开：

```text
http://127.0.0.1:8789/
```

## 目录结构

- `index.html`：英文首页
- `zh/index.html`：中文首页
- `assets/`：共享样式、脚本和品牌资源

## 赞助

如果这个项目对你有帮助，欢迎支持：

[https://afdian.com/a/justforever17](https://afdian.com/a/justforever17)

English version: [README.md](./README.md)。
