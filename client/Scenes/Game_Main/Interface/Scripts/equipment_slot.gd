extends Node2D

# stores the item that was parsed from the character.
onready var contained = Dictionary()

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button.connect("button_up", self, "slot_clicked")

func slot_clicked():
	# if this contains a item it will have an 'ident'
	if 'ident' in contained:
		print('clicked ' + contained['ident'])
		
		# this is a container
		if 'opened' in contained:
			print('opened: ' + contained['opened'])
			for item in contained['contained_items']:
				# create a button for each contained item.
				var _button = Button.new()
				var size = Vector2(32, 32)
				$contained_items.add_child(_button)
				_button.rect_size = size
				_button.set_position(Vector2(startx, starty))
