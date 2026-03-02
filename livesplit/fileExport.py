import os
import re
import time
from typing import List

from .race import RaceInfo, fmt_time


def safe_filename(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_\-]+", "", text)
    return text or "race"


def build_summary_lines(race: RaceInfo, laps: List[float]) -> List[str]:
    total = sum(laps)
    lines: List[str] = []
    lines.append("-----------Race Completed-----------")
    lines.append(f"Course:  {race.course}")
    lines.append(f"Vehicle: {race.vehicle}")
    lines.append("")
    for i, t in enumerate(laps, start=1):
        lines.append(f"Lap {i}:  {fmt_time(t)}")
    lines.append("")
    lines.append(f"Total Time: {fmt_time(total)}")
    lines.append("-----------------------------------")
    return lines


def save_results_txt(race: RaceInfo, laps: List[float], folder: str = ".") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    base = f"{safe_filename(race.course)}__{safe_filename(race.vehicle)}__{ts}.txt"
    path = os.path.join(folder, base)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(build_summary_lines(race, laps)) + "\n")

    return path
