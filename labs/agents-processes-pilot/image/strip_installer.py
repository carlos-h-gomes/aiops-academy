"""Build-stage only: remove unused package installers from a disposable Alpine root."""
from pathlib import Path
import shutil
import sys


def main() -> None:
    if (
        sys.platform != "linux"
        or sys.version_info[:2] != (3, 14)
        or Path(__file__).resolve() != Path("/tmp/strip_installer.py")
        or not Path("/etc/alpine-release").is_file()
        or not Path("/tmp/libuuid.apk").is_file()
    ):
        raise SystemExit("build_stage_required")
    library = Path("/usr/local/lib/python3.14")
    targets = [
        library / "ensurepip",
        library / "site-packages/pip",
        library / "site-packages/pip-26.2.1.dist-info",
    ]
    for target in targets:
        if target.is_symlink() or not target.resolve().is_relative_to(library):
            raise SystemExit("installer_path_invalid")
        if not target.is_dir():
            raise SystemExit("expected_installer_missing")
        shutil.rmtree(target)
    for filename in ("pip", "pip3", "pip3.14"):
        path = Path("/usr/local/bin") / filename
        if path.is_file() or path.is_symlink():
            path.unlink()
    Path("/tmp/libuuid.apk").unlink()
    Path(__file__).unlink()
    if list((library / "site-packages").glob("pip*")) or (library / "ensurepip").exists():
        raise SystemExit("installer_remains")


if __name__ == "__main__":
    main()
