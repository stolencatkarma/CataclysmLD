extends Node

var HOST = "127.0.0.1"
var PORT = 6317
var client = StreamPeerTCP.new()
var username = "q"
var password = "q"
var localmap_chunks = Array()
var should_update_localmap = false
var should_update_inventory = false
var character_name = null # this is set when a created character is chosen.
var controlled_character = null # as dictionary data for updating the Interface (stats, injuries, etc)
var list_characters

func connect_to_server():
	client.connect_to_host(str(HOST), int(PORT))
	var login_request = Dictionary()
	login_request["ident"] = username
	login_request["command"] = "request_login"
	login_request["args"] = password
	var to_send = JSON.print(login_request).to_utf8()
	client.put_data(to_send)

func _process(delta): # where we check for new data recieved from server.
	if client.is_connected_to_host() and client.get_available_bytes() > 0:
		var recieved_string = ""
		while client.get_available_bytes() > 0: # must be taken 64kb at a time so this loop is required
			var recieved_data = client.get_data(client.get_available_bytes())
			recieved_string = recieved_string + recieved_data[1].get_string_from_utf8()
		
		var parsed_container = JSON.parse(recieved_string)
		var parsed_data = JSON.parse(parsed_container.result)
		
		var result = parsed_data.result
		# the 'header' of the data recieved.
		var response_name = result["name"]
		if result["status"] != "SUCCESS":
			# TODO: Pass a failure message to render here, along with any necessary state transitions.
			# example: localmap_update fails because the player was disconnected from the server -> go back to login screen
			# and render the appropriate failure prompt.
			return
		match response_name:
			"login":
				print("logged in.") # login was successfully accepted.
				# request character list
				var characters_request = Dictionary()
				characters_request["ident"] = username
				characters_request["command"] = "request_character_list"
				characters_request["args"] = "[]"
				var to_send = JSON.print(characters_request).to_utf8()
				client.put_data(to_send)
			"character_list":
				list_characters = Array()
				for character in result["args"]['characters']:
					character = parse_json(character) # convert character json string to dictionary.
					list_characters.append(character)
				#window_ch
				get_tree().change_scene("res://Scenes/Game_Menus/Character_Menus/window_character_select.tscn")
			"completed_character":
				var characters_request = Dictionary()
				characters_request["ident"] = username
				characters_request["command"] = "request_character_list"
				characters_request["args"] = "[]"
				var to_send = JSON.print(characters_request).to_utf8()
				client.put_data(to_send)
			"choose_character":
				controlled_character = result["args"]["character"]
				get_tree().change_scene("res://Scenes/Game_Main/window_main.tscn")
			"localmap_update":
				manager_connection.localmap_chunks.clear()
				for chunk in result["args"]["localmap"]:
					manager_connection.localmap_chunks.append(chunk)
				manager_connection.should_update_localmap = true
				manager_connection.should_update_inventory = true
			_:
				print("Received invalid response from server: " + response_name)
