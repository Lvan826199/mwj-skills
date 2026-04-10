---
name: code-review
description: 自动化代码审查流程。运行代码质量检查工具（Flake8、Black、isort、Mypy），同时进行深度架构审查（SOLID原则、安全风险、代码质量），并提供修复建议。
---

# 代码审查技能

此技能提供自动化的代码审查流程，结合工具检查与资深工程师视角的深度审查，确保代码符合项目规范和质量标准。

## 何时使用

**触发条件：**
- 用户完成代码修改后
- 用户要求进行代码审查
- 用户提交代码前（git commit 之前）
- 用户明确提到 "review"、"检查"、"质量"

**自动触发：**
- 每次使用 Edit/Write 工具修改 Python 代码后
- 创建新的 Python 模块后

---

## 审查流程

### 第一步：预检上下文

- 使用 `git status -sb`、`git diff --stat` 和 `git diff` 确定变更范围
- 如有需要，使用搜索工具查找相关模块、调用方和接口契约
- 识别入口点、所有权边界和关键路径（认证、支付、数据写入、网络）

**边界情况处理：**
- **无变更**：若 `git diff` 为空，告知用户并询问是否审查暂存区或指定提交范围
- **大型 diff（>500 行）**：先按文件汇总，再按模块/功能区域分批审查
- **混合关注点**：按逻辑功能分组，而非按文件顺序

### 第二步：运行代码质量工具

自动按以下顺序执行代码审查：

1. **Flake8** - 代码规范检查
   ```bash
   uv run flake8 app/ --max-line-length=88 --extend-ignore=E203,E501,W503 --statistics
   ```

2. **Black** - 代码格式化
   ```bash
   uv run black app/
   ```

3. **isort** - 导入排序
   ```bash
   uv run isort app/
   ```

4. **Mypy** - 类型检查（可选）
   ```bash
   uv run mypy app/
   ```

### 第三步：SOLID 原则与架构审查

加载 `references/solid-checklist.md` 进行专项检查：

- **SRP（单一职责）**：模块是否承担了不相关的多个职责
- **OCP（开闭原则）**：添加新行为是否需要修改核心逻辑而非扩展
- **LSP（里氏替换）**：子类是否破坏了父类的行为预期
- **ISP（接口隔离）**：接口是否过宽，实现方存在大量未使用的方法
- **DIP（依赖倒置）**：高层逻辑是否直接依赖低层具体实现

提出重构建议时，说明*为何*能改善内聚性/耦合度，并给出最小化、安全的拆分方案。若重构非轻量级，提出渐进式计划而非大规模重写。

### 第四步：冗余代码识别与迭代计划

加载 `references/removal-plan.md` 作为模板：

- 识别未使用、冗余或已关闭特性开关的代码
- 区分**立即可安全删除**与**需要计划后延迟删除**
- 提供包含具体步骤和检查点（测试/指标）的后续计划

### 第五步：安全与可靠性扫描

加载 `references/security-checklist.md` 进行全面检查：

- XSS、注入（SQL/NoSQL/命令注入）、SSRF、路径遍历
- 认证/授权漏洞、缺失的租户检查
- 密钥泄露或 API Key 出现在日志/环境变量/文件中
- 限流缺失、无界循环、CPU/内存热点
- 不安全的反序列化、弱加密算法、不安全的默认配置
- **竞态条件**：并发访问、先检查后操作（TOCTOU）、缺失锁

同时指出**可利用性**和**影响范围**。

### 第六步：代码质量扫描

加载 `references/code-quality-checklist.md` 进行检查：

- **错误处理**：吞掉的异常、过于宽泛的 catch、缺失的错误处理、异步错误
- **性能**：N+1 查询、热路径中的 CPU 密集操作、缺失缓存、无界内存增长
- **边界条件**：null/undefined 处理、空集合、数值边界、差一错误

标记可能导致静默失败或生产事故的问题。

### 第七步：分析工具检查结果

根据工具输出分析问题类型：

#### 常见问题类型

**F401 - 导入但未使用**
- 删除未使用的导入
- 如果是 `__init__.py` 中的导出，添加 `# noqa: F401` 注释

**E712 - 布尔值比较**
- `== True` → `.is_(True)` (SQLAlchemy)
- `== True` → 直接使用变量
- `== False` → `.is_(False)` 或使用 `not`

**F541 - f-string 无占位符**
- 删除不必要的 `f` 前缀
- 或添加实际的占位符

**E501 - 行太长**
- 如果超过 88 字符，拆分成多行
- 或在配置中忽略（已配置）

**E402 - 模块导入不在顶部**
- 如果是在 `sys.path.insert` 之后的导入，添加 `# noqa: E402`

**Pydantic 错误**
- 确保使用正确的类型：`Any` 而不是 `any`
- 使用 `SettingsConfigDict` 而不是内部 `Config` 类

**循环导入**
- 将共享的基类移到独立模块（如 `app/core/base.py`）
- 在函数内部导入而不是模块级别

### 第八步：生成审查报告

```
## 代码审查报告

**审查文件**：X 个文件，Y 行变更
**总体评估**：[批准 / 请求修改 / 仅评论]

---

## 发现问题

### P0 - 严重
（无 或 列表）

### P1 - 高优先级
1. **[文件:行号]** 简要标题
   - 问题描述
   - 修复建议

### P2 - 中优先级
2. （跨章节连续编号）
   - ...

### P3 - 低优先级
...

---

### ✅ 工具检查结果
- Flake8: X 个错误
- Black: 已格式化
- isort: 已排序
- Mypy: X 个类型错误

### 📊 统计信息
- 检查文件数: X
- 发现问题: Y
- 已修复: Z
- 代码质量: 优秀/良好/需改进

## 冗余代码/迭代计划
（如适用）

## 补充建议
（可选改进，不阻塞合并）
```

