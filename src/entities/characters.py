from typing import List, Tuple
from src.entities.base_character import Character
from src.entities.grid_position import GridPosition
from src.entities.effect import Effect
from src.constants.game_constants import (
    FIGHTER_COLOR, ROGUE_COLOR, WIZARD_COLOR, ENEMY_COLOR,
    POWER_ATTACK_COLOR, MAGIC_MISSILE_COLOR, SHIELD_COLOR,
    IMAGE_PATHS
)

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
        
    def power_attack(self, target: Character, game: 'Game') -> Tuple[int, bool]:
        """Execute a Power Attack action"""
        if game.actions_left < 2:
            game.add_message("Not enough actions for Power Attack!")
            return 0, False
            
        game.add_message(f"{self.name} uses Power Attack!")
        
        # Add power attack animation
        game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), 
                             POWER_ATTACK_COLOR, effect_type="power_attack"))
        
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
        
    def strike(self, target: Character, game: 'Game') -> Tuple[int, bool]:
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
        
    def twin_feint(self, target: Character, game: 'Game') -> Tuple[int, bool]:
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
                                   lambda t: self.magic_missile(target, game, count))))
        
        # Add Shield spell (no target needed) if have enough actions and not already up
        if game.actions_left >= 1 and not self.shield_up:
            actions.append(("Shield [1]", self.position, lambda: self.cast_shield(game)))
        
        # Always add End Turn action
        actions.append(("End Turn [0]", self.position, lambda: game.next_turn()))
        
        return actions
        
    def arcane_blast(self, target: Character, game: 'Game') -> Tuple[int, bool]:
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
        
    def magic_missile(self, target: Character, game: 'Game', action_count: int = 1) -> Tuple[int, bool]:
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
            game.add_effect(Effect(self.get_pixel_pos(), target.get_pixel_pos(), 
                                 MAGIC_MISSILE_COLOR, effect_type="magic_missile"))
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