extends Button

func _pressed():
	manager_connection.HOST = get_node("/root/Node2D/Menu_Margin/Menu_Container/server_container/ip-port_container/txt_IP").text
	manager_connection.PORT = get_node("/root/Node2D/Menu_Margin/Menu_Container/server_container/ip-port_container/txt_PORT").text
	manager_connection.username = get_node("/root/Node2D/Menu_Margin/Menu_Container/name_container/txt_username").text
	manager_connection.password = get_node("/root/Node2D/Menu_Margin/Menu_Container/password_container/txt_password").text
	manager_connection.connect_to_server()
