# -*- coding: utf-8 -*-
"""
PF2E Grid Combat - Main entry point
"""
from src.game.main import Game

def main():
    """Main entry point for the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 