"""Build a portable .skill ZIP with stable entry order and timestamps."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/pixel-art-studio"


def main():
    dest = ROOT / "dist"
    dest.mkdir(exist_ok=True)
    archive = dest / "pixel-art-studio.skill"
    excluded = {"__pycache__", ".DS_Store", "Thumbs.db"}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(SKILL.rglob("*")):
            if not path.is_file() or excluded.intersection(path.relative_to(SKILL).parts) or path.suffix in {".pyc", ".pyo"}:
                continue
            info = zipfile.ZipInfo(path.relative_to(SKILL.parent).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
    print(f"Built {archive.name}: {archive.stat().st_size} bytes")


if __name__ == "__main__":
    main()
