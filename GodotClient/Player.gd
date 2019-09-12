extends Node2D

func _ready():
	var tile_index = $players_tilemap.get_tileset().find_tile_by_name("player_male")
	$players_tilemap.set_cellv( Vector2(0,0), tile_index )
