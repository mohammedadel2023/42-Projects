# 👻 Pacman: Object-Oriented Arcade Engine & State Manager

*This project has been created as part of the 42 curriculum by Mohammad Khashan and Kanaan Lafi.*

A full-scale, object-oriented recreation of the classic Pac-Man arcade game. Built in Python using Pygame, this project demonstrates advanced system design by decoupling the core game logic from the graphical rendering engine. The system integrates an external third-party maze generation package (`mazegen-*.whl`), handles persistent local data storage, and is packaged for public distribution on itch.io.

---
![alt text](<Screenshot From 2026-07-09 21-26-29.png>)

## ⚙️ System Architecture & Data Flow

The game operates on a strict Model-View-Controller (MVC) inspired architecture. By isolating the game state (player movement, entity collisions, score tracking) from the visual drawing functions, the codebase remains highly modular, scalable, and easy to debug. The complex interactions within the game loop are governed by this strictly decoupled architectural framework.



* **MVC Flow:** The diagram visualizes how user inputs (Controller) trigger state updates (Model), which are subsequently reflected in the visual renderer (View). This prevents spaghetti code and makes the loop deterministic.
* **JSON Storage:** Detailed data flow diagrams show exactly how the engine leverages isolated, commented JSON files (`config.json`) for initialization and sorts local JSON lists for highscore management, proving memory safety in file I/O operations.
* **External Integration:** The diagram highlights where the imported `mazegen-*.whl` package is called to initialize the game world boundary constraints.

### Configuration & State Initialization
The game engine is dynamically configured at runtime via a custom JSON parser that supports inline comments and fallback defaults, preventing application crashes due to malformed user input.

| Parameter | Type | System Impact |
| :--- | :--- | :--- |
| **highscore_filename** | String | Defines the target file for persistent score I/O operations. |
| **lives** | Integer | Sets the global fail-state threshold for the player. |
| **pacgum** | Integer | Dictates the procedural distribution density of standard points. |
| **points_per_* ** | Integer | Controls the mathematical weighting of different collision events (pacgums, super-pacgums, edible ghosts). |
| **seed** | Integer | Injects a fixed random seed into the external maze generator to ensure reproducibility for level 1 testing. |
| **level_max_time** | Integer | Enforces a strict time complexity constraint on the game loop for each level. |

### External Dependency Integration
Rather than relying on internal maze logic, this engine dynamically imports the `A-Maze-ing` wheel package. During level initialization, the engine calls the external generator with the `PERFECT = False` flag to ensure the topology contains playable loops, translating the external hex-data into Pygame collision boundaries.

---

## 🧠 Core Game Logic & Features

![alt text](<Screenshot From 2026-07-09 21-26-49.png>)
### Entity AI & State Machines
The ghosts utilize basic state machines to alternate between two primary behaviors depending on the player's interactions with the environment:
* **Chase State:** Ghosts autonomously calculate paths through the generated corridors to intercept the player coordinates.
* **Flee State (Edible):** Triggered by Super-Pacgums. Ghost movement speed is throttled, and pathfinding logic is inverted to maximize distance from the player entity until the timer expires.

### Persistent Highscore Architecture
Scores are managed via a lightweight, local JSON storage system rather than a heavy database (like SQLite). 
* **Mechanism:** The system loads existing data into memory, sorts the dictionary values, and enforces a strict Top 10 capacity limit. If a new game-over score exceeds the minimum value in the array, the lowest score is popped and the new data is serialized back to disk. 
* **Benefits:** This ensures zero external dependencies and rapid read/write execution during the game loop transitions.

---

## 🚀 Execution & Usage

The application requires a virtual environment to manage the Pygame and Maze Generator dependencies cleanly.

**Environment Setup:**
```bash
make env
source .env/bin/activate
make install
make run 
```
