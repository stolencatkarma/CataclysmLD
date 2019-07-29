extends Node2D

# Declare member variables here. Examples:
# var a = 2
# var b = "text"

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if manager_connection.should_update_localmap:
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
				pass
				
		# finally set back to false until we recieve a new localmap from the server
		manager_connection.should_update_localmap = false