import curses

from binding import load_bindings, bind_controls_flow, Bindings
from race import RaceInfo, run_race_tui
from fileExport import build_summary_lines, save_results_txt


def clear_terminal() -> None:
    print("\033[2J\033[H", end="")


def menu(stdscr, title: str, options: list[str], footer: str = "") -> int:
    curses.curs_set(0)
    stdscr.nodelay(False)
    selected = 0

    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, title)
        stdscr.addstr(1, 0, "-" * max(20, len(title)))

        row = 3
        for i, opt in enumerate(options):
            prefix = "➤ " if i == selected else "  "
            stdscr.addstr(row, 0, f"{prefix}{opt}")
            row += 1

        if footer:
            stdscr.addstr(row + 1, 0, footer)

        stdscr.refresh()
        ch = stdscr.getch()

        if ch in (curses.KEY_UP, ord('k')):
            selected = (selected - 1) % len(options)
        elif ch in (curses.KEY_DOWN, ord('j')):
            selected = (selected + 1) % len(options)
        elif ch in (10, 13, curses.KEY_ENTER):
            return selected
        elif ch in (27, ord('q')):  # ESC or q
            return len(options) - 1


def prompt_text(stdscr, prompt: str) -> str:
    curses.curs_set(1)
    stdscr.nodelay(False)
    stdscr.erase()
    stdscr.addstr(0, 0, prompt)
    stdscr.addstr(1, 0, "> ")
    curses.echo()
    s = stdscr.getstr(1, 2).decode("utf-8").strip()
    curses.noecho()
    return s


def post_race_prompt(stdscr, race: RaceInfo, laps: list[float]) -> str | None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    summary = build_summary_lines(race, laps)

    while True:
        stdscr.erase()
        row = 0
        for line in summary:
            stdscr.addstr(row, 0, line)
            row += 1

        row += 1
        stdscr.addstr(row, 0, "Save results to .txt or leave?")
        row += 2
        stdscr.addstr(row, 0, "[S] Save   [L] Leave")
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('s'), ord('S')):
            return "save"
        if key in (ord('l'), ord('L'), 27):
            return None

def show_post_race_screen(stdscr, race: RaceInfo, laps: list[float], saved_path: str | None):
    stdscr.nodelay(False)
    stdscr.timeout(-1)
    curses.curs_set(0)

    summary = build_summary_lines(race, laps)

    stdscr.erase()
    row = 0
    for line in summary:
        stdscr.addstr(row, 0, line)
        row += 1

    row += 1
    if saved_path:
        stdscr.addstr(row, 0, f"Saved to: {saved_path}")
    else:
        stdscr.addstr(row, 0, "Not saved.")

    row += 2
    stdscr.addstr(row, 0, "Press any key to return to the menu...")
    stdscr.refresh()

    stdscr.getch()

def main_curses(stdscr):
    while True:
        existing = load_bindings()
        has_bindings = existing is not None

        title = "Seriphai's Terminal Livesplit"
        options = []
        if has_bindings:
            options += ["Start Race", "Bind Keys (rebind)"]
        else:
            options += ["Bind Keys (required first)"]
        options += ["Quit"]

        footer = ""
        if has_bindings:
            footer = "Bindings loaded from ~/.config/seriphai-livesplit/bindings.json"

        choice = menu(stdscr, title, options, footer=footer)
        selected = options[choice]

        if selected == "Quit":
            return

        if selected.startswith("Bind Keys"):
            try:
                b = bind_controls_flow(stdscr)
                stdscr.erase()
                stdscr.addstr(0, 0, "Bindings saved!")
                stdscr.addstr(2, 0, "Press any key to return to menu...")
                stdscr.nodelay(False)
                stdscr.getch()
            except KeyboardInterrupt:
                stdscr.erase()
                stdscr.addstr(0, 0, "Binding cancelled. Press any key to return to menu...")
                stdscr.nodelay(False)
                stdscr.getch()
            continue

        if selected == "Start Race":
            if not existing:
                continue

            course = prompt_text(stdscr, "What Course Are you Timing?...")
            vehicle = prompt_text(stdscr, "What Vehicle are you using?")
            race = RaceInfo(course=course or "Unknown Course", vehicle=vehicle or "Unknown Vehicle")

            laps = run_race_tui(stdscr, race, existing)

            action = post_race_prompt(stdscr, race, laps)

            saved_path = None
            if action == "save":
                saved_path = save_results_txt(race, laps)

            # Leave curses, print clean summary, then wait for Enter
            show_post_race_screen(stdscr, race, laps, saved_path) 


def main():
    clear_terminal()
    curses.wrapper(main_curses)


if __name__ == "__main__":
    main()
