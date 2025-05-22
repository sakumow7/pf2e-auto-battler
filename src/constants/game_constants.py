import pygame
import os

# Initialize Pygame for display info
pygame.init()
pygame.font.init()

# Get the display info to set window size
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Set window size to 80% of screen size
WINDOW_WIDTH = int(SCREEN_WIDTH * 0.95)
WINDOW_HEIGHT = int(SCREEN_HEIGHT * 0.95)

# Grid dimensions
GRID_COLS = 16
GRID_ROWS = 12

# Calculate grid size
GRID_SIZE = min((WINDOW_WIDTH) // GRID_COLS, (WINDOW_HEIGHT - 100) // GRID_ROWS)

# Recalculate window size to fit grid exactly
WINDOW_WIDTH = GRID_COLS * GRID_SIZE
WINDOW_HEIGHT = (GRID_ROWS * GRID_SIZE) + 100  # Add 100 for UI elements

# Colors
BACKGROUND_COLOR = (40, 40, 40)
GRID_COLOR = (60, 60, 60)
GRID_HIGHLIGHT = (80, 80, 80)
TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (200, 200, 100)
BUTTON_COLOR = (100, 100, 100)

# Character colors
FIGHTER_COLOR = (200, 100, 100)
ROGUE_COLOR = (100, 200, 100)
WIZARD_COLOR = (100, 100, 200)
ENEMY_COLOR = (200, 50, 50)

# Effect colors
STRIKE_COLOR = (255, 255, 255)
POWER_ATTACK_COLOR = (255, 100, 100)
MAGIC_MISSILE_COLOR = (100, 100, 255)
SHIELD_COLOR = (200, 200, 255)
HEAL_COLOR = (100, 255, 100)
MISS_COLOR = (100, 100, 100)
CRITICAL_COLOR = (255, 255, 100)
SNEAK_ATTACK_COLOR = (100, 255, 100)

# Animation timing
EFFECT_DELAY = 5  # Frames before effect starts
EFFECT_DURATION = 30  # Frames effect lasts

# Fonts
FONT = pygame.font.SysFont('Arial', 16)
TITLE_FONT = pygame.font.SysFont('Arial', 24)
LARGE_TITLE_FONT = pygame.font.SysFont('Arial', 36)

# Image paths
IMAGE_PATHS = {
    'fighter': os.path.join('assets', 'fighter.png'),
    'rogue': os.path.join('assets', 'rogue.png'),
    'wizard': os.path.join('assets', 'wizard.png'),
    'goblin': os.path.join('assets', 'goblin.png'),
    'ogre': os.path.join('assets', 'ogre.png'),
    'wyvern': os.path.join('assets', 'wyvern.png')
}

# Animation types
ANIMATIONS = {
    'strike': {'color': STRIKE_COLOR, 'duration': EFFECT_DURATION},
    'power_attack': {'color': POWER_ATTACK_COLOR, 'duration': EFFECT_DURATION * 1.5},
    'sneak_attack': {'color': SNEAK_ATTACK_COLOR, 'duration': EFFECT_DURATION},
    'magic_missile': {'color': MAGIC_MISSILE_COLOR, 'duration': EFFECT_DURATION},
    'heal': {'color': HEAL_COLOR, 'duration': EFFECT_DURATION},
    'shield': {'color': SHIELD_COLOR, 'duration': EFFECT_DURATION},
    'critical': {'color': CRITICAL_COLOR, 'duration': EFFECT_DURATION},
    'miss': {'color': MISS_COLOR, 'duration': EFFECT_DURATION * 0.5}
} 