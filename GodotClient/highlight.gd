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
		 