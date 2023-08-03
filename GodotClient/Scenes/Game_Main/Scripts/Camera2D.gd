extends Camera2D

var zoom_step = 1.1
var min_zoom = 0.5
var max_zoom = 2.0
var pan_speed = 800
var mouse_captured = false
## Rectangle used to limit camera panning.
## Note that the built in camera limits do not work: they don't actually constrain the position of the camera.
## They only stop the view from moving. For the user, this makes the camera appear to "stick" at the edges of the map, 
## which is bad.
var limit_rect = null setget set_limit_rect
var move_request = Dictionary()

func _input(event):
	
	if Input.is_action_just_released("ui_left"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["west"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if Input.is_action_just_released("ui_right"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["east"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if Input.is_action_just_released("ui_down"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["south"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if Input.is_action_just_released("ui_up"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["north"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if Input.is_action_just_released("ui_ascend"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["up"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if Input.is_action_just_released("ui_decend"):
		move_request["ident"] = manager_connection.username
		move_request["command"] = "move"
		move_request["args"] = ["down"]
		var to_send = JSON.print(move_request).to_utf8()
		manager_connection.client.put_data(to_send)
		manager_connection.request_localmap()
		
	if event.is_action_pressed("view_pan_mouse"):
		mouse_captured = true
	elif event.is_action_released("view_pan_mouse"):
		mouse_captured = false
	if mouse_captured && event is InputEventMouseMotion:
		position -= event.relative * zoom #like we're grabbing the map
	if event is InputEventMouse:
		if event.is_pressed() and not event.is_echo():
			var mouse_position = event.position
			if event.button_index == BUTTON_WHEEL_DOWN:
				if zoom < Vector2( max_zoom, max_zoom ):
					zoom_at_point(zoom_step,mouse_position)
					_snap_zoom_limits()
			elif event.button_index == BUTTON_WHEEL_UP:
				if zoom > Vector2( min_zoom, min_zoom ):
					zoom_at_point(1/zoom_step,mouse_position)
					_snap_zoom_limits()
	if event.is_action_pressed("zoom_in"):
		zoom /= zoom_step
		_snap_zoom_limits()
	if event.is_action_pressed("zoom_out"):
		zoom *= zoom_step
		_snap_zoom_limits()
	

	
func zoom_at_point(zoom_change, point):
	var c0 = global_position # camera position
	var v0 = get_viewport().size # viewport size
	var c1 # next camera position
	var z0 = zoom # current zoom value
	var z1 = z0 * zoom_change # next zoom value

	c1 = c0 + (-0.5*v0 + point)*(z0 - z1)
	zoom = z1
	global_position = c1

# force position to be inside limit_rect
func _snap_to_limits():
	position.x = clamp(position.x, limit_rect.position.x, limit_rect.end.x)
	position.y = clamp(position.y, limit_rect.position.y, limit_rect.end.y)

func _snap_zoom_limits():
	zoom.x = clamp(zoom.x, min_zoom, max_zoom)
	zoom.y = clamp(zoom.y, min_zoom, max_zoom)

func set_limit_rect(rect):
	limit_rect = rect
	_snap_to_limits()
