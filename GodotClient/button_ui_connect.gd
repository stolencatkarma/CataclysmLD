extends Button

func _pressed():
	manager_connection.connect_to_server()
