"""Validate local README links case-sensitively and parse shell examples without executing training."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
from ml.common import ROOT, save_json


def exact_path(path):
    path = path.resolve()
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return False
    current = ROOT
    for part in relative.parts:
        if part not in {p.name for p in current.iterdir()}:
            return False
        current = current / part
    return current.exists()


def main():
    source = (ROOT / "README.md").read_text()
    markdown = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", source)
    html = re.findall(r'(?:src|href)="([^"]+)"', source)
    results = []
    for target in markdown + html:
        target = target.strip("<>")
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = unquote(target.split("#")[0])
        valid = exact_path(ROOT / path)
        results.append({"target": target, "exists_with_exact_case": valid})
    scripts = []
    for i, code in enumerate(re.findall(r"```bash\n(.*?)```", source, re.S)):
        r = subprocess.run(["bash", "-n"], input=code, text=True, capture_output=True)
        scripts.append(
            {
                "example": i + 1,
                "shell_syntax_valid": r.returncode == 0,
                "executed": False,
            }
        )
    for name in [
        "scripts/start_backend.sh",
        "scripts/start_frontend.sh",
        "scripts/reproduce.sh",
    ]:
        subprocess.run(["bash", "-n", str(ROOT / name)], check=True)
    report = {
        "local_links_and_images": results,
        "shell_examples": scripts,
        "scope": "Local target existence with exact filename case and bash parsing. Startup/test commands were separately executed; fresh installation and full retraining were not rerun. External docs were opened separately; remote link uptime is not monitored.",
    }
    save_json("reports/v6-readme-validation.json", report)
    assert all(x["exists_with_exact_case"] for x in results), [
        x for x in results if not x["exists_with_exact_case"]
    ]
    assert all(x["shell_syntax_valid"] for x in scripts)
    print(
        f"{len(results)} exact-case local links/assets and {len(scripts)} shell examples verified."
    )


if __name__ == "__main__":
    main()
