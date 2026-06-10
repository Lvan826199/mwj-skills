---
name: mwj-design-system
description: MWJ Design System 前端开发规范执行器 v1.2。当用户需要开发、重构、创建前端页面、Vue 组件、UI 界面、前端样式时，必须使用此 skill 确保所有输出严格遵循 MWJ 设计系统。触发场景包括：用户说"写个页面"、"创建组件"、"重构前端"、"实现 UI"、"设计样式"、"写前端代码"、"开发视图"、"做个表单/表格/卡片/按钮/菜单/导航"、提到 MWJ 设计规范、提到前端重构、要求实现任何 Vue/TypeScript/TailwindCSS 相关的界面代码、涉及测试平台业务组件（用例卡片/缺陷面板/报告看板/AI 对话）。即使用户没有明确提到"设计规范"，只要涉及本项目的前端 UI 开发，都应触发此 skill。
---

# MWJ Design System v1.2 — 前端开发执行规范

本 skill 确保所有前端代码输出严格遵循 Mwj 一体化测试平台设计系统 v1.2。

**规范文档位置：** 目标项目中的 `MWJ_Design_System.md`（18 章完整规范，通常位于项目根目录或 `doc/` 目录；缺失时见 Step 1 降级策略）

**权威优先级：**
1. MWJ Design Token（颜色/圆角/阴影/间距/字体/动效）— 最高优先级，不可覆盖
2. MWJ 组件规范（`Mwj*` / `MwjBiz*` 前缀、Element Plus 封装）
3. MWJ 布局系统（Header 64 / Sidebar 240 / 12 栅格）
4. `ui-ux-pro-max-new` 脚本查询结果 — 补充 UX 最佳实践，不得与 MWJ Token 冲突

---

## 执行流程

每次触发时，严格按三个阶段执行，**不得跳过或乱序**：

---

### Phase 1 · 分析阶段（写代码前）

**Step 1 — 读取 MWJ 设计规范**
在目标项目中查找并读取 `MWJ_Design_System.md`（18 章完整规范，通常位于项目根目录或 `doc/` 目录），确认当前任务适用的 Token、组件、布局规范。

> **降级策略：** 若目标项目中不存在该文件，直接以本 SKILL.md 内的「Design Token 速查」「布局规范」「组件编写规范」章节为准执行，不阻塞任务，但需在输出中告知用户完整规范文档缺失。

**Step 2 — 判断页面/组件类型**

| 类型 | 布局 | 说明 |
|------|------|------|
| 登录页 | 全屏居中 | 极简分栏或居中卡片 |
| 管理类页面 | Header 64px + Sidebar 240px + Content | 用户权限、项目、环境 |
| 接口测试 | 左右分栏面板 | 类 Postman 请求/响应 |
| 功能测试 | 双栏/多栏面板 | 用例编写 + 执行结果 |
| Web 自动化 | 复合面板 | 执行树 + 录制预览 + 日志 |
| 缺陷管理 | 看板流 | 多列状态看板 + 生命周期 |
| 测试报告 | 数据看板 | 大量图表 + Dashboard |

**Step 3 — 决策树：是否调用 `ui-ux-pro-max-new` 补充查询**

```
任务包含图表（ECharts/数据可视化）？
  → YES: 查询 chart domain（图表类型推荐）

任务包含复杂动效/过渡/加载状态？
  → YES: 查询 ux domain（animation/loading）

任务涉及 Vue 特定模式（Pinia/Vue Router/Composable）？
  → YES: 查询 vue stack

任务有明确可访问性要求（aria/键盘/焦点）？
  → YES: 查询 web domain

以上均为 NO（普通组件/表单/表格/卡片）？
  → 跳过补充查询，直接进入 Phase 2
```

补充查询命令（按需选用）。下列 `$UI_SKILL` 指 `ui-ux-pro-max-new` skill 的实际安装目录（通常为 `.claude/skills/ui-ux-pro-max-new` 或 `skills/ui-ux-pro-max-new`，按实际位置替换）：
```bash
# 图表类型推荐
python3 $UI_SKILL/scripts/search.py "trend comparison timeline funnel" --domain chart

# 动效/加载/UX 规范
python3 $UI_SKILL/scripts/search.py "animation loading accessibility z-index" --domain ux

# Vue 栈最佳实践
python3 $UI_SKILL/scripts/search.py "dashboard admin saas" --stack vue

# Web 可访问性规范
python3 $UI_SKILL/scripts/search.py "aria focus keyboard semantic" --domain web
```

