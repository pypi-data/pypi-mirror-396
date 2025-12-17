from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, cast

from . import __version__
from .default_page import render_default_html
from .profiles import delete_profile_dir_if_allowed, ensure_dir, resolve_profile_dir


@dataclass(frozen=True)
class Options:
    url: str | None
    width: int
    height: int
    resizable: bool
    always_on_top: bool
    title: str
    debug: bool
    lang: str

    # 스토리지 모드
    persist: bool  # True=유지(고정), False=임시(휘발)
    profile_name: str
    profile_dir: Path | None  # 사용자가 직접 지정한 경우에만 사용
    clear_now: bool
    clear_on_exit: bool
    allow_delete_profile_dir: bool


def normalize_url(raw: str) -> str:
    """
    사용자가 입력한 URL을 간단히 정규화한다.
    - http/https/file 스킴이 없으면 https://를 붙인다.
    """
    url = raw.strip()
    if not url:
        return url

    if url.startswith(("http://", "https://", "file://")):
        return url

    return "https://" + url


def _python_launcher_cmd() -> str:
    return "python" if sys.platform.startswith("win") else "python3"


def _invocation_for_example() -> str:
    argv0_name = Path(sys.argv[0]).name
    lower = argv0_name.lower()

    if lower.startswith("easywebview"):
        return "easywebview"

    if argv0_name == "__main__.py":
        return f"{_python_launcher_cmd()} -m easywebview"

    if argv0_name.endswith(".py"):
        return f"{_python_launcher_cmd()} {argv0_name}"

    return argv0_name or "easywebview"


def _build_usage_example(opt: Options) -> str:
    lang_part = f" --lang {opt.lang}" if (opt.lang and opt.lang != "auto") else ""
    return f"{_invocation_for_example()}{lang_part} --persist --url https://www.google.com"


def parse_args(argv: list[str]) -> Options:
    """
    커맨드라인 인자를 파싱한다.
    """
    class _HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    prog = Path(sys.argv[0]).name
    if prog == "__main__.py":
        prog = "python -m easywebview"

    parser = argparse.ArgumentParser(
        prog=prog,
        description="EasyWebView: pywebview 기반의 독립 WebView 창(간단 브라우저)",
        formatter_class=_HelpFormatter,
        epilog=(
            "Examples:\n"
            "  # 도움말\n"
            "  python3 easywebview.py --help\n"
            "  python3 easywebview.py help\n"
            "  python3 -m easywebview --help\n"
            "\n"
            "  # URL 열기 (임시/프라이빗 모드; 기본값)\n"
            "  python3 easywebview.py --url https://example.com\n"
            "\n"
            "  # 유지 모드 (고정 프로필: 쿠키/LocalStorage 등이 남을 수 있음)\n"
            "  python3 easywebview.py --persist --profile-name work --url https://example.com\n"
            "\n"
            "  # 유지 모드 + 실행 전 초기화\n"
            "  python3 easywebview.py --persist --clear-now --url https://example.com\n"
            "\n"
            "  # 유지 모드처럼 쓰되, 종료 시 삭제(격리 세션)\n"
            "  python3 easywebview.py --persist --clear-on-exit --url https://example.com\n"
            "\n"
            "Notes:\n"
            "  - --persist는 디스크에 프로필을 생성/사용합니다.\n"
            "  - 앱 전용 폴더 밖의 --profile-dir 삭제는 --allow-delete-profile-dir가 필요합니다.\n"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"EasyWebView {__version__}",
    )

    nav_group = parser.add_argument_group("Navigation")
    nav_group.add_argument(
        "--url",
        type=str,
        default=None,
        help=(
            "접속할 URL (http(s)://, file://).\n"
            "- 스킴이 없으면 https://를 자동으로 붙입니다.\n"
            "- 생략하면 기본 안내/입력 페이지를 표시합니다."
        ),
    )

    window_group = parser.add_argument_group("Window")
    window_group.add_argument("--width", type=int, default=1100, help="창 너비(px).")
    window_group.add_argument("--height", type=int, default=720, help="창 높이(px).")
    window_group.add_argument("--no-resize", action="store_true", help="창 크기 조절 비활성화.")
    window_group.add_argument("--always-on-top", action="store_true", help="항상 위(지원 플랫폼 한정).")
    window_group.add_argument("--title", type=str, default="EasyWebView", help="창 제목.")
    window_group.add_argument("--debug", action="store_true", help="pywebview 디버그 모드.")

    ui_group = parser.add_argument_group("UI")
    ui_group.add_argument(
        "--lang",
        choices=["auto", "ko", "en"],
        default="auto",
        help="기본 안내 페이지 언어(자동/한국어/영어). URL 없이 실행할 때만 적용됩니다.",
    )

    storage_group = parser.add_argument_group("Storage / Profile")
    mode_group = storage_group.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--persist",
        action="store_true",
        help=(
            "유지 모드(고정 프로필).\n"
            "- 쿠키/LocalStorage 등이 다음 실행에도 남을 수 있습니다.\n"
            "- 프로필 경로: --profile-dir 또는 (기본 프로필 루트)/(--profile-name)"
        ),
    )
    mode_group.add_argument(
        "--temp",
        action="store_true",
        help=(
            "임시 모드(기본값).\n"
            "- private_mode=True로 실행하여 세션 데이터를 최소화합니다."
        ),
    )

    storage_group.add_argument(
        "--profile-name",
        type=str,
        default="default",
        help="기본 프로필 이름(기본 프로필 경로 사용 시 하위 폴더명). 예: default, work, test",
    )
    storage_group.add_argument(
        "--profile-dir",
        type=str,
        default=None,
        help=(
            "유지 모드에서 사용할 프로필 폴더를 직접 지정합니다(절대/상대 경로).\n"
            "- 지정 시 --profile-name은 무시됩니다."
        ),
    )
    storage_group.add_argument(
        "--clear-now",
        action="store_true",
        help="실행 전에 프로필 폴더를 삭제(초기화)합니다. (--persist에서 의미 있음)",
    )
    storage_group.add_argument(
        "--clear-on-exit",
        action="store_true",
        help="종료 후 프로필 폴더를 삭제(정리)합니다. (--persist에서 의미 있음)",
    )
    storage_group.add_argument(
        "--allow-delete-profile-dir",
        action="store_true",
        help="앱 전용 폴더 밖의 --profile-dir 삭제를 허용합니다(데이터 손실 위험).",
    )

    args = parser.parse_args(argv)

    # temp 플래그가 없고 persist도 없으면 기본은 임시 모드로 처리한다.
    persist = bool(args.persist)

    profile_dir_path: Path | None = None
    if args.profile_dir is not None:
        profile_dir_path = Path(args.profile_dir)

    return Options(
        url=args.url,
        width=max(200, args.width),
        height=max(200, args.height),
        resizable=not args.no_resize,
        always_on_top=args.always_on_top,
        title=args.title,
        debug=args.debug,
        lang=str(args.lang),
        persist=persist,
        profile_name=(args.profile_name.strip() or "default"),
        profile_dir=profile_dir_path,
        clear_now=bool(args.clear_now),
        clear_on_exit=bool(args.clear_on_exit),
        allow_delete_profile_dir=bool(args.allow_delete_profile_dir),
    )


