import pygame
import random
import os
from typing import List, Tuple, Optional, Dict, Any

from src.entities.grid_position import GridPosition
from src.entities.effect import Effect
from src.constants.game_constants import (
    GRID_SIZE, GRID_COLS, GRID_ROWS,
    STRIKE_COLOR, MISS_COLOR, CRITICAL_COLOR,
    SNEAK_ATTACK_COLOR, HEAL_COLOR, SHIELD_COLOR
)

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
        self.bonus_damage = 0
        
    def load_sprite(self, sprite_path: str):
        """Load and scale character sprite"""
        try:
            if os.path.exists(sprite_path):
                self.sprite_path = sprite_path
                original_sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite = pygame.transform.scale(original_sprite, (GRID_SIZE, GRID_SIZE))
        except Exception as e:
            print(f"Error loading sprite {sprite_path}: {e}")
            self.sprite = None
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hp > 0
    
    def get_ac(self) -> int:
        """Get current armor class, accounting for conditions"""
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
        return False
    
    def draw(self, surface: pygame.Surface, game: Optional['Game'] = None):
        """Draw the character on the surface"""
        if not self.alive:
            return
        
        x, y = self.position.get_pixel_pos()
        
        # Draw active turn indicator if this is the current character
        if (game and not self.is_enemy and 
            game.state == "combat" and 
            game.current_member_idx < len(game.party) and 
            game.party[game.current_member_idx] == self):
            # Draw pulsing highlight around active character
            pulse = abs(math.sin(pygame.time.get_ticks() / 500))
            highlight_color = (255, 255, 255, int(100 + 155 * pulse))
            highlight_surface = pygame.Surface((GRID_SIZE + 8, GRID_SIZE + 8), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, highlight_color, 
                           (0, 0, GRID_SIZE + 8, GRID_SIZE + 8), 4, border_radius=4)
            surface.blit(highlight_surface, (x - 4, y - 4))
        
        # Draw character sprite or fallback shape
        if self.sprite:
            surface.blit(self.sprite, (x, y))
        else:
            if self.is_enemy:
                # Draw enemy as diamond
                points = [
                    (x + GRID_SIZE//2, y),  # Top
                    (x + GRID_SIZE, y + GRID_SIZE//2),  # Right
                    (x + GRID_SIZE//2, y + GRID_SIZE),  # Bottom
                    (x, y + GRID_SIZE//2)  # Left
                ]
                pygame.draw.polygon(surface, self.color, points)
                pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            else:
                # Draw hero as circle
                pygame.draw.circle(surface, self.color, 
                                 (x + GRID_SIZE//2, y + GRID_SIZE//2), 
                                 GRID_SIZE//2)
                pygame.draw.circle(surface, (255, 255, 255),
                                 (x + GRID_SIZE//2, y + GRID_SIZE//2),
                                 GRID_SIZE//2, 2)
        
        # Draw health bar
        health_percent = self.hp / self.max_hp
        bar_width = GRID_SIZE * health_percent
        pygame.draw.rect(surface, (100, 0, 0),
                        (x, y - 10, GRID_SIZE, 5))
        if health_percent > 0:
            pygame.draw.rect(surface, (0, 255, 0),
                           (x, y - 10, bar_width, 5))

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

    def apply_upgrade(self, upgrade_type: str) -> str:
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
            
    def heal_full(self) -> int:
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
            # Add miss animation
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), MISS_COLOR, effect_type="miss"))
            target.off_guard = False
            return 1, False
            
        # Calculate damage
        dice_num, dice_sides = dice
        if roll == 20 or total >= target_ac + 10:
            game.add_message("Critical Hit!")
            dmg = sum(random.randint(1, dice_sides) for _ in range(dice_num * 2))
            # Add critical hit animation
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), CRITICAL_COLOR, effect_type="critical"))
        elif total >= target_ac:
            game.add_message("Hit!")
            dmg = sum(random.randint(1, dice_sides) for _ in range(dice_num))
            # Add basic strike animation
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), STRIKE_COLOR, effect_type="strike"))
        else:
            game.add_message("Miss!")
            # Add miss animation
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), MISS_COLOR, effect_type="miss"))
            target.off_guard = False
            return 1, False
            
        if sneak_attack or target.off_guard:
            sa_dmg = random.randint(1, 6)
            dmg += sa_dmg
            game.add_message(f"Sneak Attack! Extra d6: {sa_dmg}")
            # Add sneak attack animation
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), SNEAK_ATTACK_COLOR, effect_type="sneak_attack"))
            
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
            actions.append(("Heal", self.position, lambda: self.heal(game)))
            
        return actions
        
    def select_stride(self, game: 'Game') -> Tuple[int, bool]:
        """Select Stride action to show movement options"""
        game.selected_character = self
        game.highlighted_squares = self.get_valid_moves(game)
        game.add_message(f"{self.name} is selecting where to Stride (move up to {self.speed} feet)")
        return 0, True  # Don't consume action yet, will be consumed on actual move

    def get_pixel_pos(self) -> Tuple[int, int]:
        """Get the pixel position of the character for animations"""
        return self.position.get_pixel_pos() 