> **重要**：补充查询结果仅作参考。若与 MWJ Token 冲突，以 MWJ Token 为准。

---

### Phase 2 · 实现阶段（写代码时）

**Step 4 — 应用 MWJ Token**
所有颜色/圆角/阴影/间距/字体/动效必须引用 `--color-*` / `--radius-*` / `--shadow-*` / `--space-*` / `--duration-*` CSS 变量或对应 Tailwind 语义类名，禁止硬编码任何数值。

**Step 5 — 编写代码**
- 技术栈：Vue3 `<script setup lang="ts">` + TypeScript + TailwindCSS + SCSS
- 组件：基于 Element Plus 二次封装，基础组件用 `Mwj*` 前缀，业务组件用 `MwjBiz*` 前缀
- 图标：Lucide / Tabler / IconPark / HeroIcons（团队选定一套），线性 2px 描边，禁止 emoji 作图标
- 参考 Phase 1 补充查询结果（不覆盖 MWJ Token）

---

### Phase 3 · 交付阶段（提交前）

**Step 6 — 过完整自检清单**（见文末）

---

## SCSS → CSS Token 迁移（旧页面重构）

执行旧页面重构 / SCSS 变量迁移任务时，**必须先读取 `references/migration-guide.md`** 再动手。该文档包含：

- 旧 SCSS 变量 → 新 CSS Token 映射速查表
- Element Plus `--el-*` 变量替换表
- 硬编码色值替换表
- 组件替换规则（el-table / el-pagination / el-card → Mwj*，含 el-table-column 不可替换的陷阱）
- 迁移执行方式（字符串替换，禁用正则）与替换后必须添加的 import

---

## 技术栈要求

| 技术 | 要求 |
|------|------|
| Vue 3 | Composition API + `<script setup lang="ts">` |
| TypeScript | 严格模式，禁止 `any` |
| TailwindCSS | 仅使用语义化 Token 类名，禁止原生色值类名（`bg-blue-500` 等） |
| SCSS | 复杂样式、变量、Mixin |
| Element Plus | 二次封装为 `Mwj*` / `MwjBiz*` 前缀组件，不直接对外使用 |
| Pinia | 状态管理 |
| 图标 | Lucide / Tabler / IconPark / HeroIcons（线性，2px 描边，SVG，禁止 emoji） |

---

## Design Token 速查（v1.2 完整版）

### 颜色

```css
/* 品牌色与衍生 */
--color-primary: #1677FF;
--color-primary-hover: #4096FF;
--color-primary-active: #0958D9;
--color-primary-bg: #E6F4FF;
--color-primary-border: #91CAFF;

/* 状态色（含衍生） */
--color-success: #22C55E;
--color-success-hover: #4ADE80;
--color-success-active: #16A34A;
--color-success-bg: #DCFCE7;

--color-warning: #F59E0B;
--color-danger: #EF4444;
--color-info: #0EA5E9;

/* 中性色阶（Slate 10 阶） */
--gray-50: #F8FAFC;
--gray-100: #F1F5F9;
--gray-200: #E2E8F0;
--gray-300: #CBD5E1;
--gray-400: #94A3B8;
--gray-500: #64748B;
--gray-600: #475569;
--gray-700: #334155;
--gray-800: #1E293B;
--gray-900: #0F172A;

/* 背景与文本（语义层） */
--bg-page: #F5F7FB;
--bg-card: #FFFFFF;
--bg-mask: rgba(15,23,42,0.45);
--text-primary: #0F172A;
--text-secondary: #64748B;
--text-tertiary: #94A3B8;
--text-disabled: #CBD5E1;
--border-base: #E2E8F0;
--border-strong: #CBD5E1;

/* 扩展功能色（高频复用） */
--blue-light: #EAF2FF;
--blue-border: #CFE0FF;
--shadow-blue: rgba(22,119,255,0.08);
--bg-hover: #F8FBFF;
--bg-header: #F8FAFC;
```

### Typography

