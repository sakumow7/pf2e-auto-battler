# res://scripts/Character.gd
extends Resource
class_name Character               #  <-- makes the class visible to Rogue/Fighter/Wizard

const DiceUtils := preload("res://scripts/DiceUtils.gd")   # adjust path if needed

# -------------------------------------------------------------------------
#  FIELDS
# -------------------------------------------------------------------------
var name: String
var max_hp := 0
var hp := 0
var ac := 0
var attack_bonus := 0
var position: GridPosition

var potions := 3
var speed := 25
var bonus_damage := 0
var off_guard := false
var is_enemy := false
var alive := true


# -------------------------------------------------------------------------
#  CONSTRUCTOR
# -------------------------------------------------------------------------
func _init(_name: String, _hp: int, _ac: int, _atk: int) -> void:
	name = _name
	max_hp = _hp
	hp = _hp
	ac = _ac
	attack_bonus = _atk
	position = GridPosition.new(0, 0)


# -------------------------------------------------------------------------
#  BASIC HELPERS
# -------------------------------------------------------------------------
func is_alive() -> bool:	return hp > 0
func get_ac()    -> int:	return ac - 2 if off_guard else ac

func take_damage(amount: int) -> void:
	hp = max(0, hp - amount)
	alive = hp > 0


# -------------------------------------------------------------------------
#  GENERIC MELEE/RANGED ATTACK
#  Returns  [actions_used, did_hit]
#  Sub-classes can call this to avoid re-writing the roll logic.
# -------------------------------------------------------------------------
func attack(target: Character,
		dice_num: int,
		dice_sides: int,
		bonus: int = 0) -> Array:

	if not target.is_alive():
		return [0, false]

	# assume melee (distance ≤1) — subclasses can check range first
	if position.distance_to(target.position) > 1:
		return [0, false]

	var roll := DiceUtils.roll_dice(1, 20)
	var total := roll + attack_bonus
	var target_ac := target.get_ac()

	var dmg := 0
	var hit := false

	if roll == 20 or total >= target_ac + 10:           # crit
		dmg = DiceUtils.roll_dice(dice_num * 2, dice_sides)
		hit = true
	elif total >= target_ac:                             # normal hit
		dmg = DiceUtils.roll_dice(dice_num, dice_sides)
		hit = true

	dmg += bonus + bonus_damage
	if hit:
		target.take_damage(dmg)

	return [1, hit]   # always costs 1 action here
