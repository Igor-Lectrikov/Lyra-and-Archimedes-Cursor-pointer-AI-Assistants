
extends Node2D

@onready var lyra_instance = preload("res://Lyra.gd").instantiate()
@onready var arch_instance = preload("res://Archimedes.gd").instantiate()

func _ready():
    add_child(lyra_instance)
    add_child(arch_instance)

func _process(delta):
    # The individual scripts handle their own _process logic
    pass


