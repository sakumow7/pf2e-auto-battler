# -*- coding: utf-8 -*-
"""
PF2E Grid Combat - Game launcher
"""
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from game.main import Game

def main():
    """Launch the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 