extends Node2D
var _dt = preload("res://DynamicTile.tscn")

func _process(delta):
	if manager_connection.should_update_localmap:
		var dynamic_tiles = get_tree().get_nodes_in_group("DynamicTiles")
		for dt in dynamic_tiles:
	    	dt.queue_free()
		var draw_x = null
		var draw_y = null
		# loop through the chunks finding smallest x and y for our origin draw point
		for chunk in manager_connection.localmap_chunks:
			for tile in chunk['tiles']:
				if draw_x == null: # first tile. set both because we need both.
					draw_x = tile['position']['x']
					draw_y = tile['position']['y']
				if(tile['position']['x'] < draw_x):
					draw_x = tile['position']['x']
				if(tile['position']['y'] < draw_y):
					draw_y = tile['position']['y']
		# now we have a draw_x, and draw_y origin. loop through again and draw the tiles.
		for chunk in manager_connection.localmap_chunks:
			for tile in chunk['tiles']:
				# draw a dynamic tile at that position and fill it with the data from the dictionary. 
				var _instance = _dt.instance()
				add_child(_instance)
				_instance.position.x = (tile['position']['x'] - draw_x) * 32
				_instance.position.y = (tile['position']['y'] - draw_y) * 32
				_instance.add_to_group("DynamicTiles")
				
		# finally set back to false until we recieve a new localmap from the server
		manager_connection.should_update_localmap = false