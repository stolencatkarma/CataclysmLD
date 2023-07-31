extends Node2D

# stores the item that was parsed from the character.
@onready var contained = Dictionary()

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button.connect("button_up", Callable(self, "slot_clicked"))

func slot_clicked():
	# if this contains a item it will have an 'ident'
	if 'ident' in contained:
		print('clicked ' + contained['ident'])
