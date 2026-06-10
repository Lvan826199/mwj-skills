#!/usr/bin/env python3
"""PreToolUse hook：拦截未经代码审查的 git commit。

确定性字符串匹配，不消耗 LLM 调用：
- 非 git commit 命令直接放行（exit 0）
- git commit 命令若未携带 `# review-passed` 标记则拦截（exit 2），
  提示先用 py-code-review skill 完成审查，确认无 P0/P1 问题后
  在提交命令末尾附加 `# review-passed` 重新提交
"""
import json
import sys


def main() -> int:
    data: dict = json.load(sys.stdin)
    command: str = data.get("tool_input", {}).get("command", "")

    if "git commit" in command and "review-passed" not in command:
        print(
            "已拦截 git commit：请先使用 py-code-review skill 完成代码审查。"
            "确认无 P0/P1 问题后，在提交命令末尾附加注释 `# review-passed` 重新提交，"
            "例如：git commit -m \"fix(scope): 描述\" # review-passed",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
