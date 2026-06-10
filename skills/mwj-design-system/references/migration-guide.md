# SCSS → CSS Token 迁移实战规则（MWJ Design System v1.2）

> 基于全平台 90+ 页面/组件重构经验总结，执行旧页面重构时必须遵守。

### 变量映射速查表

| 旧 SCSS 变量 | 新 CSS Token | 备注 |
|---|---|---|
| `$spacing-1` | `var(--space-1)` | 4px |
| `$spacing-2` | `var(--space-2)` | 8px |
| `$spacing-3` | `var(--space-3)` | 12px |
| `$spacing-4` | `var(--space-4)` | 16px |
| `$spacing-5` | `var(--space-5)` | 24px |
| `$spacing-6` | `var(--space-6)` | 32px |
| `$font-size-xs` | `12px` | 直接写像素值 |
| `$font-size-sm` | `12px` | 直接写像素值 |
| `$font-size-base` | `14px` | 直接写像素值 |
| `$font-size-lg` | `16px` | 直接写像素值 |
| `$font-family-mono` | `'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace` | 代码/日志字体 |
| `$text-primary` | `var(--text-primary)` | |
| `$text-secondary` | `var(--text-secondary)` | |
| `$text-regular` | `var(--text-secondary)` | 同 secondary |
| `$text-tertiary` | `var(--text-tertiary)` | |
| `$color-primary` | `var(--color-primary)` | |
| `$color-success` | `var(--color-success)` | |
| `$color-warning` | `var(--color-warning)` | |
| `$color-danger` | `var(--color-danger)` | |
| `$border-color` | `var(--border-base)` | |
| `$border-base` | `var(--border-base)` | |
| `$border-radius` | `var(--radius-sm)` | 8px |
| `$border-radius-sm` | `var(--radius-sm)` | 8px |
| `$border-radius-md` | `var(--radius-md)` | 12px |
| `$border-radius-lg` | `var(--radius-lg)` | 16px |
| `$bg-card` | `var(--bg-card)` | |
| `$bg-page` | `var(--bg-page)` | |
| `$bg-light` | `var(--bg-page)` | |
| `$shadow-sm` | `var(--shadow-sm)` | |
| `$shadow-md` | `var(--shadow-md)` | |
| `$transition-base` | `var(--duration-base) var(--ease-standard)` | |
| `$transition-fast` | `var(--duration-fast) var(--ease-standard)` | |

### Element Plus 变量替换

| 旧 `var(--el-*)` | 新 MWJ Token |
|---|---|
| `var(--el-color-primary)` | `var(--color-primary)` |
| `var(--el-color-primary-dark-2)` | `var(--color-primary-active)` |
| `var(--el-color-primary-light-9)` | `var(--color-primary-bg)` |
| `var(--el-color-primary-light-8)` | `var(--color-primary-bg)` |
| `var(--el-color-danger)` | `var(--color-danger)` |
| `var(--el-color-success)` | `var(--color-success)` |
| `var(--el-color-warning)` | `var(--color-warning)` |
| `var(--el-border-color)` | `var(--border-base)` |
| `var(--el-border-color-lighter)` | `var(--border-base)` |
| `var(--el-fill-color)` | `var(--bg-page)` |
| `var(--el-fill-color-light)` | `var(--bg-page)` |
| `var(--el-fill-color-lighter)` | `var(--bg-page)` |
| `var(--el-text-color-primary)` | `var(--text-primary)` |
| `var(--el-text-color-secondary)` | `var(--text-secondary)` |
| `var(--el-font-size-base)` | `14px` |
| `var(--el-font-size-small)` | `13px` |
| `var(--el-font-size-extra-small)` | `12px` |
| `var(--el-font-size-medium)` | `16px` |
| `var(--el-font-size-extra-large)` | `20px` |

### 硬编码色值替换

| 硬编码值 | 替换为 |
|---|---|
| `#1677ff` / `#409eff` | `var(--color-primary)` |
| `#67c23a` | `var(--color-success)` |
| `#e6a23c` | `var(--color-warning)` |
| `#f56c6c` / `#ef4444` | `var(--color-danger)` |
| `#909399` / `#606266` | `var(--text-secondary)` |
| `#c0c4cc` / `#c9cdd4` | `var(--text-tertiary)` |
| `#f5f7fa` / `#f5f7fb` | `var(--bg-page)` |
| `rgba(0,0,0,0.5)` | `var(--bg-mask)` |
| `color: #fff` | `color: white` |

### 组件替换规则

**el-table → MwjTable（必须）**
```vue
<!-- ❌ 旧 -->
<el-table :data="list" border>
  <el-table-column prop="name" label="名称" />
</el-table>

<!-- ✅ 新 -->
<MwjTable :data="list" border>
  <el-table-column prop="name" label="名称" />  <!-- el-table-column 保持不变！ -->
</MwjTable>
```

> ⚠️ **关键陷阱：** `el-table-column` 是 MwjTable 的 slot，**不得替换为 MwjTable-column**。只替换 `<el-table>` 标签本身。

**el-pagination → MwjPagination（必须）**
```vue
<!-- ❌ 旧 -->
<el-pagination v-model:current-page="page" :total="total" @current-change="load" />

<!-- ✅ 新：包裹在 pagination-wrap div 中 -->
<div class="pagination-wrap">
  <MwjPagination v-model:current-page="page" :total="total" @current-change="load" />
</div>
```

```scss
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-4);
}
```

**el-card → MwjCard（必须）**
```vue
<!-- ❌ 旧 -->
<el-card class="my-card">内容</el-card>

<!-- ✅ 新 -->
<MwjCard class="my-card">内容</MwjCard>
```

### 迁移执行方式

使用 Python 字符串替换（**不要用正则**，避免部分匹配污染）：

```python
# 安全的批量替换方式
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('$spacing-4', 'var(--space-4)'),
    # ... 其他替换
]

for old, new in replacements:
    content = content.replace(old, new)  # 字符串替换，不用 re.sub

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```

> ⚠️ **已知陷阱：** 用正则 `re.sub(r'\$spacing-(\d+)', ...)` 会导致 `$spacingvar(--space-4)` 这类污染。用字符串替换可完全避免。

### 迁移后必须添加的 import

```typescript
// 替换 el-table 后必须添加
import MwjTable from '@/components/mwj/MwjTable/index.vue'

// 替换 el-pagination 后必须添加
import MwjPagination from '@/components/mwj/MwjPagination/index.vue'

// 替换 el-card 后必须添加
import MwjCard from '@/components/mwj/MwjCard/index.vue'
```
