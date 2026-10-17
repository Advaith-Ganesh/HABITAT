"""Focused token contrast check; not a full WCAG or rendered accessibility audit."""

import re
import json
from ml.common import ROOT, save_json

css = (ROOT / "frontend/src/style.css").read_text()
light = dict(
    re.findall(
        r"--([\w-]+):\s*(#[a-fA-F0-9]{3,6})",
        re.search(r":root\s*\{([^}]+)\}", css).group(1),
    )
)
dark = {
    **light,
    **dict(
        re.findall(
            r"--([\w-]+):\s*(#[a-fA-F0-9]{3,6})",
            re.search(r':root\[data-theme=["\']?dark["\']?\]\s*\{([^}]+)\}', css).group(
                1
            ),
        )
    ),
}


def luminance(value):
    if len(value) == 4:
        value = "#" + "".join(c * 2 for c in value[1:])
    channels = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [
        v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels
    ]
    return sum(v * w for v, w in zip(channels, [0.2126, 0.7152, 0.0722]))


def contrast(a, b):
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


pairs = [
    ("text", "surface"),
    ("muted", "surface"),
    ("muted", "bg"),
    ("subtle", "surface"),
    ("accent", "surface"),
    ("accent", "accent-soft"),
    ("teal", "teal-soft"),
    ("amber", "amber-soft"),
]
result = {
    "scope": "Source token pairs used for normal text, not all rendered combinations. Axe execution was blocked by browser-launch restrictions.",
    "checks": [
        {
            "theme": theme,
            "foreground": fg,
            "background": bg,
            "ratio": round(contrast(values[fg], values[bg]), 3),
            "passes_4_5": contrast(values[fg], values[bg]) >= 4.5,
        }
        for theme, values in [("light", light), ("dark", dark)]
        for fg, bg in pairs
    ],
}
result["checks"].append(
    {
        "theme": "both",
        "foreground": "#ffffff",
        "background": "#5558e8",
        "ratio": round(contrast("#ffffff", "#5558e8"), 3),
        "passes_4_5": contrast("#ffffff", "#5558e8") >= 4.5,
    }
)
save_json("reports/v2-contrast.json", result)
print(json.dumps(result, indent=2))
assert all(c["passes_4_5"] for c in result["checks"])
