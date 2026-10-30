"""前端页面无头截图 + 机器检查（ui-selfcheck skill 附带脚本）。

用法（在被测项目根目录执行，输出落在项目的 .tmp/ 下）：

    uv run --with playwright python <skill>/scripts/shot.py \
        --base https://localhost:5173 --page /home@home --page /settings \
        --viewports 1920x1080,390x844

复杂场景（登录态、模拟接口、点开弹窗）用 --scenario JSON，格式见
references/scenario-format.md。

只做截图和机器检查（控制台错误、页面异常、横向溢出、白屏、接口 4xx/5xx），
不做视觉判定——截图由 agent 用 Read 逐张看。任一机器检查失败时退出码为 1。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

from playwright.sync_api import Browser, Page, Route, sync_playwright

# 视口拉到页面全高时的上限：再高的页面截图按段看（MoneyFree 自测经验：
# full_page=True 会让 ECharts 画出界，所以改为放大视口而不是 full_page）
MAX_FULL_HEIGHT = 6000

# 白屏判定：可见文字少于这个字数、且没有图片/画布/SVG
BLANK_TEXT_MIN = 5

# 浏览器自动请求、与页面无关的资源，404 不算问题
IGNORED_URL_SUFFIXES = ("/favicon.ico",)

CHROME_CANDIDATES = (
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
)


@dataclass
class PageSpec:
    """一个待截图的页面及其交互步骤。"""

    key: str
    path: str
    click: list[str] = field(default_factory=list)
    wait_for: str | None = None
    # 预期内的报错（子串匹配），例如专门截「接口失败态」时模拟的 500
    allow_errors: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """一次截图任务的完整配置。"""

    name: str
    base: str
    viewports: list[tuple[int, int]]
    pages: list[PageSpec]
    wait_ms: int = 1500
    full_height: bool = False
    local_storage: dict[str, Any] = field(default_factory=dict)
    storage_state: str | None = None
    mock: dict[str, dict[str, Any]] = field(default_factory=dict)


def parse_viewports(text: str) -> list[tuple[int, int]]:
    """把 "1920x1080,390x844" 解析成 [(1920, 1080), (390, 844)]。"""
    result: list[tuple[int, int]] = []
    for item in text.split(","):
        width, height = item.lower().strip().split("x")
        result.append((int(width), int(height)))
    return result


def parse_page(text: str) -> PageSpec:
    """把 "/settings@settings" 解析成页面规格；没给 key 时由路径推导。"""
    path, _, key = text.partition("@")
    if not key:
        key = path.strip("/").replace("/", "_").replace("?", "_") or "root"
    return PageSpec(key=key, path=path)


def load_scenario(args: argparse.Namespace) -> Scenario:
    """合并 --scenario JSON 与命令行参数，命令行优先。"""
    data: dict[str, Any] = {}
    if args.scenario:
        data = json.loads(Path(args.scenario).read_text(encoding="utf-8"))

    pages = [
        PageSpec(
            key=p.get("key") or parse_page(p["path"]).key,
            path=p["path"],
            click=list(p.get("click", [])),
            wait_for=p.get("wait_for"),
            allow_errors=list(p.get("allow_errors", [])),
        )
        for p in data.get("pages", [])
    ]
    pages += [parse_page(p) for p in args.page or []]

    local_storage = dict(data.get("local_storage", {}))
    for item in args.local_storage or []:
        k, _, v = item.partition("=")
        local_storage[k] = v

    base = args.base or data.get("base")
    if not base:
        sys.exit("缺少 --base（或 scenario 里的 base）")
    if not pages:
        sys.exit("缺少 --page（或 scenario 里的 pages）")

    viewports_text = args.viewports or ",".join(data.get("viewports", ["1920x1080"]))
    return Scenario(
        name=args.name or data.get("name", "default"),
        base=base,
        viewports=parse_viewports(viewports_text),
        pages=pages,
        wait_ms=args.wait_ms if args.wait_ms is not None else data.get("wait_ms", 1500),
        full_height=args.full_height or bool(data.get("full_height", False)),
        local_storage=local_storage,
        storage_state=args.storage_state or data.get("storage_state"),
        mock=dict(data.get("mock", {})),
    )


def find_chrome(explicit: str | None) -> str | None:
    """优先用本机 Chrome（Playwright 自带浏览器可能没下载）。"""
    for candidate in (explicit, os.environ.get("MWJ_BROWSER_PATH")):
        if candidate and Path(candidate).exists():
            return candidate
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return shutil.which("google-chrome") or shutil.which("chromium")


def install_mocks(page: Page, mock: dict[str, dict[str, Any]], root: Path) -> None:
    """按 URL glob 拦截接口并返回固定数据。"""
    for pattern, spec in mock.items():
        page.route(pattern, make_mock_handler(spec, root))


def make_mock_handler(spec: dict[str, Any], root: Path) -> Callable[[Route], None]:
    """生成单条模拟规则的处理函数。

    用工厂而不是默认参数绑定 spec：Playwright 会把 request 作为第二个
    位置参数传进 handler，默认参数会被它覆盖。
    """

    def handler(route: Route) -> None:
        body: str
        if "file" in spec:
            body = (root / spec["file"]).read_text(encoding="utf-8")
        elif "json" in spec:
            body = json.dumps(spec["json"], ensure_ascii=False)
        else:
            body = str(spec.get("body", ""))
        route.fulfill(
            status=int(spec.get("status", 200)),
            content_type=spec.get("content_type", "application/json"),
            body=body,
        )

    return handler


# 在页面里执行的机器检查：横向溢出、白屏
PAGE_CHECK_JS = """
() => {
  const doc = document.documentElement;
  const text = (document.body && document.body.innerText || '').trim();
  const media = document.querySelectorAll('img,canvas,svg,video').length;
  return {
    overflow_x: doc.scrollWidth - doc.clientWidth,
    scroll_height: doc.scrollHeight,
    text_len: text.length,
    media_count: media,
  };
}
"""


def shoot_page(
    browser: Browser,
    scenario: Scenario,
    spec: PageSpec,
    viewport: tuple[int, int],
    out_dir: Path,
    root: Path,
) -> dict[str, Any]:
    """截一个页面在一个视口下的图，并返回该页的检查结果。"""
    width, height = viewport
    context = browser.new_context(
        viewport={"width": width, "height": height},
        ignore_https_errors=True,  # Vite basicSsl 自签证书
        storage_state=scenario.storage_state,
    )
    page = context.new_page()
    console_errors: list[str] = []
    http_errors: list[str] = []

    def on_console(msg: Any) -> None:
        # 资源加载失败 Chrome 会在控制台再报一遍，已由 http_errors 记录，不重复计
        if msg.type == "error" and not msg.text.startswith("Failed to load resource"):
            console_errors.append(msg.text)

    def on_response(resp: Any) -> None:
        if resp.status >= 400 and not resp.url.endswith(IGNORED_URL_SUFFIXES):
            http_errors.append(f"{resp.status} {resp.url}")

    page.on("console", on_console)
    page.on("pageerror", lambda exc: console_errors.append(f"pageerror: {exc}"))
    page.on("response", on_response)
    install_mocks(page, scenario.mock, root)

    url = urljoin(scenario.base.rstrip("/") + "/", spec.path.lstrip("/"))
    step_errors: list[str] = []
    metrics: dict[str, Any] = {
        "overflow_x": 0,
        "scroll_height": height,
        "text_len": 0,
        "media_count": 0,
    }
    shot_height = height
    shot_path = out_dir / f"{spec.key}-{width}x{height}.png"
    try:
        if scenario.local_storage:
            # localStorage 只能在同源页面上写：先打开一次，写完再正式导航
            page.goto(url, wait_until="domcontentloaded")
            page.evaluate(
                "(items) => { for (const [k, v] of Object.entries(items)) "
                "localStorage.setItem(k, typeof v === 'string' ? v : "
                "JSON.stringify(v)); }",
                scenario.local_storage,
            )
            # 预加载那一次产生的报错不算，只统计正式导航之后的
            console_errors.clear()
            http_errors.clear()
        # SPA 路由切换不一定触发 load，等 networkidle 超时也照常往下走
        try:
            page.goto(url, wait_until="networkidle", timeout=20000)
        except Exception as exc:  # noqa: BLE001 - 超时不致命，记下来继续截
            step_errors.append(f"goto: {exc}")
        # 交互步骤失败也要截下当时的样子，并把失败记进结果，不中断整批
        try:
            if spec.wait_for:
                page.wait_for_selector(spec.wait_for, timeout=10000)
            for selector in spec.click:
                page.click(selector, timeout=10000)
                page.wait_for_timeout(500)
        except Exception as exc:  # noqa: BLE001 - 记进结果，继续截图
            step_errors.append(f"step: {exc}")
        page.wait_for_timeout(scenario.wait_ms)

        metrics = page.evaluate(PAGE_CHECK_JS)
        if scenario.full_height and metrics["scroll_height"] > height:
            shot_height = min(int(metrics["scroll_height"]), MAX_FULL_HEIGHT)
            page.set_viewport_size({"width": width, "height": shot_height})
            page.wait_for_timeout(500)
        # 文件名写实际截图尺寸（--full-height 时高度会变）
        shot_path = out_dir / f"{spec.key}-{width}x{shot_height}.png"
        page.screenshot(path=str(shot_path))
    except Exception as exc:  # noqa: BLE001 - 单页失败不影响其他页面
        step_errors.append(f"shot: {exc}")
    finally:
        context.close()

    def is_allowed(err: str) -> bool:
        return any(pattern in err for pattern in spec.allow_errors)

    allowed = [e for e in console_errors + http_errors if is_allowed(e)]
    console_errors = [e for e in console_errors if not is_allowed(e)]
    http_errors = [e for e in http_errors if not is_allowed(e)]
    is_blank = metrics["text_len"] < BLANK_TEXT_MIN and metrics["media_count"] == 0
    overflow = int(metrics["overflow_x"]) > 1
    return {
        "key": spec.key,
        "page": spec.path,
        "viewport": f"{width}x{height}",
        "path": str(shot_path.resolve()) if shot_path.exists() else None,
        "console_errors": console_errors,
        "http_errors": http_errors,
        "step_errors": step_errors,
        "allowed_errors": allowed,
        "overflow_x": int(metrics["overflow_x"]),
        "is_blank": is_blank,
        "ok": not (
            console_errors or http_errors or step_errors or overflow or is_blank
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="前端页面无头截图 + 机器检查")
    parser.add_argument("--scenario", help="场景 JSON 文件")
    parser.add_argument("--name", help="场景名，决定输出子目录")
    parser.add_argument("--base", help="站点根地址，如 https://localhost:5173")
    parser.add_argument("--page", action="append", help="页面：/path[@key]，可重复")
    parser.add_argument("--viewports", help="视口列表，如 1920x1080,390x844")
    parser.add_argument("--wait-ms", type=int, help="页面就绪后再等多少毫秒")
    parser.add_argument(
        "--full-height", action="store_true", help="把视口拉到页面全高再截"
    )
    parser.add_argument(
        "--local-storage", action="append", help="注入 localStorage：key=value"
    )
    parser.add_argument("--storage-state", help="Playwright storage_state 文件")
    parser.add_argument("--chrome", help="浏览器可执行文件路径")
    parser.add_argument(
        "--no-sandbox", action="store_true", help="以 --no-sandbox 启动浏览器"
    )
    parser.add_argument("--out", help="输出根目录，默认 .tmp/screenshots")
    args = parser.parse_args(argv)

    scenario = load_scenario(args)
    root = Path(args.scenario).parent if args.scenario else Path.cwd()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out or ".tmp/screenshots") / scenario.name / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome(args.chrome)
    launch_args = ["--no-sandbox"] if args.no_sandbox else []
    items: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=chrome, headless=True, args=launch_args
        )
        for spec in scenario.pages:
            for viewport in scenario.viewports:
                items.append(
                    shoot_page(browser, scenario, spec, viewport, out_dir, root)
                )
        browser.close()

    manifest = {
        "scenario": scenario.name,
        "base": scenario.base,
        "viewports": [f"{w}x{h}" for w, h in scenario.viewports],
        "generated_at": stamp,
        "browser": chrome or "playwright-bundled",
        "items": items,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    failed = [i for i in items if not i["ok"]]
    for item in items:
        flag = "OK " if item["ok"] else "BAD"
        print(f"{flag} {item['path'] or item['key'] + ' （未截到图）'}")
        for err in item["console_errors"] + item["http_errors"] + item["step_errors"]:
            print(f"     {err}")
        if item["overflow_x"] > 1:
            print(f"     横向溢出 {item['overflow_x']}px")
        if item["is_blank"]:
            print("     疑似白屏")
    print(f"manifest: {manifest_path.resolve()}")
    print(f"共 {len(items)} 张，机器检查未通过 {len(failed)} 张")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
