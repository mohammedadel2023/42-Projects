*This activity has been created as part of the 42 curriculum by mkhashan, klafi.*

**This repository contains my personal solutions for the 42 curriculum. It is provided for portfolio and educational purposes only. Active 42 students must not copy or use this code, as doing so violates the school's strict academic integrity policies and will result in severe penalties for plagiarism**

# A_maze_ing

## Description
The "A_maze_ing" project aims to enable students to create a maze (perfect/imperfect) using different algorithms of their choice, and to find the path between two predefined starting and ending points using one of these algorithms.

The student then visually displays this maze using various tools (such as mlx, etc.).

## Instructions
 - Use `make env` to create a venv
 - activate the venv using `source .env/bin/activate`
 - Use make to install dependancy `make install`
 - create your config.txt file as mention down
 - run the script with passing the config file by `python -m mazegen.amazing config.txt`
## Resources
 -  https://en.wikipedia.org/wiki/Maze_generation_algorithm 
      - Used to study different maze generation algorithems
 -  "man files provided with the resources"
      - Used to study the mlx.
 -  https://medium.com/mitb-for-all/building-python-wheel-for-third-party-execution-4669b3d64cc9
       - used to understand how to create a .whl file 


## Config file structure
This file desigin to take different args based on the user choice such as:
 -  WIDTH: This arg define the width of the maze (in term of number of cells).
 -  HIGHT: This arg define the height of the maze (in term of number of cells).
    - This two args has some constraints as having values greater than specific point to make it possible for 42 logo appear in the middle of the maze.
 -  ENTRY: This arg define the start point of the maze.
 -  EXIT: This arg define the end poin of the maze.
    - Since no cell is isolated except the 42 cells and if the start or end point is a 42 cell so there is no open walls to go through so these points can not be a 42 cell.
 -  OUTPUT_FILE: This args define the name of the output file
    - This file will contain the maze(each cell describe in hexa numbers)
    - each hexa numbers represent the walls stat od the cell(open/closed)
    - This file will have the path from the start point to the end as (L'LEFT',R'RIGHT', ...)
    - The start and end pints will mentioned too
 -  PERFECT: This args define if the generated maze will be perfict or not.
 -  SEED: This args define if using seed or not which ensure the reproducibility.

## Maze generation algo
We use the DFS(depth-first-search) recursive implementation to create a maze and we based on our implementaino on using a stack to achieve an recursive part of algorithms.

## Reasons of chosen algorithms
 -  Simplicity: This algo is one of the simplest maze generation algorithms you can use.
 -  Clearity: The cleare advangaes and disadvatage of using this algo (like long paths) reduce the risk.
 -  personally (the motivation to implement the recursive part:) 

## Reusable code
In our coding we focus to ensure reusability by using the OOP approach so our maze generation code , path finding and the maze visualization is reusable.

## Team responability and project managments
The main way we used to build this project is a pair prograimg so reduce the mistacks can happen and all members be awaer of each decision we made.

While in the maze visualization two ways are implement and one of them are choosen.