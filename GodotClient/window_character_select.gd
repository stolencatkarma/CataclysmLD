extends Node2D
const start_x = 150
const start_y = 200
# Called when the node enters the scene tree for the first time.
func _ready():
	# load characters into the character list.
	var count = 2 # 3 characters max, either shows a character or a button to create one.
	for character in manager_connection.list_characters:
		# create button for each character
		var _character_button = Button.new()
		_character_button.icon = load("res://characters/" + character["tile_ident"] + ".png")
		_character_button.text = character["name"]
		.add_child(_character_button)
		_character_button.set_position(Vector2(start_x+150*count,start_y))
		_character_button.connect("button_down", self, "button_pressed"+str(count))
		count = count - 1
	while count > -1:
		var _create_new_character_button = Button.new()
		_create_new_character_button.icon = load("res://ui_button_create.png")
		.add_child(_create_new_character_button)
		_create_new_character_button.set_position(Vector2(start_x+150*count,start_y))
		_create_new_character_button.connect("button_down", self, "create_new_character_pressed")
		count = count - 1

func button_pressed0():
	print("pressed " + manager_connection.list_characters[2]['name'])
	var characters_select = Dictionary()
	characters_select["ident"] = manager_connection.username
	characters_select["command"] = "choose_character"
	characters_select["args"] = manager_connection.list_characters[2]['name']
	var to_send = JSON.print(characters_select).to_utf8()
	manager_connection.client.put_data(to_send)

func button_pressed1():
	print("pressed " + manager_connection.list_characters[1]['name'])
	var characters_select = Dictionary()
	characters_select["ident"] = manager_connection.username
	characters_select["command"] = "choose_character"
	characters_select["args"] = manager_connection.list_characters[1]['name']
	var to_send = JSON.print(characters_select).to_utf8()
	manager_connection.client.put_data(to_send)
	
func button_pressed2():
	print("pressed " + manager_connection.list_characters[0]['name'])
	var characters_select = Dictionary()
	characters_select["ident"] = manager_connection.username
	characters_select["command"] = "choose_character"
	characters_select["args"] = manager_connection.list_characters[0]['name']
	var to_send = JSON.print(characters_select).to_utf8()
	manager_connection.client.put_data(to_send)
	
func create_new_character_pressed():
	get_tree().change_scene("res://window_character_create.tscn")