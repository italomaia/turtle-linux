'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "lib"
directory.
'''
from game_engine import GameEngine

def main():
    engine = GameEngine()
    engine.main()

if __name__ == "__main__":
    main()
