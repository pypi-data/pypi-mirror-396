import platform
from pathlib import Path
from typing import Optional


def detect_os() -> str:
    """Return Foojay-compatible OS name.

    Follows jbang.sh heuristics and maps to Foojay values when known:
    - macOS -> "macos"
    - Linux (Alpine) -> "alpine-linux"
    - Other Linux -> "linux"
    - Windows -> "windows"
    """
    sys = platform.system().lower()
    if sys.startswith("darwin") or sys == "mac" or sys == "macos":
        return "macos"
    if sys.startswith("linux"):
        # Detect Alpine specifically (Foojay treats this as a distinct OS)
        try:
            if Path("/etc/alpine-release").exists():
                return "alpine-linux"
        except Exception:
            pass
        return "linux"
    if sys.startswith("windows") or sys.startswith("msys") or sys.startswith("cygwin"):
        return "windows"
    # Fallback
    return sys or "linux"

def detect_libc_type() -> Optional[str]:
    """Detect libc for Foojay lib_c_type parameter.

    - Linux: try to distinguish musl vs glibc (default glibc)
    - macOS: jbang.sh uses "libc" but Foojay doesn't require it; omit
    - Windows: jbang.sh uses "c_std_lib" but Foojay doesn't require it; omit
    """
    osname = detect_os()
    if osname not in {"linux", "alpine-linux"}:
        return None
    # Try to detect musl vs glibc heuristically
    try:
        out = os.popen("ldd --version 2>&1").read().lower()
        if "musl" in out:
            return "musl"
        if "glibc" in out or "gnu libc" in out or "gnu" in out:
            return "glibc"
    except Exception:
        pass
    # Fallback to glibc if unsure on Linux
    return "glibc"

def is_windows() -> bool:
    return detect_os() == "windows"