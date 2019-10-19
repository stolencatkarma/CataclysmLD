extends Button

func _pressed():
	manager_connection.HOST = get_parent().get_parent().get_node("server_container/ip-port_container/txt_IP").text
	manager_connection.PORT = get_parent().get_parent().get_node("server_container/ip-port_container/txt_PORT").text
	manager_connection.username = get_parent().get_parent().get_node("name_container/txt_username").text
	manager_connection.password = get_parent().get_parent().get_node("password_container/txt_password").text
	manager_connection.connect_to_server()
