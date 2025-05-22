extends CharacterBody2D
class_name Player

# Movement properties
@export var speed: float = 200.0
@export var tile_size: int = 64  # Should match your TileMap's cell size

# Player state
var in_combat: bool = false
var can_move: bool = true
var current_tile: Vector2i

# References
@onready var tilemap = get_node("/root/Main/TileMap")  # Adjust path to your TileMap

# Signal for position changes
signal position_changed(new_position: Vector2)
signal tile_changed(new_tile: Vector2i)

# Called when the node enters the scene tree
func _ready():
    # Add to player group for easy access
    add_to_group("players")
    
    # Initialize current tile
    if tilemap:
        current_tile = tilemap.local_to_map(position)

# Called every frame
func _process(_delta):
    if not is_multiplayer_authority() or not can_move or in_combat:
        return
        
    # Get input direction
    var direction = Vector2.ZERO
    direction.x = Input.get_axis("ui_left", "ui_right")
    direction.y = Input.get_axis("ui_up", "ui_down")
    direction = direction.normalized()
    
    # Set velocity
    if direction != Vector2.ZERO:
        velocity = direction * speed
    else:
        velocity = Vector2.ZERO
    
    # Move and snap to tile
    move_and_slide()
    _snap_to_tile()
    
    # Update current tile
    if tilemap:
        var new_tile = tilemap.local_to_map(position)
        if new_tile != current_tile:
            current_tile = new_tile
            emit_signal("tile_changed", current_tile)
    
    # Emit position changed signal
    emit_signal("position_changed", position)

# Snap position to tile
func _snap_to_tile():
    if not tilemap:
        return
        
    var map_pos = tilemap.local_to_map(position)
    var world_pos = tilemap.map_to_local(map_pos)
    position = world_pos

# Get current tile position
func get_tile_position() -> Vector2i:
    if tilemap:
        return tilemap.local_to_map(position)
    return Vector2i.ZERO

# Set position from tile coordinates
func set_tile_position(tile_pos: Vector2i):
    if tilemap:
        position = tilemap.map_to_local(tile_pos)
        current_tile = tile_pos
        emit_signal("position_changed", position)
        emit_signal("tile_changed", current_tile)

# Enter combat mode
func enter_combat():
    in_combat = true
    can_move = false
    velocity = Vector2.ZERO

# Exit combat mode
func exit_combat():
    in_combat = false
    can_move = true

# Check if a tile is walkable
func is_tile_walkable(tile_pos: Vector2i) -> bool:
    if not tilemap:
        return false
        
    # Get the tile data at the position
    var tile_data = tilemap.get_cell_tile_data(0, tile_pos)
    if not tile_data:
        return false
        
    # Check if the tile has the "walkable" custom data layer
    # You'll need to set this up in your TileSet
    return tile_data.get_custom_data("walkable") 