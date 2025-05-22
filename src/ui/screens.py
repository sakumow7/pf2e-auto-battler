import pygame
from typing import List, Tuple, Dict, Any
from src.constants.game_constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE,
    BACKGROUND_COLOR, TITLE_COLOR, TEXT_COLOR, BUTTON_COLOR,
    FONT, TITLE_FONT, LARGE_TITLE_FONT
)

class Screen:
    """Base class for game screens"""
    def __init__(self, game: 'Game'):
        self.game = game
        
    def draw(self, surface: pygame.Surface):
        """Draw the screen"""
        pass
        
    def handle_click(self, pos: Tuple[int, int], right_click: bool = False):
        """Handle mouse click events"""
        pass

class IntroScreen(Screen):
    """Introduction screen with game information and start button"""
    def draw(self, surface: pygame.Surface):
        surface.fill(BACKGROUND_COLOR)
        
        title = LARGE_TITLE_FONT.render("Pathfinder 2E Combat Simulator", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        surface.blit(title, title_rect)
        
        premise_lines = [
            "Welcome to the PF2E Grid Combat Simulator!", "",
            "You lead a party of three adventurers against waves of increasingly",
            "dangerous foes. Work together, use tactical positioning, and manage",
            "your actions wisely to survive!", "", "Controls:",
            "• Left-click: Select characters, actions, and movement squares",
            "• Right-click: Target enemies for attacks/spells",
            "• Mouse wheel: Scroll combat log", "", "Combat Rules:",
            "• Each character has 3 actions per turn.",
            "• Movement (Stride) costs 1 action.",
            "• Attacks & Spells usually cost 1 action (some 2 or more).",
            "• Flanking enemies (ally on opposite side) makes them Off-Guard (-2 AC).", "",
            "Party Members:",
            "• Fighter: Tough warrior, excels at melee.",
            "• Rogue: Agile striker, benefits from Off-Guard targets.",
            "• Wizard: Ranged spellcaster with various arcane powers."
        ]
        
        y = 140
        for line in premise_lines:
            is_header = line.endswith(":") and not line.startswith("•")
            text_surf = TITLE_FONT.render(line, True, TITLE_COLOR) if is_header else FONT.render(line, True, TEXT_COLOR)
            x_offset = WINDOW_WIDTH//4 if not line.startswith("•") else WINDOW_WIDTH//4 + 20
            surface.blit(text_surf, (x_offset, y))
            y += 25 if is_header else 20
            if not line: y += 5  # Extra space for blank lines

class ClassSelectScreen(Screen):
    """Class selection screen"""
    def draw(self, surface: pygame.Surface):
        surface.fill(BACKGROUND_COLOR)
        
        title = LARGE_TITLE_FONT.render("Choose Your Class", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        surface.blit(title, title_rect)
        
        # Draw class options
        classes = [
            ("Fighter", "High HP and armor, powerful melee attacks"),
            ("Rogue", "Mobile striker, excels at flanking"),
            ("Wizard", "Versatile spellcaster with ranged attacks")
        ]
        
        button_width = 200
        button_height = 100
        margin = 40
        total_width = (len(classes) * button_width) + ((len(classes) - 1) * margin)
        start_x = (WINDOW_WIDTH - total_width) // 2
        button_y = WINDOW_HEIGHT // 2 - button_height
        
        for i, (class_name, description) in enumerate(classes):
            button_x = start_x + (button_width + margin) * i
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Draw button
            pygame.draw.rect(surface, BUTTON_COLOR, button_rect)
            pygame.draw.rect(surface, TITLE_COLOR, button_rect, 2)
            
            # Draw class name
            name_text = TITLE_FONT.render(class_name, True, TEXT_COLOR)
            name_rect = name_text.get_rect(center=(button_x + button_width//2, button_y + 30))
            surface.blit(name_text, name_rect)
            
            # Draw description (wrapped)
            words = description.split()
            line = ""
            y_offset = 60
            for word in words:
                test_line = line + word + " "
                test_surf = FONT.render(test_line, True, TEXT_COLOR)
                if test_surf.get_width() > button_width - 20:
                    text_surf = FONT.render(line, True, TEXT_COLOR)
                    text_rect = text_surf.get_rect(center=(button_x + button_width//2, button_y + y_offset))
                    surface.blit(text_surf, text_rect)
                    line = word + " "
                    y_offset += 20
                else:
                    line = test_line
            if line:
                text_surf = FONT.render(line, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(center=(button_x + button_width//2, button_y + y_offset))
                surface.blit(text_surf, text_rect)

class UpgradeScreen(Screen):
    """Character upgrade selection screen"""
    def draw(self, surface: pygame.Surface):
        if self.game.upgrade_selection is None or self.game.upgrade_selection >= len(self.game.party):
            return
            
        surface.fill(BACKGROUND_COLOR)
        char = self.game.party[self.game.upgrade_selection]
        
        # Draw character name and stats
        title = LARGE_TITLE_FONT.render(f"Choose {char.name}'s Upgrade", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        surface.blit(title, title_rect)
        
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
            surface.blit(surf, (WINDOW_WIDTH//4, y))
            y += 30
        
        # Draw upgrade buttons
        button_width = 200
        button_height = 50
        start_y = 300
        
        for i, upgrade in enumerate(self.game.available_upgrades):
            button_rect = pygame.Rect((WINDOW_WIDTH - button_width)//2,
                                    start_y + i * (button_height + 20),
                                    button_width, button_height)
            pygame.draw.rect(surface, BUTTON_COLOR, button_rect)
            pygame.draw.rect(surface, TITLE_COLOR, button_rect, 2)
            
            text = FONT.render(upgrade, True, TEXT_COLOR)
            text_rect = text.get_rect(center=button_rect.center)
            surface.blit(text, text_rect)

class WaveConfirmationScreen(Screen):
    """Wave completion and confirmation screen"""
    def draw(self, surface: pygame.Surface):
        if not self.game.wave_summary:
            return
            
        surface.fill(BACKGROUND_COLOR)
        
        # Draw wave completion title
        title = LARGE_TITLE_FONT.render(self.game.wave_summary["completed"], True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        surface.blit(title, title_rect)
        
        # Draw next wave info
        next_wave = TITLE_FONT.render(self.game.wave_summary["next"], True, TITLE_COLOR)
        next_rect = next_wave.get_rect(center=(WINDOW_WIDTH//2, 140))
        surface.blit(next_wave, next_rect)
        
        # Draw party summary
        y = 200
        summary_title = TITLE_FONT.render("Party Status:", True, TITLE_COLOR)
        surface.blit(summary_title, (WINDOW_WIDTH//4, y))
        y += 40
        
        for status in self.game.wave_summary["upgrades"]:
            text = FONT.render(status, True, TEXT_COLOR)
            surface.blit(text, (WINDOW_WIDTH//4, y))
            y += 30
        
        # Draw continue and quit buttons
        button_width = 300
        button_height = 60
        margin = 40
        start_y = WINDOW_HEIGHT - 150
        
        # Continue button
        continue_rect = pygame.Rect((WINDOW_WIDTH//2 - button_width - margin//2),
                                  start_y, button_width, button_height)
        pygame.draw.rect(surface, BUTTON_COLOR, continue_rect)
        pygame.draw.rect(surface, TITLE_COLOR, continue_rect, 2)
        continue_text = FONT.render("Continue to Next Wave", True, TEXT_COLOR)
        text_rect = continue_text.get_rect(center=continue_rect.center)
        surface.blit(continue_text, text_rect)
        
        # Quit button
        quit_rect = pygame.Rect((WINDOW_WIDTH//2 + margin//2),
                               start_y, button_width, button_height)
        pygame.draw.rect(surface, BUTTON_COLOR, quit_rect)
        pygame.draw.rect(surface, TITLE_COLOR, quit_rect, 2)
        quit_text = FONT.render("Quit Game", True, TEXT_COLOR)
        text_rect = quit_text.get_rect(center=quit_rect.center)
        surface.blit(quit_text, text_rect)

class EndGameScreen(Screen):
    """Victory or game over screen"""
    def draw(self, surface: pygame.Surface):
        surface.fill(BACKGROUND_COLOR)
        
        # Draw title
        if self.game.state == "victory":
            title_text = "🏆 Congratulations! You are Victorious! 🏆"
            subtitle_text = "You have defeated all waves of enemies!"
        else:  # game_over
            title_text = "💀 Game Over 💀"
            subtitle_text = "Your party has fallen in battle..."
        
        # Draw main title
        title = LARGE_TITLE_FONT.render(title_text, True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        surface.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = TITLE_FONT.render(subtitle_text, True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 60))
        surface.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        button_width = 200
        button_height = 60
        margin = 40
        total_width = (2 * button_width) + margin
        start_x = (WINDOW_WIDTH - total_width) // 2
        button_y = WINDOW_HEIGHT // 2 + 50
        
        # Restart button
        restart_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, BUTTON_COLOR, restart_rect)
        pygame.draw.rect(surface, TITLE_COLOR, restart_rect, 2)
        restart_text = TITLE_FONT.render("Play Again", True, TEXT_COLOR)
        text_rect = restart_text.get_rect(center=restart_rect.center)
        surface.blit(restart_text, text_rect)
        
        # Quit button
        quit_rect = pygame.Rect(start_x + button_width + margin, button_y, button_width, button_height)
        pygame.draw.rect(surface, BUTTON_COLOR, quit_rect)
        pygame.draw.rect(surface, TITLE_COLOR, quit_rect, 2)
        quit_text = TITLE_FONT.render("Quit Game", True, TEXT_COLOR)
        text_rect = quit_text.get_rect(center=quit_rect.center)
        surface.blit(quit_text, text_rect) 