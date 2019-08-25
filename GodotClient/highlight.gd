extends Node2D

var highlighted_coord = Vector2()
onready var tilemap_rect = get_viewport().get_visible_rect()
onready var tilemap_cell_size = get_parent().cell_size
onready var color = Color(0.4, 0.9, 0.4)

func _input(event):
	if event is InputEventMouseMotion:
		var mousepos = get_global_mouse_position()
		var coordpos = get_parent().get_node("terrain_tileset").world_to_map( mousepos )
		highlighted_coord = coordpos
		
	if event is InputEventMouseButton:
		if event.button_mask == 0: # button released
			if event.button_index == 1: # left click
				# get tile position from highlighted_coord
				var draw_x = null
				var draw_y = null
				var draw_z = null
				
				for chunk in manager_connection.localmap_chunks:
					for tile in chunk['tiles']:
						if draw_x == null: # first tile. set both because we need both.
							draw_x = tile['position']['x']
							draw_y = tile['position']['y']
							draw_z = tile['position']['z']
						if(tile['position']['x'] < draw_x):
							draw_x = tile['position']['x']
						if(tile['position']['y'] < draw_y):
							draw_y = tile['position']['y']
				
				var calulated_move = Dictionary()
				calulated_move["ident"] = manager_connection.character_name
				calulated_move["command"] = "calculated_move"
				calulated_move["args"] = [highlighted_coord[0]+draw_x, highlighted_coord[1]+draw_y, draw_z] 
				print("Tile clicked at: ", calulated_move["args"])
				var to_send = JSON.print(calulated_move).to_utf8()
				manager_connection.client.put_data(to_send)
			
			if event.button_index == 2: # right click
				print("Tile clicked at: ", highlighted_coord)

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
		 