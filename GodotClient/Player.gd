extends Node2D

# Declare member variables here. Examples:
# var a = 2
# var b = "text"

# Called when the node enters the scene tree for the first time.
func _ready():
	var tile_index = $players_tilemap.get_tileset().find_tile_by_name("player_male")
	$players_tilemap.set_cellv( Vector2(0,0), tile_index )
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