```css
/* 字体族 */
--font-family-base: 'Inter', 'HarmonyOS Sans SC', 'Microsoft YaHei', system-ui, sans-serif;
--font-family-mono: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace;

/* 字号体系（size / line-height / weight） */
--font-display: 32px / 40px / 600;  /* 大屏数字、登录主标 */
--font-h1: 24px / 32px / 600;       /* 页面主标题 */
--font-h2: 20px / 28px / 600;       /* 模块标题 */
--font-h3: 16px / 24px / 600;       /* 卡片标题 */
--font-body: 14px / 22px / 400;     /* 正文（默认） */
--font-body-strong: 14px / 22px / 500;
--font-caption: 12px / 20px / 400;  /* 辅助说明、表格副信息 */
--font-code: 13px / 20px / 400;     /* 等宽（接口、日志、JSON） */
```

### Spacing（4px 基准）

```css
--space-0: 0;
--space-1: 4px;    /* 图标与文字间距 */
--space-2: 8px;    /* 紧凑间距 */
--space-3: 12px;   /* 表单字段内 */
--space-4: 16px;   /* 默认间距 */
--space-5: 24px;   /* 卡片内边距 */
--space-6: 32px;   /* 模块间距 */
--space-7: 48px;   /* 页面区块间距 */
--space-8: 64px;   /* 大区块 / 顶部留白 */
```

### Radius

```css
--radius-sm: 8px;    /* Tag、小按钮、Input */
--radius-md: 12px;   /* 默认按钮、Select */
--radius-lg: 16px;   /* 弹窗、Drawer */
--radius-xl: 24px;   /* 卡片、容器 */
--radius-full: 9999px; /* 头像、Pill 标签 */
```

**元素圆角推荐对照：**
- Button / Input → `8px`（--radius-sm）
- Select / Dropdown → `12px`（--radius-md）
- Modal / Drawer → `16px`（--radius-lg）
- Card / 大容器 / 看板卡 → `24px`（--radius-xl）
- Pill Tag / Avatar → `9999px`（--radius-full）

### Shadow

```css
--shadow-sm: 0 2px 8px rgba(15, 23, 42, 0.04);   /* 卡片默认 */
--shadow-md: 0 8px 24px rgba(15, 23, 42, 0.06);  /* 悬浮 / Hover */
--shadow-lg: 0 16px 40px rgba(15, 23, 42, 0.08); /* 弹窗 / Drawer */
--shadow-focus: 0 0 0 3px rgba(22, 119, 255, 0.15); /* 输入聚焦光环 */
```

### Motion

```css
/* 时长 */
--duration-fast: 120ms;   /* 微交互（Hover、按钮） */
--duration-base: 200ms;   /* 默认（弹窗、Tab） */
--duration-slow: 320ms;   /* 大面积切换 */

/* 缓动 */
--ease-standard: cubic-bezier(0.2, 0, 0, 1);
--ease-emphasized: cubic-bezier(0.4, 0, 0.2, 1);
```

**场景动效对照：**
- 按钮 Hover → 背景色渐变 `120ms`
- 卡片 Hover → 微上浮 `translateY(-1px)` + 阴影 Sm → Md
- Modal 打开 → 淡入 + 缩放 `200ms`
- Drawer 打开 → 侧滑入 `320ms`
- 页面切换 → 淡入淡出 `200ms`
- AI 生成 → 打字机逐字 + 光标闪烁
- 加载状态 → Skeleton 呼吸动效 `1.5s infinite`

> 必须支持 `prefers-reduced-motion: reduce`，命中时全局动效缩短至 1ms 或停用。

### Z-index

```css
--z-base: 0;
--z-sticky: 100;
--z-dropdown: 1000;
--z-drawer: 1200;
--z-modal: 1300;
--z-message: 1500;
--z-popover-top: 1800;
```

---

## 布局规范

```
┌──────────────────────── TopNav 64 ─────────────────────────┐
│ Logo  ProjectSwitcher          Search   Help  AI  User    │
├────┬───────────────────────────────────────────────────────┤
│ S  │  Breadcrumb                                           │
│ i  ├───────────────────────────────────────────────────────┤
│ d  │                                                       │
│ e  │              Page Content（1200~1440）                │
│ 240│                                                       │
└────┴───────────────────────────────────────────────────────┘
```

