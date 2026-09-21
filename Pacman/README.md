# 🟡 Pac-Man — A Python/Pygame Arcade Clone

A fully playable Pac-Man clone built from scratch in Python using **Pygame**, featuring procedurally generated mazes, BFS-driven ghost AI, a persistent JSON-based highscore board, and a complete UI flow (menu, pause, controls, game-over, scoreboard).

This project was built to deepen my skills in **game loop architecture, pathfinding algorithms, event-driven programming, and clean object-oriented design in Python.**

---

![alt text](<main_window.png>)

## 🎮 Features

- **10 progressively generated levels** — each level's maze is procedurally built using an external maze-generation package, with a fixed seed on level 1 for reproducibility and random generation afterward.
- **Smart ghost AI**
  - *Chase mode*: the lead ghost uses a custom **Breadth-First Search (BFS)** pathfinder to find the shortest route to Pac-Man through the maze graph.
  - *Flee mode*: when Pac-Man eats a super pacgum, ghosts evaluate all open neighboring cells and move toward the one that **maximizes Euclidean distance** from the player.
  - *Wander mode*: idle ghosts pick a random target cell and path to it with the same BFS logic, so movement never looks scripted.
- **Full game loop**: pacgums, super pacgums (in the four maze corners), score tracking, lives, per-level countdown timer, and win/lose states.
- **Cheat / demo mode**: doubled movement speed, invincibility, and instant level-skip (`L` key) — used for testing and demoing gameplay quickly.
- **Persistent highscore board**: scores are stored in a local JSON file, kept sorted, and capped at the top 10 entries.
- **Complete UI flow**: animated main menu, in-game pause overlay, a controls/help screen, a scoreboard screen, and a game-over screen with live username input and validation.
- **Configurable via JSON**: lives, pacgum counts, point values, level timers, and the maze seed are all adjustable through a `config.json` file, with safe fallback defaults if a value is missing or invalid.

---

## 🛠️ Tech Stack

| Area | Tool / Library |
|---|---|
| Language | Python 3, fully type-hinted |
| Rendering & input | [Pygame](https://www.pygame.org/) |
| Maze generation | Custom external `.whl` package |
| Data persistence | JSON (config + highscores) |
| Pathfinding | Custom BFS implementation using `queue.Queue` |

---

## 🧠 What I Focused On

- **Separation of concerns**: game-state logic (movement, collisions, scoring) is kept distinct from rendering code, which made the project much easier to debug and extend as features were added.
- **Algorithmic thinking**: implementing BFS pathfinding on a grid represented as bitmask wall data (`NESW` open/closed per cell) rather than relying on a pre-built graph library.
- **Robust I/O handling**: a dedicated parser class manages config loading (with comment support and fallback defaults) and highscore persistence, isolating file-handling errors from the game loop.
- **Finite-state style UI flow**: every screen (menu, pause, controls, scoreboard, game over) is its own self-contained loop with consistent event handling, which mirrors how simple state machines are built in game development.

---

![alt text](<play.png>)

## 🚀 Running the Game

```bash
# Create and activate a virtual environment
make env
source .env/bin/activate

# Install dependencies (including the maze generator package)
make install

# Configure the game (see below), then run
make run
```

This runs `python3 pac-man.py config.json`.

### Controls
| Key | Action |
|---|---|
| Arrow Keys | Move Pac-Man |
| Esc | Pause |
| L | Skip level (only active in demo/cheat mode) |

---

## ⚙️ Configuration

Game parameters are controlled through `config.json`. Any missing or invalid value automatically falls back to a sensible default.

| Key | Description | Default |
|---|---|---|
| `highscore_filename` | JSON file used to load/store the top 10 scores | `score_board.json` |
| `lives` | Player lives across all levels | `3` |
| `pacgum` | Number of pacgums per maze | `42` |
| `points_per_pacgum` | Points for a normal pacgum | `10` |
| `points_per_super_pacgum` | Points for a super pacgum | `50` |
| `points_per_ghost` | Points for eating an edible ghost | `200` |
| `seed` | Random seed for level 1's maze | `42` |
| `level_max_time` | Time limit per level (seconds) | `90` |

---

## 🏆 Highscore System

Scores are stored locally as JSON rather than in a database — a deliberate choice for a lightweight, dependency-free, single-player arcade game. On save, the board is loaded, the new score is inserted if it beats the current lowest of the top 10, the list is re-sorted, and any overflow entry is dropped.

---

## 🧩 Architecture

```
Game            → main game loop, level progression, entity & UI management
JsonParser      → config parsing (with comment support), fallback defaults, highscore I/O
MazeGenerator   → external package providing procedurally generated maze layouts
```

Helper utilities (`collidePoint`, `collideRect`, `dec_to_bin`) keep collision detection and bitmask-to-wall conversion logic small, testable, and reusable across the codebase.

---

## 📌 Notes

This project was originally built as part of a structured coding curriculum and has since been cleaned up and shared here as a portfolio piece to demonstrate applied skills in Python, game development, algorithms, and software architecture.

Feedback and suggestions are welcome — feel free to open an issue or reach out!
