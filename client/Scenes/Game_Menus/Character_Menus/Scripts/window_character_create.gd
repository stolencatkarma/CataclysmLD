extends Node2D

var character_name = ""
func _ready():
	var _submit_character_button = Button.new()
	_submit_character_button.icon = load("res://Scenes/Game_Menus/Character_Menus/gfx/ui_button_submit.png")
	.add_child(_submit_character_button)
	_submit_character_button.set_position(Vector2(450,350))
	_submit_character_button.connect("button_up", self, "submit_character")


func submit_character():
	character_name = get_node("background_blank/txt_character_name").text
	var character_submit = Dictionary()
	character_submit["ident"] = manager_connection.username
	character_submit["command"] = "completed_character"
	character_submit["args"] = character_name
	manager_connection.character_name = character_name # fixes not having name on first login.
	var to_send = JSON.print(character_submit).to_utf8()
	manager_connection.client.put_data(to_send)
	get_tree().change_scene("res://Scenes/Game_Main/window_main.tscn")