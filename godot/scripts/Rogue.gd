extends Character
class_name Rogue

func _init(_name: String) -> void:
	super(_name, 38, 17, 8)
	speed = 30        # rogues are faster


# --------------------------------------------------------------
# Twin Feint – two strikes, second counts as sneak
# --------------------------------------------------------------
func twin_feint(target: Character) -> Array:
	var first   := super.attack(target, 1, 6)          # normal strike
	var second  := attack_rogue(target, true)          # sneak strike
	return [2, first[1] or second[1]]                  # 2 actions


# --------------------------------------------------------------
# Rogue-specific strike with optional sneak damage
# (kept separate so we don’t clash with Character.attack())
# --------------------------------------------------------------
func attack_rogue(target: Character, sneak: bool = false) -> Array:
	if not target.is_alive():
		return [0, false]
	if position.distance_to(target.position) > 1:
		return [0, false]

	var roll  := DiceUtils.roll_dice(1, 20)
	var total := roll + attack_bonus
	var target_ac := target.get_ac()

	var dmg := 0
	var hit := false
	if roll == 20 or total >= target_ac + 10:
		dmg = DiceUtils.roll_dice(2, 6)   # crit = double dice
		hit = true
	elif total >= target_ac:
		dmg = DiceUtils.roll_dice(1, 6)
		hit = true

	if sneak:
		dmg += DiceUtils.roll_dice(1, 6)  # extra sneak d6
	dmg += bonus_damage

	if hit:
		target.take_damage(dmg)

	return [1, hit]                        # 1 action
