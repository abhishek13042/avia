"""Assemble the folder uploaded to the Hugging Face Space. Usage: python stage.py <out_dir>"""
import shutil
import sqlite3
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
out = Path(sys.argv[1])
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)

for name in ["Dockerfile", "README.md", "nginx.conf", "start.sh"]:
    shutil.copy(here / name, out / name)
shutil.copy(repo / "pyproject.toml", out)
shutil.copytree(repo / "src", out / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
shutil.copytree(repo / "web", out / "web",
                ignore=shutil.ignore_patterns("node_modules", ".next", "tsconfig.tsbuildinfo"))
(out / "model").mkdir()
shutil.copy(repo / "artifacts/t24/final/model.pt", out / "model/model.pt")
(out / "artifacts").mkdir()
shutil.copy(repo / "artifacts/benchmarks.json", out / "artifacts/benchmarks.json")

# Copy the database as one file, with no WAL alongside it.
(out / "seed").mkdir()
src = sqlite3.connect(repo / "storage/avia.db")
dst = sqlite3.connect(out / "seed/avia.db")
src.backup(dst)
dst.execute("PRAGMA journal_mode=DELETE")
dst.close()
src.close()
shutil.copytree(repo / "storage/files", out / "seed/files")
(out / "seed/README.md").write_text("""---
license: cc-by-4.0
pretty_name: AVIA example runs
---

The two example runs shown on the AVIA demo site: a SQLite database and the tracked videos.
The footage comes from APPLE MOTS (De Jong et al., 2022, CC BY 4.0, doi:10.5281/zenodo.5939726).
Code: https://github.com/abhishek13042/avia
""", encoding="utf-8")
print(out)
