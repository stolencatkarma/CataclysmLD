extends Node

var HOST = "127.0.0.1"
var PORT = 6317
var client = StreamPeerTCP.new()
var username = "q"
var password = "q"
var list_characters = Array()
var localmap_chunks = Array()

func connect_to_server():
	client.connect_to_host(HOST, PORT)
	var login_request = Dictionary()
	login_request["ident"] = username
	login_request["command"] = "login"
	login_request["args"] = password
	var to_send = JSON.print(login_request).to_utf8()
	client.put_data(to_send)

func _process(delta): # where we check for new data recieved from server.
	if client.is_connected_to_host() and client.get_available_bytes() > 0:
		var _recieved_string = ""
		while client.get_available_bytes() > 0:
			print("available bytes: " + str(client.get_available_bytes()))
			var _recieved_data = client.get_data(client.get_available_bytes())
			_recieved_string = _recieved_string + _recieved_data[1].get_string_from_utf8()
			# print("Received: " + _recieved_string)
		
		var _parsed = JSON.parse(_recieved_string) # parse container.
		var _parsed2 = JSON.parse(_parsed.result) # parse data
		
		var _result = _parsed2.result
		for k in _result.keys():
			# print(k)
			if k == "login":
				if _result[k] == "Accepted":
					print("logged in.") # login was successfully accepted.
					# request character list
					var characters_request = Dictionary()
					characters_request["ident"] = username
					characters_request["command"] = "request_character_list"
					characters_request["args"] = "[]"
					var to_send = JSON.print(characters_request).to_utf8()
					client.put_data(to_send)
			if k == "character_list":
				print(typeof(_result[k])) # _result[k] is an json array of characters.
				for character in _result[k]:
					character = parse_json(character) # convert character json string to dictionary.
					print(character["name"] + " found.")
					list_characters.append(character)
				get_tree().change_scene("res://window_character_select.tscn")
			if k == "localmap":
				manager_connection.localmap_chunks.clear()
				for chunk in _result[k]:
					manager_connection.localmap_chunks.append(chunk)
				get_tree().change_scene("res://window_main.tscn")
		