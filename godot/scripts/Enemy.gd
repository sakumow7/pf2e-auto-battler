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

	# We ignore the incoming dice_num / dice_sides and use this enemy's own dice
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

# ------------------------------------------------------------------
# AI functionality
# ------------------------------------------------------------------

# Returns the moves this AI can make
func get_valid_moves(game_controller) -> Array[Vector2i]:
	var moves: Array[Vector2i] = []
	var grid_cols = game_controller.GRID_COLS
	var grid_rows = game_controller.GRID_ROWS
	
	# Check all 8 surrounding cells
	for dx in range(-1, 2):
		for dy in range(-1, 2):
			if dx == 0 and dy == 0:
				continue  # Skip current position
				
			var new_x = position.x + dx
			var new_y = position.y + dy
			
			# Check if within grid bounds
			if new_x >= 0 and new_x < grid_cols and new_y >= 0 and new_y < grid_rows:
				var pos = Vector2i(new_x, new_y)
				# Check if cell is empty
				if game_controller._grid_to_unit(pos) == null:
					moves.append(pos)
	
	return moves

# Execute the enemy's turn
func execute_turn(game_controller, target: Character) -> Dictionary:
	var result = {
		"moved": false,
		"attacked": false,
		"move_position": null
	}
	
	# First action: move closer if not adjacent
	var dist := position.distance_to(target.position)
	if dist > 1:
		var moves := get_valid_moves(game_controller)
		if moves.size() > 0:
			# Sort moves by distance to target (closest first)
			moves.sort_custom(func(a, b): return a.distance_to(Vector2i(target.position.x, target.position.y)) < b.distance_to(Vector2i(target.position.x, target.position.y)))
			move_to(GridPosition.new(moves[0].x, moves[0].y), game_controller)
			result.moved = true
			result.move_position = moves[0]
	
	# Second action: attack if adjacent
	dist = position.distance_to(target.position)
	if dist <= 1 and target.is_alive():
		# Use the enemy's own damage dice
		var attack_result = attack(target, damage_dice[0], damage_dice[1])
		result.attacked = attack_result[1]  # [1] is the hit bool
	
	return result

# Move to a new position
func move_to(new_position: GridPosition, game_controller) -> void:
	position = new_position
