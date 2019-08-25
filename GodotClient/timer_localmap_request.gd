extends Timer
func _ready():
	self.connect("timeout", self, "_on_Timer_timeout")

func _on_Timer_timeout():
	var request_localmap_update = Dictionary()
	request_localmap_update["ident"] = manager_connection.username
	request_localmap_update["command"] = "request_localmap_update"
	request_localmap_update["args"] = manager_connection.character_name
	var to_send = JSON.print(request_localmap_update).to_utf8()
	manager_connection.client.put_data(to_send)