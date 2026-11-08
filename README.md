# 🐳 大肥鱼的治愈小窝

无后端、无数据库、无构建依赖的静态表情包展示站。现已接入 **50 张静态表情 + 30 张真正的 GIF 动图**，素材保存在项目本地。

## 本地预览

双击 `site/index.html`，或在项目目录运行：

```sh
python -m http.server 5173 --bind 127.0.0.1 -d site
```

访问 http://localhost:5173 。浏览网页不需要安装任何依赖。

## 展示功能

- 全部、静态、GIF 筛选，可叠加心情分类与关键词搜索。
- 卡片使用轻量静态预览，点开后加载原始 GIF；关闭预览释放动画。
- 放大预览、随机一鱼、左右方向键切换、Esc 关闭。
- 保存原图，保留实际的 GIF / WebP / JPG 扩展名。
- 我的喜欢保存在当前浏览器 localStorage。
- 每张图片可查看来源、署名与原站标注的许可。

## 素材与来源

导入日期：2026-11-08。

- 静态图：[梗鲸](https://aigengtu.com/)，50 张。
- GIF：[蓝色大肥鱼开放档案](https://xn--pssy23gqgbz2d718b.com/gifs.html)，30 张；校验帧数为 4～200 帧。原站有一件 GIF 实际只有单帧，已跳过。
- 原图合计约 109 MB，主要为 GIF；卡片使用预览，GIF 原文件在预览或下载时才加载。
- `site/assets/imported/sources.json` 记录逐图来源、原图 URL、署名、许可、尺寸、帧数、文件大小及 SHA-256。
- 原站部分索引的标题已过期，本地按实际画面校正了标题，并替换了相似素材。

版权归原作者。梗鲸站点说明为非营利粉丝向使用；动图中 11 张标为 CC0，4 张标为投稿者确认授权收录与下载，15 张标为授权状态不明。这里保留原站状态，不将其统一视为开放许可；用于非官方、非商业同人展示；再利用或商业使用需按逐图条件核实。

## 文件结构

```text
site/
  index.html              页面
  styles.css              样式
  app.js                  分类、搜索、收藏和预览交互
  gallery-data.js         80 张素材的数据（支持直接双击打开）
  assets/imported/        原图、GIF 预览与 sources.json
  assets/*.svg            原始鲸鱼演示资源，保留但不进入图库
tools/import_gallery.py  公开素材导入与完整性校验脚本
```

## 维护

修改素材时同步维护 `gallery-data.js` 与 `sources.json`。导入脚本需要 Python、Pillow、BeautifulSoup4 和联网环境：

```sh
python tools/import_gallery.py
```

脚本使用最多 4 个并发请求、重试和本地文件复用，检查图片有效性、动画帧数与文件重复。原站内容可能变化，重新导入后应检查画面和标题。

## 部署

静态服务根目录为 `site`，无需构建。GitHub Pages 发布配置已准备，尚未创建远程仓库或上线。确认发布后，GitHub Actions 会在 `main` 分支更新时自动发布。

- 计划网站（尚未上线）：https://bluefateludi.github.io/blue-fish-nest/
- 计划仓库（尚未创建）：https://github.com/bluefateludi/blue-fish-nest
- 发布内容仅为 `site/`，不包含本地截图、检查脚本输出和缓存。

## 本次验证

已验证 80 张素材的 SHA-256、文件可读性与动画帧数；浏览器验证通过分类、组合筛选、搜索、空结果、收藏持久化、GIF 播放和真实下载，以及桌面与 390px 手机布局。截图保存在 `output/playwright/`。
