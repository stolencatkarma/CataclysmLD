extends Node

var HOST = "127.0.0.1"
var PORT = 6317
var client = StreamPeerTCP.new()
var username = "q"
var password = "q"
var list_characters = Array()
var localmap_chunks = Array()
var should_update_localmap = false
var should_update_inventory = false
var character_name = null # this is set when a created character is chosen.
var controlled_character = null # as dictionary data for updating the Interface (stats, injuries, etc)

func connect_to_server():
	client.connect_to_host(str(HOST), int(PORT))
	var login_request = Dictionary()
	login_request["ident"] = username
	login_request["command"] = "login"
	login_request["args"] = password
	var to_send = JSON.stringify(login_request).to_utf8_buffer()
	client.put_data(to_send)

func _process(delta): # where we check for new data recieved from server.
	if client.get_status() == 2 and client.get_available_bytes() > 0:
		var _recieved_string = ""
		while client.get_available_bytes() > 0: # must be taken 64kb at a time so this loop is required
			# print("available bytes: " + str(client.get_available_bytes()))
			var _recieved_data = client.get_data(client.get_available_bytes())
			_recieved_string = _recieved_string + _recieved_data[1].get_string_from_utf8()
			# print("Received: " + _recieved_string)
		
		var test_json_conv = JSON.new()
		test_json_conv.parse(_recieved_string) # parse container.
		var _parsed = test_json_conv.get_data()
		# var test_json_conv = JSON.new()
		test_json_conv.parse(_parsed.result) # parse data
		var _parsed2 = test_json_conv.get_data()
		
		var _result = _parsed2.result
		for k in _result.keys():
			# the 'header' of the data recieved.
			if k == "login":
				if _result[k] == "Accepted":
					print("logged in.") # login was successfully accepted.
					# request character list
					var characters_request = Dictionary()
					characters_request["ident"] = username
					characters_request["command"] = "request_character_list"
					characters_request["args"] = "[]"
					var to_send = JSON.stringify(characters_request).to_utf8_buffer()
					client.put_data(to_send)
			if k == "character_list":
				# print(typeof(_result[k])) # _result[k] is an json array of characters.
				for character in _result[k]:
					# var test_json_conv = JSON.new()
					test_json_conv.parse(character) # convert character json string to dictionary.
					character = test_json_conv.get_data()
					# print(character["name"] + " found.")
					list_characters.append(character)
				get_tree().change_scene_to_file("res://Scenes/Game_Menus/Character_Menus/window_character_select.tscn")
			if k == "localmap":
				manager_connection.localmap_chunks.clear()
				for chunk in _result[k]:
					manager_connection.localmap_chunks.append(chunk)
				manager_connection.should_update_localmap = true
				get_tree().change_scene_to_file("res://Scenes/Game_Main/window_main.tscn")
			if k == "localmap_update":
				manager_connection.localmap_chunks.clear()
				for chunk in _result[k]:
					manager_connection.localmap_chunks.append(chunk)
				manager_connection.should_update_localmap = true
				manager_connection.should_update_inventory = true
