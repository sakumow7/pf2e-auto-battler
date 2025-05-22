extends Node
class_name DiceUtils          # lets the editor recognise it everywhere

static func roll_dice(num: int, sides: int) -> int:
	var total := 0
	for _i in range(num):
		total += randi() % sides + 1
	return total
