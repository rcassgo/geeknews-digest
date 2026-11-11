#!/usr/bin/env python3
"""digest/*.md 를 정적 HTML로 변환해 site/ 에 쓴다.

- site/index.html      : 날짜별 다이제스트 목록 (최신순, 카드 그리드)
- site/YYYY-MM-DD.html : 세 줄 요약 + 기사 카드 그리드
디자인: 회색 바탕 위 흰 카드, 파랑 단일 강조색, 큰 라운드, 해요체 카피.
다이제스트 형식(제목·번호목록·문단·링크)만 다루는 최소 파서라 외부 의존성이 없다.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "digest"
OUT = ROOT / "site"

FONT = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'

CSS = """
:root{
  --blue-500:oklch(0.620 0.191 258);--blue-50:oklch(0.959 0.020 250);
  --grey-900:oklch(0.237 0.020 258);--grey-700:oklch(0.460 0.028 256);--grey-600:oklch(0.562 0.025 254);
  --grey-500:oklch(0.666 0.021 253);--grey-400:oklch(0.779 0.016 251);--grey-200:oklch(0.930 0.005 248);
  --grey-100:oklch(0.966 0.003 248);
  --bg:var(--grey-100);--surface:oklch(1 0 0);--line:var(--grey-200);
  --fg:var(--grey-900);--fg-2:var(--grey-700);--fg-3:var(--grey-500);
  --accent:var(--blue-500);--accent-weak:var(--blue-50);
  --shadow-2:0 4px 12px oklch(0.155 0.060 261 / 0.06),0 1px 2px oklch(0.155 0.060 261 / 0.04);
  --ease:cubic-bezier(0.22,0.61,0.36,1);
}
@media (prefers-color-scheme:dark){:root{
  --bg:oklch(0.174 0.006 286);--surface:oklch(0.247 0.013 285);--line:oklch(0.361 0.019 285);
  --fg:oklch(1 0 0);--fg-2:oklch(0.818 0.004 286);--fg-3:oklch(0.701 0.009 286);
  --accent:oklch(0.700 0.160 258);--accent-weak:oklch(0.300 0.062 267);
  --shadow-2:0 4px 12px oklch(0 0 0 / 0.30);
}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;
  font-size:15px;line-height:1.5;letter-spacing:-0.005em;-webkit-font-smoothing:antialiased}
main{max-width:1080px;margin:0 auto;padding:40px 24px 80px}
a{color:inherit;text-decoration:none}
.back{display:inline-flex;align-items:center;gap:4px;min-height:44px;color:var(--fg-2);font-weight:600}
.back:hover{color:var(--fg)}
.eyebrow{margin:0 0 8px;color:var(--fg-3);font-size:13px;font-weight:600}
h1{margin:0;font-size:28px;line-height:1.3;font-weight:700;letter-spacing:-0.02em}
.lead{margin:8px 0 0;color:var(--fg-2);font-size:17px}
.section-title{margin:48px 0 16px;font-size:20px;font-weight:700;letter-spacing:-0.015em;display:flex;align-items:center;gap:8px}
.count{font-size:13px;font-weight:600;color:var(--accent);background:var(--accent-weak);border-radius:999px;padding:3px 10px}
.num{font-variant-numeric:tabular-nums}

.hero{margin-top:32px;background:var(--surface);border-radius:24px;padding:28px}
.hero h2{margin:0 0 16px;font-size:17px;font-weight:600}
.hero ol{margin:0;padding:0;list-style:none;display:grid;gap:14px;counter-reset:n}
.hero li{display:grid;grid-template-columns:28px 1fr;gap:12px;font-size:17px;line-height:1.55;color:var(--fg)}
.hero li::before{counter-increment:n;content:counter(n);display:grid;place-items:center;width:28px;height:28px;border-radius:999px;
  background:var(--accent-weak);color:var(--accent);font-size:13px;font-weight:700;font-variant-numeric:tabular-nums;margin-top:1px}

.grid{display:grid;grid-template-columns:1fr;gap:16px}
@media (min-width:641px){.grid{grid-template-columns:repeat(2,1fr)}}
@media (min-width:1024px){.grid{grid-template-columns:repeat(3,1fr)}}

.card{display:flex;flex-direction:column;background:var(--surface);border-radius:20px;padding:24px;
  transition:box-shadow 200ms var(--ease),transform 200ms var(--ease)}
.card:hover{box-shadow:var(--shadow-2);transform:translateY(-2px)}
.card .idx{font-size:13px;font-weight:600;color:var(--fg-3);font-variant-numeric:tabular-nums}
.card h3{margin:8px 0 10px;font-size:18px;line-height:1.45;font-weight:600;letter-spacing:-0.01em}
.card p{margin:0;color:var(--fg-2)}
.card .foot{margin-top:auto;padding-top:20px;display:flex;align-items:center;justify-content:space-between}
.card .src{font-size:12px;font-weight:500;color:var(--fg-3)}
.link{display:inline-flex;align-items:center;gap:2px;min-height:44px;padding:0 4px;margin-right:-4px;
  color:var(--accent);font-weight:600;border-radius:10px;transition:background 120ms var(--ease)}
.link:hover{background:var(--accent-weak)}
.link:focus-visible,.date-card:focus-visible,.back:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.date-card{display:flex;flex-direction:column;gap:6px;background:var(--surface);border-radius:20px;padding:24px;min-height:132px;
  transition:box-shadow 200ms var(--ease),transform 200ms var(--ease)}
