# MWJ 下拉框样式规格

本规范用于统一 Mwj 系列项目中的自定义下拉框。它适用于运行配置、筛选器、设备选择、模型选择等需要比浏览器原生 `select` 更稳定视觉表现的场景。

## 设计目标

- 保持白底、浅蓝边框和柔和阴影的 MWJ 视觉语言。
- 箭头位置固定、与右侧边缘保持明确间距，不随文字长度移动。
- 箭头使用连续的实心 V 形轮廓，避免两条独立线段造成“断头”或缺口。
- 下拉菜单支持滚动，选项内容较多时不拉长页面。
- 保留原生 `select` 作为表单值和提交语义的事实来源；自定义层只负责呈现和交互。

## 尺寸与 Token

| 元素 | 规格 |
| --- | --- |
| 触发器最小高度 | `40px` |
| 触发器圆角 | `var(--radius-md)`，默认 `12px` |
| 触发器左内边距 | `var(--space-4)`，默认 `16px` |
| 触发器右内边距 | `44px`，为箭头和文字截断预留空间 |
| 箭头绘制区域 | `14px × 10px` |
| 箭头距右边 | `14px`，不得贴边 |
| 菜单顶部间距 | `8px` |
| 菜单最大高度 | `240px`，超出后滚动 |
| 菜单内边距 | `10px` |
| 选项最小高度 | `40px` |
| 选项圆角 | `var(--radius-md)`，默认 `12px` |
| 选项左右内边距 | `14px` |
| 选项间距 | `4px` |
| 动效时长 | `var(--duration-base)`，默认 `200ms` |

颜色、阴影和字体必须引用项目 Design Token。推荐使用：

- 默认边框：`var(--border-base)`
- Hover 边框：`var(--color-primary-hover)`
- Focus 光环：`var(--shadow-focus)`
- 默认箭头：`var(--gray-500)`
- 展开箭头：`var(--color-primary-active)`
- 选中背景：`var(--color-primary-bg)` 或等价浅蓝 Token
- 菜单背景：`var(--bg-card)`
- 菜单阴影：`var(--shadow-lg)`

## 推荐结构

```html
<div class="custom-select" data-custom-select>
  <select id="model" class="native-select">
    <option value="default">默认模型</option>
  </select>
</div>
```

脚本应在 `.custom-select` 内生成一个按钮式触发器和菜单选项。原生 `select` 隐藏视觉呈现，但不能删除，必须持续同步当前值、表单提交值和键盘可访问语义。

触发器至少应具备：

- `type="button"`
- `aria-haspopup="listbox"`
- `aria-expanded="false|true"`
- 与菜单对应的 `aria-controls`
- 当前值文字的单独容器，支持 `overflow: hidden`、`text-overflow: ellipsis` 和 `white-space: nowrap`
- 箭头单独使用 `aria-hidden="true"`

菜单使用 `role="listbox"`，选项使用 `role="option"` 和 `aria-selected`。不要把长提示语塞进触发器；说明文字放在字段下方，避免控件高度不稳定。

## 箭头实现

推荐用单个连续几何轮廓绘制箭头，不使用两条旋转线段拼接：

```css
.custom-select-caret {
  position: absolute;
  top: 50%;
  right: 14px;
  width: 14px;
  height: 10px;
  background: currentColor;
  clip-path: polygon(0 12%, 50% 76%, 100% 12%, 100% 42%, 50% 100%, 0 42%);
  color: var(--gray-500);
  transform: translateY(-50%);
  transition: color var(--duration-base) var(--ease-standard),
    transform var(--duration-base) var(--ease-standard);
}

.custom-select.open .custom-select-caret {
  color: var(--color-primary-active);
  transform: translateY(-50%) rotate(180deg);
}
```

箭头不得使用字符 `⌄`、`﹀` 或普通文本三角形代替，也不得通过负的右侧偏移贴住边框。若目标环境不支持 `clip-path`，应使用项目图标库中的 SVG 线性图标作为降级方案，并保持相同的 `14px` 右侧安全距离。

## 状态与交互

- 默认：白色或轻微渐变背景，边框使用 `var(--border-base)`。
- Hover：边框切换为主色衍生色，阴影增强；不得改变控件尺寸。
- Focus：显示 `var(--shadow-focus)`，不能只依赖颜色变化。
- Open：触发器保持焦点，箭头旋转 180 度，菜单显示在触发器下方。
- Selected：选项使用浅蓝背景、主色文字，并提供勾选图标或等价非颜色标识。
- Disabled：降低对比度并禁用指针交互，同时保留可读值。
- Empty：菜单显示明确的空状态，不显示空白白框。
- Long text：触发器和选项允许截断；完整内容通过原生 `title`、辅助文本或可访问名称提供。

交互必须支持：点击打开/关闭、点击外部关闭、`Escape` 关闭、`ArrowUp` / `ArrowDown` 移动选项、`Enter` / `Space` 选择、`Home` / `End` 跳转首尾。移动端菜单可以改为固定定位，但左右至少保留 `14px` 页面边距，最大高度仍为 `240px`。

## 验收清单

- [ ] 箭头与右边框有稳定间距，视觉上不贴边。
- [ ] 箭头是完整尖锐的 V 形，没有断口、短横线或被裁掉的尖角。
- [ ] 收起和展开状态方向正确，位置不跳动。
- [ ] 长选项不会撑宽触发器，也不会撑长整个页面。
- [ ] 菜单超过最大高度后出现滚动区域。
- [ ] Hover、Focus、Selected、Disabled 状态可区分且不改变布局。
- [ ] 支持键盘操作、ARIA 状态和点击外部关闭。
- [ ] 在 `375px`、`768px` 和桌面宽度下检查无横向溢出。
- [ ] 开启 `prefers-reduced-motion: reduce` 时关闭或缩短旋转过渡。
