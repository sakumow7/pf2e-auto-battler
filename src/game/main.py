# -*- coding: utf-8 -*-
"""
PF2E Grid Combat - Main game module
"""
import pygame
import sys
from typing import List, Dict, Any, Optional, Tuple

from src.entities.base_character import BaseCharacter
from src.entities.characters import Fighter, Rogue, Wizard, Enemy
from src.entities.grid_position import GridPosition
from src.entities.effect import Effect
from src.ui.screens import (
    Screen, IntroScreen, ClassSelectScreen, UpgradeScreen,
    WaveConfirmationScreen, EndGameScreen
)
from src.constants.game_constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, GRID_COLS, GRID_ROWS,
    BACKGROUND_COLOR, GRID_COLOR, GRID_HIGHLIGHT,
    TEXT_COLOR, BUTTON_COLOR,
    FONT, TITLE_FONT
)

class Game:
    """Main game class handling game state and logic"""
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PF2E Grid Combat")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.state = "intro"  # intro, class_select, combat, upgrade, wave_complete, victory, game_over
        self.party: List[BaseCharacter] = []
        self.enemies: List[Enemy] = []
        self.current_wave = 0
        self.current_member_idx = 0
        self.actions_left = 3
        self.selected_character: Optional[BaseCharacter] = None
        self.selected_target: Optional[BaseCharacter] = None
        self.highlighted_squares: List[GridPosition] = []
        self.combat_log: List[str] = []
        self.scroll_offset = 0
        self.wave_summary: Optional[Dict[str, Any]] = None
        self.upgrade_selection: Optional[str] = None
        self.available_upgrades = ["Accuracy", "Damage", "Speed", "Vitality"]
        
        # Set up screens
        self.screens: Dict[str, Screen] = {
            "intro": IntroScreen(self),
            "class_select": ClassSelectScreen(self),
            "upgrade": UpgradeScreen(self),
            "wave_complete": WaveConfirmationScreen(self),
            "victory": EndGameScreen(self),
            "game_over": EndGameScreen(self)
        }
        
        # Set up effects
        self.active_effects: List[Effect] = []
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button == 3)  # Right click is button 3
                elif event.type == pygame.MOUSEWHEEL:
                    if self.state == "combat":
                        self.scroll_offset = max(0, min(
                            len(self.combat_log) - 10,
                            self.scroll_offset - event.y
                        ))
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
        
    def update(self):
        """Update game state"""
        # Update active effects
        self.active_effects = [effect for effect in self.active_effects if effect.update()]
        
        # Check for game over conditions
        if self.state == "combat":
            # Check if all party members are dead
            if all(not char.is_alive() for char in self.party):
                self.state = "game_over"
            
            # Check if all enemies are dead
            elif all(not enemy.is_alive() for enemy in self.enemies):
                self.check_wave_complete()
        
    def draw(self):
        """Draw the current game state"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw appropriate screen based on game state
        if self.state in self.screens:
            self.screens[self.state].draw(self.screen)
        elif self.state == "combat":
            self.draw_combat()
        
        pygame.display.flip()
        
    def draw_combat(self):
        """Draw the combat screen"""
        # Draw grid
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                color = GRID_HIGHLIGHT if GridPosition(x, y) in self.highlighted_squares else GRID_COLOR
                pygame.draw.rect(self.screen, color, rect, 1)
        
        # Draw characters
        for char in self.party + self.enemies:
            char.draw(self.screen, self)
        
        # Draw effects
        for effect in self.active_effects:
            effect.draw(self.screen)
        
        # Draw UI elements
        self.draw_combat_ui()
        
    def draw_combat_ui(self):
        """Draw combat UI elements"""
        # Draw turn indicator
        if self.current_member_idx < len(self.party):
            char = self.party[self.current_member_idx]
            turn_text = f"{char.name}'s Turn - Actions: {self.actions_left}"
            text_surf = TITLE_FONT.render(turn_text, True, TEXT_COLOR)
            self.screen.blit(text_surf, (10, WINDOW_HEIGHT - 150))
        
        # Draw combat log
        log_height = 120
        log_surface = pygame.Surface((WINDOW_WIDTH - 20, log_height))
        log_surface.fill(BACKGROUND_COLOR)
        pygame.draw.rect(log_surface, TEXT_COLOR, log_surface.get_rect(), 1)
        
        y = 5
        visible_messages = self.combat_log[self.scroll_offset:self.scroll_offset + 6]
        for message in visible_messages:
            text_surf = FONT.render(message, True, TEXT_COLOR)
            log_surface.blit(text_surf, (5, y))
            y += 20
        
        self.screen.blit(log_surface, (10, WINDOW_HEIGHT - 140))
        
        # Draw available actions if a character is selected
        if self.selected_character and self.current_member_idx < len(self.party):
            actions = self.selected_character.get_actions(self)
            button_width = 120
            button_height = 30
            start_x = WINDOW_WIDTH - button_width - 10
            start_y = 10
            
            for i, (action_name, pos, _) in enumerate(actions):
                button_rect = pygame.Rect(start_x, start_y + i * (button_height + 5),
                                        button_width, button_height)
                pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
                pygame.draw.rect(self.screen, TEXT_COLOR, button_rect, 1)
                
                text_surf = FONT.render(action_name, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(center=button_rect.center)
                self.screen.blit(text_surf, text_rect)
        
    def handle_click(self, pos: Tuple[int, int], right_click: bool = False):
        """Handle mouse click events"""
        if self.state in self.screens:
            self.screens[self.state].handle_click(pos, right_click)
            return
            
        if self.state != "combat":
            return
            
        # Get grid position
        grid_x = pos[0] // GRID_SIZE
        grid_y = pos[1] // GRID_SIZE
        click_pos = GridPosition(grid_x, grid_y)
        
        # Handle right click (targeting)
        if right_click:
            for enemy in self.enemies:
                if enemy.position == click_pos and enemy.is_alive():
                    self.selected_target = enemy
                    return
            return
        
        # Handle left click
        # Check for UI button clicks first
        if self.selected_character:
            actions = self.selected_character.get_actions(self)
            button_width = 120
            button_height = 30
            start_x = WINDOW_WIDTH - button_width - 10
            start_y = 10
            
            for i, (action_name, action_pos, action) in enumerate(actions):
                button_rect = pygame.Rect(start_x, start_y + i * (button_height + 5),
                                        button_width, button_height)
                if button_rect.collidepoint(pos):
                    if isinstance(action, tuple):
                        # Action requires a target
                        if self.selected_target:
                            _, func = action
                            used, success = func(self.selected_target)
                            if success:
                                self.actions_left -= used
                                if self.actions_left <= 0:
                                    self.next_turn()
                    else:
                        # Direct action
                        used, success = action()
                        if success:
                            self.actions_left -= used
                            if self.actions_left <= 0:
                                self.next_turn()
                    return
        
        # Check for character selection
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            # Check party members first
            for char in self.party:
                if char.position == click_pos and char.is_alive():
                    if char == self.party[self.current_member_idx]:
                        self.selected_character = char
                        self.highlighted_squares = []
                    return
            
            # Check if clicking a highlighted square (movement)
            if click_pos in self.highlighted_squares and self.selected_character:
                if self.selected_character.move_to(click_pos, self):
                    self.actions_left -= 1
                    self.highlighted_squares = []
                    if self.actions_left <= 0:
                        self.next_turn()
                return
        
        # Clear selections if clicking empty space
        self.selected_character = None
        self.highlighted_squares = []
        
    def next_turn(self):
        """Advance to the next turn"""
        self.current_member_idx += 1
        self.selected_character = None
        self.selected_target = None
        self.highlighted_squares = []
        
        # Reset actions
        self.actions_left = 3
        
        # Handle enemy turns
        if self.current_member_idx >= len(self.party):
            self.enemy_turn()
            self.current_member_idx = 0
            
        # Clear any expired effects
        for char in self.party:
            if isinstance(char, Wizard) and char.shield_up:
                char.shield_up = False
                char.base_ac -= 2
                self.add_message(f"{char.name}'s Shield fades.")
            char.off_guard = False
            
    def enemy_turn(self):
        """Handle enemy turn logic"""
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
                
            # Simple AI: Move towards closest living party member and attack if possible
            target = min((char for char in self.party if char.is_alive()),
                        key=lambda c: enemy.position.distance_to(c.position),
                        default=None)
            
            if not target:
                continue
                
            actions_left = 3
            while actions_left > 0:
                distance = enemy.position.distance_to(target.position)
                
                if distance <= 1:
                    # Attack if in range
                    used, _ = enemy.attack(target, self)
                    actions_left -= used
                else:
                    # Move towards target
                    moves = enemy.get_valid_moves(self)
                    if moves:
                        best_move = min(moves,
                                      key=lambda p: p.distance_to(target.position))
                        if enemy.move_to(best_move, self):
                            actions_left -= 1
                            continue
                
                # If we can't move or attack, end turn
                break
                
    def add_message(self, message: str):
        """Add a message to the combat log"""
        self.combat_log.append(message)
        if len(self.combat_log) > 100:  # Limit log size
            self.combat_log = self.combat_log[-100:]
            
    def add_effect(self, effect: Effect):
        """Add a visual effect"""
        self.active_effects.append(effect)
        
    def get_all_characters(self) -> List[BaseCharacter]:
        """Get all characters (party and enemies)"""
        return self.party + self.enemies
        
    def check_wave_complete(self):
        """Check if current wave is complete and handle wave transition"""
        if all(not enemy.is_alive() for enemy in self.enemies):
            self.current_wave += 1
            
            if self.current_wave >= len(self.get_wave_data()):
                self.state = "victory"
                return
            
            # Prepare wave summary
            self.wave_summary = {
                "completed": f"Wave {self.current_wave} Complete!",
                "next": f"Prepare for Wave {self.current_wave + 1}",
                "upgrades": [
                    f"{char.name}: HP {char.hp}/{char.max_hp}"
                    for char in self.party if char.is_alive()
                ]
            }
            
            # Heal party members
            for char in self.party:
                if char.is_alive():
                    healed = char.heal_full()
                    self.wave_summary["upgrades"].append(
                        f"{char.name} restored {healed} HP!"
                    )
            
            self.state = "wave_complete"
            self.upgrade_selection = 0
            
    def start_next_wave(self):
        """Start the next wave of combat"""
        wave_data = self.get_wave_data()[self.current_wave]
        self.enemies = []
        
        # Spawn enemies
        for enemy_type, count, stats in wave_data:
            for i in range(count):
                enemy = Enemy(f"{enemy_type} {chr(65+i)}", *stats)
                # Place enemy on right side of grid
                col = GRID_COLS - 2
                row = (GRID_ROWS // (count + 1)) * (i + 1)
                enemy.position = GridPosition(col, row)
                self.enemies.append(enemy)
        
        self.state = "combat"
        self.current_member_idx = 0
        self.actions_left = 3
        self.selected_character = None
        self.selected_target = None
        self.highlighted_squares = []
        self.combat_log = [f"Wave {self.current_wave + 1} begins!"]
        
    def get_wave_data(self) -> List[List[Tuple[str, int, Tuple[int, int, int]]]]:
        """Get wave configuration data"""
        return [
            # Wave 1: 2 Goblins
            [("Goblin", 2, (20, 15, 6, (1, 6)))],
            
            # Wave 2: 3 Goblins
            [("Goblin", 3, (20, 15, 6, (1, 6)))],
            
            # Wave 3: 2 Goblins, 1 Ogre
            [
                ("Goblin", 2, (20, 15, 6, (1, 6))),
                ("Ogre", 1, (40, 17, 8, (2, 8)))
            ],
            
            # Wave 4: 2 Ogres
            [("Ogre", 2, (40, 17, 8, (2, 8)))],
            
            # Wave 5: Boss - 1 Wyvern, 2 Goblins
            [
                ("Wyvern", 1, (80, 19, 10, (2, 10))),
                ("Goblin", 2, (20, 15, 6, (1, 6)))
            ]
        ]

if __name__ == "__main__":
    game = Game()
    game.run() 