import time
from dataclasses import dataclass
from typing import Optional, List, Tuple

import curses

from .binding import Bindings, InputBinding, init_joystick_optional

try:
    import pygame
except ImportError:
    raise SystemExit("Missing dependency: pygame. Install with: pip install pygame")


@dataclass
class RaceInfo:
    course: str
    vehicle: str


def fmt_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    s = total % 60
    m = (total // 60) % 60
    h = total // 3600
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def key_name(code: int) -> str:
    if code is None:
        return "None"
    if 32 <= code <= 126:
        return chr(code)
    names = {
        10: "ENTER",
        27: "ESC",
        curses.KEY_UP: "UP",
        curses.KEY_DOWN: "DOWN",
        curses.KEY_LEFT: "LEFT",
        curses.KEY_RIGHT: "RIGHT",
        curses.KEY_BACKSPACE: "BACKSPACE",
        curses.KEY_DC: "DELETE",
        curses.KEY_HOME: "HOME",
        curses.KEY_END: "END",
        curses.KEY_NPAGE: "PAGEDOWN",
        curses.KEY_PPAGE: "PAGEUP",
    }
    return names.get(code, f"KEY({code})")


def binding_label(b: InputBinding) -> str:
    if b.type == "keyboard":
        return f"Keyboard: {key_name(b.key)}"
    return f"Controller: Button {b.button}"


def input_matches(binding: InputBinding, key: int, joy_button: Optional[int]) -> bool:
    if binding.type == "keyboard":
        return key == binding.key
    if binding.type == "controller":
        return joy_button is not None and joy_button == binding.button
    return False


def run_race_tui(stdscr, race: RaceInfo, bindings: Bindings) -> List[float]:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(20)

    js = init_joystick_optional()

    laps: List[float] = []
    running = False
    race_start: Optional[float] = None
    lap_start: Optional[float] = None
    status_line = "Waiting on Start Input..."
    last_ui_update = 0.0

    while True:
        key = stdscr.getch()

        joy_button: Optional[int] = None
        if js:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    joy_button = int(event.button)
                    break

        if key != -1 or joy_button is not None:
            if input_matches(bindings.reset, key, joy_button):
                laps.clear()
                running = False
                race_start = None
                lap_start = None
                status_line = "RESET. Waiting on Start Input..."

            elif input_matches(bindings.lap, key, joy_button):
                now = time.perf_counter()
                if not running:
                    running = True
                    race_start = now
                    lap_start = now
                    status_line = "Timing Lap 1..."
                else:
                    assert lap_start is not None
                    lap_time = now - lap_start
                    laps.append(lap_time)
                    lap_start = now
                    status_line = f"LAP {len(laps)} TIME: {fmt_time(lap_time)} | Timing Lap {len(laps)+1}..."

            elif input_matches(bindings.stop, key, joy_button) and running:
                now = time.perf_counter()
                assert lap_start is not None
                final_lap = now - lap_start
                laps.append(final_lap)
                return laps

        now = time.perf_counter()
        if now - last_ui_update > 0.05:
            stdscr.erase()
            stdscr.addstr(0, 0, "Seriphai's Terminal Livesplit")
            stdscr.addstr(1, 0, f"Course : {race.course}")
            stdscr.addstr(2, 0, f"Vehicle: {race.vehicle}")
            stdscr.addstr(3, 0, "-" * 70)

            row = 5
            stdscr.addstr(row, 0, f"LAP   -> {binding_label(bindings.lap)}"); row += 1
            stdscr.addstr(row, 0, f"STOP  -> {binding_label(bindings.stop)}"); row += 1
            stdscr.addstr(row, 0, f"RESET -> {binding_label(bindings.reset)}"); row += 2

            stdscr.addstr(row, 0, f"Controller: {js.get_name()}" if js else "Controller: (none detected)")
            row += 2

            stdscr.addstr(row, 0, status_line)
            row += 2

            if running and race_start is not None and lap_start is not None:
                total_elapsed = now - race_start
                current_lap_elapsed = now - lap_start
                stdscr.addstr(row, 0, f"Total:       {fmt_time(total_elapsed)}"); row += 1
                stdscr.addstr(row, 0, f"Current Lap: {fmt_time(current_lap_elapsed)}"); row += 2

            shown = laps[-10:]
            start_idx = max(1, len(laps) - len(shown) + 1)
            for i, t in enumerate(shown, start=start_idx):
                stdscr.addstr(row, 0, f"Lap {i}: {fmt_time(t)}")
                row += 1

            stdscr.refresh()
            last_ui_update = now
