extends Control

func _ready():
	self.get_node("GridContainer/Move").connect("button_down", Callable(self, "move_pressed")) 

func move_pressed():
	get_parent().get_node("SuperMenu").is_open = false
	var calculated_move = Dictionary()
	calculated_move["ident"] = manager_connection.character_name
	calculated_move["command"] = "calculated_move"
	print(get_parent().clicked_tile)
	calculated_move["args"] = [get_parent().clicked_tile['position']['x'], get_parent().clicked_tile['position']['y'], 0] # TODO: set z 
	print("Move pressed for: ", calculated_move["args"])
	var to_send = JSON.stringify(calculated_move).to_utf8_buffer()
	manager_connection.client.put_data(to_send)
	self.visible = false