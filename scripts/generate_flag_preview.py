"""Generate local comparison assets without changing production flag behavior."""
from pathlib import Path
import colorsys
import re
import shutil

INK, PAPER, RED = "#15110e", "#f1ece3", "#e63322"

def adapt(color: str, code: str) -> str:
    if color == "none" or color.startswith("url("):
        return color
    color = {"red": "#ff0000", "white": "#ffffff", "black": "#000000"}.get(color.lower(), color)
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    r, g, b = (int(value[i:i+2], 16) / 255 for i in (0, 2, 4))
    hue, saturation, brightness = colorsys.rgb_to_hsv(r, g, b)
    if saturation < .18:
        return PAPER if brightness > .65 else INK
    if code in ("ar", "uy") and r > g > b:
        return RED if brightness > .7 else INK
    if code in ("ie", "in") and .06 <= hue < .18:
        return RED
    if hue < .06 or hue > .9:
        return RED
    if hue < .18:
        return PAPER if brightness > .65 else INK
    return INK

if __name__ == "__main__":
    target = Path("public/flags-preview")
    target.mkdir(exist_ok=True)
    for source in Path("public/flags").glob("*.svg"):
        svg = re.sub(r'(fill|stroke|stop-color)="([^"]+)"', lambda m: f'{m[1]}="{adapt(m[2], source.stem)}"', source.read_text())
        svg = svg.replace('<svg ', f'<svg fill="{INK}" ', 1)
        (target / source.name).write_text(svg)
    shutil.copyfile("public/flags/LICENSE", target / "LICENSE")
