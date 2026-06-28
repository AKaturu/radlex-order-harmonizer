from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import imageio.v2 as imageio
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate README demo media from real demo outputs.")
    parser.add_argument("--output", type=Path, default=Path("outputs/demo-media"))
    parser.add_argument("--assets", type=Path, default=Path("docs/assets"))
    parser.add_argument("--skip-run", action="store_true")
    return parser.parse_args()


def font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if os.name == "nt":
        candidates.extend(
            [
                "C:/Windows/Fonts/consola.ttf" if mono else "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]
        )
    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" if mono else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Menlo.ttc" if mono else "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def clean(text: str) -> str:
    return ANSI_RE.sub("", text).replace("\r\n", "\n").strip()


def wrap_line(draw: ImageDraw.ImageDraw, text: str, max_width: int, fnt: ImageFont.ImageFont) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    max_width: int,
    fnt: ImageFont.ImageFont,
    fill: str,
    line_height: int,
) -> int:
    x, y = xy
    for raw in text.splitlines():
        for line in wrap_line(draw, raw, max_width, fnt):
            draw.text((x, y), line, font=fnt, fill=fill)
            y += line_height
    return y


def make_frame(title: str, body: list[str], stats: list[tuple[str, str]], footer: str) -> Image.Image:
    image = Image.new("RGB", (1280, 720), "#111318")
    draw = ImageDraw.Draw(image)
    title_font = font(42)
    body_font = font(23, mono=True)
    small_font = font(20)
    stat_font = font(26)

    draw.rectangle((0, 0, 1280, 88), fill="#202936")
    draw.rectangle((0, 88, 1280, 96), fill="#f59e0b")
    draw.text((40, 24), title, font=title_font, fill="#f8fafc")
    draw.text((40, 675), footer, font=small_font, fill="#a8b3bd")

    draw.rounded_rectangle((40, 130, 760, 630), radius=14, fill="#0b0f14", outline="#334155", width=2)
    draw.text((70, 158), "$ radlex-harmonize demo --n 30 --seed 11", font=body_font, fill="#bfdbfe")
    y = 205
    for line in body:
        y = draw_wrapped(draw, (70, y), line, 650, body_font, "#d9e2ec", 31) + 6

    draw.rounded_rectangle((800, 130, 1240, 630), radius=14, fill="#151922", outline="#3b4658", width=2)
    draw.text((830, 160), "Demo run summary", font=stat_font, fill="#f8fafc")
    y = 220
    for label, value in stats:
        draw.text((830, y), label, font=small_font, fill="#9fb0c0")
        draw.text((830, y + 28), value, font=stat_font, fill="#2ec4b6")
        y += 92
    return image


def run_demo(output: Path) -> str:
    command = [
        sys.executable,
        "-m",
        "radlex_order_harmonizer.cli",
        "demo",
        "--output",
        str(output),
        "--n",
        "30",
        "--seed",
        "11",
    ]
    env = {**os.environ, "NO_COLOR": "1", "PYTHONUTF8": "1"}
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return clean(result.stdout)


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.assets.mkdir(parents=True, exist_ok=True)

    transcript = "" if args.skip_run else run_demo(args.output)
    results = pd.read_csv(args.output / "matching_results.csv")
    synthetic = pd.read_csv(args.output / "synthetic_procedures.csv")
    mapped = int(results["selected_rpid"].notna().sum())
    exact = int((results["selected_strategy"] == "exact").sum()) if "selected_strategy" in results else 0
    mean_score = float(results["selected_score"].fillna(0).mean()) if "selected_score" in results else 0.0

    stats = [
        ("Synthetic orders", str(len(synthetic))),
        ("Mapped candidates", str(mapped)),
        ("Exact matches", str(exact)),
        ("Mean top score", f"{mean_score:.2f}"),
    ]
    transcript_lines = [line for line in transcript.splitlines() if line][:5]
    sample_lines = (
        results[["local_name", "selected_rpid", "selected_score", "selected_strategy"]]
        .head(5)
        .to_string(index=False)
        .splitlines()
    )
    candidate_lines = (
        results[["local_name", "candidate_rpids"]]
        .head(4)
        .to_string(index=False)
        .splitlines()
    )

    frames = [
        make_frame(
            "radlex-order-harmonizer",
            transcript_lines or ["Loaded RadLex entries.", "Generated synthetic local procedure names.", "Ran candidate matching."],
            stats,
            "Real CLI demo output rendered for GitHub README media.",
        ),
        make_frame(
            "Local orders mapped to RadLex candidates",
            sample_lines,
            stats,
            "Top candidates, scores, and strategies are exported for adjudication.",
        ),
        make_frame(
            "Transparent candidate review",
            candidate_lines,
            stats,
            "Review candidates before changing production order dictionaries.",
        ),
    ]

    poster = args.assets / "demo-poster.png"
    gif = args.assets / "demo.gif"
    mp4 = args.assets / "demo.mp4"
    frames[0].save(poster)
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=1500, loop=0)
    imageio.mimsave(mp4, frames, fps=1)
    print(f"Wrote {poster}")
    print(f"Wrote {gif}")
    print(f"Wrote {mp4}")


if __name__ == "__main__":
    main()
