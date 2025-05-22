# GridPosition.gd
class_name GridPosition
extends Resource

var x: int
var y: int

func _init(_x: int, _y: int):
	x = _x
	y = _y

func distance_to(other: GridPosition) -> int:
	return max(abs(x - other.x), abs(y - other.y))
