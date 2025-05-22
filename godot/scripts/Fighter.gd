extends Character
class_name Fighter


func _init(_name: String):
	super(_name, 50, 18, 9)

func power_attack(target: Character) -> Array:
	var result = attack(target, 2, 10, 2)
	return [2, result[1]]

func attack(target: Character, dice_num := 1, dice_sides := 10, bonus := 0) -> Array:
	if not target.is_alive():
		return [0, false]
	var distance = position.distance_to(target.position)
	if distance > 1:
		return [0, false]
	var roll = DiceUtils.roll_dice(1, 20)
	var total = roll + attack_bonus
	var target_ac = target.get_ac()
	var dmg = 0
	var hit = false
	if roll == 20 or total >= target_ac + 10:
		dmg = DiceUtils.roll_dice(dice_num * 2, dice_sides)
		hit = true
	elif total >= target_ac:
		dmg = DiceUtils.roll_dice(dice_num, dice_sides)
		hit = true
	dmg += bonus + bonus_damage
	if hit:
		target.take_damage(dmg)
	return [1, hit]