.date-card:hover{box-shadow:var(--shadow-2);transform:translateY(-2px)}
.date-card:active,.card:active{transform:none}
.date-card .d{font-size:22px;font-weight:700;letter-spacing:-0.015em;font-variant-numeric:tabular-nums}
.date-card .w{color:var(--fg-3);font-size:13px;font-weight:600}
.date-card .m{margin-top:auto;display:flex;justify-content:space-between;align-items:center;color:var(--fg-2);font-weight:600}
.date-card .m span:last-child{color:var(--fg-3)}

.empty{margin-top:32px;background:var(--surface);border-radius:24px;padding:48px 24px;text-align:center}
.empty strong{display:block;font-size:18px;font-weight:600}
.empty p{margin:6px 0 0;color:var(--fg-2)}
@media (max-width:640px){main{padding:24px 16px 64px}.hero{padding:24px 20px}.card,.date-card{padding:20px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

WEEKDAYS = "월화수목금토일"


def esc(s):
    return html.escape(s, quote=True)


def parse(md):
    """다이제스트 md → {'title', 'lines': [...], 'articles': [{'title','body','link'}]}"""
    d = {"title": None, "lines": [], "articles": []}
    section, cur = None, None
    for raw in md.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("# "):
            d["title"] = s[2:]
        elif s.startswith("## "):
            section = s[3:]
        elif s.startswith("### "):
            cur = {"title": s[4:], "body": [], "link": None}
            d["articles"].append(cur)
        elif re.match(r"\d+\.\s", s) and cur is None:
            d["lines"].append(re.sub(r"^\d+\.\s", "", s))
        elif cur is not None:
            m = re.fullmatch(r"\[[^\]]*\]\((https?://[^)\s]+)\)", s)
            if m:
                cur["link"] = m.group(1)
            else:
                cur["body"].append(s)
    return d


def weekday(date):
    import datetime
    y, m, dd = map(int, date.split("-"))
    return WEEKDAYS[datetime.date(y, m, dd).weekday()] + "요일"


def shell(title, inner):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>{FONT}<style>{CSS}</style></head>
<body><main>
{inner}
</main></body></html>
"""


def article_card(i, a):
    body = "".join(f"<p>{esc(p)}</p>" for p in a["body"])
    link = (f'<a class="link" href="{esc(a["link"])}" target="_blank" rel="noopener">원문 보기<span aria-hidden="true">›</span></a>'
            if a["link"] else "")
    return f"""<article class="card">
  <span class="idx">{i:02d}</span>
  <h3>{esc(a["title"])}</h3>
  {body}
  <div class="foot"><span class="src">GeekNews</span>{link}</div>
</article>"""


def detail_page(date, d):
    head = f"""<a class="back" href="index.html"><span aria-hidden="true">‹</span> 목록으로</a>
<header style="margin-top:16px">
  <p class="eyebrow num">{date} · {weekday(date)}</p>
  <h1>오늘의 AI 소식</h1>
  <p class="lead">AI 에이전트, 업무 자동화, 클로드 관련 글을 골라 짧게 정리했어요.</p>
</header>"""
    if not d["articles"]:
        return head + '<div class="empty"><strong>오늘은 관련 글이 없어요</strong><p>다음 날 다이제스트를 확인해 주세요.</p></div>'
    lines = "".join(f"<li>{esc(t)}</li>" for t in d["lines"])
    hero = f'<section class="hero" aria-label="세 줄 요약"><h2>세 줄로 보면</h2><ol>{lines}</ol></section>' if lines else ""
    cards = "\n".join(article_card(i, a) for i, a in enumerate(d["articles"], 1))
    return f"""{head}
{hero}
<h2 class="section-title">기사 <span class="count num">{len(d["articles"])}건</span></h2>
<div class="grid">
{cards}
</div>"""


def index_page(items):
    head = """<header>
  <p class="eyebrow">GeekNews 다이제스트</p>
  <h1>날짜별로 모아 봤어요</h1>
  <p class="lead">AI 에이전트, 업무 자동화, 클로드 관련 글을 하루 최대 5건씩 정리해요.</p>
</header>"""
    if not items:
        return head + '<div class="empty"><strong>아직 다이제스트가 없어요</strong><p>python3 src/digest.py 를 실행하면 여기에 쌓여요.</p></div>'
    cards = "\n".join(
        f"""<a class="date-card" href="{date}.html">
  <span class="w">{weekday(date)}</span>
  <span class="d">{date}</span>
  <span class="m"><span class="num">{f"기사 {n}건" if n else "관련 글 없음"}</span><span aria-hidden="true">›</span></span>
</a>""" for date, n in items)
    return f"""{head}
<h2 class="section-title">전체 <span class="count num">{len(items)}일</span></h2>
<div class="grid">
{cards}
</div>"""


def build():
    OUT.mkdir(exist_ok=True)
    files = sorted(SRC.glob("????-??-??.md"), reverse=True) if SRC.exists() else []
    items = []
    for f in files:
        date = f.stem
        d = parse(f.read_text(encoding="utf-8"))
        (OUT / f"{date}.html").write_text(shell(f"AI 소식 {date}", detail_page(date, d)), encoding="utf-8")
        items.append((date, len(d["articles"])))
    (OUT / "index.html").write_text(shell("GeekNews 다이제스트", index_page(items)), encoding="utf-8")
    return len(files)


if __name__ == "__main__":
    print(f"{OUT} — 다이제스트 {build()}개")
