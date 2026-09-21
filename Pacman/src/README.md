*This activity has been created as part of the 42 curriculum by mkhashan, klafi.*

**This repository contains my personal solutions for the 42 curriculum. It is provided for portfolio and educational purposes only. Active 42 students must not copy or use this code, as doing so violates the school's strict academic integrity policies and will result in severe penalties for plagiarism**

# Pacman

## Description
The "Pacman" project involves building a complete Pac-Man clone in Python. It includes multiple features that allow students to practice different topics they have learned, such as GUI visualization (using Pygame or MLX), object-oriented design patterns, persistent data storage, and external package integration.

## Instructions
 - Create a virtual environment: `make env`
 - Activate the virtual environment: `source .env/bin/activate`
 - Install dependencies (including the maze generator wheel): `make install`
 - Create your configuration file (`config.json`) as mentioned below.
 - Run the game: `make run` (which executes `python3 pac-man.py config.json`)

## Resources
 - https://www.geeksforgeeks.org/python/pygame-tutorial
 - https://www.pygame.org/wiki/tutorials
      - Used to learn the fundamentals of the Pygame library.
 - AI Assistance: AI was utilized specifically to understand the deployment process and how to package and push the game to itch.io.

## Configuration File Structure
The configuration uses a JSON file format (with support for comments) to customize the game parameters. If any value is missing or invalid, the game safely falls back to default values.
 - `highscore_filename`: The name of the JSON file used to load and store the top 10 player scores. (Default: `score_board.json`)
 - `lives`: The number of lives the player has across all levels before game over. (Default: 3)
 - `pacgum`: The amount of normal pacgums in the maze. (Default: 42)
 - `points_per_pacgum`: Points the player earns when eating a normal pacgum. (Default: 10)
 - `points_per_super_pacgum`: Points the player earns when eating a super pacgum. (Default: 50)
 - `points_per_ghost`: Points the player earns when eating an edible ghost. (Default: 200)
 - `seed`: Defines the random seed for maze generation to ensure reproducibility for the first level. (Default: 42)
 - `level_max_time`: The maximum time allowed for each level in seconds. (Default: 90)

## Highscore
The highscore system relies on local JSON file storage. It loads the existing data into a dictionary, sorts it, and maintains a strict Top 10 list. If a new score is greater than the minimum score in the list, it is added and the lowest score is deleted. 
**Why this approach?** We chose a local JSON file instead of a database (like SQLite) because it is lightweight, requires no external dependencies or server setup, and perfectly suits the scale of a localized arcade game while fulfilling the persistence requirements.

## Maze Generation 
The maze generation utilizes the provided A-Maze-ing `.whl` package. After installing the package via our Makefile, we import it and call the `generate` function (with `PERFECT` set to `False` to allow loops). This updates the `maze` attribute within our game state, standardizing the level architecture based on the external module's output.

## Implementation
The core of our implementation focused on strictly splitting the logic of the gameplay environment from the UI rendering. By isolating the game state updates (player movement, collisions, scoring) from the visual drawing functions, we significantly increased code readability and made the codebase easier to debug and scale.

## General Software Architecture
We utilized an object-oriented approach:
- `Game`: The main class that orchestrates the game loop, level progression, and entity management.
- `JsonParser`: A dedicated class handling all file I/O logic, including parsing the configuration file with comment support, applying fallback defaults, and managing the highscore data.
- Custom Exceptions: Built-in classes to handle specific configuration or file errors gracefully without causing a Python traceback.

## Project Management
- **Team Organization:** The project was primarily built utilizing a pair-programming approach, ensuring both developers understood the core architecture and debugging steps.
- **Project Artifacts:** You can view our timeline, task distribution, and risk analysis in our dedicated project management directory here: [`./project_management/`]