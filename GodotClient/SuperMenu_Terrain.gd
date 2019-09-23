extends Control

func _ready():
	self.get_node("GridContainer/Move").connect("button_down", self, "move_pressed") 

func move_pressed():
	self.visible = false
	get_parent().get_node("SuperMenu").is_open = false
	var calulated_move = Dictionary()
	calulated_move["ident"] = manager_connection.character_name
	calulated_move["command"] = "calculated_move"
	print(get_parent().clicked_tile)
	calulated_move["args"] = [get_parent().clicked_tile['position']['x'], get_parent().clicked_tile['position']['y'], 0] # TODO: set z 
	print("Tile clicked at: ", calulated_move["args"])
	var to_send = JSON.print(calulated_move).to_utf8()
	manager_connection.client.put_data(to_send)