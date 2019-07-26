extends Button

func _pressed():
	manager_connection.HOST = get_parent().get_node("txt_IP").text
	manager_connection.PORT = get_parent().get_node("txt_PORT").text
	manager_connection.username = get_parent().get_node("txt_username").text
	manager_connection.password = get_parent().get_node("txt_password").text
	manager_connection.connect_to_server()
