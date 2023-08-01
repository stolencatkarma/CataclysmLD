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
var controlled_character = null # a dictionary for updating the Interface (stats, injuries, etc)

func connect_to_server():
	print('connecting to server ' + HOST)
	client.set_no_delay(true)
	client.connect_to_host(str(HOST), int(PORT))
	var login_request = Dictionary()
	login_request["ident"] = username
	login_request["command"] = "login"
	login_request["args"] = password
	#print(login_request)
	var to_send = JSON.print(login_request).to_utf8()
	client.put_data(to_send)
	

func request_localmap():
	var _request = Dictionary()
	_request["ident"] = manager_connection.username
	_request["command"] = "request_localmap"
	_request["args"] = []
	var to_send = JSON.print(_request).to_utf8()
	manager_connection.client.put_data(to_send)
	print('sent localmap request')

func _process(delta): # where we check for new data recieved from server.
	if client.is_connected_to_host() and client.get_available_bytes() > 0:
		var _recieved_string = ""
		while client.get_available_bytes() > 0: # must be taken 64kb at a time so this loop is required
			# print("available bytes: " + str(client.get_available_bytes()))
			var _recieved_data = client.get_data(client.get_available_bytes())
			_recieved_string = _recieved_string + _recieved_data[1].get_string_from_utf8()
			# print("Received: " + _recieved_string)
		
		var _command = JSON.parse(_recieved_string).result # parse ident, command, args
		#print("RECIEVED: " + str(_command))
		
		if _command['command'] == "login":
			if _command['args'] == "accepted":
				print("logged in.") # login was successfully accepted.
				# request character list
				var _request = Dictionary()
				_request["ident"] = username
				_request["command"] = "request_character_list"
				_request["args"] = "[]"
				var to_send = JSON.print(_request).to_utf8()
				client.put_data(to_send)

		if _command['command'] == "character_list":
			# print(typeof(_result[k])) # _result[k] is an json array of characters.
			for character in _command['args']:
				character = parse_json(character) # convert character json string to dictionary.
				# print(character["name"] + " found.")
				list_characters.append(character)
			get_tree().change_scene("res://Scenes/Game_Menus/Character_Menus/window_character_select.tscn")

		if _command['command'] == "enter_game":
			manager_connection.request_localmap()
			manager_connection.should_update_localmap = true
			get_tree().change_scene("res://Scenes/Game_Main/window_main.tscn")

		if _command['command'] == "localmap_update": # the full localmap for the character.
			manager_connection.localmap_chunks.clear()
			for chunk in _command['args']:
				# print('added chunk to localmap update.')
				manager_connection.localmap_chunks.append(chunk)
			manager_connection.should_update_localmap = true
			manager_connection.should_update_inventory = true
			print('recieved a new localmap')
			return
		
