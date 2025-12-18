from pathlib import Path
import json
import re

def detect():
    # ------------------
    # Next.js (strong)
    # ------------------
    for name in ("next.config.js", "next.config.mjs", "next.config.ts"):
        if Path(name).exists():
            return "nextjs"

    # ------------------
    # Django (strong)
    # ------------------
    if Path("manage.py").exists():
        return "django"

    # ------------------
    # Flask (strong + medium)
    # ------------------
    flask_signals = 0

    # 1. Look for Flask(...) usage
    for py in Path(".").rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"Flask\s*\(", text):
                flask_signals += 2
                break
        except Exception:
            pass

    # 2. .flaskenv
    if Path(".flaskenv").exists():
        flask_signals += 2

    # 3. requirements.txt
    req = Path("requirements.txt")
    if req.exists() and "flask" in req.read_text().lower():
        flask_signals += 1

    # 4. pyproject.toml
    pyproject = Path("pyproject.toml")
    if pyproject.exists() and "flask" in pyproject.read_text().lower():
        flask_signals += 1

    if flask_signals >= 2:
        return "flask"

    # ------------------
    # Node.js
    # ------------------
    pkg = Path("package.json")
    if pkg.exists():
        data = json.loads(pkg.read_text())
        deps = {
            **data.get("dependencies", {}),
            **data.get("devDependencies", {}),
        }
        if "next" in deps:
            return "nextjs"
        return "node"

    # ------------------
    # Docker
    # ------------------
    if Path("docker-compose.yml").exists():
        return "docker"

    return None

