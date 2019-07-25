extends Node2D
const start_x = 150
const start_y = 200
# Called when the node enters the scene tree for the first time.
func _ready():
	# load characters into the character list.
	var count = 0
	for character in manager_connection.list_characters:
		var sprite = Sprite.new()
		sprite.texture = load("res://characters/" + character["tile_ident"] + ".png")
		.add_child(sprite)
		sprite.position.x = start_x + count*150
		sprite.position.y = start_y
		var _name = Label.new()
		_name.text = character["name"]
		.add_child(_name)
		_name.rect_position.x = start_x + count*150
		_name.rect_position.y = start_y+30
		count = count + 1