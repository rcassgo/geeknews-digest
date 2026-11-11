> 타입: app (Python 스크립트) + site (생성된 정적 페이지)
> 코드: `src/` (생성 결과 `site/`)
> 실행: 다이제스트 `python3 src/digest.py` · 페이지 서버 `python3 -m http.server <포트>` (프로젝트 루트에서, 포트는 3000부터 빈 번호) → http://localhost:<포트>/site/
> 배포: GitHub Pages — `main`에 `site/` 변경을 push하면 `.github/workflows/pages.yml`이 배포

# GeekNews RSS 다이제스트

GeekNews RSS 피드의 제목·요약만 읽어 관심 주제(AI 에이전트, 업무 자동화, 클로드) 관련 글을 최대 5건 골라
`digest/YYYY-MM-DD.md`로 저장합니다. 같은 날짜 파일은 덮어씁니다. 기사 본문 페이지는 열지 않습니다.

- 선별·재서술 요약은 로컬 `claude` CLI(`claude -p`, 도구 비활성)로 처리합니다. Claude Code 로그인이 필요합니다.
- 관심 주제·최대 건수는 `src/digest.py` 상단의 `TOPICS`, `MAX_ITEMS`에서 바꿉니다.
- 피드는 항상 최신 20건만 제공합니다. 사이트 목록 페이지는 자동 접근을 차단하므로 읽지 않습니다.

## 정적 페이지

`src/build_site.py`가 `digest/*.md`를 `site/index.html`(날짜 목록)과 `site/YYYY-MM-DD.html`로 변환합니다.
`digest.py` 실행 시 자동으로 다시 만들어지며, 따로 돌리려면 `python3 src/build_site.py`.
원본 마크다운은 http://localhost:<포트>/digest/ 에서도 받을 수 있습니다.
