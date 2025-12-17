# Complete

## 2025-12-15

- 코드 분리: `easywebview/` 패키지로 모듈화 (`cli.py`, `default_page.py`, `profiles.py`)
- `pywebview` 미설치 상태에서도 `--help` / `help` 명령이 동작하도록 의존성 지연 import 적용
- 기본 안내 페이지 한/영 자동 전환(i18n) 추가
- `--lang {auto,ko,en}` 옵션 추가 및 기본 안내 페이지에 반영
- 기본 안내 페이지의 예시 실행 명령어를 실행 방식에 맞게 동적으로 생성
- CLI 옵션 도움말을 그룹화/상세화하고 예시/주의사항 추가
- Pylance(Pyright) `reportUnknownMemberType` 경고를 줄이기 위해 `webview`를 `Any`로 캐스트 후 `create_window`/`start` 호출
- `README.md` 작성(로고 `logo.png` 사용)
- `pyproject.toml` 추가(hatchling, 콘솔 스크립트 `easywebview`, optional extras `qt`/`gtk` 등)
- `easywebview/py.typed` 추가(PEP 561)
- 패키지 빌드/검증: `python -m build` 및 `twine check dist/*` 확인
- `.gitignore` 추가(빌드 산출물/가상환경 무시)
