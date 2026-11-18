"""MWJ Guide Site 生成脚本：读 site.json，生成 index.html（指南页）+ view.html（文档阅读页）+ files/（可下载文件）到输出目录。
放在项目的 site/ 目录，同目录放 template.html、guide.css、marked.min.js（从 skill 复制）。
site.json 示例：
{
  "title": "某某助手", "logo": "AI", "contact": "维护：某某 · 有问题钉钉找我",
  "version_from": {"file": "../agent.py", "regex": "VERSION = \\"([^\\"]+)\\""},
  "changelog": "../CHANGELOG.md",
  "out": "~/xxx-site",
  "docs": [{"src": "../docs/部署文档.md", "title": "部署文档", "note": "新同事从这里开始"},
           {"src": "../agent.py", "title": "源码", "note": "主程序"}]
}
- docs 第一项会被首屏和第 1 步的「下载」按钮引用（{{DOC0}}）。
- 输出目录不要放桌面 / 文稿（macOS 后台服务读不了）。
用法：python3 -I build_site.py [site.json]"""
import html, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "site.json"), encoding="utf-8"))
rel = lambda p: os.path.normpath(os.path.join(HERE, os.path.expanduser(p)))
OUT = os.path.expanduser(cfg["out"])
os.makedirs(os.path.join(OUT, "files"), exist_ok=True); os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
for f in ("guide.css", "marked.min.js"):
    shutil.copy(os.path.join(HERE, f), os.path.join(OUT, "assets", f))
vf = cfg["version_from"]
ver = re.search(vf["regex"], open(rel(vf["file"]), encoding="utf-8").read()).group(1)
cards, names = [], []
for i, d in enumerate(cfg["docs"]):
    src = rel(d["src"]); name = os.path.basename(src); dst = f"doc{i}" + os.path.splitext(name)[1]
    shutil.copy(src, os.path.join(OUT, "files", dst)); names.append(name)
    kb = os.path.getsize(src) // 1024 + 1
    cards.append(f'<div class="dl"><b>{html.escape(d["title"])}</b><span>{html.escape(d.get("note", ""))} · {kb} KB</span><div class="row">'
                 f'<a href="view.html?f={dst}&n={html.escape(name)}">在线看</a><a href="files/{dst}" download="{html.escape(name)}">下载</a></div></div>')
cl = open(rel(cfg["changelog"]), encoding="utf-8").read().replace("</", "<\\/") if cfg.get("changelog") else ""
page = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
for k, v in {"{{TITLE}}": html.escape(cfg["title"]), "{{LOGO}}": html.escape(cfg.get("logo", cfg["title"][:2])), "{{VER}}": html.escape(ver),
             "{{VER_SHORT}}": html.escape(ver.split()[0]), "{{DOC0}}": html.escape(names[0] if names else ""), "{{CHANGELOG}}": cl,
             "{{DOWNLOADS}}": "".join(cards), "{{CONTACT}}": html.escape(cfg.get("contact", ""))}.items():
    page = page.replace(k, v)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
T = html.escape(cfg["title"]); L = html.escape(cfg.get("logo", cfg["title"][:2]))
open(os.path.join(OUT, "view.html"), "w", encoding="utf-8").write(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{T} · 文档</title><script>try{{var t=localStorage.getItem('qa-theme');if(t&&t!=='auto')document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<link rel="stylesheet" href="assets/guide.css"><style>#c{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:28px 32px;margin-top:20px;overflow-x:auto}}#c pre{{background:var(--surface-soft);padding:14px;border-radius:8px;overflow-x:auto;font-size:13px}}#c table{{border-collapse:collapse;display:block;overflow-x:auto}}#c td,#c th{{border:1px solid var(--border);padding:6px 10px}}#c h1,#c h2,#c h3{{margin:1.2em 0 .5em}}#c p{{margin:.6em 0}}</style>
<script src="assets/marked.min.js"></script></head><body>
<header class="site-header"><div class="header-inner"><a class="brand" href="./"><span class="logo">{L}</span>{T}</a><nav class="header-nav"><a href="./">← 返回指南</a></nav><a class="button ghost" id="dl" download>下载原文件</a></div></header>
<main class="page"><div id="c">加载中…</div></main>
<script>const q=new URLSearchParams(location.search),f=q.get('f')||'',n=q.get('n')||f;
if(!/^doc\\d+\\.[a-z]+$/.test(f)){{document.getElementById('c').textContent='文件不存在';}}else{{
document.getElementById('dl').href='files/'+f;document.getElementById('dl').download=n;document.title=n;
fetch('files/'+f).then(r=>r.text()).then(t=>{{const c=document.getElementById('c');
if(!f.endsWith('.md')){{const p=document.createElement('pre');p.textContent=t;c.replaceChildren(p);}}
else{{c.innerHTML=marked.parse(t.replace(/</g,'&lt;'));}}}});}}</script></body></html>""")
print("网页已生成", OUT, ver)
