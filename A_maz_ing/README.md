# 🧩 Amazing: Procedural Maze Generation & Pathfinding Engine

**This project has been created as part of the 42 curriculum by Mohammad Khashan and Kanaan Lafi.**

**This repository contains my personal solutions for the 42 curriculum. It is provided for portfolio and educational purposes only. Active 42 students must not copy or use this code, as doing so violates the school's strict academic integrity policies and will result in severe penalties for plagiarism**

A modular Python package designed to dynamically generate, solve, and visually render both perfect and imperfect mazes using graph theory algorithms. The system is built with a strict Object-Oriented approach, allowing the core generation engine to be exported as a standalone Python Wheel (`.whl`) for integration into external graphical applications.

## ⚙️ System Architecture & Data Flow

The engine operates on a strict pipeline: Configuration Parsing -> Graph Generation -> Pathfinding -> Hexadecimal Serialization -> Visualization. 

### Engine Configuration Parameters
The generation state is strictly controlled via a plain text configuration file, ensuring high reproducibility and modular testing. 

| Parameter | Type | System Impact |
| :--- | :--- | :--- |
| **WIDTH / HEIGHT** | Integer | Defines the grid constraints. Must be large enough to accommodate the hardcoded '42' central pattern without isolating cells. |
| **ENTRY / EXIT** | Tuple (x,y) | Defines the start and end nodes for the pathfinding algorithm. Cannot intersect with the internal '42' pattern boundaries. |
| **PERFECT** | Boolean | Toggles the topological mode. `True` generates an academic labyrinth (single path, no loops). `False` generates a Pac-Man style playable board (guaranteed alternative routes, minimal dead-ends). |
| **SEED** | Integer | Injects a fixed seed into the randomizer to ensure deterministic generation for debugging. |
| **OUTPUT_FILE** | String | Defines the destination for the serialized grid data. |

### Data Representation: Hexadecimal Wall Encoding
To optimize storage and ensure external compatibility, the generated maze is not saved as raw visual ASCII. Instead, each cell's topological state (open/closed walls) is serialized into a 4-bit hexadecimal integer.

* **Bit 0 (LSB):** North Wall
* **Bit 1:** East Wall
* **Bit 2:** South Wall
* **Bit 3:** West Wall

For example, a cell encoded as `A` (binary `1010`) dictates that the East and West walls are closed, while North and South remain open.

---

## 🧠 Core Algorithmic Logic

### Generation: Iterative Depth-First Search (DFS)
The core generation relies on a Depth-First Search algorithm. While DFS is inherently recursive, standard recursion in Python is dangerous for large grid sizes due to the default maximum recursion depth limit. 

To ensure system stability regardless of the `WIDTH` and `HEIGHT` parameters, the recursive logic was unrolled into an **explicit stack data structure**. This guarantees memory safety and prevents runtime crashes, successfully generating complex paths while respecting the `PERFECT` boolean constraint.

### Architecture & Reusability
The project is strictly compartmentalized. The maze generation logic, the pathfinding solver, and the MLX graphical visualizer are decoupled. This OOP architecture allows the core generation engine to be packaged via `setuptools` into a distribution wheel (`mazegen-*.whl`), making it importable as a third-party library in standard Python environments.

---

## 🚀 Execution & Usage

The application relies on isolated environments to prevent dependency pollution.

**Environment Setup:**
```bash
make env
source .env/bin/activate
make install
make run
```
![alt text](<image.png>)