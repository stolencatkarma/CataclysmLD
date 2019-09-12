extends Node2D

var highlighted_coord = Vector2()
onready var tilemap_cell_size = Vector2( 32, 32 )
onready var color = Color(1.0, 0.5, 0.0)

func _input(event):
	if event is InputEventMouseMotion:
		var mousepos = get_global_mouse_position()
		var coordpos = get_parent().get_node("terrain_tilemap").world_to_map( mousepos )
		highlighted_coord = coordpos
		
	if event is InputEventMouseButton:
		if event.button_mask == 0: # button released
			if event.button_index == 1: # left click
				# get tile position from highlighted_coord

				var draw_z = 0 #TODO: set this to z of where the player is looking.
				
				var calulated_move = Dictionary()
				calulated_move["ident"] = manager_connection.character_name
				calulated_move["command"] = "calculated_move"
				calulated_move["args"] = [highlighted_coord[0], highlighted_coord[1], draw_z] 
				print("Tile clicked at: ", calulated_move["args"])
				var to_send = JSON.print(calulated_move).to_utf8()
				manager_connection.client.put_data(to_send)
			
			if event.button_index == 2: # right click
				print("Tile right clicked at: ", highlighted_coord)
				# create super-menu with available options what can be done to the clicked tile.
				

func _process(delta):
    update()

func _draw():
		var sizex = tilemap_cell_size.x
		var sizey = tilemap_cell_size.y
		var x = highlighted_coord.x * sizex
		var y = highlighted_coord.y * sizey
		# first horizontal line
		draw_line( Vector2( x, y ), Vector2( x + sizex, y ), color )
		# second horizontal line
		draw_line( Vector2( x, y + sizey ), Vector2( x + sizex, y + sizey ) , color )
		# first vertical line
		draw_line( Vector2( x, y ), Vector2( x, y + sizey ), color )
		# second horizontal line
		draw_line( Vector2( x + sizex, y ), Vector2( x + sizex, y + sizey ), color )
		 