- 顶部导航：`64px`
- 左侧菜单（展开）：`240px` / 收起：`64px`
- 最大宽度：`1920px` / 主内容区：`1440px` / 工作区：`1200px`
- 12 栅格：`grid-template-columns: repeat(12, 1fr); gap: 16px`
- 页面外边距：`24px` / 卡片间距：`16px` / 区块间距：`24px`
- 响应式断点：`sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536 / 3xl 1920`

---

## 组件编写规范

### Button（四种类型 × 四种状态）

| 类型 | Default | Hover | Active | Disabled |
|------|---------|-------|--------|----------|
| Primary | `bg #1677FF` 白字 | `bg #4096FF` | `bg #0958D9` | `opacity 0.4` |
| Outline | 透明底 + `#1677FF` 边 + 蓝字 | `bg rgba(22,119,255,0.05)` | `bg rgba(22,119,255,0.10)` | `opacity 0.4` |
| Text | 透明底 + 蓝字 | 浅蓝底 | 深蓝底 | `opacity 0.4` |
| Danger | `bg #EF4444` 白字 | `bg #F87171` | `bg #DC2626` | `opacity 0.4` |

尺寸：`sm 28px` / `md 32px`（默认） / `lg 40px`

```vue
<template>
  <button class="mwj-btn-primary">
    <LucideIcon name="check" class="w-4 h-4" />
    <span>确认</span>
  </button>
</template>

<style lang="scss" scoped>
.mwj-btn-primary {
  height: 32px;
  padding: 0 var(--space-4);
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-standard);

  &:hover { background: var(--color-primary-hover); }
  &:active { background: var(--color-primary-active); }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}
</style>
```

### Card

```vue
<style lang="scss" scoped>
.mwj-card {
  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--duration-base) var(--ease-standard);

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
}
</style>
```

### Input / Form

```vue
<style lang="scss" scoped>
.mwj-input {
  height: 40px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-base);
  padding: 0 12px;
  font-size: 14px;
  transition: border-color var(--duration-base), box-shadow var(--duration-base);

  &:hover { border-color: var(--gray-300); }
  &:focus {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-focus);
    outline: none;
  }
  &:disabled {
    background: var(--gray-100);
    cursor: not-allowed;
  }
}
</style>
```

- 必填标签带红色 `*`，label 使用 `<label for>` 关联 input
- 校验文案位置：字段下方左对齐，`12px / 20`，错误用 `--color-danger`
- 文本域支持字数统计（`0 / 200`）

### Table

```scss
.mwj-table {
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  overflow: hidden;

  th {
    background: var(--bg-header);
    font-weight: 600;
    height: 52px;
  }

  tr {
    height: 52px; /* 标准 52px / 紧凑 40px */
    transition: background var(--duration-fast);
  }
  tr:hover { background: var(--bg-hover); }
  tr.selected { background: var(--blue-light); }
}
```

**测试业务状态色映射（Tag）：**
- Pass / 通过 → `--color-success` 绿
- Fail / 失败 → `--color-danger` 红
- Running / 运行中 → `--color-primary` 蓝
- Block / 阻塞 / 等待 → `--color-warning` 橙
- Idle / 未执行 → `--gray-500` 灰

**MwjTag 组件（必须使用，禁止 el-tag）：**
```html
<!-- 路径：src/components/mwj/MwjTag/index.vue -->
<!-- Props: type = 'primary' | 'success' | 'warning' | 'danger' | 'info' -->
<MwjTag type="success">通过</MwjTag>
<MwjTag type="danger">失败</MwjTag>
<MwjTag type="warning">阻塞</MwjTag>
<MwjTag type="info">未执行</MwjTag>
<MwjTag type="primary">运行中</MwjTag>
```
- Pill 形（radius-full），无边框，font-weight 600
- 背景用 `--color-{type}-bg`，文字用 `--color-{type}-active`
- info 类型：背景 `--gray-100`，文字 `--gray-600`

### AI 模块

```scss
.mwj-ai-panel {
  background: linear-gradient(180deg, rgba(22,119,255,0.05), rgba(22,119,255,0.02));
  border: 1px solid var(--blue-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

/* AI Chat 气泡 */
.user-message {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  padding: var(--space-3);
}

.ai-message {
  background: #F8FAFC;
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: var(--space-3);
}
```

