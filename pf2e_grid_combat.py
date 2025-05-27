import pygame
import sys
import random
import os
import math
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Union

# Initialize Pygame
pygame.init()
pygame.font.init()

# Get the display info to set window size
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Set window size to 80% of screen size
WINDOW_WIDTH = int(SCREEN_WIDTH * 0.95)
WINDOW_HEIGHT = int(SCREEN_HEIGHT * 0.95)

# Grid dimensions (number of cells)
GRID_COLS = 16
GRID_ROWS = 8

# Calculate grid size based on window dimensions and desired grid layout
# We subtract 100 from height to account for UI elements (50px top bar + 50px bottom margin)
GRID_SIZE = min((WINDOW_WIDTH) // GRID_COLS, (WINDOW_HEIGHT - 100) // GRID_ROWS)

# Recalculate window size to fit grid exactly
WINDOW_WIDTH = GRID_COLS * GRID_SIZE
WINDOW_HEIGHT = (GRID_ROWS * GRID_SIZE) + 100  # Add 100 for UI elements

# Add near the top, after GRID_SIZE and before colors
GRID_TOP = 50  # Space at the top for turn indicator, etc.

# Colors
BACKGROUND_COLOR = (40, 40, 40)
GRID_COLOR = (60, 60, 60)
GRID_HIGHLIGHT = (80, 80, 80)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
TITLE_COLOR = (255, 200, 100)  # Golden color for titles
OVERLAY_COLOR = (0, 0, 0, 180)  # Semi-transparent black

# Character colors
FIGHTER_COLOR = (200, 50, 50)  # Red
ROGUE_COLOR = (50, 200, 50)    # Green
WIZARD_COLOR = (50, 50, 200)   # Blue
CLERIC_COLOR = (200, 200, 50)  # Yellow
ENEMY_COLOR = (200, 50, 200)   # Purple

# Special Effects Constants
EFFECT_DURATION = 60  # frames (1 second at 60 FPS)
EFFECT_DELAY = 30  # frames (0.5 seconds at 60 FPS)
MAGIC_MISSILE_COLOR = (100, 100, 255)  # Light blue
HEAL_COLOR = (100, 255, 100)  # Light green
SHIELD_COLOR = (200, 200, 255)  # Light blue
STRIKE_COLOR = (255, 100, 100)  # Light red
POWER_ATTACK_COLOR = (255, 50, 50)  # Bright red
SNEAK_ATTACK_COLOR = (255, 255, 100)  # Yellow
CRITICAL_COLOR = (255, 215, 0)  # Gold
MISS_COLOR = (150, 150, 150)  # Gray
SPIRIT_LINK_COLOR = (255, 200, 100)  # Golden
SANCTUARY_COLOR = (200, 255, 200)  # Light green

# Animation types
ANIMATIONS = {
    'strike': {'color': STRIKE_COLOR, 'duration': EFFECT_DURATION},
    'power_attack': {'color': POWER_ATTACK_COLOR, 'duration': EFFECT_DURATION * 1.5},
    'sneak_attack': {'color': SNEAK_ATTACK_COLOR, 'duration': EFFECT_DURATION},
    'magic_missile': {'color': MAGIC_MISSILE_COLOR, 'duration': EFFECT_DURATION},
    'heal': {'color': HEAL_COLOR, 'duration': EFFECT_DURATION},
    'shield': {'color': SHIELD_COLOR, 'duration': EFFECT_DURATION},
    'critical': {'color': CRITICAL_COLOR, 'duration': EFFECT_DURATION},
    'miss': {'color': MISS_COLOR, 'duration': EFFECT_DURATION * 0.5},
    'link': {'color': SPIRIT_LINK_COLOR, 'duration': EFFECT_DURATION},
    'buff': {'color': SANCTUARY_COLOR, 'duration': EFFECT_DURATION}
}

# UI Constants
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 15
FONT_SIZE = 20
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
TITLE_FONT = pygame.font.SysFont('Arial', 32)
LARGE_TITLE_FONT = pygame.font.SysFont('Arial', 48)

# Image paths for character sprites
IMAGE_PATHS = {
    'fighter': 'images/fighter.webp',
    'rogue': 'images/rogue.webp',
    'wizard': 'images/wizard.webp',
    'cleric': 'images/cleric.webp',
    'goblin': 'images/goblin.webp',
    'ogre': 'images/ogre.webp',
    'wyvern': 'images/wyvern.webp'
}

class Effect:
    """
    Handles visual effects and animations in the game.
    This class manages various combat animations like magic missiles, strikes, healing effects, etc.
    Each effect has its own draw method and lifecycle.
    
    Attributes:
        start_pos: Starting position of the effect
        end_pos: Ending position of the effect
        color: RGB color tuple for the effect
        duration: How long the effect lasts in frames
        effect_type: Type of effect (e.g., "magic_missile", "strike", "heal")
        damage: Optional damage amount to display
        hit_type: Optional hit type ("hit", "miss", "critical")
    """
    def __init__(self, start_pos: Union['GridPosition', Tuple[int, int]], 
                 end_pos: Union['GridPosition', Tuple[int, int]], 
                 color: Tuple[int, int, int], 
                 duration: int = EFFECT_DURATION, 
                 effect_type: str = "basic",
                 damage: Optional[int] = None,
                 hit_type: Optional[str] = None):
        # Convert grid positions to pixel coordinates
        if isinstance(start_pos, GridPosition):
            self.start_pos = (start_pos.x * GRID_SIZE, start_pos.y * GRID_SIZE)
        else:
            self.start_pos = start_pos
            
        if isinstance(end_pos, GridPosition):
            self.end_pos = (end_pos.x * GRID_SIZE, end_pos.y * GRID_SIZE)
        else:
            self.end_pos = end_pos
            
        self.color = color
        self.duration = duration
        self.current_frame = -EFFECT_DELAY  # Start with negative frames for delay
        self.effect_type = effect_type
        self.damage = damage
        self.hit_type = hit_type
        
        # Calculate trajectory
        self.dx = self.end_pos[0] - self.start_pos[0]
        self.dy = self.end_pos[1] - self.start_pos[1]
        
    def update(self) -> bool:
        """Update effect animation. Returns True if effect is still active."""
        self.current_frame += 1
        return self.current_frame < self.duration
        
    def draw(self, surface: pygame.Surface):
        # Don't draw during delay period
        if self.current_frame < 0:
            return
            
        progress = self.current_frame / self.duration
        
        # Draw the main effect animation
        if self.effect_type == "magic_missile":
            self._draw_magic_missile(surface, progress)
        elif self.effect_type == "heal":
            self._draw_heal(surface, progress)
        elif self.effect_type == "shield":
            self._draw_shield(surface, progress)
        elif self.effect_type == "strike":
            self._draw_strike(surface, progress)
        elif self.effect_type == "power_attack":
            self._draw_power_attack(surface, progress)
        elif self.effect_type == "sneak_attack":
            self._draw_sneak_attack(surface, progress)
        elif self.effect_type == "critical":
            self._draw_critical(surface, progress)
        elif self.effect_type == "miss":
            self._draw_miss(surface, progress)
        elif self.effect_type == "link":
            self._draw_link(surface, progress)
        elif self.effect_type == "buff":
            self._draw_buff(surface, progress)
            
        # Draw damage numbers and hit/miss overlay
        if self.damage is not None or self.hit_type is not None:
            self._draw_damage_and_hit(surface, progress)
            
    def _draw_damage_and_hit(self, surface: pygame.Surface, progress: float):
        """Draw damage numbers and hit/miss overlay"""
        # Calculate position for damage numbers (slightly above target)
        x = self.end_pos[0] + GRID_SIZE//2
        y = self.end_pos[1] + GRID_SIZE//2 - 30  # Start above target
        
        # Draw hit/miss overlay
        if self.hit_type:
            overlay_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
            alpha = int(255 * (1 - progress))
            
            if self.hit_type == "hit":
                color = (0, 255, 0, alpha)  # Green for hit
                text = "HIT!"
            elif self.hit_type == "miss":
                color = (255, 0, 0, alpha)  # Red for miss
                text = "MISS!"
            elif self.hit_type == "critical":
                color = (255, 215, 0, alpha)  # Gold for critical
                text = "CRITICAL!"
            
            # Draw text
            font = pygame.font.SysFont('Arial', 24, bold=True)
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(GRID_SIZE, GRID_SIZE))
            overlay_surface.blit(text_surf, text_rect)
            
            # Draw the overlay
            surface.blit(overlay_surface, (x - GRID_SIZE, y - GRID_SIZE + 50))
        
        # Draw damage numbers
        if self.damage is not None:
            # Calculate y position with a slight bounce effect
            bounce = math.sin(progress * math.pi) * 20
            damage_y = y - bounce
            
            # Create damage text surface
            font = pygame.font.SysFont('Arial', 24, bold=True)
            damage_text = f"-{self.damage}"
            text_surf = font.render(damage_text, True, (255, 50, 50))  # Red color for damage
            
            # Calculate alpha based on progress
            alpha = int(255 * (1 - progress))
            text_surf.set_alpha(alpha)
            
            # Draw the damage text
            text_rect = text_surf.get_rect(center=(x, damage_y + 50))
            surface.blit(text_surf, text_rect)
        
    def _draw_magic_missile(self, surface, progress):
        # Draw multiple magic missile particles
        current_x = self.start_pos[0] + self.dx * progress
        current_y = self.start_pos[1] + self.dy * progress
        
        # Draw a glowing trail
        for i in range(5):  # 5 particles
            trail_progress = max(0, progress - i * 0.15)
            trail_x = self.start_pos[0] + self.dx * trail_progress
            trail_y = self.start_pos[1] + self.dy * trail_progress
            
            size = max(4, 12 - i * 2)
            alpha = max(0, 255 - i * 40)
            
            # Draw outer glow
            glow_size = size * 2
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha // 3), (glow_size, glow_size), glow_size)
            surface.blit(glow_surface, (trail_x - glow_size + GRID_SIZE//2, trail_y - glow_size + GRID_SIZE//2))
            
            # Draw core particle
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (size, size), size)
            surface.blit(particle_surface, (trail_x - size + GRID_SIZE//2, trail_y - size + GRID_SIZE//2))
            
    def _draw_strike(self, surface, progress):
        """Draw a basic strike animation"""
        start_x = self.start_pos[0] + GRID_SIZE//2
        start_y = self.start_pos[1] + GRID_SIZE//2
        end_x = self.end_pos[0] + GRID_SIZE//2
        end_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create slash trail
        slash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw multiple slash lines with varying angles
        for i in range(3):
            p = max(0, min(1, progress * 3 - i * 0.3))
            if 0 < p < 1:
                current_x = start_x + (end_x - start_x) * p
                current_y = start_y + (end_y - start_y) * p
                
                # Add vertical variation for slash effect
                offset = math.sin(p * math.pi) * 30
                pygame.draw.line(slash_surface, (*self.color, alpha),
                               (current_x - 25, current_y + offset),
                               (current_x + 25, current_y - offset), 4)
        
        surface.blit(slash_surface, (0, 50))  # Offset by 50 to account for turn indicator
        
    def _draw_power_attack(self, surface, progress):
        """Draw a power attack animation with multiple heavy strikes"""
        start_x = self.start_pos[0] + GRID_SIZE//2
        start_y = self.start_pos[1] + GRID_SIZE//2
        end_x = self.end_pos[0] + GRID_SIZE//2
        end_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create effect surface
        effect_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw multiple powerful slashes
        for i in range(4):
            p = max(0, min(1, progress * 4 - i * 0.25))
            if 0 < p < 1:
                current_x = start_x + (end_x - start_x) * p
                current_y = start_y + (end_y - start_y) * p
                
                # Larger slashes with more dramatic angles
                offset = math.sin(p * math.pi) * 40
                width = 6  # Thicker lines
                
                # Draw main slash
                pygame.draw.line(effect_surface, (*self.color, alpha),
                               (current_x - 35, current_y + offset),
                               (current_x + 35, current_y - offset), width)
                
                # Draw impact burst at the end
                if p > 0.8:
                    burst_radius = (p - 0.8) * 5 * GRID_SIZE
                    pygame.draw.circle(effect_surface, (*self.color, alpha//2),
                                     (end_x, end_y), burst_radius, 3)
        
        surface.blit(effect_surface, (0, 50))
        
    def _draw_sneak_attack(self, surface, progress):
        """Draw a sneak attack animation with quick, precise strikes"""
        center_x = self.end_pos[0] + GRID_SIZE//2
        center_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create sparkle effect
        effect_surface = pygame.Surface((GRID_SIZE * 3, GRID_SIZE * 3), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw multiple quick strikes from different angles
        for i in range(8):
            angle = (i / 8) * math.pi * 2 + progress * math.pi * 6
            distance = GRID_SIZE * (0.5 + math.sin(progress * math.pi * 3) * 0.5)
            
            x = GRID_SIZE * 1.5 + math.cos(angle) * distance
            y = GRID_SIZE * 1.5 + math.sin(angle) * distance
            
            # Draw strike lines
            line_progress = max(0, min(1, progress * 3 - 0.5))
            if line_progress > 0:
                line_x = GRID_SIZE * 1.5 + math.cos(angle) * distance * line_progress
                line_y = GRID_SIZE * 1.5 + math.sin(angle) * distance * line_progress
                pygame.draw.line(effect_surface, (*self.color, alpha),
                               (GRID_SIZE * 1.5, GRID_SIZE * 1.5),
                               (line_x, line_y), 2)
            
            # Draw sparkle effects
            size = max(2, 6 * (1 - progress))
            pygame.draw.circle(effect_surface, (*self.color, alpha), (x, y), size)
        
        # Add a subtle glow effect
        glow_radius = GRID_SIZE * (0.5 + math.sin(progress * math.pi) * 0.3)
        pygame.draw.circle(effect_surface, (*self.color, alpha//3),
                         (GRID_SIZE * 1.5, GRID_SIZE * 1.5), glow_radius)
        
        surface.blit(effect_surface, (center_x - GRID_SIZE * 1.5, center_y - GRID_SIZE * 1.5 + 50))
        
    def _draw_critical(self, surface, progress):
        """Draw a critical hit animation"""
        center_x = self.end_pos[0] + GRID_SIZE//2
        center_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create burst effect
        effect_surface = pygame.Surface((GRID_SIZE * 4, GRID_SIZE * 4), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw expanding burst
        burst_radius = GRID_SIZE * 2 * progress
        pygame.draw.circle(effect_surface, (*self.color, alpha//2),
                         (GRID_SIZE * 2, GRID_SIZE * 2), burst_radius, 4)
        
        # Draw radiating lines
        for i in range(12):
            angle = (i / 12) * math.pi * 2
            length = burst_radius * 1.2
            end_x = GRID_SIZE * 2 + math.cos(angle) * length
            end_y = GRID_SIZE * 2 + math.sin(angle) * length
            pygame.draw.line(effect_surface, (*self.color, alpha),
                           (GRID_SIZE * 2, GRID_SIZE * 2),
                           (end_x, end_y), 3)
        
        surface.blit(effect_surface, (center_x - GRID_SIZE * 2, center_y - GRID_SIZE * 2 + 50))
        
    def _draw_miss(self, surface, progress):
        """Draw a miss animation"""
        center_x = self.end_pos[0] + GRID_SIZE//2
        center_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create whiff effect
        effect_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw swoosh lines that fade quickly
        for i in range(3):
            p = progress + i * 0.2
            if p < 1:
                offset = math.sin(p * math.pi) * GRID_SIZE * 0.3
                pygame.draw.line(effect_surface, (*self.color, alpha),
                               (GRID_SIZE - 20, GRID_SIZE + offset),
                               (GRID_SIZE + 20, GRID_SIZE - offset), 2)
        
        surface.blit(effect_surface, (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))
        
    def _draw_shield(self, surface, progress):
        """Draw a shield animation"""
        center_x = self.start_pos[0] + GRID_SIZE//2
        center_y = self.start_pos[1] + GRID_SIZE//2
        
        # Draw rotating shield effect
        angle = progress * math.pi * 4
        radius = GRID_SIZE//2 + 5
        
        shield_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress * 0.5))
        
        # Draw multiple shield arcs
        for i in range(3):
            start_angle = angle + (i * math.pi * 2 / 3)
            end_angle = start_angle + math.pi / 2
            
            points = []
            for a in range(int(start_angle * 180/math.pi), int(end_angle * 180/math.pi)):
                rad = a * math.pi / 180
                x = GRID_SIZE + math.cos(rad) * radius
                y = GRID_SIZE + math.sin(rad) * radius
                points.append((x, y))
                
            if len(points) > 1:
                pygame.draw.lines(shield_surface, (*self.color, alpha), False, points, 3)
        
        surface.blit(shield_surface, (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))
        
    def _draw_heal(self, surface, progress):
        """Draw a healing animation"""
        center_x = self.start_pos[0] + GRID_SIZE//2
        center_y = self.start_pos[1] + GRID_SIZE//2
        radius = GRID_SIZE//2 * progress
        
        # Draw expanding healing circle
        circle_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        pygame.draw.circle(circle_surface, (*self.color, alpha), (GRID_SIZE, GRID_SIZE), radius, 3)
        
        # Draw healing crosses
        for i in range(4):
            angle = math.pi * 2 * (i / 4) + progress * math.pi
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            cross_size = 10
            pygame.draw.line(surface, self.color, (x - cross_size, y + 50), (x + cross_size, y + 50), 2)
            pygame.draw.line(surface, self.color, (x, y - cross_size + 50), (x, y + cross_size + 50), 2)
            
        surface.blit(circle_surface, (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))

    def _draw_link(self, surface, progress):
        """Draw the spirit link animation"""
        center_x = self.start_pos[0] + GRID_SIZE//2
        center_y = self.start_pos[1] + GRID_SIZE//2
        
        # Create link effect
        effect_surface = pygame.Surface((GRID_SIZE * 4, GRID_SIZE * 4), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw connecting lines
        for i in range(4):
            p = max(0, min(1, progress * 4 - i * 0.25))
            if 0 < p < 1:
                current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * p
                current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * p
                
                # Draw line with varying thickness
                line_width = int(GRID_SIZE * (1 - p * 0.5))
                pygame.draw.line(effect_surface, (*self.color, alpha),
                               (self.start_pos[0] + GRID_SIZE//2, self.start_pos[1] + GRID_SIZE//2),
                               (current_x, current_y), line_width)
        
        surface.blit(effect_surface, (center_x - GRID_SIZE * 2, center_y - GRID_SIZE * 2 + 50))

    def _draw_buff(self, surface, progress):
        """Draw the sanctuary animation"""
        center_x = self.start_pos[0] + GRID_SIZE//2
        center_y = self.start_pos[1] + GRID_SIZE//2
        
        # Create shield effect
        effect_surface = pygame.Surface((GRID_SIZE * 4, GRID_SIZE * 4), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        # Draw multiple shield arcs
        for i in range(4):
            start_angle = math.pi * 2 * (i / 4)
            end_angle = start_angle + math.pi / 2
            
            points = []
            for a in range(int(start_angle * 180/math.pi), int(end_angle * 180/math.pi)):
                rad = a * math.pi / 180
                x = GRID_SIZE + math.cos(rad) * GRID_SIZE
                y = GRID_SIZE + math.sin(rad) * GRID_SIZE
                points.append((x, y))
                
            if len(points) > 1:
                pygame.draw.lines(effect_surface, (*self.color, alpha), False, points, 3)
        
        surface.blit(effect_surface, (center_x - GRID_SIZE * 2, center_y - GRID_SIZE * 2 + 50))

class GridPosition:
    """
    Represents a position on the game grid.
    Handles grid-based positioning and calculations for movement and distance.
    Provides utility methods for converting between grid and pixel coordinates.
    
    Attributes:
        x: X coordinate on the grid
        y: Y coordinate on the grid
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, GridPosition):
            return False
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'GridPosition') -> int:
        """Calculate grid distance (in squares) to another position"""
        return max(abs(self.x - other.x), abs(self.y - other.y))
    
    def get_pixel_pos(self, y_offset=0) -> Tuple[int, int]:
        """Convert grid position to pixel coordinates"""
        return (self.x * GRID_SIZE, self.y * GRID_SIZE + y_offset)

class Character:
    """
    Base class for all characters in the game (both player characters and enemies).
    Implements core functionality like movement, combat, health management, and rendering.
    
    Attributes:
        name: Character's name
        hp/max_hp: Current and maximum health points
        base_ac: Base armor class
        attack_bonus: Bonus to attack rolls
        position: Current GridPosition
        sprite: Character's visual representation
        potions: Number of healing potions available
        speed: Movement speed in feet
    """
    def __init__(self, name: str, hp: int, ac: int, attack_bonus: int):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.base_ac = ac
        self.attack_bonus = attack_bonus
        self.position = GridPosition(0, 0)
        self.sprite = None
        self.sprite_path = None
        self.color = (200, 200, 200)
        self.potions = 3
        self.alive = True
        self.off_guard = False
        self.is_enemy = False
        self.speed = 25  # Speed in feet (5 feet per square)
        self.selected_action = None
        self.bonus_damage = 0  # New attribute for damage upgrade
        
    def load_sprite(self, sprite_path: str):
        """Load and scale character sprite"""
        try:
            if os.path.exists(sprite_path):
                self.sprite_path = sprite_path
                original_sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite = pygame.transform.scale(original_sprite, (GRID_SIZE, GRID_SIZE))
        except Exception as e:
            logging.error(f"Error loading sprite {sprite_path}: {e}")
            self.sprite = None
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def get_ac(self) -> int:
        return self.base_ac - 2 if self.off_guard else self.base_ac
    
    def can_move_to(self, new_pos: GridPosition, game: 'Game') -> bool:
        """Check if character can move to the given position"""
        if not (0 <= new_pos.x < GRID_COLS and 0 <= new_pos.y < GRID_ROWS):
            return False
        
        # Check if position is occupied
        for char in game.get_all_characters():
            if char != self and char.position == new_pos:
                return False
        
        # Calculate movement cost (diagonal movement costs more)
        distance = self.position.distance_to(new_pos)
        movement_cost = distance * 5  # 5 feet per square
        
        return movement_cost <= self.speed
    
    def get_valid_moves(self, game: 'Game') -> List[GridPosition]:
        """Get all valid movement positions"""
        valid_moves = []
        max_squares = self.speed // 5
        
        for x in range(max(0, self.position.x - max_squares), 
                      min(GRID_COLS, self.position.x + max_squares + 1)):
            for y in range(max(0, self.position.y - max_squares),
                         min(GRID_ROWS, self.position.y + max_squares + 1)):
                pos = GridPosition(x, y)
                if self.can_move_to(pos, game):
                    valid_moves.append(pos)
        
        return valid_moves
    
    def move_to(self, new_pos: GridPosition, game: 'Game') -> bool:
        """Attempt to move character to new position"""
        if self.can_move_to(new_pos, game):
            self.position = new_pos
            return True
        else:
            if hasattr(game, 'add_message'):
                game.add_message(f"[DEBUG] {self.name} tried to move to occupied square {new_pos.x},{new_pos.y}")
            return False
    
    def draw(self, surface: pygame.Surface, game: Optional['Game'] = None):
        if not self.alive:
            return
        x = self.position.x * GRID_SIZE
        y = self.position.y * GRID_SIZE  # Remove GRID_TOP - it's added when grid_surface is blitted
        # Draw active turn indicator if this is the current character
        if (game and not self.is_enemy and 
            game.state == "combat" and 
            game.current_member_idx < len(game.party) and 
            game.party[game.current_member_idx] == self):
            pulse = abs(math.sin(pygame.time.get_ticks() / 500))
            highlight_color = (255, 255, 255, int(100 + 155 * pulse))
            highlight_surface = pygame.Surface((GRID_SIZE + 8, GRID_SIZE + 8), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, highlight_color, 
                           (0, 0, GRID_SIZE + 8, GRID_SIZE + 8), 4, border_radius=4)
            surface.blit(highlight_surface, (x - 4, y - 4))
        # Draw character sprite or fallback shape
        if self.sprite:
            # Always scale sprite to fit grid square
            sprite = pygame.transform.scale(self.sprite, (GRID_SIZE, GRID_SIZE))
            surface.blit(sprite, (x, y))
        else:
            if self.is_enemy:
                points = [
                    (x + GRID_SIZE//2, y),
                    (x + GRID_SIZE, y + GRID_SIZE//2),
                    (x + GRID_SIZE//2, y + GRID_SIZE),
                    (x, y + GRID_SIZE//2)
                ]
                pygame.draw.polygon(surface, self.color, points)
                pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            else:
                pygame.draw.circle(surface, self.color, 
                                 (x + GRID_SIZE//2, y + GRID_SIZE//2), 
                                 GRID_SIZE//2)
                pygame.draw.circle(surface, (255, 255, 255),
                                 (x + GRID_SIZE//2, y + GRID_SIZE//2),
                                 GRID_SIZE//2, 2)
        # Draw health bar below the character instead of above
        health_percent = self.hp / self.max_hp
        bar_width = GRID_SIZE * health_percent
        pygame.draw.rect(surface, (100, 0, 0),
                        (x, y + GRID_SIZE + 2, GRID_SIZE, 5))
        if health_percent > 0:
            pygame.draw.rect(surface, (0, 255, 0),
                           (x, y + GRID_SIZE + 2, bar_width, 5))

    def is_flanking(self, target: 'Character', game: 'Game') -> bool:
        """Check if this character is flanking the target with an ally"""
        if not target.is_alive():
            return False
            
        # Get all allies (characters on the same side)
        allies = [char for char in game.get_all_characters() 
                 if char != self and char.is_alive() and 
                 char.is_enemy == self.is_enemy]
        
        # Check if any ally is on the opposite side of the target
        my_pos = self.position
        target_pos = target.position
        
        for ally in allies:
            ally_pos = ally.position
            # Check if ally is also adjacent to target
            if ally_pos.distance_to(target_pos) <= 1:
                # Check if ally is on opposite side
                # If we're on same row
                if my_pos.y == target_pos.y == ally_pos.y:
                    if (my_pos.x < target_pos.x < ally_pos.x) or (ally_pos.x < target_pos.x < my_pos.x):
                        return True
                # If we're on same column
                elif my_pos.x == target_pos.x == ally_pos.x:
                    if (my_pos.y < target_pos.y < ally_pos.y) or (ally_pos.y < target_pos.y < my_pos.y):
                        return True
                # If we're diagonal
                elif abs(my_pos.x - ally_pos.x) == 2 and abs(my_pos.y - ally_pos.y) == 2:
                    if target_pos.x == (my_pos.x + ally_pos.x) // 2 and target_pos.y == (my_pos.y + ally_pos.y) // 2:
                        return True
        
        return False

    def apply_upgrade(self, upgrade_type: str):
        """Apply an upgrade to the character"""
        if upgrade_type == "Accuracy":
            self.attack_bonus += 1
            return f"{self.name} gains +1 to attack rolls!"
        elif upgrade_type == "Damage":
            self.bonus_damage += 2
            return f"{self.name} gains +2 to damage!"
        elif upgrade_type == "Speed":
            self.speed += 10  # +2 squares = +10 feet
            return f"{self.name} can move 2 more squares!"
        elif upgrade_type == "Vitality":
            self.max_hp += 10
            self.hp += 10
            return f"{self.name} gains 10 max HP!"
            
    def heal_full(self):
        """Heal to full health"""
        old_hp = self.hp
        self.hp = self.max_hp
        return self.hp - old_hp

    def attack(self, target: 'Character', game: 'Game', dice: Tuple[int, int] = (1, 8), 
              bonus_damage: int = 0, sneak_attack: bool = False) -> Tuple[int, bool]:
        """Execute an attack against a target"""
        if game.actions_left < 1:
            game.add_message("Not enough actions!")
            return 0, False
            
        if not target.is_alive():
            return 0, False
            
        # Check range
        distance = self.position.distance_to(target.position)
        if distance > 1:  # Melee range is 1 square
            game.add_message(f"{target.name} is out of range!")
            return 0, False
            
        # Check for flanking
        if self.is_flanking(target, game):
            target.off_guard = True
            game.add_message(f"{target.name} is flanked and Off-Guard!")
            
        roll = random.randint(1, 20)
        total = roll + self.attack_bonus
        target_ac = target.get_ac()
        
        game.add_message(f"{self.name} rolls to hit: d20({roll}) + {self.attack_bonus} = {total} vs AC {target_ac}")
        
        if roll == 1:
            game.add_message("Critical Miss!")
            # Add miss animation with overlay
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), MISS_COLOR, 
                                 effect_type="miss", hit_type="miss"))
            target.off_guard = False
            return 1, False
            
        # Calculate damage
        dice_num, dice_sides = dice
        if roll == 20 or total >= target_ac + 10:
            game.add_message("Critical Hit!")
            dmg = sum(random.randint(1, dice_sides) for _ in range(dice_num * 2))
            # Add critical hit animation with overlay and damage
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), CRITICAL_COLOR, 
                                 effect_type="critical", damage=dmg, hit_type="critical"))
        elif total >= target_ac:
            game.add_message("Hit!")
            dmg = sum(random.randint(1, dice_sides) for _ in range(dice_num))
            # Add basic strike animation with overlay and damage
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), STRIKE_COLOR, 
                                 effect_type="strike", damage=dmg, hit_type="hit"))
        else:
            game.add_message("Miss!")
            # Add miss animation with overlay
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), MISS_COLOR, 
                                 effect_type="miss", hit_type="miss"))
            target.off_guard = False
            return 1, False
            
        if sneak_attack or target.off_guard:
            sa_dmg = random.randint(1, 6)
            dmg += sa_dmg
            game.add_message(f"Sneak Attack! Extra d6: {sa_dmg}")
            # Add sneak attack animation with damage
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), SNEAK_ATTACK_COLOR, 
                                 effect_type="sneak_attack", damage=sa_dmg))
            
        dmg += bonus_damage + self.bonus_damage
        game.add_message(f"Damage Total: {dmg}")
        target.take_damage(dmg, game)
        target.off_guard = False
        
        # Check for wave completion after each successful attack
        if not target.is_alive():
            game.check_wave_complete()
        
        return 1, True

    def take_damage(self, damage: int, game: 'Game'):
        """Take damage and update health"""
        self.hp = max(0, self.hp - damage)
        game.add_message(f"{self.name} takes {damage} damage! (HP: {self.hp}/{self.max_hp})")
        
        if self.hp == 0:
            self.alive = False
            game.add_message(f"{self.name} has fallen!")

    def heal(self, game: 'Game') -> int:
        """Use a potion to heal"""
        if self.potions > 0:
            game.add_message(f"{self.name} uses a potion to heal 15 HP.")
            # Add heal animation
            game.add_effect(Effect(self.get_pixel_pos(), self.get_pixel_pos(), HEAL_COLOR, effect_type="heal"))
            self.hp = min(self.hp + 15, self.max_hp)
            self.potions -= 1
            game.add_message(f"HP after healing: {self.hp}/{self.max_hp} | Potions left: {self.potions}")
            return 1
        else:
            game.add_message("No potions left!")
            return 0

    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get basic actions available to all characters"""
        actions = []
        
        # Add Stride action button (doesn't show movement squares yet)
        if game.actions_left >= 1:
            actions.append(("Stride", self.position, lambda: self.select_stride(game)))
            
        # Add Heal action
        if game.actions_left >= 1 and self.potions > 0:
            actions.append(("Potion", self.position, lambda: self.heal(game)))
            
        return actions
        
    def select_stride(self, game: 'Game') -> Tuple[int, bool]:
        """Select Stride action to show movement options"""
        game.selected_character = self
        game.highlighted_squares = self.get_valid_moves(game)
        game.add_message(f"{self.name} is selecting where to Stride (move up to {self.speed} feet)")
        return 0, True  # Don't consume action yet, will be consumed on actual move

    def get_pixel_pos(self) -> Tuple[int, int]:
        """Get the pixel position of the character for animations"""
        return (self.position.x * GRID_SIZE, self.position.y * GRID_SIZE)

class Fighter(Character):
    """
    Fighter class character specializing in melee combat.
    Features high HP, good armor, and powerful melee attacks.
    Special ability: Power Attack (2 actions) for increased damage.
    
    Starting Stats:
        HP: 50
        AC: 18
        Attack Bonus: +9
    """
    def __init__(self, name: str):
        super().__init__(name, hp=50, ac=18, attack_bonus=9)
        self.color = FIGHTER_COLOR
        self.load_sprite(IMAGE_PATHS['fighter'])
        
    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get available actions for the fighter"""
        actions = []  # Start fresh instead of using super() to control action order
        
        # Add Stride action button (doesn't show movement squares yet)
        if game.actions_left >= 1:
            actions.append(("Stride [1]", self.position, lambda: self.select_stride(game)))
            
        # Add Heal action
        if game.actions_left >= 1 and self.potions > 0:
            actions.append(("Heal [1]", self.position, lambda: self.heal(game)))
        
        # Add melee actions if we have a selected target
        if game.selected_target and game.selected_target.is_alive():
            distance = self.position.distance_to(game.selected_target.position)
            target = game.selected_target  # Store target to avoid lambda capture issues
            
            if distance <= 1:  # Melee range
                # Add Strike if we have enough actions
                if game.actions_left >= 1:
                    actions.append(("Strike [1]", self.position,
                                  ("Strike", lambda t: self.attack(t, game, dice=(1, 10)))))
                
                # Add Power Attack if we have enough actions
                if game.actions_left >= 2:
                    actions.append(("Power Attack [2]", self.position, 
                                  ("Power Attack", lambda t: self.power_attack(t, game))))
        
        # Always add End Turn action
        actions.append(("End Turn [0]", self.position, lambda: game.next_turn()))
        
        return actions
        
    def power_attack(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Execute a Power Attack action"""
        if game.actions_left < 2:
            game.add_message("Not enough actions for Power Attack!")
            return 0, False
            
        game.add_message(f"{self.name} uses Power Attack!")
        
        # Add power attack animation
        game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), POWER_ATTACK_COLOR, effect_type="power_attack"))
        
        used, hit = self.attack(target, game, dice=(2, 10), bonus_damage=2)
        return 2, True  # Always consume 2 actions, regardless of hit

class Rogue(Character):
    """
    Rogue class character focusing on mobility and tactical positioning.
    Excels at flanking and dealing extra damage to off-guard targets.
    Special abilities: Sneak Attack and Twin Feint.
    
    Starting Stats:
        HP: 38
        AC: 17
        Attack Bonus: +8
        Speed: 30 feet (faster than other classes)
    """
    def __init__(self, name: str):
        super().__init__(name, hp=38, ac=17, attack_bonus=8)
        self.color = ROGUE_COLOR
        self.load_sprite(IMAGE_PATHS['rogue'])
        self.speed = 30  # Rogues are faster
        
    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get available actions for the rogue"""
        actions = []  # Start fresh instead of using super()
        
        # Add Stride action button (doesn't show movement squares yet)
        if game.actions_left >= 1:
            actions.append(("Stride [1]", self.position, lambda: self.select_stride(game)))
            
        # Add Heal action
        if game.actions_left >= 1 and self.potions > 0:
            actions.append(("Heal [1]", self.position, lambda: self.heal(game)))
        
        # Add melee actions if we have a selected target
        if game.selected_target and game.selected_target.is_alive():
            distance = self.position.distance_to(game.selected_target.position)
            target = game.selected_target  # Store target to avoid lambda capture issues
            
            if distance <= 1:  # Melee range
                # Add Strike if we have enough actions
                if game.actions_left >= 1:
                    actions.append(("Strike [1]", self.position,
                                  ("Strike", lambda t: self.strike(t, game))))
                
                # Add Twin Feint if we have enough actions
                if game.actions_left >= 2:
                    actions.append(("Twin Feint [2]", self.position,
                                  ("Twin Feint", lambda t: self.twin_feint(t, game))))
        
        # Always add End Turn action
        actions.append(("End Turn [0]", self.position, lambda: game.next_turn()))
        
        return actions
        
    def strike(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Execute a Strike with potential Sneak Attack"""
        if game.actions_left < 1:
            game.add_message("Not enough actions!")
            return 0, False
            
        sneak = target.off_guard
        used, hit = self.attack(target, game, dice=(1, 6), sneak_attack=sneak)
        game.actions_left -= used  # Consume action regardless of hit
        if hit and random.random() < 0.5:
            target.off_guard = True
            game.add_message(f"{target.name} is now Off-Guard until their next turn!")
        return used, hit
        
    def twin_feint(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Execute a Twin Feint action"""
        if game.actions_left < 2:
            game.add_message("Not enough actions for Twin Feint!")
            return 0, False
            
        game.add_message(f"{self.name} uses Twin Feint!")
        
        # First strike
        used1, hit1 = self.attack(target, game, dice=(1, 6))
        
        # Second strike with target Off-Guard
        target.off_guard = True
        used2, hit2 = self.attack(target, game, dice=(1, 6), sneak_attack=True)
        target.off_guard = False
        
        return 2, hit1 or hit2  # Always consume exactly 2 actions total

class Wizard(Character):
    """
    Wizard class character specializing in ranged magical attacks.
    Features various spells with different ranges and effects.
    Special abilities: Magic Missile, Arcane Blast, and Shield spell.
    
    Starting Stats:
        HP: 32
        AC: 16
        Attack Bonus: +6
        
    Spell Ranges:
        Arcane Blast: 20 feet (4 squares)
        Magic Missile: 120 feet (24 squares)
    """
    # Spell ranges in squares (1 square = 5 feet)
    ARCANE_BLAST_RANGE = 4  # 20 feet
    MAGIC_MISSILE_RANGE = 24  # 120 feet
    
    def __init__(self, name: str):
        super().__init__(name, hp=32, ac=16, attack_bonus=6)
        self.color = WIZARD_COLOR
        self.shield_up = False
        self.load_sprite(IMAGE_PATHS['wizard'])
        
    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get available actions for the wizard"""
        actions = []  # Start fresh instead of using super()
        
        # Add Stride action button (doesn't show movement squares yet)
        if game.actions_left >= 1:
            actions.append(("Stride [1]", self.position, lambda: self.select_stride(game)))
            
        # Add Heal action
        if game.actions_left >= 1 and self.potions > 0:
            actions.append(("Heal [1]", self.position, lambda: self.heal(game)))
        
        # Add spells that need targeting
        if game.selected_target and game.selected_target.is_alive():
            distance = self.position.distance_to(game.selected_target.position)
            target = game.selected_target  # Store target to avoid lambda capture issues
            
            # Add Arcane Blast if in range and have enough actions
            if distance <= self.ARCANE_BLAST_RANGE and game.actions_left >= 1:
                actions.append(("Arcane Blast [1]", self.position,
                              ("Arcane Blast", lambda t: self.arcane_blast(target, game))))
            
            # Add Magic Missile options if in range and have enough actions
            if distance <= self.MAGIC_MISSILE_RANGE:
                for i in range(1, min(game.actions_left + 1, 4)):
                    count = i  # Store count to avoid lambda capture issues
                    actions.append((f"Magic Missile [{i}]", self.position,
                                  (f"Magic Missile ({i})", 
                                   lambda t, c=count: self.magic_missile(t, game, c))))
        
        # Add Shield spell (no target needed) if have enough actions and not already up
        if game.actions_left >= 1 and not self.shield_up:
            actions.append(("Shield [1]", self.position, lambda: self.cast_shield(game)))
        
        # Always add End Turn action
        actions.append(("End Turn [0]", self.position, lambda: game.next_turn()))
        
        return actions
        
    def arcane_blast(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Execute an Arcane Blast attack"""
        # Check range
        distance = self.position.distance_to(target.position)
        if distance > self.ARCANE_BLAST_RANGE:
            game.add_message(f"{target.name} is out of range for Arcane Blast (range: 20 feet)")
            return 0, False
            
        used, hit = self.attack(target, game, dice=(2, 4))
        if self.shield_up:
            game.add_message("Shield fades.")
            self.base_ac -= 2
            self.shield_up = False
        return 1, True  # Always consume 1 action
        
    def magic_missile(self, target: 'Character', game: 'Game', action_count: int = 1) -> Tuple[int, bool]:
        """Cast Magic Missile"""
        # Check range
        distance = self.position.distance_to(target.position)
        if distance > self.MAGIC_MISSILE_RANGE:
            game.add_message(f"{target.name} is out of range for Magic Missile (range: 120 feet)")
            return 0, False
            
        if game.actions_left < action_count:
            game.add_message("Not enough actions!")
            return 0, False
            
        game.add_message(f"{self.name} uses {action_count} action(s) to cast Magic Missile!")
        
        # Add magic missile animation for each missile
        for i in range(action_count):
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), MAGIC_MISSILE_COLOR, effect_type="magic_missile"))
            dmg = random.randint(1, 4) + 1
            game.add_message(f"Magic Missile #{i+1}: {dmg} force damage")
            target.take_damage(dmg, game)
            
        if self.shield_up:
            game.add_message("Shield fades.")
            self.base_ac -= 2
            self.shield_up = False
            
        return action_count, True
        
    def cast_shield(self, game: 'Game') -> Tuple[int, bool]:
        """Cast the Shield spell"""
        game.add_message(f"{self.name} casts Shield! +2 AC until next turn.")
        
        # Add shield animation
        game.add_effect(Effect(self.position, self.position, SHIELD_COLOR, effect_type="shield"))
        
        self.base_ac += 2
        self.shield_up = True
        return 1, True
    
class Cleric(Character):
    """
    Cleric class character specializing in supportive magical spells.
    Features various spells with different ranges and effects.
    Special abilities: Lesser Heal, Sanctuary, and Spirit Link spell.
    
    Starting Stats:
        HP: 32
        AC: 16
        Attack Bonus: +6
        
    Spell Ranges:
        Lesser Heal: 5 feet (1 squares) but variable
        Sanctuary: 5 feet (1 square)
        Spirit Link: 30 feet (6 square)
    """
    # Spell ranges in squares (1 square = 5 feet)
    LESSER_HEAL_RANGE = 1 # 5 feet and variable
    LESSER_HEAL_UP_RANGE = 6 # 30 feet
    SANCTUARY_RANGE = 1 # 5 feet
    SPIRIT_LINK_RANGE = 6 # 30 feet
    
    def __init__(self, name: str):
        super().__init__(name, hp=32, ac=16, attack_bonus=6)
        self.color = CLERIC_COLOR
        # self.shield_up = False
        self.load_sprite(IMAGE_PATHS['cleric'])
        
    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get available actions for the cleric"""
        actions = []  # Start fresh instead of using super()
        
        # Add Stride action button (doesn't show movement squares yet)
        if game.actions_left >= 1:
            actions.append(("Stride [1]", self.position, lambda: self.select_stride(game)))
            
        # Add Heal action (potion)
        if game.actions_left >= 1 and self.potions > 0:
            actions.append(("Potion [1]", self.position, lambda: self.heal(game)))
        
        # Add spells that need targeting
        if game.selected_target and game.selected_target.is_alive():
            distance = self.position.distance_to(game.selected_target.position)
            target = game.selected_target  # Store target to avoid lambda capture issues
            
            # Add Strike if in melee range and have enough actions
            if distance <= 1 and game.actions_left >= 1:
                actions.append(("Strike [1]", self.position,
                              ("Strike", lambda t: self.attack(t, game, dice=(1, 6)))))
            
            # Add Spirit Link if in range and have enough actions
            if distance <= self.SPIRIT_LINK_RANGE and game.actions_left >= 1:
                actions.append(("Spirit Link [1]", self.position,
                              ("Spirit Link", lambda t: self.spirit_link(target, game))))
            
            # Add Sanctuary if in range and have enough actions
            if distance <= self.SANCTUARY_RANGE and game.actions_left >= 1:
                actions.append(("Sanctuary [1]", self.position,
                              ("Sanctuary", lambda t: self.sanctuary(target, game))))
            
            # Add Heal [1] if in touch range
            if distance <= self.LESSER_HEAL_RANGE and game.actions_left >= 1:
                actions.append(("Heal [1]", self.position,
                                ("Heal (1)", lambda t: self.lesser_heal(target, game, 1))))

            # Add Heal [2] if in 30-foot range
            if  distance <= self.LESSER_HEAL_UP_RANGE and game.actions_left >= 2:
                actions.append(("Heal [2]", self.position,
                                ("Heal (2)", lambda t: self.lesser_heal(target, game, 2))))

            # Add Heal [3] (AoE, no target check needed)
            if game.actions_left >= 3:
                actions.append(("Heal [3]", self.position,
                                ("Heal (3)", lambda t: self.lesser_heal(target, game, 3))))
        
        # Always add End Turn action
        actions.append(("End Turn [0]", self.position, lambda: game.next_turn()))
        
        return actions
        
    def spirit_link(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Cast Spirit Link to balance HP between self and the target."""
        distance = self.position.distance_to(target.position)
        if distance > self.SPIRIT_LINK_RANGE:
            game.add_message(f"{target.name} is out of range for Spirit Link (range: 30 feet).")
            return 0, False

        # Calculate average HP (rounded down)
        total_hp = self.hp + target.hp
        new_hp = total_hp // 2

        # Show visual effect
        game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), SPIRIT_LINK_COLOR, effect_type="link"))

        game.add_message(f"{self.name} casts Spirit Link on {target.name} to equalize their HP.")
        game.add_message(f"HP Before: {self.name} = {self.hp} HP | {target.name} = {target.hp} HP")

        # Set both HPs to the average
        self.hp = min(new_hp, self.max_hp)
        target.hp = min(new_hp, target.max_hp)

        game.add_message(f"HP After: {self.name} = {self.hp}/{self.max_hp} | {target.name} = {target.hp}/{target.max_hp}")

        return 1, True  # Consumes 1 action
    
    def sanctuary(self, target: 'Character', game: 'Game') -> Tuple[int, bool]:
        """Cast Sanctuary to protect an ally from hostile actions"""
        distance = self.position.distance_to(target.position)
        if distance > self.SANCTUARY_RANGE:
            game.add_message(f"{target.name} is out of range for Sanctuary (range: 5 feet).")
            return 0, False

        game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), SANCTUARY_COLOR, effect_type="buff"))
        game.add_message(f"{self.name} casts Sanctuary on {target.name}.")

        target.add_condition("Sanctuary", duration=1)  # Implement this in your condition/effect system
        return 1, True
        

    def lesser_heal(self, target: 'Character', game: 'Game', action_count: int) -> Tuple[int, bool]:
        """Cast Lesser Heal with variable action cost (1–3 actions)"""
        if game.actions_left < action_count:
            game.add_message("Not enough actions to cast Lesser Heal.")
            return 0, False

        distance = self.position.distance_to(target.position)
        if action_count == 1 and distance > 1:
            game.add_message("Lesser Heal [1 Action] is touch only — target too far.")
            return 0, False
        elif action_count in (2, 3) and distance > self.LESSER_HEAL_UP_RANGE:
            game.add_message("Lesser Heal [2+ Actions] requires target within 30 feet.")
            return 0, False

        game.add_message(f"{self.name} casts Lesser Heal with {action_count} action(s)!")

        if action_count == 1:
            # 1-action: touch only
            heal_amount = random.randint(1, 8)
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), HEAL_COLOR, effect_type="heal"))
            old_hp = target.hp
            target.hp = min(target.hp + heal_amount, target.max_hp)
            healed = target.hp - old_hp
            game.add_message(f"{target.name} heals for {healed} HP. Now at {target.hp}/{target.max_hp} HP.")

        elif action_count == 2:
            # 2-actions: ranged + bonus healing
            heal_amount = random.randint(1, 8) + 8
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), HEAL_COLOR, effect_type="heal"))
            old_hp = target.hp
            target.hp = min(target.hp + heal_amount, target.max_hp)
            healed = target.hp - old_hp
            game.add_message(f"{target.name} heals for {healed} HP. Now at {target.hp}/{target.max_hp} HP.")

        else:
            # 3-actions: AoE to all friendlies within 30 feet
            heal_amount = random.randint(1, 8)
            game.add_message(f"A wave of healing energy pulses outward from {self.name}, restoring {heal_amount} HP to all allies in range!")

            for char in game.party:
                if not char.is_alive() or char.is_enemy:
                    continue
                if self.position.distance_to(char.position) <= self.LESSER_HEAL_UP_RANGE:
                    old_hp = char.hp
                    char.hp = min(char.hp + heal_amount, char.max_hp)
                    healed = char.hp - old_hp
                    game.add_effect(Effect(self.get_pixel_pos(), char.get_pixel_pos(), HEAL_COLOR, effect_type="heal"))
                    if healed > 0:
                        game.add_message(f"{char.name} heals for {healed} HP. Now at {char.hp}/{char.max_hp} HP.")
                    else:
                        game.add_message(f"{char.name} is already at full HP.")

        return action_count, True

class Enemy(Character):
    """
    Enemy class representing various hostile creatures.
    Implements AI behavior and enemy-specific attributes.
    Different enemy types (Goblin, Ogre, Wyvern) have unique stats and abilities.
    
    Enemy Types:
        - Goblin: Basic enemy with balanced stats
        - Ogre: Tough enemy with high damage
        - Wyvern: Boss enemy with high stats across the board
    """
    def __init__(self, name: str, hp: int, ac: int, attack_bonus: int, damage_dice: Tuple[int, int] = (1, 8)):
        super().__init__(name, hp, ac, attack_bonus)
        self.damage_dice = damage_dice
        self.color = ENEMY_COLOR
        self.is_enemy = True
        
        # Load appropriate sprite based on enemy type
        if name == "Goblin":
            self.load_sprite(IMAGE_PATHS['goblin'])
            self.speed = 25
        elif name == "Ogre":
            self.load_sprite(IMAGE_PATHS['ogre'])
            self.speed = 30
        elif name == "Wyvern":
            self.load_sprite(IMAGE_PATHS['wyvern'])
            self.speed = 35
    
    def get_actions(self, game: 'Game') -> List[Tuple[str, GridPosition, callable]]:
        """Get available actions for the enemy"""
        actions = []
        
        # Get all party members in range
        for char in game.party:
            if char.is_alive():
                distance = self.position.distance_to(char.position)
                if distance <= 1:  # Melee range
                    actions.append(("Attack", char.position,
                                  lambda t=char: self.attack(t, game, dice=self.damage_dice)))
        
        # Add movement options
        if game.actions_left >= 1:
            for pos in self.get_valid_moves(game):
                actions.append(("Move", pos, lambda p=pos: self.move_to(p, game)))
        
        return actions

class Game:
    """
    Main game class handling the core game loop and state management.
    Controls game flow, UI rendering, input handling, and battle mechanics.
    
    Features:
        - Turn-based combat system
        - Wave-based progression
        - Character upgrades between waves
        - Visual effects and animations
        - Message log system
        - Multiple game states (combat, upgrade, wave confirmation)
        
    Game Flow:
        1. Player selects character class
        2. Battle starts with wave 1 (Goblins)
        3. After each wave, characters can be upgraded
        4. Wave 2 features Ogres
        5. Final wave 3 features the Wyvern boss
        6. Victory achieved after defeating all waves
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PF2E Grid Combat")
        
        self.clock = pygame.time.Clock()
        self.state = "intro"
        self.selected_action = None
        self.selected_character = None
        self.selected_target = None
        self.highlighted_squares = []
        self.party = []
        self.enemies = []
        self.current_enemies = []
        self.current_enemy = None
        self.current_member_idx = 0
        self.actions_left = 3
        self.messages = []
        self.message_scroll = 0
        self.available_actions = []
        self.pending_action = None
        self.valid_targets = []
        self.action_delay = 0
        self.wave_number = 0
        self.wave_announcement = None
        self.wave_announcement_end = 0
        self.upgrade_selection = None
        self.available_upgrades = ["Accuracy", "Damage", "Speed", "Vitality"]
        self.wave_summary = None
        self.effects = []  # List to store active effects
        self.showing_help = False  # New state for help overlay
        self.help_button_rect = None  # Store help button rectangle
        self.ai_action_queue = []  # Queue of AI actions to perform
        self.ai_current_char = None  # Current AI character taking actions
        self.ai_actions_remaining = 0  # Actions left for current AI character
        self._schedule_next_ai_action = False  # Flag to schedule next AI action after delay
        self._end_turn_after_delay = False  # Flag to end turn after delay
        
        # Create surfaces
        self.grid_surface = pygame.Surface((GRID_COLS * GRID_SIZE, GRID_ROWS * GRID_SIZE))
        self.message_surface = pygame.Surface((WINDOW_WIDTH - 40, 200))
        self.action_surface = pygame.Surface((WINDOW_WIDTH, 100))
        self.overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.action_buttons = []
        
        self.init_game()
    
    def add_effect(self, effect: Effect):
        """Add a new visual effect"""
        self.effects.append(effect)

    def update_effects(self):
        """Update and remove finished effects"""
        self.effects = [effect for effect in self.effects if effect.update()]

    def init_game(self):
        """Initialize the game state"""
        self.state = "intro"  # Changed from "class_select" to "intro"
        self.party = []
        self.enemies = []
        self.current_enemies = []
        self.current_enemy = None
        self.current_member_idx = 0
        self.actions_left = 3
        self.messages = []
        self.wave_number = 0  # Initialize wave number to 0
        self.available_actions = [
            ("Start Game", GridPosition(GRID_COLS//2, GRID_ROWS-2), lambda: self.start_game())
        ]
    
    def add_message(self, message: str):
        """Add a message to the message log"""
        self.messages.append(message)
        print(message)  # Also print to terminal/console
        # Automatically scroll to bottom when new message arrives
        self.message_scroll = max(0, len(self.messages) - 8)  # Show last 8 messages
    
    def get_all_characters(self) -> List['Character']:
        """Get list of all characters in the game that are actually on the grid"""
        chars = self.party.copy()
        # Only include enemies that are positioned on the grid (not at -1, -1)
        chars.extend([enemy for enemy in self.current_enemies 
                     if enemy.position.x >= 0 and enemy.position.y >= 0])
        return chars
    
    def draw_action_buttons(self):
        """Draw action buttons at the bottom of the screen"""
        self.action_surface.fill(BACKGROUND_COLOR)
        self.action_buttons = []  # Clear previous buttons
        
        if not self.available_actions:
            return
            
        # Calculate button layout
        num_buttons = len(self.available_actions)
        total_margin = (num_buttons - 1) * BUTTON_MARGIN
        available_width = WINDOW_WIDTH - 40  # Leave 20px margin on each side
        button_width = min(150, (available_width - total_margin) // num_buttons)
        button_height = 40
        
        # Calculate total width of all buttons with margins
        total_width = (button_width * num_buttons) + total_margin
        start_x = (WINDOW_WIDTH - total_width) // 2
        
        # Draw each action button
        x = start_x
        y = 30  # Centered vertically in the action surface
        for action_name, target_pos, action_func in self.available_actions:
            button_rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(self.action_surface, BUTTON_COLOR, button_rect)
            pygame.draw.rect(self.action_surface, (255, 255, 255), button_rect, 2)
            
            # Draw button text
            text = FONT.render(action_name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=button_rect.center)
            self.action_surface.blit(text, text_rect)
            
            # Store button with its action
            self.action_buttons.append((button_rect.copy(), action_func))
            
            x += button_width + BUTTON_MARGIN

    def handle_click(self, pos: Tuple[int, int], right_click: bool = False):
        """Handle mouse click events"""
        # If help overlay is showing, clicking anywhere closes it
        if self.showing_help:
            self.showing_help = False
            return
            
        # Check if help button was clicked
        if self.help_button_rect and self.help_button_rect.collidepoint(pos):
            self.showing_help = True
            return
            
        # Don't handle clicks during action delay
        if self.action_delay > pygame.time.get_ticks():
            return
            
        # Handle victory/game over screen clicks
        if self.state in ["victory", "game_over"]:
            for button_rect, action_func in self.action_buttons:
                if button_rect.collidepoint(pos):
                    action_func()
                    return
            return
            
        # Handle intro screen clicks differently
        if self.state == "intro":
            if not right_click:  # Only handle left clicks
                # For the action buttons at the bottom
                if pos[1] > WINDOW_HEIGHT - 100:
                    adjusted_pos = (pos[0], pos[1] - (WINDOW_HEIGHT - 100))
                    for button_rect, action_func in self.action_buttons:
                        if button_rect.collidepoint(adjusted_pos):
                            action_func()
                            return
            return
            
        # Handle upgrade screen clicks
        if self.state == "upgrade":
            if not right_click:  # Only handle left clicks
                for button_rect, action_func in self.action_buttons:
                    if button_rect.collidepoint(pos[0], pos[1]):
                        action_func()
                        return
            return
            
        # Handle wave confirmation screen clicks
        if self.state == "wave_confirmation":
            if not right_click:  # Only handle left clicks
                for button_rect, action_func in self.action_buttons:
                    if button_rect.collidepoint(pos[0], pos[1]):
                        action_func()
                        return
            return
            
        # Ensure we never exceed 3 actions
        if self.actions_left <= 0:
            self.next_turn()
            return
        
        # Check if click is on an action button
        if pos[1] > WINDOW_HEIGHT - 100:  # In action button area
            if not right_click:  # Only handle left clicks for buttons
                button_y = pos[1] - (WINDOW_HEIGHT - 100)
                for button_rect, action_func in self.action_buttons:
                    if button_rect.collidepoint(pos[0], button_y):
                        if isinstance(action_func, tuple):
                            # This is an action that needs a target
                            action_name, action_func = action_func
                            if self.selected_target and self.selected_target.is_alive():  # Valid target check
                                self.perform_action(action_func, self.selected_target)
                                # Only clear target if it died
                                if self.selected_target and not self.selected_target.is_alive():
                                    self.selected_target = None
                                self.update_available_actions()
                            else:  # If no target selected or target is dead, enter target selection mode
                                self.pending_action = (action_name, action_func)
                                self.valid_targets = self.get_valid_targets()
                                self.add_message(f"Select a target for {action_name}")
                        else:
                            self.perform_action(action_func)
                        self.update_available_actions()
                        return
        
        # Handle grid clicks
        grid_x = pos[0] // GRID_SIZE
        grid_y = (pos[1] - 50) // GRID_SIZE  # Adjust for turn indicator offset
        
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return
        
        clicked_pos = GridPosition(grid_x, grid_y)
        
        # Handle right-click targeting
        if right_click and self.current_member_idx < len(self.party):
            current_char = self.party[self.current_member_idx]
            
            # First check for enemies
            for enemy in self.current_enemies:
                if enemy.position == clicked_pos and enemy.is_alive():
                    distance = current_char.position.distance_to(enemy.position)
                    # Check if target is in range based on character type
                    valid_target = False
                    if isinstance(current_char, (Fighter, Rogue)):
                        valid_target = distance <= 1  # Melee range
                    elif isinstance(current_char, Wizard):
                        valid_target = distance <= current_char.MAGIC_MISSILE_RANGE
                    elif isinstance(current_char, Cleric):
                        valid_target = distance <= current_char.SPIRIT_LINK_RANGE
                    
                    if valid_target:
                        self.selected_character = current_char
                        self.selected_target = enemy
                        self.add_message(f"Selected {enemy.name} as target. Choose an action.")
                        self.update_available_actions()
                    else:
                        self.add_message(f"{enemy.name} is out of range!")
                    return
            
            # Then check for allies (for Cleric spells)
            if isinstance(current_char, Cleric):
                for ally in self.party:
                    if ally != current_char and ally.position == clicked_pos and ally.is_alive():
                        distance = current_char.position.distance_to(ally.position)
                        valid_target = distance <= current_char.SPIRIT_LINK_RANGE
                        
                        if valid_target:
                            self.selected_character = current_char
                            self.selected_target = ally
                            self.add_message(f"Selected {ally.name} as target. Choose an action.")
                            self.update_available_actions()
                        else:
                            self.add_message(f"{ally.name} is out of range!")
                        return
            
            # If we clicked empty space or invalid target, clear the target
            self.selected_target = None
            self.update_available_actions()
            return
        
        # Handle target selection if we have a pending action
        if self.pending_action:
            for target in self.valid_targets:
                if target.position == clicked_pos:
                    _, action_func = self.pending_action
                    self.perform_action(action_func, target)
                    self.pending_action = None
                    self.valid_targets = []
                    self.update_available_actions()
                    return
            
            # If we clicked somewhere else, cancel the pending action
            self.pending_action = None
            self.valid_targets = []
            self.add_message("Target selection cancelled")
            self.update_available_actions()
            return
        
        # Handle movement
        if self.selected_character and clicked_pos in self.highlighted_squares:
            # Check if space is occupied
            space_occupied = False
            for char in self.get_all_characters():
                if char != self.selected_character and char.position == clicked_pos:
                    space_occupied = True
                    break
            
            if not space_occupied:
                if self.selected_character.move_to(clicked_pos, self):
                    self.add_message(f"{self.selected_character.name} strides to new position")
                    self.action_delay = pygame.time.get_ticks() + 500  # 0.5 second delay for movement
                    self.actions_left -= 1
                    if self.actions_left <= 0:
                        self.action_delay += 500  # Add extra delay before next turn
                        self.next_turn()
            else:
                self.add_message("Cannot move to an occupied space!")
            
            self.selected_character = None
            self.highlighted_squares = []
            self.update_available_actions()
        else:
            # Try to select a character at the clicked position
            for char in self.get_all_characters():
                if char.position == clicked_pos:
                    if char in self.party and self.current_member_idx == self.party.index(char):
                        self.selected_character = char
                        # Get valid moves (excluding occupied spaces)
                        all_moves = char.get_valid_moves(self)
                        self.highlighted_squares = [
                            pos for pos in all_moves 
                            if not any(other.position == pos 
                                     for other in self.get_all_characters()
                                     if other != char)
                        ]
                        self.update_available_actions()
                    break
    
    def update_available_actions(self):
        """Update the list of available actions"""
        self.available_actions = []
        if self.state == "class_select":
            self.available_actions = [
                ("Fighter", GridPosition(2, 3), lambda: self.choose_class("Fighter")),
                ("Rogue", GridPosition(4, 3), lambda: self.choose_class("Rogue")),
                ("Wizard", GridPosition(6, 3), lambda: self.choose_class("Wizard")),
                ("Cleric", GridPosition(8, 3), lambda: self.choose_class("Cleric"))
            ]
        elif self.state == "upgrade":
            # Show upgrade options for current character
            char = self.party[self.upgrade_selection]
            self.add_message(f"\nChoose an upgrade for {char.name}:")
            self.available_actions = [
                (upgrade, GridPosition(0, 0), lambda u=upgrade: self.apply_upgrade(u))
                for upgrade in self.available_upgrades
            ]
        elif self.state == "wave_confirmation":
            self.available_actions = [
                ("Continue to Next Wave", GridPosition(0, 0), lambda: self.continue_to_next_wave()),
                ("Quit Game", GridPosition(0, 0), lambda: self.quit_game())
            ]
        elif self.state == "combat" and self.current_member_idx < len(self.party):
            current_char = self.party[self.current_member_idx]
            if current_char.is_alive():
                self.available_actions = current_char.get_actions(self)
    
    def choose_class(self, choice: str):
        """Handle class selection"""
        self.add_message(f"\nDebug: Choosing {choice} class")
        if choice == "Fighter":
            player = Fighter("Valeros")
            self.party = [player, Rogue("Merisiel"), Wizard("Ezren"), Cleric("Kyra")]
        elif choice == "Rogue":
            player = Rogue("Merisiel")
            self.party = [player, Fighter("Valeros"), Wizard("Ezren"), Cleric("Kyra")]
        elif choice == "Wizard":
            player = Wizard("Ezren")
            self.party = [player, Fighter("Valeros"), Rogue("Merisiel"), Cleric("Kyra")]
        elif choice == "Cleric":
            player = Cleric("Kyra")
            self.party = [player, Fighter("Valeros"), Rogue("Merisiel"), Wizard("Ezren")]
        
        # Set initial positions for party members higher up the grid
        for i, member in enumerate(self.party):
            member.position = GridPosition(i + 1, GRID_ROWS - 5)
        
        # Create enemies for all waves but position them OFF-GRID initially
        self.enemies = [
            # Wave 1
            Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
            Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
            Enemy("Goblin", hp=20, ac=15, attack_bonus=5),
            # Wave 2
            Enemy("Ogre", hp=40, ac=17, attack_bonus=7, damage_dice=(2, 6)),
            Enemy("Ogre", hp=40, ac=17, attack_bonus=7, damage_dice=(2, 6)),
            # Wave 3 (Boss)
            Enemy("Wyvern", hp=55, ac=19, attack_bonus=9, damage_dice=(2, 8))
        ]
        
        # Position all enemies OFF-GRID initially
        for enemy in self.enemies:
            enemy.position = GridPosition(-1, -1)  # Off-grid position
        
        self.wave_number = 0  # Explicitly set wave number to 0
        self.state = "combat"
        self.add_message("Debug: Starting first battle")
        self.start_battle()

    def start_battle(self):
        """Start a new battle or the next wave"""
        self.add_message(f"\nDebug: Starting battle. Current wave: {self.wave_number}")
        
        if not any(m.is_alive() for m in self.party):
            self.add_message("Debug: No party members alive, ending battle")
            self.end_battle()
            return
            
        # Always increment wave number at the start of a new battle
        self.wave_number += 1
        self.add_message(f"Debug: Incremented wave number to {self.wave_number}")

        # Reset party member positions at the start of each wave
        for i, member in enumerate(self.party):
            if member.is_alive():
                member.position = GridPosition(i + 1, GRID_ROWS - 5)

        # Determine number of enemies for the current wave
        if self.wave_number == 1: # First wave (Goblins)
            num_enemies_this_wave = 3
            self.show_wave_announcement("Wave 1: Goblins")
            positions = [(GRID_COLS - 4, 1), (GRID_COLS - 2, 1), (GRID_COLS - 1, 2)]
            self.add_message("Debug: Setting up Wave 1 - Goblins")
        elif self.wave_number == 2: # Second wave (Ogres)
            num_enemies_this_wave = 2
            self.show_wave_announcement("Wave 2: Ogres' Fury")
            positions = [(GRID_COLS - 3, 1), (GRID_COLS - 1, 1)]
            self.add_message("Debug: Setting up Wave 2 - Ogres")
        elif self.wave_number == 3: # Third wave (Wyvern Boss)
            num_enemies_this_wave = 1
            self.show_wave_announcement("Wave 3: The Wyvern Lord!")
            positions = [(GRID_COLS // 2, 1)]
            self.add_message("Debug: Setting up Wave 3 - Wyvern")
        else:
            self.add_message(f"Debug: Invalid wave number {self.wave_number}, ending battle")
            self.end_battle(victory=True)
            return

        # Check if we have enough enemies for this wave
        if len(self.enemies) < num_enemies_this_wave:
            self.add_message(f"Debug: Not enough enemies for wave {self.wave_number}. Needed {num_enemies_this_wave}, have {len(self.enemies)}")
            self.end_battle(victory=True)
            return

        # Set up the current wave's enemies
        self.current_enemies = self.enemies[:num_enemies_this_wave]
        self.enemies = self.enemies[num_enemies_this_wave:]
        
        # Position the enemies
        for i, enemy in enumerate(self.current_enemies):
            enemy.position = GridPosition(*positions[i])
        
        self.add_message(f"\n--- Wave {self.wave_number}: {len(self.current_enemies)} enemies appear! ---")
        self.current_member_idx = 0
        self.actions_left = 3
        self.state = "combat"
        self.update_available_actions()

    def next_turn(self):
        """Advance to the next turn"""
        # Clear any selections
        self.selected_character = None
        self.selected_target = None
        self.highlighted_squares = []
        
        self.current_member_idx += 1
        self.actions_left = 3
        
        if self.current_member_idx >= len(self.party):
            # Enemy's turn
            for enemy in self.current_enemies:
                if enemy.is_alive():
                    self.current_enemy = enemy
                    self.handle_enemy_turn()
            self.current_member_idx = 0
            
            # Reset any per-turn effects
            for char in self.party:
                if isinstance(char, Wizard):
                    if char.shield_up:
                        char.shield_up = False
                        char.base_ac -= 2
                        self.add_message(f"{char.name}'s Shield spell fades")
            
            # Check if wave is complete after enemy turns
            self.check_wave_complete()
        else:
            # Check if current character is AI-controlled (not the player's chosen class)
            current_char = self.party[self.current_member_idx]
            if current_char != self.party[0]:  # If not the player's character
                self.handle_ai_turn(current_char)
                # Don't call next_turn() here - let the AI system handle turn progression
        
        self.update_available_actions()
    
    def handle_enemy_turn(self):
        """Handle enemy AI turn"""
        if not self.current_enemy or not self.current_enemy.is_alive():
            return
            
        self.add_message(f"\n{self.current_enemy.name}'s turn!")
        actions = 3
        
        while actions > 0:
            # Find closest living party member
            targets = [(char, self.current_enemy.position.distance_to(char.position))
                      for char in self.party if char.is_alive()]
            if not targets:
                break
                
            target, distance = min(targets, key=lambda x: x[1])
            
            if distance <= 1:
                # Attack if in range
                used, _ = self.current_enemy.attack(target, self)
                actions -= used
            else:
                # Move towards target
                moves = self.current_enemy.get_valid_moves(self)
                if moves:
                    best_move = min(moves, 
                                  key=lambda pos: pos.distance_to(target.position))
                    if self.current_enemy.move_to(best_move, self):
                        actions -= 1
                else:
                    break
        
        # Check if battle is over
        if not any(char.is_alive() for char in self.party):
            self.end_battle()

    def end_battle(self, victory=False):
        """End the current battle or game"""
        if victory:
            self.add_message("\n🏆 Congratulations! Your party has defeated all foes!")
            self.state = "victory"
        else:
            self.add_message("\n💀 Game Over - Your party was defeated...")
            self.state = "game_over"
        
        self.available_actions = [
            ("Restart", GridPosition(4, 3), self.init_game),
            ("Quit", GridPosition(GRID_COLS - 5, 3), self.quit_game)
        ]
        self.update_available_actions() # To refresh buttons on screen
    
    def draw_grid(self):
        """Draw the combat grid"""
        self.grid_surface.fill(BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(GRID_COLS + 1):
            pygame.draw.line(self.grid_surface, GRID_COLOR,
                           (x * GRID_SIZE, 0),
                           (x * GRID_SIZE, GRID_ROWS * GRID_SIZE))
        
        for y in range(GRID_ROWS + 1):
            pygame.draw.line(self.grid_surface, GRID_COLOR,
                           (0, y * GRID_SIZE),
                           (GRID_COLS * GRID_SIZE, y * GRID_SIZE))
        
        # Highlight valid moves
        for pos in self.highlighted_squares:
            pygame.draw.rect(self.grid_surface, GRID_HIGHLIGHT,
                           (pos.x * GRID_SIZE, pos.y * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE))
        
        # Draw characters
        for char in self.party:
            char.draw(self.grid_surface, self)
            
        # Draw all current enemies
        for enemy in self.current_enemies:
            enemy.draw(self.grid_surface, self)
        
        # Draw range indicators and valid targets
        if self.selected_character:
            x, y = self.selected_character.position.get_pixel_pos()
            center = (x + GRID_SIZE//2, y + GRID_SIZE//2)
            
            # Draw character selection circle
            pygame.draw.circle(self.grid_surface, (255, 255, 255),
                             center, GRID_SIZE//2, 1)
            
            # Draw spell ranges for wizard
            if isinstance(self.selected_character, Wizard):
                # Arcane Blast range (red circle)
                arcane_radius = self.selected_character.ARCANE_BLAST_RANGE * GRID_SIZE
                pygame.draw.circle(self.grid_surface, (255, 50, 50),
                                 center, arcane_radius, 1)
                
                # Magic Missile range (blue circle)
                missile_radius = self.selected_character.MAGIC_MISSILE_RANGE * GRID_SIZE
                pygame.draw.circle(self.grid_surface, (50, 50, 255),
                                 center, missile_radius, 1)
                
                # Highlight enemies in range
                for enemy in self.current_enemies:
                    if enemy.is_alive():
                        distance = self.selected_character.position.distance_to(enemy.position)
                        ex, ey = enemy.position.get_pixel_pos()
                        if distance <= self.selected_character.ARCANE_BLAST_RANGE:
                            # Red highlight for Arcane Blast range
                            pygame.draw.rect(self.grid_surface, (255, 100, 100),
                                          (ex, ey, GRID_SIZE, GRID_SIZE), 2)
                        elif distance <= self.selected_character.MAGIC_MISSILE_RANGE:
                            # Blue highlight for Magic Missile range
                            pygame.draw.rect(self.grid_surface, (100, 100, 255),
                                          (ex, ey, GRID_SIZE, GRID_SIZE), 2)
            
            # Draw melee range for Fighter and Rogue
            elif isinstance(self.selected_character, (Fighter, Rogue)):
                radius = GRID_SIZE  # 1 square range
                pygame.draw.circle(self.grid_surface, (255, 255, 255),
                                 center, radius, 1)
                
                # Highlight enemies in melee range
                for enemy in self.current_enemies:
                    if enemy.is_alive():
                        distance = self.selected_character.position.distance_to(enemy.position)
                        if distance <= 1:
                            ex, ey = enemy.position.get_pixel_pos()
                            pygame.draw.rect(self.grid_surface, (255, 255, 255),
                                          (ex, ey, GRID_SIZE, GRID_SIZE), 2)
        
        # Highlight valid targets for pending action
        for target in self.valid_targets:
            x, y = target.position.get_rect().center
            pygame.draw.rect(self.grid_surface, (255, 255, 0),  # Yellow highlight
                           (x - GRID_SIZE//2, y - GRID_SIZE//2, GRID_SIZE, GRID_SIZE), 2)
    
    def draw_messages(self):
        """Draw the message log with scrolling"""
        # Draw a clear, visible message log box above the action buttons
        log_height = 220
        self.message_surface = pygame.Surface((WINDOW_WIDTH - 40, log_height))
        self.message_surface.fill((20, 20, 20))  # Dark background for contrast
        pygame.draw.rect(self.message_surface, (255, 200, 100), self.message_surface.get_rect(), 2)  # Golden border

        # Draw scroll indicators if needed
        if self.message_scroll > 0:
            text = FONT.render("▲ More", True, TEXT_COLOR)
            self.message_surface.blit(text, (5, 0))
        if self.message_scroll < len(self.messages) - 8:
            text = FONT.render("▼ More", True, TEXT_COLOR)
            self.message_surface.blit(text, (5, log_height - 25))

        # Draw visible messages
        y = 25
        visible_messages = self.messages[self.message_scroll:self.message_scroll + 8]
        for message in visible_messages:
            text = FONT.render(message, True, TEXT_COLOR)
            self.message_surface.blit(text, (5, y))
            y += 25
    
    def draw_turn_indicator(self):
        """Draw the turn indicator"""
        if self.state == "combat":
            indicator_surface = pygame.Surface((200, 40))
            indicator_surface.fill(BACKGROUND_COLOR)
            
            if self.current_member_idx < len(self.party):
                current = self.party[self.current_member_idx]
                color = current.color
                text = f"{current.name}'s Turn"
            else:
                current = self.current_enemy
                color = ENEMY_COLOR
                text = f"Enemy Turn"
            
            # Draw colored border
            pygame.draw.rect(indicator_surface, color, indicator_surface.get_rect(), 2)
            
            # Draw text
            text_surf = FONT.render(text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=indicator_surface.get_rect().center)
            indicator_surface.blit(text_surf, text_rect)
            
            # Draw action points
            if self.current_member_idx < len(self.party):
                action_text = f"Actions: {self.actions_left}"
                action_surf = FONT.render(action_text, True, TEXT_COLOR)
                self.screen.blit(action_surf, (220, 10))
            
            self.screen.blit(indicator_surface, (10, 10))
    
    def handle_scroll(self, event):
        """Handle scrolling of the combat log"""
        if event.button == 4:  # Mouse wheel up
            self.message_scroll = max(0, self.message_scroll - 1)
        elif event.button == 5:  # Mouse wheel down
            self.message_scroll = min(len(self.messages) - 8, self.message_scroll + 1)
    
    def draw(self):
        """Draw the game screen"""
        self.screen.fill(BACKGROUND_COLOR)

        if self.state == "intro":
            self.draw_intro_screen()
        elif self.state == "upgrade":
            self.draw_upgrade_screen()
        elif self.state == "wave_confirmation":
            self.draw_wave_confirmation_screen()
        elif self.state == "victory" or self.state == "game_over":
            self.draw_end_game_screen()
        else:  # Combat or Class Select
            # Draw combat grid
            self.draw_grid()
            self.screen.blit(self.grid_surface, (0, GRID_TOP))

            # Draw turn indicator
            self.draw_turn_indicator()

            # Draw message log (now always visible and clear)
            self.draw_messages()
            self.screen.blit(self.message_surface, (20, WINDOW_HEIGHT - 320))  # Place above action buttons

            # Draw action buttons
            self.draw_action_buttons()
            self.screen.blit(self.action_surface, (0, WINDOW_HEIGHT - 100))

            # Draw all active effects
            for effect in self.effects:
                effect.draw(self.screen)

            # Draw wave announcement overlay if active
            if self.state == "combat":
                self.draw_wave_announcement()

        # Draw help button in all states except help overlay, intro, and class_select
        if not self.showing_help and self.state not in ["intro", "class_select"]:
            self.draw_help_button()

        # Draw help overlay if active
        if self.showing_help:
            self.draw_help_overlay()

        pygame.display.flip()

    def draw_end_game_screen(self):
        """Draw the game over or victory screen"""
        # Fill background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw title
        if self.state == "victory":
            title_text = "🏆 Congratulations! You are Victorious! 🏆"
            subtitle_text = "You have defeated all waves of enemies!"
        else:  # game_over
            title_text = "💀 Game Over 💀"
            subtitle_text = "Your party has fallen in battle..."

        # Draw main title
        title = LARGE_TITLE_FONT.render(title_text, True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        # Draw subtitle
        subtitle = TITLE_FONT.render(subtitle_text, True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 60))
        self.screen.blit(subtitle, subtitle_rect)

        # Draw buttons
        button_width = 200
        button_height = 60
        margin = 40
        total_width = (2 * button_width) + margin
        start_x = (WINDOW_WIDTH - total_width) // 2
        button_y = WINDOW_HEIGHT // 2 + 50

        # Restart button
        restart_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, BUTTON_COLOR, restart_rect)
        pygame.draw.rect(self.screen, TITLE_COLOR, restart_rect, 2)
        restart_text = TITLE_FONT.render("Play Again", True, TEXT_COLOR)
        text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, text_rect)

        # Quit button
        quit_rect = pygame.Rect(start_x + button_width + margin, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, BUTTON_COLOR, quit_rect)
        pygame.draw.rect(self.screen, TITLE_COLOR, quit_rect, 2)
        quit_text = TITLE_FONT.render("Quit Game", True, TEXT_COLOR)
        text_rect = quit_text.get_rect(center=quit_rect.center)
        self.screen.blit(quit_text, text_rect)

        # Store buttons for click handling
        self.action_buttons = [
            (restart_rect, lambda: self.init_game()),
            (quit_rect, lambda: self.quit_game())
        ]

    def run(self):
        """Main game loop"""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            if self.action_delay > current_time:
                # Update and draw effects even during delay
                self.update_effects()
                self.draw()
                self.clock.tick(60)
                continue
            
            # Check if we need to perform the next AI action after delay
            if hasattr(self, '_schedule_next_ai_action') and self._schedule_next_ai_action:
                self._schedule_next_ai_action = False
                self.perform_next_ai_action()
                continue
            
            # If turn should end after delay, do it now
            if hasattr(self, '_end_turn_after_delay') and self._end_turn_after_delay:
                self._end_turn_after_delay = False
                self.next_turn()
            
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        self.quit_game()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button in (4, 5): 
                            mouse_pos = pygame.mouse.get_pos()
                            message_area = pygame.Rect(20, WINDOW_HEIGHT - 300, WINDOW_WIDTH - 40, 200)
                            if message_area.collidepoint(mouse_pos):
                                self.handle_scroll(event)
                        elif event.button == 1: 
                            self.handle_click(event.pos)
                        elif event.button == 3: 
                            self.handle_click(event.pos, right_click=True)
            except Exception as e:
                print(f"Error handling event: {e}")
                continue
            
            # Update effects
            self.update_effects()
            
            self.draw()
            self.clock.tick(60)

    def get_valid_targets(self) -> List['Character']:
        """Get valid targets for the current action"""
        if not self.pending_action or not isinstance(self.pending_action[1], tuple):
            return []
            
        action_name = self.pending_action[0]
        current_char = self.party[self.current_member_idx]
        
        if isinstance(current_char, Wizard):
            if "Arcane Blast" in action_name:
                return [enemy for enemy in self.current_enemies 
                       if enemy.is_alive() and 
                       current_char.position.distance_to(enemy.position) <= current_char.ARCANE_BLAST_RANGE]
            elif "Magic Missile" in action_name:
                return [enemy for enemy in self.current_enemies 
                       if enemy.is_alive() and 
                       current_char.position.distance_to(enemy.position) <= current_char.MAGIC_MISSILE_RANGE]
        elif isinstance(current_char, Cleric):
            if "Strike" in action_name:
                return [enemy for enemy in self.current_enemies
                       if enemy.is_alive() and
                       current_char.position.distance_to(enemy.position) <= 1]
            elif "Spirit Link" in action_name:
                return [ally for ally in self.party 
                       if ally != current_char and ally.is_alive() and 
                       current_char.position.distance_to(ally.position) <= current_char.SPIRIT_LINK_RANGE]
            elif "Sanctuary" in action_name:
                return [ally for ally in self.party 
                       if ally != current_char and ally.is_alive() and 
                       current_char.position.distance_to(ally.position) <= current_char.SANCTUARY_RANGE]
            elif "Lesser Heal" in action_name:
                if "1" in action_name:  # Touch range
                    return [ally for ally in self.party 
                           if ally != current_char and ally.is_alive() and 
                           current_char.position.distance_to(ally.position) <= current_char.LESSER_HEAL_RANGE]
                else:  # 30-foot range
                    return [ally for ally in self.party 
                           if ally != current_char and ally.is_alive() and 
                           current_char.position.distance_to(ally.position) <= current_char.LESSER_HEAL_UP_RANGE]
        elif isinstance(current_char, (Fighter, Rogue)): # Basic melee targeting for now
             return [enemy for enemy in self.current_enemies
                   if enemy.is_alive() and
                   current_char.position.distance_to(enemy.position) <= 1]
        
        return []

    def perform_action(self, action_func, target=None):
        """Perform an action with delay"""
        if target:
            result = action_func(target)
        else:
            result = action_func()
            
        if isinstance(result, tuple):
            actions_used, success = result
            # Only apply delay and action cost if an action was actually attempted (actions_used > 0)
            if actions_used > 0: 
                self.action_delay = pygame.time.get_ticks() + 1000
                self.actions_left = max(0, self.actions_left - actions_used)
                # Schedule next_turn to happen after the delay if out of actions
                if self.actions_left <= 0:
                    # Instead of calling next_turn() immediately, schedule it after the delay
                    self._end_turn_after_delay = True
                else:
                    self._end_turn_after_delay = False
                # Check for wave completion only if the action was successful or had an effect
                # For attacks, success means hit. For other actions, it means they completed.
                if success: 
                    self.check_wave_complete()
            elif success: # Action used 0 points but was successful (e.g. selecting Stride)
                 pass # Do nothing specific here, Stride is handled on move click
        
        # Only update available actions if actions_left > 0 or turn is not scheduled to end
        if self.actions_left > 0 or not (hasattr(self, '_end_turn_after_delay') and self._end_turn_after_delay):
            self.update_available_actions() # Always update actions after an attempt
        return result

    def start_game(self):
        """Transition from intro to class selection"""
        self.state = "class_select"
        self.messages = ["Choose your class:"]
        self.update_available_actions()

    def draw_intro_screen(self):
        """Draw the introduction screen with improved spacing and centering"""
        self.screen.fill(BACKGROUND_COLOR)
        
        title = LARGE_TITLE_FONT.render("Pathfinder 2E Grid Combat", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Intro content as (text, type) tuples for better spacing
        intro_content = [
            ("Welcome to the PF2E Grid Combat Simulator!", "header"),
            ("", "spacer"),
            ("You lead a party of three adventurers against waves of increasingly dangerous foes. Work together, use tactical positioning, and manage your actions wisely to survive!", "paragraph"),
            ("", "section_gap"),
            ("Controls:", "section_header"),
            ("Left-click: Select characters, actions, and movement squares", "bullet"),
            ("Right-click: Target enemies for attacks/spells", "bullet"),
            ("Mouse wheel: Scroll combat log", "bullet"),
            ("", "section_gap"),
            ("Combat Rules:", "section_header"),
            ("Each character has 3 actions per turn.", "bullet"),
            ("Movement (Stride) costs 1 action.", "bullet"),
            ("Attacks & Spells usually cost 1 action (some 2 or more).", "bullet"),
            ("Flanking enemies (ally on opposite side) makes them Off-Guard (-2 AC).", "bullet"),
            ("", "section_gap"),
            ("Party Members:", "section_header"),
            ("Fighter: Tough warrior, excels at melee.", "bullet"),
            ("Rogue: Agile striker, benefits from Off-Guard targets.", "bullet"),
            ("Wizard: Ranged spellcaster with various arcane powers.", "bullet"),
            ("Cleric: Divine spellcaster specializing in healing and support.", "bullet")
        ]

        # Centered text block
        block_width = min(700, WINDOW_WIDTH - 80)
        x_left = (WINDOW_WIDTH - block_width) // 2
        y = 140
        for text, typ in intro_content:
            if typ == "header":
                surf = TITLE_FONT.render(text, True, TITLE_COLOR)
                self.screen.blit(surf, (x_left, y))
                y += 38
            elif typ == "paragraph":
                # Wrap paragraph text
                words = text.split()
                line = ""
                for word in words:
                    test_line = line + word + " "
                    test_surf = FONT.render(test_line, True, TEXT_COLOR)
                    if test_surf.get_width() > block_width:
                        surf = FONT.render(line, True, TEXT_COLOR)
                        self.screen.blit(surf, (x_left, y))
                        y += 26
                        line = word + " "
                    else:
                        line = test_line
                if line:
                    surf = FONT.render(line, True, TEXT_COLOR)
                    self.screen.blit(surf, (x_left, y))
                    y += 32
            elif typ == "section_header":
                surf = TITLE_FONT.render(text, True, TITLE_COLOR)
                self.screen.blit(surf, (x_left, y))
                y += 34
            elif typ == "bullet":
                surf = FONT.render("• " + text, True, TEXT_COLOR)
                self.screen.blit(surf, (x_left + 24, y))
                y += 26
            elif typ == "section_gap":
                y += 24
            elif typ == "spacer":
                y += 12
        
        self.draw_action_buttons() # This will draw the single "Start Game" button
        self.screen.blit(self.action_surface, (0, WINDOW_HEIGHT - 100))

    def show_wave_announcement(self, text):
        """Show wave announcement overlay"""
        self.wave_announcement = text
        self.wave_announcement_end = pygame.time.get_ticks() + 1500  # 1.5 seconds

    def draw_wave_announcement(self):
        """Draw the wave announcement overlay if active"""
        if self.wave_announcement and pygame.time.get_ticks() < self.wave_announcement_end:
            # Clear the overlay surface
            self.overlay_surface.fill((0, 0, 0, 0))
            
            # Add semi-transparent black background
            overlay_bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay_bg.fill((0, 0, 0))
            overlay_bg.set_alpha(180)
            self.screen.blit(overlay_bg, (0, 0))
            
            # Draw the announcement text
            text = LARGE_TITLE_FONT.render(self.wave_announcement, True, TITLE_COLOR)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(text, text_rect)
        elif self.wave_announcement and pygame.time.get_ticks() >= self.wave_announcement_end:
            self.wave_announcement = None

    def start_upgrades(self):
        """Start the upgrade selection process"""
        # Heal all party members to full
        for member in self.party:
            healed = member.heal_full()
            if healed > 0:
                self.add_message(f"{member.name} recovers {healed} HP!")
        
        self.state = "upgrade"
        self.upgrade_selection = 0  # Start with first party member
        self.update_available_actions()

    def apply_upgrade(self, upgrade: str):
        """Apply selected upgrade to current character"""
        if self.upgrade_selection is not None and self.upgrade_selection < len(self.party):
            char = self.party[self.upgrade_selection]
            message = char.apply_upgrade(upgrade)
            self.add_message(message)
            
            # Move to next character or to confirmation
            self.upgrade_selection += 1
            if self.upgrade_selection >= len(self.party):
                self.show_wave_confirmation()
            self.update_available_actions()

    def check_wave_complete(self):
        """Check if current wave is complete and start upgrades or end game if so"""
        if self.state != "combat": return False # Only check during combat

        alive_enemies = [e for e in self.current_enemies if e.is_alive()]
        self.add_message(f"\nChecking wave completion: Wave {self.wave_number}, {len(alive_enemies)} enemies remaining")
        
        if not alive_enemies:
            if self.wave_number == 3: # Just completed the final wave (Wyvern)
                self.end_battle(victory=True)
            elif self.wave_number < 3: # Completed wave 1 or 2
                self.add_message("\nWave complete! Time to rest and upgrade!")
                self.start_upgrades()
            else: # Should not be reached if logic is correct
                self.end_battle()
            return True
        return False

    def draw_upgrade_screen(self):
        """Draw the upgrade selection screen"""
        if self.upgrade_selection is None or self.upgrade_selection >= len(self.party):
            return
            
        char = self.party[self.upgrade_selection]
        
        # Draw character name and stats
        title = LARGE_TITLE_FONT.render(f"Choose {char.name}'s Upgrade", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw current stats
        stats_text = [
            f"Current Stats:",
            f"HP: {char.hp}/{char.max_hp}",
            f"Attack Bonus: +{char.attack_bonus}",
            f"Bonus Damage: +{char.bonus_damage}",
            f"Movement: {char.speed//5} squares"
        ]
        
        y = 150
        for text in stats_text:
            surf = FONT.render(text, True, TEXT_COLOR)
            self.screen.blit(surf, (WINDOW_WIDTH//4, y))
            y += 30
        
        # Draw upgrade buttons
        button_width = 200
        button_height = 50
        start_y = 300
        
        self.action_buttons = []
        for i, upgrade in enumerate(self.available_upgrades):
            button_rect = pygame.Rect((WINDOW_WIDTH - button_width)//2,
                                    start_y + i * (button_height + 20),
                                    button_width, button_height)
            pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
            pygame.draw.rect(self.screen, TITLE_COLOR, button_rect, 2)
            
            text = FONT.render(upgrade, True, TEXT_COLOR)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            self.action_buttons.append((button_rect, lambda u=upgrade: self.apply_upgrade(u)))

    def show_wave_confirmation(self):
        """Show confirmation screen after upgrades"""
        self.state = "wave_confirmation"
        
        # Determine next wave based on the wave *just completed* (which is current self.wave_number)
        if self.wave_number == 1: # After Goblins (Wave 1)
            next_wave_type = "Ogres (Wave 2)"
        elif self.wave_number == 2: # After Ogres (Wave 2)
            next_wave_type = "The Wyvern Lord (Wave 3 Boss)"
        else: 
            next_wave_type = "Error determining next wave"

        self.wave_summary = {
            "completed": f"Wave {self.wave_number} Complete!",
            "next": f"Next Up: {next_wave_type}",
            "upgrades": [
                f"{char.name}: HP {char.max_hp}, ATK +{char.attack_bonus}, DMG +{char.bonus_damage}, SPD {char.speed//5}"
                for char in self.party
            ]
        }
        self.update_available_actions()

    def continue_to_next_wave(self):
        """Continue to the next wave"""
        self.state = "combat"
        self.start_battle()

    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        sys.exit()

    def draw_wave_confirmation_screen(self):
        """Draw the wave confirmation screen"""
        if not self.wave_summary:
            return

        # Draw wave completion title
        title = LARGE_TITLE_FONT.render(self.wave_summary["completed"], True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title, title_rect)

        # Draw next wave info
        next_wave = TITLE_FONT.render(self.wave_summary["next"], True, TITLE_COLOR)
        next_rect = next_wave.get_rect(center=(WINDOW_WIDTH//2, 140))
        self.screen.blit(next_wave, next_rect)

        # Draw party summary
        y = 200
        summary_title = TITLE_FONT.render("Party Status:", True, TITLE_COLOR)
        self.screen.blit(summary_title, (WINDOW_WIDTH//4, y))
        y += 40

        for status in self.wave_summary["upgrades"]:
            text = FONT.render(status, True, TEXT_COLOR)
            self.screen.blit(text, (WINDOW_WIDTH//4, y))
            y += 30

        # Draw continue and quit buttons
        button_width = 300  # Increased from 250 to 300
        button_height = 60  # Increased from 50 to 60
        margin = 40
        start_y = WINDOW_HEIGHT - 150

        # Continue button
        continue_rect = pygame.Rect((WINDOW_WIDTH//2 - button_width - margin//2),
                                  start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BUTTON_COLOR, continue_rect)
        pygame.draw.rect(self.screen, TITLE_COLOR, continue_rect, 2)
        
        # Use regular FONT instead of TITLE_FONT for button text
        continue_text = FONT.render("Continue to Next Wave", True, TEXT_COLOR)
        text_rect = continue_text.get_rect(center=continue_rect.center)
        self.screen.blit(continue_text, text_rect)

        # Quit button
        quit_rect = pygame.Rect((WINDOW_WIDTH//2 + margin//2),
                               start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BUTTON_COLOR, quit_rect)
        pygame.draw.rect(self.screen, TITLE_COLOR, quit_rect, 2)
        
        # Use regular FONT for consistency
        quit_text = FONT.render("Quit Game", True, TEXT_COLOR)
        text_rect = quit_text.get_rect(center=quit_rect.center)
        self.screen.blit(quit_text, text_rect)

        # Store buttons for click handling
        self.action_buttons = [
            (continue_rect, lambda: self.continue_to_next_wave()),
            (quit_rect, lambda: self.quit_game())
        ]

    def draw_help_button(self):
        """Draw the help button in the top right corner"""
        button_width = 120
        button_height = 40
        self.help_button_rect = pygame.Rect(WINDOW_WIDTH - button_width - 10, 10, button_width, button_height)
        
        # Draw button
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.help_button_rect)
        pygame.draw.rect(self.screen, TITLE_COLOR, self.help_button_rect, 2)
        
        # Draw text
        text = FONT.render("How to Play", True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.help_button_rect.center)
        self.screen.blit(text, text_rect)

    def draw_help_overlay(self):
        """Draw the help overlay with game instructions (improved layout, more space)"""
        # Semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Help content (sections, headers, and bullets)
        help_sections = [
            ("Controls:", [
                "Left-click: Select characters, actions, and movement squares",
                "Right-click: Target enemies for attacks/spells",
                "Mouse wheel: Scroll combat log"
            ]),
            ("Combat Rules:", [
                "Each character has 3 actions per turn.",
                "Movement (Stride) costs 1 action",
                "Attacks & Spells usually cost 1 action (some 2 or more)",
                "Flanking enemies (ally on opposite side) makes them Off-Guard (-2 AC)."
            ]),
            ("Party Members:", [
                "Fighter: Tough warrior, excels at melee.",
                "Rogue: Agile striker, benefits from Off-Guard targets.",
                "Wizard: Ranged spellcaster with various arcane powers."
            ])
        ]

        # Box dimensions (increased height for more space)
        box_width = min(800, WINDOW_WIDTH - 80)
        box_height = 650  # Increased from 520
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # Draw rounded rectangle for help box
        pygame.draw.rect(self.screen, (30, 30, 30), box_rect, border_radius=18)
        pygame.draw.rect(self.screen, TITLE_COLOR, box_rect, 3, border_radius=18)

        # Title
        title = LARGE_TITLE_FONT.render("How to Play", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, box_y + 45))
        self.screen.blit(title, title_rect)

        # Draw sections
        y = box_y + 100
        section_gap = 38
        bullet_gap = 28
        left_margin = box_x + 36
        for header, bullets in help_sections:
            # Header
            header_surf = TITLE_FONT.render(header, True, TITLE_COLOR)
            self.screen.blit(header_surf, (left_margin, y))
            y += section_gap
            # Bullets
            for bullet in bullets:
                bullet_surf = FONT.render("• " + bullet, True, TEXT_COLOR)
                self.screen.blit(bullet_surf, (left_margin + 18, y))
                y += bullet_gap
            y += 10  # Extra space after each section

        # Closing instruction at the bottom of the box
        close_text = FONT.render("Click anywhere to close", True, (200, 200, 200))
        close_rect = close_text.get_rect(center=(WINDOW_WIDTH//2, box_y + box_height - 36))
        self.screen.blit(close_text, close_rect)

    def toggle_help(self):
        """Toggle the help overlay"""
        self.showing_help = not self.showing_help

    def handle_ai_turn(self, char: Character):
        """Handle AI-controlled party member's turn"""
        if not char.is_alive():
            return
        # Debug: Print all character positions at the start of the turn
        positions = [(c.name, c.position.x, c.position.y) for c in self.get_all_characters() if c.is_alive()]
        self.add_message(f"[DEBUG] Positions at start of {char.name}'s turn: {positions}")
        
        self.add_message(f"\n{char.name}'s turn!")
        
        # Set up AI turn state
        self.ai_current_char = char
        self.ai_actions_remaining = 3
        self.ai_action_queue = []
        
        # Start the first AI action
        self.perform_next_ai_action()

    def perform_next_ai_action(self):
        """Perform the next AI action with appropriate delay"""
        if not self.ai_current_char or not self.ai_current_char.is_alive() or self.ai_actions_remaining <= 0:
            # AI turn is complete, move to next turn
            self.ai_current_char = None
            self.ai_actions_remaining = 0
            self.next_turn()
            return
        
        char = self.ai_current_char
        
        def get_unoccupied_moves(character, target_pos):
            all_moves = character.get_valid_moves(self)
            unoccupied = []
            for pos in all_moves:
                occupied = False
                for other in self.get_all_characters():
                    if other != character and other.position == pos and other.is_alive():
                        occupied = True
                        break
                if not occupied:
                    unoccupied.append(pos)
            if unoccupied:
                return sorted(unoccupied, key=lambda p: p.distance_to(target_pos))
            return []
        
        def check_for_overlap():
            chars = [c for c in self.get_all_characters() if c.is_alive()]
            for i in range(len(chars)):
                for j in range(i+1, len(chars)):
                    if chars[i].position == chars[j].position:
                        self.add_message(f"[DEBUG] OVERLAP: {chars[i].name} and {chars[j].name} at {chars[i].position.x},{chars[i].position.y}")
        
        action_performed = False
        
        if isinstance(char, Fighter):
            targets = [(enemy, char.position.distance_to(enemy.position))
                      for enemy in self.current_enemies if enemy.is_alive()]
            if targets:
                target, distance = min(targets, key=lambda x: x[1])
                if distance <= 1:
                    if self.ai_actions_remaining >= 2:
                        used, _ = char.power_attack(target, self)
                        self.ai_actions_remaining -= used
                        action_performed = True
                    else:
                        used, _ = char.attack(target, self, dice=(1, 10))
                        self.ai_actions_remaining -= used
                        action_performed = True
                else:
                    moves = get_unoccupied_moves(char, target.position)
                    if moves:
                        best_move = moves[0]
                        if char.move_to(best_move, self):
                            check_for_overlap()
                            self.ai_actions_remaining -= 1
                            action_performed = True
        
        elif isinstance(char, Rogue):
            targets = [(enemy, char.position.distance_to(enemy.position))
                      for enemy in self.current_enemies if enemy.is_alive()]
            if targets:
                target, distance = min(targets, key=lambda x: x[1])
                if distance <= 1:
                    if char.is_flanking(target, self):
                        used, _ = char.strike(target, self)
                        self.ai_actions_remaining -= used
                        action_performed = True
                    elif self.ai_actions_remaining >= 2:
                        used, _ = char.twin_feint(target, self)
                        self.ai_actions_remaining -= used
                        action_performed = True
                    else:
                        used, _ = char.strike(target, self)
                        self.ai_actions_remaining -= used
                        action_performed = True
                else:
                    moves = get_unoccupied_moves(char, target.position)
                    if moves:
                        best_move = None
                        for move in moves:
                            original_pos = char.position
                            char.position = move
                            if char.is_flanking(target, self):
                                best_move = move
                                char.position = original_pos
                                break
                            char.position = original_pos
                        if not best_move:
                            best_move = moves[0]
                        if char.move_to(best_move, self):
                            check_for_overlap()
                            self.ai_actions_remaining -= 1
                            action_performed = True
        
        elif isinstance(char, Cleric):
            allies_needing_heal = [(ally, ally.max_hp - ally.hp) 
                                 for ally in self.party 
                                 if ally != char and ally.is_alive() and ally.hp < ally.max_hp]
            if allies_needing_heal:
                allies_needing_heal.sort(key=lambda x: x[1], reverse=True)
                target_ally, missing_hp = allies_needing_heal[0]
                distance = char.position.distance_to(target_ally.position)
                if distance <= char.LESSER_HEAL_RANGE:
                    used, _ = char.lesser_heal(target_ally, self, 1)
                    self.ai_actions_remaining -= used
                    action_performed = True
                elif distance <= char.LESSER_HEAL_UP_RANGE:
                    allies_in_range = sum(1 for ally, _ in allies_needing_heal 
                                       if char.position.distance_to(ally.position) <= char.LESSER_HEAL_UP_RANGE)
                    if allies_in_range >= 2 and self.ai_actions_remaining >= 3:
                        used, _ = char.lesser_heal(target_ally, self, 3)
                        self.ai_actions_remaining -= used
                        action_performed = True
                    elif self.ai_actions_remaining >= 2:
                        used, _ = char.lesser_heal(target_ally, self, 2)
                        self.ai_actions_remaining -= used
                        action_performed = True
                    else:
                        moves = get_unoccupied_moves(char, target_ally.position)
                        if moves:
                            best_move = moves[0]
                            if char.move_to(best_move, self):
                                check_for_overlap()
                                self.ai_actions_remaining -= 1
                                action_performed = True
                else:
                    moves = get_unoccupied_moves(char, target_ally.position)
                    if moves:
                        best_move = moves[0]
                        if char.move_to(best_move, self):
                            check_for_overlap()
                            self.ai_actions_remaining -= 1
                            action_performed = True
            else:
                targets = [(enemy, char.position.distance_to(enemy.position))
                          for enemy in self.current_enemies if enemy.is_alive()]
                if targets:
                    target, distance = min(targets, key=lambda x: x[1])
                    if distance <= 1:
                        used, _ = char.attack(target, self, dice=(1, 6))
                        self.ai_actions_remaining -= used
                        action_performed = True
                    else:
                        moves = get_unoccupied_moves(char, target.position)
                        if moves:
                            best_move = moves[0]
                            if char.move_to(best_move, self):
                                check_for_overlap()
                                self.ai_actions_remaining -= 1
                                action_performed = True
        
        elif isinstance(char, Wizard):
            targets = [(enemy, char.position.distance_to(enemy.position))
                      for enemy in self.current_enemies if enemy.is_alive()]
            if targets:
                target, distance = min(targets, key=lambda x: x[1])
                if distance <= char.MAGIC_MISSILE_RANGE:
                    used, _ = char.magic_missile(target, self, self.ai_actions_remaining)
                    self.ai_actions_remaining -= used
                    action_performed = True
                else:
                    moves = get_unoccupied_moves(char, target.position)
                    if moves:
                        best_move = moves[0]
                        if char.move_to(best_move, self):
                            check_for_overlap()
                            self.ai_actions_remaining -= 1
                            action_performed = True
        
        # If an action was performed, set a delay before the next action
        if action_performed:
            self.action_delay = pygame.time.get_ticks() + 1500  # 1.5 second delay between AI actions
            # Schedule the next AI action
            self._schedule_next_ai_action = True
        else:
            # No valid action found, end turn
            self.ai_current_char = None
            self.ai_actions_remaining = 0
            self.next_turn()

if __name__ == "__main__":
    game = Game()
    game.run() 