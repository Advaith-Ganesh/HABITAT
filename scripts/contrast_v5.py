"""Sample actual V5 CSS tokens. This is not full rendered WCAG certification."""

import re
from ml.common import ROOT, save_json


def contrast(a, b):
    def luminance(color):
        color = color.lstrip("#")
        if len(color) == 3:
            color = "".join(v * 2 for v in color)
        rgb = [int(color[i : i + 2], 16) / 255 for i in [0, 2, 4]]
        rgb = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return sum(c * w for c, w in zip(rgb, [0.2126, 0.7152, 0.0722]))

    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main():
    css = (ROOT / "frontend/src/style.css").read_text()

    def tokens(pattern):
        block = re.search(pattern, css).group(1)
        return dict(re.findall(r"--([\w-]+):\s*(#[a-fA-F0-9]{3,6})", block))

    light = tokens(r":root\s*\{([^}]+)\}")
    dark = {**light, **tokens(r':root\[data-theme="dark"\]\s*\{([^}]+)\}')}
    checks = []
    for theme, values in [("light", light), ("dark", dark)]:
        for fg, bg in [
            ("text", "surface"),
            ("muted", "surface"),
            ("muted", "bg"),
            ("accent", "accent-soft"),
            ("teal", "teal-soft"),
            ("amber", "amber-soft"),
            ("danger", "danger-soft"),
            ("on-accent", "accent"),
        ]:
            ratio = contrast(values[fg], values[bg])
            checks.append(
                {
                    "theme": theme,
                    "foreground": fg,
                    "background": bg,
                    "ratio": round(ratio, 3),
                    "minimum": 4.5,
                    "pass": ratio >= 4.5,
                }
            )
        for fg in ["control-border", "chart-positive", "chart-negative"]:
            ratio = contrast(values[fg], values["surface"])
            checks.append(
                {
                    "theme": theme,
                    "foreground": fg,
                    "background": "surface",
                    "ratio": round(ratio, 3),
                    "minimum": 3,
                    "pass": ratio >= 3,
                }
            )
    result = {
        "scope": "Source-backed normal-text and selected graphical/control token pairs only; does not replace axe or manual screen-reader review.",
        "checks": checks,
    }
    save_json("reports/v5-contrast.json", result)
    assert all(c["pass"] for c in checks), [c for c in checks if not c["pass"]]
    print(f"{len(checks)} sampled token contrast checks passed.")


if __name__ == "__main__":
    main()
