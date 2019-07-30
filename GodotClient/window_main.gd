extends Node2D
var _dt = preload("res://DynamicTile.tscn")
var player_node = preload( "res://Player.tscn")
onready var camera = $Camera2D

func _ready():
	camera.position = $Player.position

func _input(event):
	if event.is_action("zoom_in") and event.is_pressed() and not event.is_echo():
		camera.zoom = Vector2(camera.zoom.x / 1.5, camera.zoom.y / 1.5)
	if event.is_action("zoom_out") and event.is_pressed() and not event.is_echo():
		camera.zoom = Vector2(camera.zoom.x * 1.5, camera.zoom.y * 1.5)

func _physics_process(delta):
	if Input.is_action_pressed("ui_left"):
		camera.position.x = camera.position.x - 100 * delta
	if Input.is_action_pressed("ui_right"):
		camera.position.x = camera.position.x + 100 * delta
	if Input.is_action_pressed("ui_down"):
		camera.position.y = camera.position.y + 100 * delta
	if Input.is_action_pressed("ui_up"):
		camera.position.y = camera.position.y - 100 * delta

func _process(delta):
	if manager_connection.should_update_localmap:
		$terrain_tileset.clear()
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
				var tile_index = $terrain_tileset.get_tileset().find_tile_by_name(tile["terrain"]["ident"])
				var xy = Vector2( (tile['position']['x'] - draw_x), (tile['position']['y'] - draw_y) )
				$terrain_tileset.set_cellv( xy, tile_index )
				
		# finally set back to false until we recieve a new localmap from the server
		manager_connection.should_update_localmap = false