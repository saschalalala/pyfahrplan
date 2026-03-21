# Plan: Rewrite pyfahrplan as a Textual TUI Application

## Current State
pyfahrplan is a CLI tool (Click + Rich) that downloads CCC conference schedules, filters them, and displays results as a Rich table. All interaction is via command-line flags — no interactivity after launch.

## Goal
Rewrite as an interactive TUI using [Textual](https://textual.textualize.io/) so users can browse, filter, and explore talks in real-time without re-running the command.

---

## Architecture Overview

```
pyfahrplan/
├── __init__.py          # (keep) version info
├── config.py            # (keep) defaults
├── lib.py               # (keep, minor changes) core data logic
├── pyfahrplan_cli.py    # (keep as thin wrapper) CLI entry → launches TUI
├── app.py               # (NEW) Textual App subclass
├── screens/
│   ├── __init__.py
│   ├── main_screen.py   # (NEW) Main browse/filter screen
│   └── detail_screen.py # (NEW) Talk detail view screen
└── widgets/
    ├── __init__.py
    ├── filter_bar.py     # (NEW) Filter input widgets
    └── talk_table.py     # (NEW) DataTable for talks
```

---

## Step-by-Step Plan

### Step 1: Add Textual dependency
- Add `textual` to `pyproject.toml` dependencies
- Remove `click` dependency (no longer needed for interactive mode)
- Keep `requests`, `requests-cache`, `python-dateutil`
- Keep `rich` (Textual uses Rich internally)

### Step 2: Refactor `lib.py` — decouple from display
- Remove `print_formatted_talks()` from `lib.py` (display logic moves to TUI)
- Extract a pure `filter_talks(talks, filters) -> list[dict]` function that returns filtered data without printing
- Keep `Fahrplan` class, `filter_talk()`, `is_talk_in_timerange()`, `is_talk_in_past()` as-is
- Add a `sort_talks(talks, sort_key, reverse)` helper that returns sorted data

### Step 3: Create the Textual App (`app.py`)
- Subclass `textual.app.App`
- On mount: load Fahrplan data (show a loading indicator while downloading)
- Push `MainScreen` as the default screen
- Define keybindings:
  - `q` — quit
  - `?` — help/about
  - `/` — focus filter bar
  - `escape` — clear filters / go back

### Step 4: Build the Main Screen (`screens/main_screen.py`)
- Layout (vertical):
  ```
  ┌─────────────────────────────────────┐
  │ Header: "pyfahrplan — CCC Schedules"│
  ├─────────────────────────────────────┤
  │ FilterBar (collapsible)             │
  │  Conference: [dropdown]             │
  │  Day: [dropdown]  Room: [input]     │
  │  Speaker: [input] Title: [input]    │
  │  Track: [input]   Start: [input]    │
  │  [x] Hide past talks               │
  ├─────────────────────────────────────┤
  │ DataTable (scrollable)              │
  │  Conf | Day | Start | Dur | Room   │
  │       | Title | Speaker | Track    │
  ├─────────────────────────────────────┤
  │ Footer: keybindings help            │
  └─────────────────────────────────────┘
  ```
- Filters update the table reactively (on change, re-filter and repopulate)
- Selecting a row opens the Detail Screen

### Step 5: Build the Filter Bar widget (`widgets/filter_bar.py`)
- Composite widget with Textual `Input`, `Select`, and `Switch` widgets
- Conference selector: dropdown with all conference acronyms + "all"
- Day selector: dropdown [All, 1, 2, 3, 4]
- Text inputs for: room, speaker, title, track
- Time input for start time
- Checkbox/switch for "hide past talks"
- Emits a custom `FilterChanged` message when any value changes

### Step 6: Build the Talk Table widget (`widgets/talk_table.py`)
- Wraps Textual's `DataTable` widget
- Columns: Conference, Day, Start, Duration, Room, Title, Speaker(s), Track
- Supports sorting by clicking column headers
- Emits event when a row is selected (Enter or click)

### Step 7: Build the Detail Screen (`screens/detail_screen.py`)
- Full-screen view of a single talk
- Shows all fields: title, speakers, track, room, day, start, duration
- Shows abstract and description (scrollable with Textual's `ScrollableContainer`)
- `Escape` or `b` to go back to main screen

### Step 8: Update CLI entry point (`pyfahrplan_cli.py`)
- Replace Click-based CLI with a simple entry point that launches the Textual app
- Support minimal CLI args: `--update-cache` flag only (everything else is interactive now)
- Entry: `def cli(): app = FahrplanApp(); app.run()`

### Step 9: Add CSS styling
- Create `app.tcss` for Textual CSS
- Style the filter bar, table, detail view
- Use a dark theme fitting the CCC aesthetic

### Step 10: Update tests
- Keep existing filter/data tests (they test `lib.py` which stays)
- Add new tests for TUI using Textual's `pilot` testing framework
- Test: app loads, filters work, detail screen opens, keybindings work

### Step 11: Update `__main__.py` and `pyproject.toml` entry point
- Update entry point to point to new app launcher
- Ensure `python -m pyfahrplan` still works

---

## Key Design Decisions

1. **Keep `lib.py` as the data layer** — no Textual imports in it, pure data logic
2. **Reactive filtering** — filters update the table live as you type (with small debounce)
3. **Textual's built-in DataTable** — no need for custom table rendering
4. **Screen-based navigation** — MainScreen for browsing, DetailScreen for single talk
5. **Minimal CLI flags** — the TUI handles all filtering interactively

## Out of Scope (for now)
- Bookmarking/favoriting talks
- Schedule export
- Live schedule updates
- Custom conference URL input