**行内注释**：针对具体文件的发现使用以下格式：
```
::code-comment{file="path/to/file.py" line="42" severity="P1"}
问题描述及修复建议。
::
```

**无问题时**：若未发现问题，明确说明：
- 检查了哪些内容
- 哪些方面未覆盖（如"未验证数据库迁移"）
- 残余风险或建议的后续测试

### 第九步：确认下一步操作

展示发现后，询问用户如何继续：

```
---

## 下一步

发现 X 个问题（P0: _, P1: _, P2: _, P3: _）。

**您希望如何处理？**

1. **全部修复** - 实施所有建议的修复
2. **仅修复 P0/P1** - 处理严重和高优先级问题
3. **修复指定项** - 告诉我修复哪些问题
4. **无需修改** - 审查完成，不需要实施

请选择一个选项或提供具体指示。
```

**重要**：在用户明确确认之前，不要实施任何修改。这是审查优先的工作流。

---

## 自动修复常见问题

对于以下问题，自动修复并告知用户：

- 删除未使用的导入
- 修复布尔值比较
- 修复 f-string 问题
- 添加必要的 noqa 注释

修复后重新运行检查，确保没有引入新问题。

---

## 项目特定配置

### 配置文件
- `setup.cfg` - 所有工具的配置
- `.pre-commit-config.yaml` - Git pre-commit 钩子

### 代码规范
- 最大行长度: 88 字符
- Python 版本: 3.13
- 格式化工具: Black
- 导入排序: isort (black profile)
- 代码检查: Flake8

### 忽略的规则
- E203: Black 格式化产生的空格
- E501: 行长度（已在 Black 中处理）
- W503: 二元运算符前的换行

---

## 常见修复模式

### 1. 删除未使用的导入
```python
# 修复前
from app.models import User, Text  # Text 未使用

# 修复后
from app.models import User
```

### 2. 修复布尔值比较
```python
# 修复前
if user.is_active == True:

# SQLAlchemy
query.filter(User.is_active == True)

# 修复后
if user.is_active:

query.filter(User.is_active.is_(True))
```

### 3. 修复 f-string
```python
# 修复前
print(f"Hello World")

# 修复后
print("Hello World")
```

### 4. 修复模块导入顺序
```python
# 修复前
import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.models import User

# 修复后
import sys
sys.path.insert(0, str(Path(__file__).parent))
from app.models import User  # noqa: E402
```

### 5. Pydantic v2 配置
```python
# 修复前 (Pydantic v1)
class Settings(BaseSettings):
    class Config:
        case_sensitive = True

# 修复后 (Pydantic v2)
from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
```

---

## 与 Git 集成

### Pre-commit 钩子
项目已配置 pre-commit，会在每次 `git commit` 前自动运行检查：

```bash
# 首次安装钩子
uv run pre-commit install

# 手动运行所有检查
uv run pre-commit run --all-files

# 跳过钩子（不推荐）
git commit --no-verify -m "message"
```

### 建议的工作流程

1. 修改代码
2. 运行代码审查：`uv run flake8 app/ && uv run black app/ && uv run isort app/`
3. 查看审查结果
4. 修复问题
5. 重新审查直到通过
6. 提交代码：`git add . && git commit -m "message"`

---

## 注意事项

⚠️ **重要提醒：**
- Black 会自动修改代码格式，提交前确保运行
- isort 会重新排序导入，可能影响代码
- Flake8 发现的问题必须修复才能通过 pre-commit
- Mypy 类型检查是可选的，但建议启用

📝 **文档更新：**
- 修复问题后，更新相关文档
- 如果修复了 bug，在 commit message 中说明

🔒 **不要忽略：**
- 导入错误 (ImportError)
- 循环导入
- Pydantic schema 错误
- 类型不匹配
- 安全漏洞（P0 级别必须阻塞合并）

---

## 快速命令

```bash
# 完整审查流程
uv run flake8 app/ --max-line-length=88 --extend-ignore=E203,E501,W503 && uv run black app/ && uv run isort app/

# 仅检查不修改
uv run flake8 app/ --diff

# 查看格式化差异
uv run black app/ --diff

# 修复所有问题
uv run black app/ && uv run isort app/
```

---

## 参考资料

| 文件 | 用途 |
|------|------|
| `references/solid-checklist.md` | SOLID 代码异味提示与重构启发式方法 |
| `references/security-checklist.md` | Web/应用安全与运行时风险清单 |
| `references/code-quality-checklist.md` | 错误处理、性能、边界条件 |
| `references/removal-plan.md` | 删除候选项与后续计划模板 |

---

## 示例对话

**用户**: "我刚修改了 auth.py"

**Claude**:
好的，让我对 `app/api/v1/endpoints/auth.py` 进行代码审查...

[运行检查工具 + 深度审查]

✅ 审查完成！发现 2 个问题：
1. 第 8 行：未使用的导入 `timedelta`
2. 第 45 行：布尔值比较 `== True`

已自动修复这些问题。代码现在符合规范。

**用户**: "帮我审查整个项目"

**Claude**:
好的，正在对整个项目进行代码审查...

[运行完整检查 + 架构审查]

📊 审查报告：
- 检查文件：22 个
- Flake8 错误：0
- Black 格式化：已完成
- isort 排序：已完成
- 架构问题：0
- 安全风险：0

✅ 代码质量：优秀，所有检查通过！
