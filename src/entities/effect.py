import pygame
import math
from typing import Tuple, Union
from src.entities.grid_position import GridPosition
from src.constants.game_constants import (
    GRID_SIZE, EFFECT_DELAY, EFFECT_DURATION
)

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
    """
    def __init__(self, start_pos: Union[GridPosition, Tuple[int, int]], 
                 end_pos: Union[GridPosition, Tuple[int, int]], 
                 color: Tuple[int, int, int], 
                 duration: int = EFFECT_DURATION, 
                 effect_type: str = "basic"):
        # Convert grid positions to pixel coordinates
        if isinstance(start_pos, GridPosition):
            self.start_pos = start_pos.get_pixel_pos()
        else:
            self.start_pos = start_pos
            
        if isinstance(end_pos, GridPosition):
            self.end_pos = end_pos.get_pixel_pos()
        else:
            self.end_pos = end_pos
            
        self.color = color
        self.duration = duration
        self.current_frame = -EFFECT_DELAY  # Start with negative frames for delay
        self.effect_type = effect_type
        
        # Calculate trajectory
        self.dx = self.end_pos[0] - self.start_pos[0]
        self.dy = self.end_pos[1] - self.start_pos[1]
        
    def update(self) -> bool:
        """Update effect animation. Returns True if effect is still active."""
        self.current_frame += 1
        return self.current_frame < self.duration
        
    def draw(self, surface: pygame.Surface):
        """Draw the effect on the given surface"""
        # Don't draw during delay period
        if self.current_frame < 0:
            return
            
        progress = self.current_frame / self.duration
        
        effect_methods = {
            "magic_missile": self._draw_magic_missile,
            "heal": self._draw_heal,
            "shield": self._draw_shield,
            "strike": self._draw_strike,
            "power_attack": self._draw_power_attack,
            "sneak_attack": self._draw_sneak_attack,
            "critical": self._draw_critical,
            "miss": self._draw_miss
        }
        
        draw_method = effect_methods.get(self.effect_type, self._draw_basic)
        draw_method(surface, progress)
            
    def _draw_magic_missile(self, surface, progress):
        # Draw multiple magic missile particles
        for i in range(5):  # 5 particles
            trail_progress = max(0, progress - i * 0.15)
            trail_x = self.start_pos[0] + self.dx * trail_progress
            trail_y = self.start_pos[1] + self.dy * trail_progress
            
            size = max(4, 12 - i * 2)
            alpha = max(0, 255 - i * 40)
            
            # Draw outer glow
            glow_size = size * 2
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha // 3), 
                             (glow_size, glow_size), glow_size)
            surface.blit(glow_surface, 
                        (trail_x - glow_size + GRID_SIZE//2, 
                         trail_y - glow_size + GRID_SIZE//2))
            
            # Draw core particle
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), 
                             (size, size), size)
            surface.blit(particle_surface, 
                        (trail_x - size + GRID_SIZE//2, 
                         trail_y - size + GRID_SIZE//2))
            
    def _draw_strike(self, surface, progress):
        """Draw a basic strike animation"""
        start_x = self.start_pos[0] + GRID_SIZE//2
        start_y = self.start_pos[1] + GRID_SIZE//2
        end_x = self.end_pos[0] + GRID_SIZE//2
        end_y = self.end_pos[1] + GRID_SIZE//2
        
        # Create slash trail
        slash_surface = pygame.Surface((surface.get_width(), surface.get_height()), 
                                     pygame.SRCALPHA)
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
        effect_surface = pygame.Surface((surface.get_width(), surface.get_height()), 
                                      pygame.SRCALPHA)
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
        
        surface.blit(effect_surface, 
                    (center_x - GRID_SIZE * 1.5, center_y - GRID_SIZE * 1.5 + 50))
        
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
        
        surface.blit(effect_surface, 
                    (center_x - GRID_SIZE * 2, center_y - GRID_SIZE * 2 + 50))
        
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
        
        surface.blit(effect_surface, 
                    (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))
        
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
        
        surface.blit(shield_surface, 
                    (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))
        
    def _draw_heal(self, surface, progress):
        """Draw a healing animation"""
        center_x = self.start_pos[0] + GRID_SIZE//2
        center_y = self.start_pos[1] + GRID_SIZE//2
        radius = GRID_SIZE//2 * progress
        
        # Draw expanding healing circle
        circle_surface = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        pygame.draw.circle(circle_surface, (*self.color, alpha), 
                         (GRID_SIZE, GRID_SIZE), radius, 3)
        
        # Draw healing crosses
        for i in range(4):
            angle = math.pi * 2 * (i / 4) + progress * math.pi
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            cross_size = 10
            pygame.draw.line(surface, self.color, 
                           (x - cross_size, y + 50), 
                           (x + cross_size, y + 50), 2)
            pygame.draw.line(surface, self.color, 
                           (x, y - cross_size + 50), 
                           (x, y + cross_size + 50), 2)
            
        surface.blit(circle_surface, 
                    (center_x - GRID_SIZE, center_y - GRID_SIZE + 50))
                    
    def _draw_basic(self, surface, progress):
        """Draw a basic effect (fallback)"""
        current_x = self.start_pos[0] + self.dx * progress
        current_y = self.start_pos[1] + self.dy * progress
        
        pygame.draw.circle(surface, self.color, 
                         (int(current_x + GRID_SIZE//2), 
                          int(current_y + GRID_SIZE//2)), 5) 