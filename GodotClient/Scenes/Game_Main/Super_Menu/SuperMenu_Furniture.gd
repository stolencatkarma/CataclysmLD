extends Control

func _ready():
	self.get_node("GridContainer/Bash").connect("button_down", Callable(self, "bash_pressed")) 

func bash_pressed():
	self.visible = false
	get_parent().get_node("SuperMenu").is_open = false
	var bash = Dictionary()
	bash["ident"] = manager_connection.character_name
	bash["command"] = "bash"
	# print(get_parent().clicked_tile)
	bash["args"] = [get_parent().clicked_tile['position']['x'], get_parent().clicked_tile['position']['y'], 0] # TODO: set z 
	print("Tile clicked at: ", bash["args"])
	var to_send = JSON.stringify(bash).to_utf8_buffer()
	manager_connection.client.put_data(to_send)