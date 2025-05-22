extends Character
class_name Enemy


# default: 1d8  (Array[int] enforces the element type so the editor is happy)
var damage_dice: Array[int] = [1, 8]


func _init(
		_name: String,
		_hp: int,
		_ac: int,
		_attack_bonus: int,
		_damage_dice: Array[int] = [1, 8]) -> void:
	super(_name, _hp, _ac, _attack_bonus)
	damage_dice = _damage_dice
	is_enemy = true


# ------------------------------------------------------------------
# Must match the base-class signature exactly
# attack(target, dice_num, dice_sides, bonus = 0) -> Array
# ------------------------------------------------------------------
func attack(
		target: Character,
		dice_num: int,
		dice_sides: int,
		bonus: int = 0) -> Array:

	if not target.is_alive():
		return [0, false]

	if position.distance_to(target.position) > 1:
		return [0, false]

	var roll: int  = Character.DiceUtils.roll_dice(1, 20)
	var total: int = roll + attack_bonus
	var target_ac := target.get_ac()

	var dmg: int  = 0
	var hit: bool = false

	# We ignore the incoming dice_num / dice_sides and use this enemy’s own dice
	var num:   int = damage_dice[0]
	var sides: int = damage_dice[1]

	if roll == 20 or total >= target_ac + 10:              # critical hit
		dmg = Character.DiceUtils.roll_dice(num * 2, sides)
		hit = true
	elif total >= target_ac:                               # normal hit
		dmg = Character.DiceUtils.roll_dice(num, sides)
		hit = true

	dmg += bonus_damage + bonus

	if hit:
		target.take_damage(dmg)

	return [1, hit]                                        # always costs 1 action
