
# Pathfinder 2E Combat System Overview

This document provides a reference guide to the core mechanics of the Pathfinder Second Edition (PF2E) combat system. It is intended for collaborators working on the PF2E Grid Combat Python project to understand the underlying gameplay rules implemented in `pf2e_grid_combat.py`.

## Turn Structure

Combat in Pathfinder 2E uses a round-based system. Each round, every combatant takes a **turn**, during which they have:

- **3 Actions** to use on various tasks like Stride, Strike, Cast a Spell, etc.
- **1 Reaction** usable outside their turn when triggered by specific conditions.

### Common Actions
- **Strike (1 Action)**: Perform a melee or ranged attack.
- **Stride (1 Action)**: Move up to your Speed.
- **Raise a Shield (1 Action)**: Gain a +2 circumstance bonus to AC until your next turn.
- **Interact (1 Action)**: Draw a weapon, open a door, etc.
- **Cast a Spell**: Usually takes 1–3 actions depending on the spell.

## Attack Rolls

To determine if an attack hits:
- Roll 1d20 + **Attack Bonus**
- Compare the total to the target's **Armor Class (AC)**

### Degrees of Success
- **Critical Success**: Beat AC by 10+ → Double damage.
- **Success**: Meet or exceed AC → Normal damage.
- **Failure**: Below AC → No effect.
- **Critical Failure**: Roll a natural 1 or miss by 10+ → Possible drawback.

## Armor Class (AC)

A character’s AC is:
```
AC = 10 + Dexterity modifier + Armor bonus + Item bonuses + Circumstance bonuses + Status bonuses
```

In the Python system, `base_ac` is modified depending on conditions like Off-Guard.

## Conditions

- **Off-Guard**: Target loses Dexterity bonus to AC. In-game, it applies a -2 penalty to AC.
- **Flanked**: A creature is flanked if two enemies are on opposite sides; it becomes Off-Guard.
- **Sneak Attack**: Rogues deal extra damage when the enemy is Off-Guard.

## Damage Calculation

Damage is calculated using dice:
- Example: `1d8` = Roll one 8-sided die.
- Bonus damage may be added from Strength or special abilities.

### Critical Hits
- Roll double the number of damage dice (not the result).
- Effects like "Sneak Attack" are **not** doubled unless stated otherwise.

## Healing

- **Potions**: In this game, characters can use potions (1 Action) to heal a fixed amount (e.g., 15 HP).
- **Healing Spells**: Cast with varying action costs; require line of sight and sometimes touch.

## Movement

- Movement is measured in **feet**, typically 25 or 30 feet for most characters.
- 1 Grid Square = 5 feet.
- Movement uses one action per stride.

## Status Effects and Animations (in code)

Visual and mechanical feedback in the game includes:
- **Strike** → Red slashes
- **Power Attack** → Bright red, multiple slashes
- **Sneak Attack** → Yellow precise strikes
- **Critical Hit** → Gold explosion
- **Miss** → Gray whoosh
- **Heal** → Green glow and crosses
- **Shield** → Blue arcs
- **Magic Missile** → Light blue trail

## Enemy AI (Simplified)
- Move toward closest player
- Attack if in range
- Repeat up to 3 actions

## Summary of Character Roles

| Class   | HP  | AC | Attack Bonus | Speed | Special Abilities |
|---------|-----|----|--------------|--------|-------------------|
| Fighter | 50  | 18 | +9           | 25 ft  | Power Attack      |
| Rogue   | 38  | 17 | +8           | 30 ft  | Twin Feint, Sneak Attack |
| Wizard  | 32  | 16 | +6           | 25 ft  | Magic Missile, Arcane Blast, Shield |

---

This summary outlines the mechanical logic implemented in the combat simulation. For deeper rule references, consult the official [Pathfinder 2E SRD](https://2e.aonprd.com/Rules.aspx).
