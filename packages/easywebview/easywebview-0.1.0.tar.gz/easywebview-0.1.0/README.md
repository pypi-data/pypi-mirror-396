<p align="center">
  <img src="logo.png" width="180" alt="EasyWebView logo" />
</p>

# EasyWebView

`pywebview` 기반의 “일회용 브라우저(독립 WebView 창)”입니다.  
A tiny standalone WebView window powered by `pywebview`.

## 주요 기능

- URL을 받아서 독립 WebView 창으로 열기
- URL 없이 실행 시 기본 안내 페이지 제공 (URL 직접 입력 + 예시 명령어 드래그/복사)
- 기본값은 임시(프라이빗) 모드: 종료 후 쿠키/LocalStorage 등을 남기지 않는 것을 목표로 함
- `--persist`로 유지(고정 프로필) 모드 지원: 쿠키/LocalStorage 등을 디스크에 저장 가능
- `--clear-now` / `--clear-on-exit`로 프로필 초기화(삭제) 지원
- 안전장치: 기본 프로필 루트 밖의 `--profile-dir` 삭제는 `--allow-delete-profile-dir` 없이는 차단
- 기본 페이지 한/영 자동 전환(시스템 언어가 `ko*`면 한국어, 그 외는 영어)

## 요구사항

- Python 3.10+
- `pywebview` (패키지 의존성으로 함께 설치됨)

## 설치

```bash
# Windows / macOS
pip install -U easywebview

# Linux (택 1)
pip install -U "easywebview[qt]"
# 또는
pip install -U "easywebview[gtk]"
```

## 플랫폼별 참고(=pywebview 의존성)

`easywebview`는 내부적으로 `pywebview`를 사용합니다. 아래 내용은 `pywebview` 설치/의존성과 동일합니다.

### Windows

- 최신 Chromium 기반 WebView를 사용하려면 WebView2 Runtime이 필요할 수 있습니다.
  - https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### macOS

- Standalone Python 사용 시 `pyobjc-*` 계열 패키지가 필요할 수 있습니다(대개 `pywebview`가 플랫폼에 맞게 처리).

### Linux

- Linux는 백엔드 선택이 필요합니다: `easywebview[qt]` 또는 `easywebview[gtk]`
- (Ubuntu 예시) GTK(WebKit2) 의존성:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

- (Ubuntu 예시) Qt 의존성(환경에 따라 다를 수 있음):

```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5-dev
```

## 실행

```bash
# (1) URL 열기 (임시/프라이빗 모드; 기본값)
easywebview --url https://example.com

# (2) URL 없이 실행: 기본 안내 페이지 표시
easywebview

# (3) 모듈 실행도 가능
python3 -m easywebview --url https://example.com

# (4) 소스 체크아웃 상태에서는 파일 실행도 가능
python3 easywebview.py --url https://example.com
```

## 도움말

```bash
easywebview --help
easywebview help

python3 easywebview.py --help
python3 easywebview.py help
python3 -m easywebview --help
```

## 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--url` | 접속할 URL (`http(s)://`, `file://`). 스킴이 없으면 `https://` 자동 추가 | 없음 |
| `--width` | 창 너비(px) | `1100` |
| `--height` | 창 높이(px) | `720` |
| `--no-resize` | 창 크기 조절 비활성화 | 비활성 |
| `--always-on-top` | 항상 위(지원 플랫폼 한정) | 비활성 |
| `--title` | 창 제목 | `EasyWebView` |
| `--debug` | pywebview 디버그 모드 | 비활성 |
| `--lang` | 기본 안내 페이지 언어(`auto`/`ko`/`en`) | `auto` |
| `--persist` | 유지 모드(고정 프로필) | 비활성 |
| `--temp` | 임시 모드(기본값) | 활성 |
| `--profile-name` | 기본 프로필 이름(기본 경로 사용 시 하위 폴더명) | `default` |
| `--profile-dir` | 유지 모드에서 사용할 프로필 폴더를 직접 지정(지정 시 `--profile-name` 무시) | 없음 |
| `--clear-now` | 실행 전에 프로필 폴더 삭제(초기화) | 비활성 |
| `--clear-on-exit` | 종료 후 프로필 폴더 삭제(정리) | 비활성 |
| `--allow-delete-profile-dir` | 기본 프로필 루트 밖의 `--profile-dir` 삭제 허용(주의) | 비활성 |
| `--version` | 버전 출력 | - |

## 스토리지/프로필 동작

- 임시 모드(기본): `private_mode=True`로 실행하여 세션 데이터를 최소화합니다.
- 유지 모드(`--persist`): `private_mode=False` + `storage_path=프로필 경로`로 실행합니다.
- 프로필 경로 결정:
  - `--persist --profile-dir <PATH>`: 지정한 `<PATH>`
  - `--persist --profile-name <NAME>`: OS 기본 루트 아래 `<NAME>`
- 삭제(초기화) 안전장치:
  - 앱 전용 기본 프로필 루트 하위의 프로필만 기본적으로 삭제 허용
  - 그 외 경로 삭제는 `--allow-delete-profile-dir`가 있어야 수행

## 코드 구조

- `easywebview.py`: 실행용 엔트리(래퍼)
- `easywebview/cli.py`: CLI/옵션 파싱 + 실행 로직(필요 시에만 `pywebview` import)
- `easywebview/default_page.py`: 기본 안내 페이지(한/영)
- `easywebview/profiles.py`: 프로필 경로/삭제 안전장치 로직

## 개발(타입 체크)

`pywebview` 타입 스텁이 일부 환경에서 `Unknown`을 포함해 Pylance(Pyright)에서 경고가 날 수 있어, `easywebview/cli.py`에서는 `create_window`/`start`를 `Callable`로 캐스트해 사용합니다.

## PyPI 배포(빌드)

```bash
python -m pip install -U build twine
python -m build
twine upload dist/*
```
