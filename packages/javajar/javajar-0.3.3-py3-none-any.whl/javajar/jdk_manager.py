"""JDK Finder/Installer

This module emulates the logic from a shell snippet (see src/javajar/jbang.sh)
that locates a working JDK and, if none is found, downloads and installs one
via the Foojay Disco API.

Policy used here:
- Prefer a valid JAVA_HOME with a working `javac`.
- Otherwise, if `javac` is on PATH, use the system Java (`java`).
- Otherwise, install a JDK under `~/.ylk_javajar/jdkinstall/<version>` using an
  archive downloaded to `~/.ylk_javajar/jdkdownload/`.
- If `~/.ylk_javajar/jdkinstall/<version>` already exists and has `bin/javac`, reuse it.

Notes:
- Only stdlib is used (urllib, tarfile/zipfile). No network in tests; tests
  monkeypatch network-dependent functions.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import stat
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
from javajar import os_util as osutil

from loguru import logger

# Paths used for download/install (aligned with request)
HOME = Path.home()
# where archives are placed
DOWNLOAD_DIR = HOME / ".ylk_javajar" / "jdkdownload"
# per-version install base (e.g. ~/.ylk_javajar/jdkinstall/21)
INSTALL_BASE = HOME / ".ylk_javajar" / "jdkinstall"
JAVA_NAME = "java.exe" if osutil.is_windows() else "java"
JAVAC_NAME = "javac.exe" if osutil.is_windows() else "javac"


@dataclass
class JdkInfo:
    java_exec: Path
    java_home: Optional[Path]  # where bin/java and bin/javac live
    source: str  # 'JAVA_HOME', 'PATH', 'INSTALLED', 'DOWNLOADED'


def is_executable(p: Path) -> bool:
    try:
        mode = p.stat().st_mode
        return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    except FileNotFoundError:
        return False


def is_valid_jdk_home(jhome: Path) -> bool:
    return (jhome / "bin" / JAVAC_NAME).exists()


def which(cmd: str) -> Optional[str]:
    # Minimal wrapper to avoid bringing in shutil in tests when monkeypatching
    import shutil as _sh
    return _sh.which(cmd)


def detect_arch() -> str:
    m = platform.machine().lower()
    # Normalize common variants
    if m in {"x86_64", "amd64", "x64"}:
        return "x64"
    if m in {"aarch64", "arm64"}:
        return "aarch64"
    if m in {"armv7l", "armv7", "armv8l", "armv8", "arm"}:
        return "arm"
    return m


def archive_type_for_os(osname: str) -> str:
    return "zip" if osname == "windows" else "tar.gz"


def _foojay_packages_url(
        version: str,
        distro: Optional[str] = None,
        osname: Optional[str] = None,
        arch: Optional[str] = None,
        libc: Optional[str] = None,
        archive_type: Optional[str] = None,
) -> str:
    osname = osname or osutil.detect_os()
    arch = arch or detect_arch()
    archive_type = archive_type or archive_type_for_os(osname)

    if distro is None:
        parts = [
            "https://api.foojay.io/disco/v3.0/packages",
            f"?distro={distro}",
            f"&javafx_bundled=false",
            f"&operating_system={osname}",
            f"&package_type=jdk",
            f"&version={version}",
            f"&architecture={arch}",
            f"&archive_type={archive_type}",
            f"&latest=available",
        ]
    else:
        parts = [
            "https://api.foojay.io/disco/v3.0/packages",
            f"?javafx_bundled=false",
            f"&operating_system={osname}",
            f"&package_type=jdk",
            f"&version={version}",
            f"&architecture={arch}",
            f"&archive_type={archive_type}",
            f"&latest=available",
        ]

    # lib_c_type only relevant for Linux; omit for others to avoid filtering everything out
    if libc:
        parts.append(f"&lib_c_type={libc}")
    return "".join(parts)


def fetch_foojay_download_redirect(version: str, distro: Optional[str] = None) -> Tuple[str, str]:
    """
    Query Foojay Disco API for a downloadable package and return
    (redirect_url, suggested_filename_ext).

    The redirect_url can be handed to `download_file` which follows redirects.
    """
    osname = osutil.detect_os()
    libc = osutil.detect_libc_type()

    download_version = version
    download_distro = distro
    if version == "8":
        download_version = "1.8"
        download_distro = ""

    if version == "7":
        download_version = "1.7"
        download_distro = ""

    url = _foojay_packages_url(
        version=download_version, distro=download_distro, osname=osname, libc=libc
    )
    logger.info(f"JDK download list url:{url}")

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Foojay packages query failed: HTTP {resp.status}")
        data = json.loads(resp.read().decode("utf-8"))

    result = data.get("result") or []
    if not result:
        raise RuntimeError("No JDK package found from Foojay for the requested parameters")

    pkg = result[0]
    links = pkg.get("links") or {}
    redirect = links.get("pkg_download_redirect")
    if not redirect:
        raise RuntimeError("Foojay response missing pkg_download_redirect")

    archive_type = pkg.get("archive_type") or archive_type_for_os(osname)
    # Suggested filename based on archive_type
    ext = "zip" if archive_type == "zip" else "tar.gz"
    return redirect, ext


def _download_to(path: Path, url: str) -> None:
    """Download URL to path. Supports file:// for tests and follows redirects."""
    logger.info(f"Downloading JDK from {url} to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    if parsed.scheme == "file":
        # Local copy path
        src = Path(parsed.path)
        if not src.exists():
            raise FileNotFoundError(f"Local file not found: {src}")
        shutil.copyfile(src, path)
        return

    req = urllib.request.Request(url, headers={"User-Agent": "javajar-jdk-installer/1.0"})
    with urllib.request.urlopen(req) as resp, open(path, "wb") as f:
        shutil.copyfileobj(resp, f)


def _unpack(archive: Path, target_dir: Path) -> None:
    """Unpack tar.gz or zip to target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(target_dir)
        return
    # Assume tar.*
    with tarfile.open(archive, "r:*") as tf:
        tf.extractall(target_dir)


def _find_jdk_home_under(root: Path) -> Optional[Path]:
    results: list[str] = []
    for root, dirs, files in os.walk(str(root)):
        if 'bin' in dirs:
            bin_path = os.path.join(root, 'bin')

            # 排除符号链接（快捷方式）
            if os.path.islink(bin_path):
                continue

            javac_path = os.path.join(bin_path, JAVAC_NAME)
            if os.path.isfile(javac_path):
                results.append(root)
    if len(results) == 0:
        return None
    else:
        return Path(results[0])


def _parse_version_spec(version: str) -> Tuple[int, bool] | None:
    """Return (floor_major, is_range_plus) for inputs like '21' or '17+'."""
    is_plus = False
    try:
        if not version:
            return None

        version = version.strip()
        is_plus = version.endswith("+")
        version = version.replace("+", "")
        # handle 1.8 style
        if version.startswith("1."):
            minor = int(version.split(".")[1].split(".")[0].split("_")[0])
            return 8 if minor == 8 else minor, is_plus

        # standard: take leading number
        version_str = ""
        for ch in version:
            if ch.isdigit():
                version_str += ch
            else:
                break

        return int(version_str) if version_str else None, is_plus
    except Exception:
        logger.error("JDK version string conversion to int exception.version:{},is_plus:{}", version, is_plus)
        return None


def _parse_javac_major(output: str) -> Optional[int]:
    """Parse 'javac -version' output to a major integer.

    Examples:
      - 'javac 21.0.1' -> 21
      - 'javac 11.0.22' -> 11
      - 'javac 1.8.0_202' -> 8
    """
    s = (output or "").strip().lower()
    if not s:
        return None
    # expected starts with 'javac '
    if s.startswith("javac "):
        ver = s.split(" ", 1)[1]
    else:
        ver = s

    ver_num, _ = _parse_version_spec(ver)
    return ver_num if ver_num is not None else None


def get_javac_version(javac_path: Optional[Path] = None) -> Optional[int]:
    """Return detected javac major version or None if unknown.

    When javac_path is given it will be used, otherwise 'javac' from PATH.
    """
    cmd = [str(javac_path) if javac_path else JAVAC_NAME, "-version"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception:
        return None
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return _parse_javac_major(out)


def get_javac_version_origin_str(javac_path: Optional[Path] = None) -> Optional[str]:
    """Return detected javac major version or None if unknown.

    When javac_path is given it will be used, otherwise 'javac' from PATH.
    """
    cmd = [str(javac_path) if javac_path else JAVAC_NAME, "-version"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception:
        return None

    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    s = (output or "").strip().lower()

    if not s:
        return None
    if s.startswith("javac "):
        ver = s.split(" ", 1)[1]
    else:
        ver = s

    return ver


def _version_matches_spec(actual_major: int, version_spec: str) -> bool:
    floor, is_plus = _parse_version_spec(version_spec)
    return actual_major >= floor if is_plus else (actual_major == floor)


def _normalize_version_for_install(version_spec: str) -> str:
    """Return the major string to install (for '17+' -> '17')."""
    floor, _ = _parse_version_spec(version_spec)
    return str(floor)


def _find_installed_matching(version_spec: str) -> Optional[Path]:
    """Find an installed JDK that satisfies version_spec.

    - Exact version like '21' -> look only at INSTALL_BASE/21
    - Range like '17+' -> scan all INSTALL_BASE/* and pick highest >= 17
    """
    floor, is_plus = _parse_version_spec(version_spec)
    if not INSTALL_BASE.exists():
        return None
    if not is_plus:
        candidate = INSTALL_BASE / str(floor)
        jhome = _find_jdk_home_under(candidate)
        return jhome if jhome and is_valid_jdk_home(jhome) else None
    # scan and pick max major
    best: Tuple[int, Optional[Path]] = (-1, None)
    for child in INSTALL_BASE.iterdir():
        if not child.is_dir():
            continue
        try:
            major = int(child.name.split(".")[0])
        except Exception:
            continue
        if major < floor:
            continue
        jhome = _find_jdk_home_under(child)
        if jhome and is_valid_jdk_home(jhome):
            if major > best[0]:
                best = (major, jhome)
    return best[1]


def install_jdk(version: str, distro: str = "temurin") -> JdkInfo:
    """
    Download and install a JDK if not already installed.

    Returns JdkInfo with java_exec pointing at the installed JDK.
    """
    version_to_install = _normalize_version_for_install(version)
    version_dir = INSTALL_BASE / version_to_install
    if version_dir.exists():
        # Already installed?
        jhome = _find_jdk_home_under(version_dir)
        if jhome and is_valid_jdk_home(jhome):
            logger.info(f"JDK already exists, returning directly.jhome:{jhome}")
            return JdkInfo(java_exec=jhome / "bin" / JAVA_NAME, java_home=jhome, source="INSTALLED")

    # Ensure base dirs
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INSTALL_BASE.mkdir(parents=True, exist_ok=True)

    # Query Foojay, download archive

    try:
        redirect_url, ext = fetch_foojay_download_redirect(version_to_install, distro=distro)
    except:
        # 如果异常了，就去掉 distro再重试一次，有时候 有些供应商没有提供对应的 jdk 版本
        redirect_url, ext = fetch_foojay_download_redirect(version_to_install, distro=None)

    archive_path = DOWNLOAD_DIR / f"bootstrap-jdk_{version_to_install}.{ext}"
    _download_to(archive_path, redirect_url)
    logger.info(f"jdk下载完成 path:{archive_path}")

    # Unpack to a tmp dir then activate
    tmp_dir = INSTALL_BASE / f"{version}.tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        _unpack(archive_path, tmp_dir)
        jhome = _find_jdk_home_under(tmp_dir)
        if not jhome:
            # Not found; try considering tmp_dir itself
            jhome = tmp_dir
        if not is_valid_jdk_home(jhome):
            raise RuntimeError("Error installing JDK: unpacked content missing bin/javac")

        # Activate by moving jhome under final version_dir.
        # If jhome is not tmp_dir, move just that folder; else move the whole tmp_dir.
        if version_dir.exists():
            shutil.rmtree(version_dir, ignore_errors=True)
        if jhome == tmp_dir:
            # rename tmp dir to final
            tmp_dir.rename(version_dir)
            final_home = version_dir
            logger.info(f"jdk安装完成(rename) path:{final_home}")
        else:
            # Move inner jdk dir to version dir
            shutil.move(str(jhome), str(version_dir))
            # Clean remaining tmp dir
            shutil.rmtree(tmp_dir, ignore_errors=True)
            final_home = version_dir
            logger.info(f"jdk安装完成(move) path:{final_home}")

        return JdkInfo(java_exec=final_home / "bin" / JAVA_NAME, java_home=final_home, source="DOWNLOADED")
    finally:
        # Leave the downloaded archive in DOWNLOAD_DIR as a cache; do not delete.
        pass


def ensure_jdk(version: str, distro: str = "temurin") -> JdkInfo:
    """
    Ensure a usable JDK is available.

    Order:
      1) JAVA_HOME with javac
      2) javac in PATH -> use system `java`
      3) Installed under ~/.ylk_javajar/jdkinstall/<version>
      4) Download and install via Foojay
    """
    logger.info(f"Checking if JDK exists version:{version},distro:{distro}")
    # 1) JAVA_HOME
    jhome_env = os.environ.get("JAVA_HOME")
    if jhome_env:
        jhome = Path(jhome_env)
        if is_valid_jdk_home(jhome):
            # Verify version matches spec
            v = get_javac_version(jhome / "bin" / JAVAC_NAME)
            if v is not None and _version_matches_spec(v, version):
                logger.info(f"JAVA_HOME exists, version matches, no download needed.jhome:{jhome}")
                return JdkInfo(java_exec=jhome / "bin" / JAVA_NAME, java_home=jhome, source="JAVA_HOME")

    # 2) javac on PATH
    path_javac = which(JAVAC_NAME)
    if path_javac:
        v = get_javac_version()
        if v is not None and _version_matches_spec(v, version):
            # No JAVA_HOME; use `java` from PATH
            logger.info(f"java exists in PATH, version matches, no download needed.jhome:{Path('java')}")
            return JdkInfo(java_exec=Path(JAVA_NAME), java_home=None, source="PATH")

    # 3) Installed under our install base
    jhome = _find_installed_matching(version)
    if jhome and is_valid_jdk_home(jhome):
        logger.info(f"java exists in installation directory, no download needed.jhome:{jhome}")
        return JdkInfo(java_exec=jhome / "bin" / JAVA_NAME, java_home=jhome, source="INSTALLED")

    # 4) Download and install
    return install_jdk(version=version, distro=distro)


def java_list() -> list[str]:
    """
    Return a list of all installed JDKs.
    先检查 java_home、
    再检查 javac命令
    再检查 .ylk_javajar
    """
    all_javas = []

    def add_java_home(jhome: Path):
        try:
            if is_valid_jdk_home(jhome):
                v = get_javac_version_origin_str(jhome / "bin" / JAVAC_NAME)
                all_javas.append(v + " -> " + f"{str(jhome)}/bin/{JAVA_NAME}")
        except:
            pass

    # java_home
    jhome_env = os.environ.get("JAVA_HOME")
    if jhome_env:
        jhome = Path(jhome_env)
        add_java_home(jhome)

    # path
    try:
        path_javac = which("javac")
        if path_javac:
            v = get_javac_version_origin_str()
            all_javas.append(v + " -> " + f"{which('java')}")
    except:
        pass

    # .ylk_javajar
    base_path = Path(INSTALL_BASE)
    if base_path.exists() and base_path.is_dir():
        for subDir in base_path.iterdir():
            add_java_home(subDir)

    return all_javas

    # __all__ = [
    #     "JdkInfo",
    #     "ensure_jdk",
    #     "install_jdk",
    #     # helpers below are intentionally exported to ease testing/mocking
    #     "fetch_foojay_download_redirect",
    #     "_download_to",
    #     "_unpack",
    #     "_find_jdk_home_under",
    #     "is_valid_jdk_home",
    #     "detect_os",
    #     "detect_arch",
    #     "detect_libc_type",
    #     "archive_type_for_os",
    # ]
