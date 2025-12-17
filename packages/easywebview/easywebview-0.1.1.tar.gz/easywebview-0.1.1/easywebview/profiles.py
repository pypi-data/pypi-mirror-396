from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import Options


def get_default_profile_base_dir() -> Path:
    """
    OS별로 '앱 전용 기본 프로필 루트 폴더'를 계산한다.

    목적:
    - 유지 모드(--persist)에서 storage_path로 사용할 디렉터리의 기본값 제공
    - 삭제(초기화) 작업을 안전하게 하기 위해, 앱 전용 폴더 안에만 기본적으로 삭제 허용

    참고:
    - 외부 라이브러리(platformdirs 등)를 쓰지 않고, 보편적인 경로를 직접 계산한다.
    """
    platform = sys.platform

    # Windows
    if platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "EasyWebView" / "profiles"
        # APPDATA가 없으면 보수적으로 홈 기준 경로를 사용한다.
        return Path.home() / "AppData" / "Roaming" / "EasyWebView" / "profiles"

    # macOS
    if platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "EasyWebView" / "profiles"

    # Linux 및 기타 Unix
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "EasyWebView" / "profiles"
    return Path.home() / ".local" / "share" / "EasyWebView" / "profiles"


def resolve_profile_dir(opt: Options) -> tuple[Path | None, Path]:
    """
    옵션에 따라 실제 사용할 프로필 디렉터리를 결정한다.

    반환:
    - (profile_dir_or_none, default_base_dir)

    규칙:
    - 임시 모드(opt.persist=False) -> profile_dir는 None
    - 유지 모드(opt.persist=True):
      - --profile-dir를 주면 그 경로를 사용
      - 아니면 기본 루트(get_default_profile_base_dir())/profile_name 사용
    """
    base_dir = get_default_profile_base_dir()

    if not opt.persist:
        return None, base_dir

    # 사용자 지정 프로필 디렉터리
    if opt.profile_dir is not None:
        return opt.profile_dir.expanduser().resolve(), base_dir

    # 기본 프로필 디렉터리: base_dir / profile_name
    return (base_dir / opt.profile_name).resolve(), base_dir


def is_safe_deletion_target(profile_dir: Path, base_dir: Path) -> bool:
    """
    '삭제(초기화)'를 안전하게 수행할 수 있는 대상인지 판정한다.

    기본 정책:
    - 앱 전용 기본 루트(base_dir) 하위에 있는 프로필 디렉터리만 안전한 삭제 대상으로 본다.

    예:
    - base_dir = .../EasyWebView/profiles
    - profile_dir = .../EasyWebView/profiles/default  -> 안전(True)
    - profile_dir = C:\\Users\\...\\Desktop           -> 안전(False)
    """
    try:
        return profile_dir.is_relative_to(base_dir)
    except AttributeError:
        # Path.is_relative_to는 Python 3.9+에 존재한다.
        # Python 3.13 기준에서는 항상 존재하지만, 방어적으로 처리한다.
        try:
            profile_dir.relative_to(base_dir)
            return True
        except ValueError:
            return False


def delete_profile_dir_if_allowed(profile_dir: Path, base_dir: Path, allow: bool) -> bool:
    """
    프로필 디렉터리를 삭제(초기화)한다.

    안전장치:
    - base_dir 하위이면 allow=False여도 삭제 허용
    - base_dir 하위가 아니면 allow=True일 때만 삭제 수행

    반환:
    - 실제 삭제가 수행되면 True, 아니면 False
    """
    if not profile_dir.exists():
        return False

    safe_by_default = is_safe_deletion_target(profile_dir, base_dir)
    if not safe_by_default and not allow:
        print(
            f"[경고] 프로필 디렉터리가 앱 전용 폴더 밖에 있어 삭제하지 않습니다: {profile_dir}\n"
            f"       삭제를 허용하려면 --allow-delete-profile-dir 옵션을 추가하십시오.",
            file=sys.stderr,
        )
        return False

    try:
        shutil.rmtree(profile_dir, ignore_errors=False)
        return True
    except Exception as e:
        print(
            f"[오류] 프로필 디렉터리 삭제에 실패했습니다: {profile_dir}\n"
            f"       원인: {e}",
            file=sys.stderr,
        )
        return False


def ensure_dir(path: Path) -> None:
    """
    디렉터리가 존재하도록 보장한다.
    """
    path.mkdir(parents=True, exist_ok=True)
