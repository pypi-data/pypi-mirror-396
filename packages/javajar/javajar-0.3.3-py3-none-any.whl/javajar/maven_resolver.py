from pathlib import Path
from typing import List, Optional, Tuple
import shutil
import tempfile
import urllib.error
import urllib.request

from loguru import logger


# Public helpers for Maven coordinates and artifact resolution

def parse_maven_coord(coord: str) -> Tuple[str, str, str, str, Optional[str]]:
    """
    Parse a Maven coordinate string.
    Supported formats:
      - groupId:artifactId:version
      - groupId:artifactId:version:packaging
      - groupId:artifactId:version:packaging:classifier
    Returns (group_id, artifact_id, version, packaging, classifier)
    """
    parts = coord.strip().split(":")
    if len(parts) < 3:
        raise ValueError("Invalid Maven coordinate. Expected at least groupId:artifactId:version")
    group_id, artifact_id, version = parts[0], parts[1], parts[2]
    packaging = "jar"
    classifier: Optional[str] = None
    if len(parts) >= 4 and parts[3]:
        packaging = parts[3]
    if len(parts) >= 5 and parts[4]:
        classifier = parts[4]
    return group_id, artifact_id, version, packaging, classifier


def artifact_filename(artifact_id: str, version: str, packaging: str, classifier: Optional[str]) -> str:
    base = f"{artifact_id}-{version}"
    if classifier:
        base += f"-{classifier}"
    return f"{base}.{packaging}"


def cache_path(group_id: str, artifact_id: str, version: str, filename: str) -> Path:
    """
    Compute cache path for a resolved artifact.
    New layout:
      ~/.ylk_javajar/<groupId as path>/<artifactId>/<version>/<filename>
    Example:
      coord=com.alibaba:fastjson:2.0.31 ->
      ~/.ylk_javajar/com/alibaba/fastjson/2.0.31/fastjson-2.0.31.jar
    """
    home = Path.home()
    group_path = group_id.replace(".", "/")
    cache_dir = home / ".ylk_javajar" / "jars" / group_path / artifact_id / version
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / filename


def build_artifact_url(repo: str, group_id: str, artifact_id: str, version: str, filename: str) -> str:
    repo = repo.rstrip("/")
    group_path = group_id.replace(".", "/")
    return f"{repo}/{group_path}/{artifact_id}/{version}/{filename}"


def download(url: str, dest: Path, verbose: bool = False) -> bool:
    logger.info(f"Attempting to download maven dependency:{url}")
    try:
        with urllib.request.urlopen(url) as resp:
            if resp.status != 200:
                if verbose:
                    logger.info(f"HTTP status: {resp.status}")
                return False
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfileobj(resp, tmp)
                tmp_path = Path(tmp.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_path), str(dest))

        logger.info(f"Maven dependency downloaded successfully:{dest}")
        return True
    except Exception as e:
        logger.exception(f"Exception downloading maven dependency.url={url},dest={dest}")
        return False


def resolve_from_maven(
        coord: str,
        release_repos: List[str],
        snapshot_repos: List[str]
) -> Path:
    """
    Resolve the JAR file path from Maven coordinates. It checks local cache first
    and downloads from provided repositories if missing.
    """
    logger.info(
        "Resolving jar package from maven repository, coord={}, release_repos={}, snapshot_repos={}",
        coord, release_repos, snapshot_repos
    )
    group_id, artifact_id, version, packaging, classifier = parse_maven_coord(coord)
    filename = artifact_filename(artifact_id, version, packaging, classifier)
    dest = cache_path(group_id, artifact_id, version, filename)
    is_snapshot = "SNAPSHOT" in version.upper()

    # If cached, return immediately （快照每次都下载）
    if dest.exists() and not is_snapshot:
        logger.debug(f"Found maven jar locally: {dest}")
        return dest

    # Determine search order
    primary = snapshot_repos if is_snapshot else release_repos
    secondary = release_repos if is_snapshot else snapshot_repos

    tried_urls: List[str] = []

    dest_tmp = Path(str(dest) + ".tmp")

    download_success = False
    for repos in (primary, secondary):
        for repo in repos:
            url = build_artifact_url(repo, group_id, artifact_id, version, filename)
            tried_urls.append(url)
            if download(url, dest_tmp):
                download_success = True
                break
        if download_success:
            break

    if download_success:
        shutil.move(str(dest_tmp), str(dest))

    if dest.exists():
        return dest

    # Not found
    lines = [
        "根据maven坐标,下载jar失败.",
        f"Coordinate: {coord}",
        "Tried URLs:",
        *[f" - {u}" for u in tried_urls],
    ]
    raise FileNotFoundError("\n".join(lines))
