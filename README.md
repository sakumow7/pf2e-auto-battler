# PF2E Auto Battler

A Pathfinder 2nd Edition inspired auto-battler game built with Python and Pygame. Fight through waves of enemies with your chosen hero class in a tactical grid-based combat system.

## Features

- **Four Playable Classes:**
  - Fighter: Specializes in powerful melee attacks and defensive abilities
  - Rogue: Masters of positioning and sneak attacks
  - Wizard: Controls the battlefield with powerful spells and magical abilities
  - Cleric: Supports the party with spells that manipulate health

- **Tactical Grid Combat:**
  - Turn-based combat system
  - 16x8 grid battlefield
  - Strategic positioning and movement
  - Flanking mechanics

- **Dynamic Battle System:**
  - Multiple enemy types (Goblins, Ogres, Wyverns)
  - Wave-based progression
  - Character upgrades between waves
  - Visual effects for different abilities
  - Combat log with detailed action results

## Installation

1. Ensure you have Python installed on your system
2. Clone this repository
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python pf2e_grid_combat.py
```

2. Select your character class:
   - Fighter: High HP and armor, specializes in Power Attacks
   - Rogue: Agile character focusing on positioning and Sneak Attacks
   - Wizard: Ranged spellcaster with Magic Missile, Arcane Blast, and Shield spells
   - Cleric: Supportive spellcaster with Spirit Link, Sanctuary, and Lesser Heal spells.

3. Combat Controls:
   - Left-click to select your character and view available actions
   - Right-click to cancel a selection
   - Click action buttons to perform abilities
   - Click valid grid squares to move or target enemies

4. Strategy Tips:
   - Use positioning to your advantage
   - Manage your actions wisely (you have 3 actions per turn)
   - Take advantage of class-specific abilities
   - Watch your health and use tactical retreats when needed

## Dependencies

- Python 3.x
- Pygame >= 2.5.0
- PyQt6 >= 6.5
- Additional requirements listed in `requirements.txt`

## Game Features

### Character Classes

**Fighter**
- High HP and armor class
- Power Attack ability for increased damage
- Strong melee combat capabilities

**Rogue**
- Sneak Attack ability when flanking
- Twin Feint for multiple attacks
- Mobility-focused gameplay

**Wizard**
- Arcane Blast for reliable damage
- Magic Missile for guaranteed hits
- Shield spell for defensive options

**Cleric**
- Sanctuary to nullify damage
- Spirit Link to equalize HP between the Target and Cleric
- Lesser Heal to restore HP

### Combat System
- Turn-based tactical combat
- Three actions per turn
- Grid-based movement and positioning
- Visual effects for abilities
- Dynamic enemy AI
- Wave-based progression with increasing difficulty
