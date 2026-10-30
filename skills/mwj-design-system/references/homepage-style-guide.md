# MwjAppPrefTrace 首页风格参照

本文档从首页（`index.html`）实际生效的样式中提炼，作为其他页面改版时的视觉基准。规范层面以 `mwj-design-system/SKILL.md` 为权威，本文档只记录"首页已经落地的效果"，供快速参照。

---

## 1. 色板

### 品牌色

| 用途 | 变量 | 值 |
|------|------|----|
| 主色 | `--color-primary` | `#1677ff` |
| hover | `--color-primary-hover` | `#4096ff` |
| active | `--color-primary-active` | `#0958d9` |
| 浅底 | `--color-primary-bg` | `#e6f4ff` |
| 浅边 | `--color-primary-border` | `#91caff` |

### 状态色

| 状态 | 主色 | 浅底 |
|------|------|------|
| success | `#22c55e` | `#dcfce7` |
| warning | `#f59e0b` | `#fef3c7` |
| danger | `#ef4444` | `#fee2e2` |

### 灰阶（Slate 10 级）

`--gray-50` #f8fafc ~ `--gray-900` #0f172a，完整定义见 design-system SKILL.md。

### 模块入口四色（首页特有）

| 模块 | 边框 | 左边条 | 图标底 | 箭头 |
|------|------|--------|--------|------|
| 采集工作台 | `#91caff` | `#1677ff` | `#e6f4ff` / `#1677ff` | `#1677ff` |
| 报告中心 | `#86efac` | `#22c55e` | `#e8f8ef` / `#168f55` | `#22c55e` |
| 报告对比 | `#c4b5fd` | `#7b4bd6` | `#f0ecff` / `#704de0` | `#7b4bd6` |
| 指标说明 | `#99e0ee` | `#0787a8` | `#e8f7fb` / `#0787a8` | `#0787a8` |

### 背景

- 页面底色：`--bg-page: #eef2f8`（柔和变体取值，比标准变体更深，卡片层次感更强）
- 顶部渐变：`linear-gradient(180deg, #f8fafd 0, #eef2f8 260px)`
- 卡片底色：`rgba(255,255,255,.9)` 或纯白 `#fff`

---

## 2. 圆角

| 层级 | 变量 | 值 | 用途 |
|------|------|----|------|
| 外壳容器 | `--radius-lg` | `20px` | overview-head 等大容器 |
| 业务卡 | `--radius-md` | `12px` | 所有业务级卡片、模块入口、推荐流程、快速判断 |
| 按钮/输入 | `--radius-sm` | `8px` | button、input、select、小卡片 |
| 胶囊 | `--radius-full` | `9999px` | tag、badge、导航按钮 |

---

## 3. 阴影

| 层级 | 值 | 用途 |
|------|----|------|
| 柔阴影（默认卡片） | `0 8px 22px rgba(15,23,42,.045)` | 业务卡常态 |
| hover 加强 | `0 6px 16px rgba(22,119,255,.12)` | 模块入口 hover |
| focus 光环 | `0 0 0 3px rgba(22,119,255,.15)` | 输入框/按钮 focus |

---

## 4. 间距节奏

- header 高度：`64px`，sticky + 毛玻璃 `backdrop-filter: blur(12px)`
- hero 区 padding：`32px 44px 4px`（顶/左右/底）
- hero 区行间距：`20px`
- 业务卡内 padding：`14-16px`
- 卡片间 gap：`10-14px`
- 底部三栏区左右 padding：`44px`（和 hero 对齐）
- 页脚 margin-top：`8px`

---

## 5. 卡片风格

```
白底 rgba(255,255,255,.9)
+ 1px solid var(--border-base)
+ border-radius: 12px
+ box-shadow: 0 8px 22px rgba(15,23,42,.045)
+ hover: border-color 变蓝 + translateY(-2px) + 阴影加深
+ active: translateY(0) + 阴影收缩
+ transition: 140ms ease
```

---

## 6. 按钮三级

| 级别 | 常态 | hover | 用途 |
|------|------|-------|------|
| primary | 蓝底白字，圆角 8px，shadow | 更亮蓝 | 主操作（开始采集） |
| secondary | 白底灰边 | 边框蓝 + 浅蓝底 | 次操作（打开报告） |
| tertiary | 白底灰边灰字 | 蓝底白字 | 辅助入口（查看报告/报告对比/指标说明） |

---

## 7. 交互反馈

- hover 过渡：`120-140ms ease`
- 可点击元素一律 `cursor: pointer`
- 按下反馈：active 弹回 `translateY(0)` + 阴影收缩
- focus 光环：`0 0 0 3px rgba(22,119,255,.15)`

---

## 8. 导航栏

- sticky 顶部，`height: 64px`
- 背景：`rgba(255,255,255,.94)` + `backdrop-filter: blur(12px)`
- 导航项：灰色文字 `13px 700`，胶囊圆角，hover 浅蓝底 + 蓝字
- 品牌区：32px icon + 文字 `font-weight: 800`

---

## 9. 全局样式

- 滚动条：8px 细条、圆角胶囊滑块、透明轨道（common.css）
- AI 配置弹窗：common.js + common.css 共享组件
- 字体：`"Inter", "HarmonyOS Sans SC", "Microsoft YaHei", "Segoe UI", system-ui, sans-serif`
- 页脚：居中三行，11px 灰色，`border-top: 1px solid`

---

## 10. 其他页面对齐要点

改版其他页面时，重点对齐：

1. **背景色**：`#eef2f8`（已全站统一）
2. **卡片风格**：白底 + border-base + 12px 圆角 + 柔阴影 + hover 上浮
3. **按钮样式**：三级体系，不再用灰底灰字的"看不出能不能点"样式
4. **导航栏**：sticky 毛玻璃 64px，统一的「首页/采集/报告/指标说明」四项
5. **滚动条**：已由 common.css 全站覆盖
6. **表单控件**：自定义下拉箭头、hover 蓝边、focus 光环（报告中心已落地）
7. **页脚**：统一 `.mwj-footer`（common.css）
