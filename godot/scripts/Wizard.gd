extends Character
class_name Wizard

const ARCANE_BLAST_RANGE := 4
const MAGIC_MISSILE_RANGE := 24

var shield_up := false

func _init(_name: String) -> void:
	super(_name, 32, 16, 6)


# Arcane Blast – 1 action
func arcane_blast(target: Character) -> Array:
	if position.distance_to(target.position) > ARCANE_BLAST_RANGE:
		return [0, false]

	var result := attack(target, 2, 4)      # uses Character.attack()
	if shield_up:
		shield_up = false
		ac -= 2

	return [1, result[1]]                   # [actions_used, did_hit]


# Magic Missile – auto-hit force damage
func magic_missile(target: Character, count: int = 1) -> Array:
	if position.distance_to(target.position) > MAGIC_MISSILE_RANGE:
		return [0, false]

	for i in range(count):
		var dmg := DiceUtils.roll_dice(1, 4) + 1
		target.take_damage(dmg)

	if shield_up:
		shield_up = false
		ac -= 2

	return [count, true]                    # always hits


# Shield spell – +2 AC until next turn
func cast_shield() -> Array:
	if not shield_up:
		ac += 2
		shield_up = true
	return [1, true]
