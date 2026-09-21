from src.pacman import main
import sys


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main("config.json")
    else:
        main(sys.argv[1])
