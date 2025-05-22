extends Node
class_name EncounterManager

# Signals for state changes
signal encounter_started(enemy: Character)
signal encounter_ended(victor: String)
signal exploration_mode_entered()
signal transition_to_combat()  # New signal for UI transition

# References to other nodes
@onready var game_controller = get_node("/root/GameController")
@onready var player = get_node("/root/Player")
@onready var tilemap = get_node("/root/Main/TileMap")  # Adjust path to your TileMap

# State variables
var in_combat: bool = false
var current_enemy: Character = null
var encounter_radius: float = 100.0  # Distance at which encounter triggers
var player_exploration_pos: Vector2  # Store player position before combat
var player_exploration_tile: Vector2i  # Store player tile before combat

# Called when the node enters the scene tree
func _ready():
    # Connect to player movement signals
    if player:
        player.connect("position_changed", Callable(self, "_on_player_moved"))
        player.connect("tile_changed", Callable(self, "_on_player_tile_changed"))
    
    # Start in exploration mode
    emit_signal("exploration_mode_entered")

# Called every frame
func _process(_delta):
    if not in_combat and player:
        _check_for_encounters()

# Check if player is near any enemies
func _check_for_encounters():
    var enemies = get_tree().get_nodes_in_group("enemies")
    for enemy in enemies:
        if enemy.is_alive() and _is_in_encounter_range(player, enemy):
            _start_encounter(enemy)
            break

# Check if player is within encounter range of an enemy
func _is_in_encounter_range(player, enemy) -> bool:
    var distance = player.position.distance_to(enemy.position)
    return distance <= encounter_radius

# Start a combat encounter
func _start_encounter(enemy: Character):
    in_combat = true
    current_enemy = enemy
    
    # Save player's exploration position and tile
    player_exploration_pos = player.position
    if tilemap:
        player_exploration_tile = tilemap.local_to_map(player_exploration_pos)
    
    # Signal UI to start transition animation
    emit_signal("transition_to_combat")
    
    # Wait a short time for transition animation
    await get_tree().create_timer(1.0).timeout
    
    # Transition to combat mode
    emit_signal("encounter_started", enemy)
    
    # Initialize combat grid
    game_controller.start_duel()
    
    # Connect to combat end signal
    game_controller.connect("duel_finished", Callable(self, "_on_combat_ended"))

# End combat and return to exploration
func _end_encounter(victor: String):
    in_combat = false
    current_enemy = null
    
    # Clean up combat state
    game_controller.disconnect("duel_finished", Callable(self, "_on_combat_ended"))
    
    # Return player to exploration position
    if player:
        player.position = player_exploration_pos
        if tilemap:
            player.set_tile_position(player_exploration_tile)
    
    # Return to exploration mode
    emit_signal("exploration_mode_entered")
    emit_signal("encounter_ended", victor)

# Handle combat end
func _on_combat_ended(victor: String):
    _end_encounter(victor)

# Handle player movement during exploration
func _on_player_moved(new_position: Vector2):
    if not in_combat:
        _check_for_encounters()

# Handle player tile changes during exploration
func _on_player_tile_changed(new_tile: Vector2i):
    if not in_combat:
        _check_for_encounters() 