
extends Node2D

# === CONFIG ===
const MOODS = ["cheerful", "grumpy", "mischievous", "sleepy", "excited", "flustered"]
const HIDDEN_PROMPTS = [
    "Do you ever wonder what’s beyond the edge of the screen?",
    "Want to see a trick?",
    "Talk about whatever"
]
const ARCHBANTER = {
    "cheerful": ["Affirmative. Systems optimal.", "Nice flying, Lyra."],
    "grumpy": ["Your trajectory is inefficient.", "Clank off."],
    "mischievous": ["Target acquired.", "Dive‑bomb successful."],
    "sleepy": ["Low power mode…", "Wake me later…"],
    "excited": ["Boosting thrusters!", "Overclock engaged!"],
    "flustered": ["Servo… jammed…", "Not looking at you."]
}

# === NODES ===
@onready var arch = $Archimedes
@onready var bonk_sfx = preload("res://sounds/bonk.wav")
@onready var splat_sfx = preload("res://sounds/splat.wav")
@onready var gift_explosion = preload("res://particles/gift_explosion.tscn")

# === STATE ===
var arch_mood = "cheerful"
var arch_mood_timer = 0.0
var arch_prompt_timer = 0.0
var birthday_today = false

func _ready():
    randomize()
    _check_birthday()
    _reset_mood()
    _reset_prompt()

func _process(delta):
    _update_arch(delta)
    _update_moods(delta)
    _update_prompts(delta)

# === CONTROL ===
func _update_arch(delta):
    # Simple wandering AI with clumsy overshoot
    var target = Vector2(rand_range(0, 1024), rand_range(0, 768))
    arch.position = arch.position.move_toward(target, delta * (100 + randf() * 50))
    _face_direction(arch, target - arch.position)

# === COLLISION (simplified for Archimedes only) ===
func _on_bonk_arch():
    bonk_sfx.play()
    print("Archimedes:", ARCHBANTER[arch_mood][randi() % ARCHBANTER[arch_mood].size()])
    _knock_out(arch)

func _knock_out(char):
    char.modulate = Color(1, 1, 1, 0.5)
    await get_tree().create_timer(2.0).timeout
    char.modulate = Color(1, 1, 1, 1)

# === MOODS ===
func _update_moods(delta):
    arch_mood_timer -= delta
    if arch_mood_timer <= 0: _reset_mood()

func _reset_mood():
    arch_mood = MOODS[randi() % MOODS.size()]
    arch_mood_timer = rand_range(20, 60)

# === PROMPTS ===
func _update_prompts(delta):
    arch_prompt_timer -= delta
    if arch_prompt_timer <= 0:
        if randf() < 0.08: _hidden_prompt()
        _reset_prompt()

func _reset_prompt():
    arch_prompt_timer = rand_range(15, 45)

func _hidden_prompt():
    var prompt = HIDDEN_PROMPTS[randi() % HIDDEN_PROMPTS.size()]
    if prompt == "Talk about whatever":
        print("Archimedes:", ARCHBANTER[arch_mood][randi() % ARCHBANTER[arch_mood].size()])
    else:
        print("Archimedes:", prompt)

# === BIRTHDAY EVENTS ===
func _check_birthday():
    var today = Time.get_date_dict_from_system()
    # Replace with actual birthday check
    if today["month"] == 9 and today["day"] == 16:
        birthday_today = true
        _birthday_event()

func _birthday_event():
    if randi() % 2 == 0:
        _gift_explosion()
    else:
        _pie_in_face()

func _gift_explosion():
    var p = gift_explosion.instantiate()
    add_child(p)
    p.global_position = arch.position
    bonk_sfx.play()

func _pie_in_face():
    splat_sfx.play()
    print("Pie in the face for Archimedes!")
    _knock_out(arch)

# === HELPERS ===
func _face_direction(node, dir):
    node.scale.x = -1 if dir.x < 0 else 1