**AI Streaming 规范：**
- 打字机效果：`20~40 字/秒`，可被「停止生成」打断（热键 `Esc`）
- 突进式输出：代码块、JSON、表格类结构允许整段渲染
- 思考状态：三点呼吸动画 + 文案示例：`AI 助手正在分析用例需求，生成测试步骤…`
- 操作按钮：`停止生成` / `重新生成` / `复制` / `反馈（👍 👎）`

### Menu

- 宽度 `240px`，折叠 `64px`，菜单项高度 `48px`
- 项目内左侧导航必须采用两级手风琴：一级 section（如项目基础、测试能力）同一时间只展开一个；section 内分组（如功能测试、接口测试）同一时间也只展开一个
- 路由变化必须以当前页面所属 section / group 为准同步展开状态；进入概览等无子菜单页面时，应收起其他 section 及其历史子菜单展开态
- 选中态：左侧 `3px` 蓝色指示条 + `--blue-light` 背景 + `--color-primary` 文字
- 图标：Lucide / Tabler / IconPark / HeroIcons，`18~20px`（默认 `20px`），`2px` 描边

**项目内导航两级手风琴规则（强制）：**
- `/project/:id/*` 页面必须使用 `ProjectTopBar` + `ProjectSideNav` + `ProjectBreadcrumb` + `project-main` 骨架。
- `ProjectSideNav` 的 section 层（项目基础 / 测试能力 / 质量协作 / 效率工具）同一时间只能展开一个。
- section 内带二级入口的 group（功能测试 / 接口测试 / Web 自动化 / App 自动化 / 数据工厂等）同一时间也只能展开一个。
- 路由变化时自动展开当前页面所属 section/group；进入概览、成员、变量、缺陷等无二级入口页面时，必须收起其他 section 和旧 group。
- 验收时必须覆盖：从有二级入口模块切到无二级入口页面、跨 section 切换、刷新后 active section/group、面包屑和 active 高亮一致。

---

## TailwindCSS 使用规则

```html
<!-- ❌ 禁止直用默认色值类 -->
<div class="bg-blue-500 text-red-600 rounded-lg shadow-md">

<!-- ✅ 必须使用 Token 化语义类 -->
<div class="bg-primary text-white rounded-sm shadow-sm">
<div class="bg-bg-page text-text-primary border-border">
```

所有颜色、圆角、阴影通过 `tailwind.config.js` 映射到 MWJ Design Token。

