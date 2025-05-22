# res://scripts/GameController.gd
extends Node
# ----------------------------------------------------------
#  DUEL-PROTOTYPE  —  Wizard vs one Goblin
#  (no waves, no upgrades, no party array)
# ----------------------------------------------------------

const GRID_SIZE  := 64
const GRID_COLS  := 12
const GRID_ROWS  := 8

# back-end scripts
const Wizard  := preload("res://scripts/Wizard.gd")
const Enemy   := preload("res://scripts/Enemy.gd")
const Dice    := preload("res://scripts/DiceUtils.gd")
const GridPos := preload("res://scripts/GridPosition.gd")

# ----------------  runtime state  -------------------------
var wizard : Character
var goblin : Character
var player_turn : bool = true          # true = wizard’s turn
var actions_left : int = 3

# ----------------  signals for UI  ------------------------
signal log_entry(text: String)
signal unit_spawned(u: Character)
signal unit_moved(u: Character, gp: Vector2i)
signal hp_changed(u: Character)
signal mp_changed(u: Character, mp: int)
signal turn_started(active: Character)
signal duel_finished(victor_name: String)

# =====================  PUBLIC API  =======================
func start_duel() -> void:
    _reset_world()
    _spawn_units()
    emit_signal("turn_started", wizard)
    emit_signal("mp_changed", wizard, wizard.mp)

func handle_grid_click(world_pos: Vector2, button: int) -> void:
    if not player_turn: return              # ignore during Goblin AI
    var gp := _world_to_grid(world_pos)
    if button == MOUSE_BUTTON_LEFT:
        _try_stride(gp)

func cast_spell(spell_id: String, target_gp: Vector2i, cost: int) -> void:
    if not player_turn: return
    if actions_left < cost:
        _log("Not enough actions.")
        return
    var target := _grid_to_unit(target_gp) if target_gp else goblin
    match spell_id:
        "magic_missile": wizard.magic_missile(target, self, 1)
        "arcane_blast":  wizard.arcane_blast(target, self)
        _: _log("Unknown spell")
    actions_left -= cost
    emit_signal("mp_changed", wizard, wizard.mp)
    emit_signal("hp_changed", target)
    _check_end_of_turn()

func end_turn():                         # UI “End Turn” button
    if not player_turn: return
    actions_left = 0
    _check_end_of_turn()

# =====================  INTERNAL  =========================
func _reset_world():
    wizard = null
    goblin = null
    actions_left = 3
    player_turn = true

func _spawn_units():
    wizard = Wizard.new("Ezren")
    goblin = Enemy.new("Goblin", 20, 15, 5, [1,8])
    wizard.position = GridPos.new(2, GRID_ROWS-2)
    goblin.position = GridPos.new(GRID_COLS-3, 1)
    emit_signal("unit_spawned", wizard)
    emit_signal("unit_spawned", goblin)

func _try_stride(gp: Vector2i):
    if actions_left < 1: return
    if gp in wizard.get_valid_moves(self):
        wizard.move_to(GridPos.new(gp.x, gp.y), self)
        actions_left -= 1
        emit_signal("unit_moved", wizard, gp)
        _check_end_of_turn()

func _check_end_of_turn():
    if goblin.hp <= 0:
        _finish_duel(wizard.name)
        return
    if wizard.hp <= 0:
        _finish_duel(goblin.name)
        return

    if actions_left <= 0:
        player_turn = false
        _enemy_ai_turn()

func _enemy_ai_turn():
    # one action: move closer if not adjacent
    var dist := goblin.position.distance_to(wizard.position)
    if dist > 1:
        var moves := goblin.get_valid_moves(self)
        if moves.size() > 0:
            moves.sort_custom(func(a,b): return a.distance_to(wizard.position) < b.distance_to(wizard.position))
            goblin.move_to(moves[0], self)
            emit_signal("unit_moved", goblin, Vector2i(moves[0].x, moves[0].y))
    # second action: attack if adjacent
    dist = goblin.position.distance_to(wizard.position)
    if dist <= 1:
        goblin.attack(wizard, 1, 8)          # costs 1 action internally
        emit_signal("hp_changed", wizard)
    # end goblin turn
    if wizard.hp <= 0:
        _finish_duel(goblin.name)
        return
    player_turn = true
    actions_left = 3
    emit_signal("turn_started", wizard)
    emit_signal("ap_changed", wizard, actions_left)

func _finish_duel(victor: String):
    _log("%s wins the duel!" % victor)
    emit_signal("duel_finished", victor)

# -------------  helpers  ------------
func _log(t:String): emit_signal("log_entry", t)

func _world_to_grid(v:Vector2)->Vector2i:
    return Vector2i(int(v.x / GRID_SIZE), int(v.y / GRID_SIZE))

func _grid_to_unit(gp:Vector2i) -> Character:
    if wizard.position.x == gp.x and wizard.position.y == gp.y:
        return wizard
    if goblin.position.x == gp.x and goblin.position.y == gp.y:
        return goblin
    return null
