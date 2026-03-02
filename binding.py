import os
import json
import time
from dataclasses import dataclass
from typing import Optional, Any, Dict, Set

# Headless pygame (no window)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame
except ImportError:
    raise SystemExit("Missing dependency: pygame. Install with: pip install pygame")


APP_DIR = os.path.join(os.path.expanduser("~"), ".config", "seriphai-livesplit")
BINDINGS_PATH = os.path.join(APP_DIR, "bindings.json")


@dataclass
class InputBinding:
    """
    Either:
      type="keyboard", key=<curses keycode int>
      type="controller", button=<int>
    """
    type: str
    key: Optional[int] = None
    button: Optional[int] = None


@dataclass
class Bindings:
    lap: InputBinding
    stop: InputBinding
    reset: InputBinding


def ensure_app_dir() -> None:
    os.makedirs(APP_DIR, exist_ok=True)


def init_joystick_optional() -> Optional["pygame.joystick.Joystick"]:
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() <= 0:
        return None
    js = pygame.joystick.Joystick(0)
    js.init()
    return js


def current_pressed_buttons(js: "pygame.joystick.Joystick") -> Set[int]:
    pygame.event.pump()
    pressed: Set[int] = set()
    for i in range(js.get_numbuttons()):
        try:
            if js.get_button(i):
                pressed.add(i)
        except Exception:
            pass
    return pressed


def bindings_to_dict(b: Bindings) -> Dict[str, Any]:
    def one(x: InputBinding) -> Dict[str, Any]:
        if x.type == "keyboard":
            return {"type": "keyboard", "key": x.key}
        return {"type": "controller", "button": x.button}

    return {"lap": one(b.lap), "stop": one(b.stop), "reset": one(b.reset)}


def bindings_from_dict(d: Dict[str, Any]) -> Bindings:
    def one(x: Dict[str, Any]) -> InputBinding:
        t = x.get("type")
        if t == "keyboard":
            return InputBinding(type="keyboard", key=int(x["key"]))
        if t == "controller":
            return InputBinding(type="controller", button=int(x["button"]))
        raise ValueError("Invalid binding type")

    return Bindings(lap=one(d["lap"]), stop=one(d["stop"]), reset=one(d["reset"]))


def load_bindings() -> Optional[Bindings]:
    try:
        with open(BINDINGS_PATH, "r", encoding="utf-8") as f:
            return bindings_from_dict(json.load(f))
    except FileNotFoundError:
        return None
    except Exception:
        # corrupted config, treat as missing
        return None


def save_bindings(b: Bindings) -> None:
    ensure_app_dir()
    with open(BINDINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(bindings_to_dict(b), f, indent=2)


def wait_for_input_binding(stdscr, prompt: str, js: Optional["pygame.joystick.Joystick"]) -> InputBinding:
    """
    Accept keyboard OR controller, but ignore stuck/noisy controller buttons:
      - baseline snapshot of buttons held at start
      - settle window
      - accept only a fresh JOYBUTTONDOWN not in baseline
    """
    stdscr.nodelay(True)
    stdscr.timeout(20)

    baseline: Set[int] = set()
    settle_until = time.perf_counter() + 0.40  # 400ms settle
    last_accept_time = 0.0
    debounce_s = 0.25

    if js:
        baseline = current_pressed_buttons(js)

    while True:
        now = time.perf_counter()

        stdscr.erase()
        stdscr.addstr(0, 0, "Seriphai's Terminal Livesplit - Bind Controls")
        stdscr.addstr(2, 0, prompt)
        stdscr.addstr(4, 0, "Press a keyboard key OR a controller button to bind.")
        stdscr.addstr(5, 0, "Press ESC to cancel binding.")
        if js:
            stdscr.addstr(7, 0, f"Controller: {js.get_name()} (buttons: {js.get_numbuttons()})")
            stdscr.addstr(8, 0, f"Ignoring buttons held at start: {sorted(baseline)[:12]}" + (" ..." if len(baseline) > 12 else ""))
            if now < settle_until:
                stdscr.addstr(10, 0, "Settling controller input... (release buttons for a moment)")
        else:
            stdscr.addstr(7, 0, "No controller detected (keyboard-only is fine).")
        stdscr.refresh()

        # Keyboard binding
        key = stdscr.getch()
        if key != -1:
            if key == 27:  # ESC
                raise KeyboardInterrupt("Binding cancelled")
            return InputBinding(type="keyboard", key=key)

        # Controller binding (fresh press only)
        if js and now >= settle_until and (now - last_accept_time) >= debounce_s:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    btn = int(event.button)
                    if btn in baseline:
                        continue
                    last_accept_time = now
                    return InputBinding(type="controller", button=btn)


def bind_controls_flow(stdscr) -> Bindings:
    js = init_joystick_optional()

    lap = wait_for_input_binding(stdscr, "Bind LAP (Start / Split).", js)
    stop = wait_for_input_binding(stdscr, "Bind STOP (End race).", js)
    reset = wait_for_input_binding(stdscr, "Bind RESET (Clear & return to waiting).", js)

    b = Bindings(lap=lap, stop=stop, reset=reset)
    save_bindings(b)
    return b