**必须扩展 tailwind.config.js：**
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#1677FF', hover: '#4096FF', active: '#0958D9' },
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        'bg-page': '#F5F7FB',
        'text-primary': '#0F172A',
        'border-base': '#E2E8F0',
        // ... 其他 Token
      },
      borderRadius: { sm: '8px', md: '12px', lg: '16px', xl: '24px' },
      boxShadow: {
        sm: '0 2px 8px rgba(15, 23, 42, 0.04)',
        md: '0 8px 24px rgba(15, 23, 42, 0.06)',
        lg: '0 16px 40px rgba(15, 23, 42, 0.08)',
        focus: '0 0 0 3px rgba(22, 119, 255, 0.15)',
      },
    },
  },
};
```

---

## 数据状态规范

任何承载数据的视图必须显式实现以下五种状态：

| 状态 | 视觉 | 文案 |
|------|------|------|
| Loading | `MwjSkeleton` 占位（保留布局骨架） | — |
| Empty | `MwjEmpty` 居中插画 + 引导操作 | "暂无数据，去新建" |
| Error | 错误插画 + 重试按钮 + 错误码 | "加载失败，请重试" |
| Forbidden | 锁形插画 + 申请权限入口 | "无访问权限" |
| Not Found | 404 插画 + 返回首页 | "页面不存在" |

> 严禁直接显示空白屏或浏览器原生错误。

---

## 可访问性规范

| 项 | 要求 |
|------|------|
| 文本对比度（正文） | WCAG AA ≥ `4.5:1`，AAA ≥ `7:1` |
| 大字（≥18px / ≥14px Bold）对比度 | ≥ `3:1` |
| 可点击区域 | ≥ `44 × 44 px` |
| 键盘可达 | 所有交互元素必须 Tab 可达，顺序符合视觉顺序 |
| 焦点可见 | 统一使用 `--shadow-focus` 光环 |
| ARIA | 所有自定义控件必须正确声明 `role` / `aria-*` |
| 图片 | 有意义的图片必须有 `alt` 属性 |
| 表单 | `<label for>` 关联 input，不能只用 placeholder |
| 色盲友好 | 状态不仅靠颜色区分，需配图标 / 文案 |
| 动效降级 | 必须响应 `prefers-reduced-motion` |

---

## 交付前完整自检清单

### MWJ Token 合规

- [ ] 所有颜色引用 `--color-*` / `--gray-*` Token（无硬编码色值）
- [ ] 圆角使用 `--radius-*` Token
- [ ] 阴影使用 `--shadow-*` Token
- [ ] 间距使用 `--space-*` Token
- [ ] 字体使用 `--font-*` Token
- [ ] 动效时长使用 `--duration-*` / `--ease-*` Token
- [ ] TailwindCSS 类名全部为语义化 Token 映射（无 `bg-blue-500` 等）
- [ ] 基础组件使用 `Mwj*` 前缀，业务组件使用 `MwjBiz*` 前缀

### 视觉质量

- [ ] 字体使用 `--font-family-base` / `--font-family-mono`
- [ ] 图标使用 Lucide / Tabler / IconPark / HeroIcons SVG（无 emoji 图标）
- [ ] 所有图标尺寸一致（菜单 18-20px / 按钮 16px / Dashboard 24px）
- [ ] Hover 状态不引起布局偏移（用 `opacity/color/shadow`，不用 `scale`）
- [ ] 布局符合 Header 64px + Sidebar 240px 规范

### 交互质量

- [ ] 所有可点击元素有 `cursor-pointer`
- [ ] Hover 有明确视觉反馈（颜色/阴影/边框变化）
- [ ] 过渡动效 `120~320ms`，使用 `transform/opacity`
- [ ] 异步操作期间按钮禁用
- [ ] 支持 `prefers-reduced-motion`

### 数据状态

- [ ] 实现 Loading / Empty / Error / Forbidden / Not Found 五种状态
- [ ] Loading 使用 Skeleton 占位，不用 Spinner
- [ ] Empty 有引导操作（"去新建" 等）
- [ ] Error 有重试按钮 + 错误码

### 可访问性

- [ ] 文本对比度 ≥ 4.5:1
- [ ] 可点击区域 ≥ 44×44px
- [ ] 图片有 `alt` 属性
- [ ] 表单 input 有 `<label for>` 关联
- [ ] Focus 态可见（蓝色外发光）
- [ ] 颜色不是唯一信息载体

### 布局响应

- [ ] 无横向滚动（375px / 768px / 1024px / 1440px 均正常）
- [ ] 固定导航不遮挡内容
- [ ] 容器 max-width 统一（`1440px`）
- [ ] z-index 使用规范层级（100/1000/1200/1300/1500/1800）

---

## 风格关键词

```
Modern AI Testing SaaS | White & Blue | Minimal | Light Glassmorphism
Soft Shadow | Enterprise Dashboard | High Whitespace | Light UI
```

**核心特征：**
- 大面积白色背景 + 蓝色科技主色 + 浅灰边框
- 卡片化布局 + 中低对比度 + 极简 SaaS 风格
- AI 科技感（浅蓝渐变 + 微动效 + 流式输出）
- 高信息密度 + 专业企业风格

**适用场景：**
测试平台、AI Agent 平台、自动化平台、运维平台、数据分析平台、企业后台系统。

---

## 最终原则

```
Token（设计令牌） → Component（组件系统） → Page（页面装配）
```

- ✅ 所有 UI 必须基于 Design System / Component System / Layout System
- ✅ 所有颜色、间距、字号必须来自 Token
- ✅ 所有数据视图必须实现 5 种数据状态
- ✅ 所有 AI 输出必须可控（停止 / 重生 / 反馈）
- ❌ 禁止单页定制 UI
- ❌ 禁止硬编码色值、间距、字号
- ❌ 禁止多套 UI 风格混用

---

> 本规范基于 MWJ_Design_System.md v1.2（18 章完整规范），所有页面与组件开发必须严格遵循。

