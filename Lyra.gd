
extends Node2D

# === CONFIG ===
const MOODS = ["cheerful", "grumpy", "mischievous", "sleepy", "excited", "flustered"]
const HIDDEN_PROMPTS = [
    "Do you ever wonder what’s beyond the edge of the screen?",
    "Want to see a trick?",
    "Talk about whatever"
]
const LYRABANTER = {
    "cheerful": ["Sparkles make everything better!", "Oh! Let’s play a game!"],
    "grumpy": ["Watch it, owl!", "Not in the mood for clanks."],
    "mischievous": ["Oops, did I bump you?", "Catch me if you can!"],
    "sleepy": ["Mmm… nap time…", "Too… tired… to sparkle…"],
    "excited": ["Whee! Look at me go!", "Magic overload!"],
    "flustered": ["Oh! My skirt!", "I… um… wasn’t ready!"]
}

# === NODES ===
@onready var lyra = $Lyra
@onready var sparkle_trail = preload("res://SparkleTrail.tscn")
@onready var bonk_sfx = preload("res://sounds/bonk.wav")
@onready var splat_sfx = preload("res://sounds/splat.wav")
@onready var gift_explosion = preload("res://particles/gift_explosion.tscn")

# === STATE ===
var lyra_mood = "cheerful"
var lyra_mood_timer = 0.0
var lyra_prompt_timer = 0.0
var birthday_today = false

func _ready():
    randomize()
    _check_birthday()
    _reset_mood()
    _reset_prompt()

func _process(delta):
    _update_lyra(delta)
    _update_moods(delta)
    _update_prompts(delta)

# === CONTROL ===
func _update_lyra(delta):
    lyra.position = get_viewport().get_mouse_position()
    _face_direction(lyra, get_viewport().get_mouse_position() - lyra.position)
    _spawn_sparkle(lyra.position)

# === COLLISION (simplified for Lyra only) ===
func _on_bonk_lyra():
    bonk_sfx.play()
    print("Lyra:", LYRABANTER[lyra_mood][randi() % LYRABANTER[lyra_mood].size()])
    _knock_out(lyra)

func _knock_out(char):
    char.modulate = Color(1, 1, 1, 0.5)
    await get_tree().create_timer(2.0).timeout
    char.modulate = Color(1, 1, 1, 1)

# === MOODS ===
func _update_moods(delta):
    lyra_mood_timer -= delta
    if lyra_mood_timer <= 0: _reset_mood()

func _reset_mood():
    lyra_mood = MOODS[randi() % MOODS.size()]
    lyra_mood_timer = rand_range(20, 60)

# === PROMPTS ===
func _update_prompts(delta):
    lyra_prompt_timer -= delta
    if lyra_prompt_timer <= 0:
        if randf() < 0.08: _hidden_prompt()
        _reset_prompt()

func _reset_prompt():
    lyra_prompt_timer = rand_range(15, 45)

func _hidden_prompt():
    var prompt = HIDDEN_PROMPTS[randi() % HIDDEN_PROMPTS.size()]
    if prompt == "Talk about whatever":
        print("Lyra:", LYRABANTER[lyra_mood][randi() % LYRABANTER[lyra_mood].size()])
    else:
        print("Lyra:", prompt)

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
    p.global_position = lyra.position
    bonk_sfx.play()

func _pie_in_face():
    splat_sfx.play()
    print("Pie in the face for Lyra!")
    _knock_out(lyra)

# === HELPERS ===
func _face_direction(node, dir):
    node.scale.x = -1 if dir.x < 0 else 1

func _spawn_sparkle(pos):
    var s = sparkle_trail.instantiate()
    add_child(s)
    s.global_position = pos


