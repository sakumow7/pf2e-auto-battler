extends CharacterBody2D
class_name ExplorationEnemy

# Enemy properties
@export var enemy_type: String = "goblin"
@export var hp: int = 20
@export var ac: int = 15
@export var attack_bonus: int = 5
@export var damage_dice: Array[int] = [1, 8]

# Movement properties
@export var patrol_speed: float = 50.0
@export var patrol_points: Array[Vector2i] = []  # Changed to Vector2i for tile coordinates
@export var wait_time: float = 2.0
@export var detection_radius: float = 150.0  # How far the enemy can see the player

# State variables
var current_patrol_index: int = 0
var wait_timer: float = 0.0
var is_waiting: bool = false
var is_alive: bool = true
var is_alerted: bool = false
var player_last_seen: Vector2
var current_tile: Vector2i

# References
@onready var tilemap = get_node("/root/Main/TileMap")  # Adjust path to your TileMap

# Reference to combat enemy
var combat_enemy: Enemy

# Called when the node enters the scene tree
func _ready():
    # Add to enemies group for easy access
    add_to_group("enemies")
    
    # Create combat enemy instance
    combat_enemy = Enemy.new(enemy_type, hp, ac, attack_bonus, damage_dice)
    
    # Initialize current tile
    if tilemap:
        current_tile = tilemap.local_to_map(position)
    
    # If no patrol points set, use current position
    if patrol_points.size() == 0 and tilemap:
        patrol_points.append(current_tile)

# Called every frame
func _process(delta):
    if not is_alive:
        return
    
    # Update current tile
    if tilemap:
        current_tile = tilemap.local_to_map(position)
    
    # Check if player is in detection range
    var player = get_tree().get_first_node_in_group("players")
    if player and is_alive:
        var distance_to_player = position.distance_to(player.position)
        
        # If player is in detection range, become alerted
        if distance_to_player <= detection_radius:
            is_alerted = true
            player_last_seen = player.position
            
            # If player is very close, stop and face them
            if distance_to_player <= 50.0:
                velocity = Vector2.ZERO
                look_at(player.position)
                return
    
    # If not alerted, continue patrol
    if not is_alerted:
        _patrol(delta)
    else:
        # If alerted but player is out of range, return to patrol
        if not player or position.distance_to(player.position) > detection_radius * 1.5:
            is_alerted = false
            _patrol(delta)

# Handle patrol behavior
func _patrol(delta):
    if is_waiting:
        wait_timer -= delta
        if wait_timer <= 0:
            is_waiting = false
            current_patrol_index = (current_patrol_index + 1) % patrol_points.size()
    else:
        if tilemap and patrol_points.size() > 0:
            var target_tile = patrol_points[current_patrol_index]
            var target_pos = tilemap.map_to_local(target_tile)
            var direction = (target_pos - position).normalized()
            
            if position.distance_to(target_pos) < 5.0:
                is_waiting = true
                wait_timer = wait_time
            else:
                velocity = direction * patrol_speed
                move_and_slide()
                _snap_to_tile()

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

# Check if a tile is walkable
func is_tile_walkable(tile_pos: Vector2i) -> bool:
    if not tilemap:
        return false
        
    # Get the tile data at the position
    var tile_data = tilemap.get_cell_tile_data(0, tile_pos)
    if not tile_data:
        return false
        
    # Check if the tile has the "walkable" custom data layer
    return tile_data.get_custom_data("walkable")

# Called when enemy is defeated in combat
func on_defeated():
    is_alive = false
    queue_free()

# Get the combat enemy instance
func get_combat_enemy() -> Enemy:
    return combat_enemy 