def main(argv: list[str] | None = None) -> int:
    """
    진입점.
    - URL이 있으면: 해당 URL로 시작
    - URL이 없으면: DEFAULT_HTML(드래그/복사/수동입력 기능 포함)을 표시

    스토리지 모드:
    - 임시(기본): private_mode=True (저장 최소화)
    - 유지(--persist): private_mode=False + storage_path=프로필 디렉터리
    """
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == "help":
        argv = ["--help"]

    opt = parse_args(argv)

    # 유지 모드일 때만 프로필 디렉터리를 결정/준비한다.
    profile_dir, base_dir = resolve_profile_dir(opt)

    # --clear-now: 실행 전 초기화
    if opt.persist and profile_dir is not None and opt.clear_now:
        deleted = delete_profile_dir_if_allowed(
            profile_dir=profile_dir,
            base_dir=base_dir,
            allow=opt.allow_delete_profile_dir,
        )
        if deleted:
            # 삭제 후 다시 생성해 둔다(엔진이 쓰기 쉽도록).
            ensure_dir(profile_dir)

    if opt.persist and profile_dir is not None:
        ensure_dir(profile_dir)

    try:
        import webview  # type: ignore
    except ModuleNotFoundError:
        print(
            "[오류] pywebview가 설치되어 있지 않습니다.\n"
            "       설치: pip install -U pywebview",
            file=sys.stderr,
        )
        return 1

    webview_any = cast(Any, webview)
    create_window = cast(Callable[..., Any], webview_any.create_window)
    start = cast(Callable[..., None], webview_any.start)

    if opt.url:
        start_url = normalize_url(opt.url)
        window = create_window(
            title=opt.title,
            url=start_url,
            width=opt.width,
            height=opt.height,
            resizable=opt.resizable,
            on_top=opt.always_on_top,
        )
    else:
        html = render_default_html(
            usage_example=_build_usage_example(opt),
            lang=opt.lang,
        )
        window = create_window(
            title=opt.title,
            html=html,
            width=opt.width,
            height=opt.height,
            resizable=opt.resizable,
            on_top=opt.always_on_top,
        )

    _ = window

    private_mode = not opt.persist
    storage_path_str = str(profile_dir) if (opt.persist and profile_dir is not None) else None

    start(
        debug=opt.debug,
        private_mode=private_mode,
        storage_path=storage_path_str,
    )

    if opt.persist and profile_dir is not None and opt.clear_on_exit:
        delete_profile_dir_if_allowed(
            profile_dir=profile_dir,
            base_dir=base_dir,
            allow=opt.allow_delete_profile_dir,
        )

    return 0
