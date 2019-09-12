extends Node2D
# var player_node = preload( "res://Player.tscn")
onready var camera = $Camera2D
var player_position = Vector2()


func _ready():
	camera.position = player_position

func _process(delta):
	if not camera.mouse_captured:
		camera.position = lerp(camera.position, player_position, delta*2)
	# TODO: add a keypress to switch between locked and free camera. 
	if manager_connection.should_update_localmap:
		$terrain_tilemap.clear()
		$furniture_tilemap.clear()
		$creature_tilemap.clear()
		$players_tilemap.clear()
		
		for chunk in manager_connection.localmap_chunks:
			for tile in chunk['tiles']:
				var xy = Vector2( (tile['position']['x']), (tile['position']['y']) )
				
				var terrain_index = $terrain_tilemap.get_tileset().find_tile_by_name(tile["terrain"]["ident"])
				$terrain_tilemap.set_cellv( xy, terrain_index )
				
				if tile["furniture"]:
					var furniture_index = $furniture_tilemap.get_tileset().find_tile_by_name(tile["furniture"]["ident"])
					$furniture_tilemap.set_cellv( xy, furniture_index )
				
				if tile["creature"]:
					var creature_index = 0
					if tile["creature"]['tile_ident']: # this is a player
						if tile["creature"]["name"] == manager_connection.character_name:
							player_position = Vector2(xy.x*32, xy.y*32) # this is the client's character. save the position for the camera.
						creature_index = $players_tilemap.get_tileset().find_tile_by_name(tile["creature"]["tile_ident"])
						$players_tilemap.set_cellv( xy, creature_index )
					else:
						creature_index = $creature_tilemap.get_tileset().find_tile_by_name(tile["creature"]["ident"])
						$creature_tilemap.set_cellv( xy, creature_index )
					
				
				
		# finally set back to false until we recieve a new localmap from the server
		manager_connection.should_update_localmap = false
		