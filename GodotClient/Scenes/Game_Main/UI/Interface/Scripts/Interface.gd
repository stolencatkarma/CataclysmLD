extends Node2D

var clicked_tile = null

# tile highlight vars
var highlighted_coord = Vector2()
onready var tilemap_cell_size = Vector2( 32, 32 )
onready var color = Color(1.0, 0.5, 0.0)
# -------------------

func _ready():
	# if not impassable -> move, build, 
	# if creature -> submenu - attack, trade,
	# if items -> mini loot window
	# if furniture -> grab, bash, deconstruct, activate (activate a sofa to sit, activate a door to open/close, lock/unlock, peek)
	# if vehicle -> enter, ride on top, other (to be implemented chapter 2)
	# if trap -> disarm, trigger,
	$SuperMenu.get_node("Terrain").connect("button_down", self, "terrain_pressed") 

func terrain_pressed():
	# create instance of SuperMenu_Terrain and give it what it needs.
	$SuperMenu_Terrain.visible = true
	$SuperMenu.visible = false


func _input(event):
	if event is InputEventMouseMotion:
		var mousepos = get_parent().get_global_mouse_position()
		highlighted_coord = Vector2(int(mousepos.x/32), int(mousepos.y/32))
		
	if event is InputEventMouseButton:
		var mousepos = get_parent().get_node("Viewport/node_window_main/terrain_tilemap").get_global_mouse_position()
		var coordpos = get_parent().get_node("Viewport/node_window_main/terrain_tilemap").world_to_map( mousepos )
		if event.is_pressed(): # button pressed.
			if event.button_index == 1: # left click
				if self.get_node("SuperMenu").is_open == false:
					var draw_z = 0 #TODO: set this to z of where the player is looking.
					
					var calculated_move = Dictionary()
					calculated_move["ident"] = manager_connection.character_name
					calculated_move["command"] = "calculated_move"
					calculated_move["args"] = [coordpos[0], coordpos[1], draw_z] 
					print("Tile clicked at: ", calculated_move["args"])
					var to_send = JSON.print(calculated_move).to_utf8()
					manager_connection.client.put_data(to_send)
				
			if event.button_index == 2: # right click
				print("Tile right clicked at: ", coordpos)
				for chunk in manager_connection.localmap_chunks:
					for tile in chunk['tiles']:
						if tile['position']['x'] == coordpos.x:
							if tile['position']['y'] == coordpos.y:
								clicked_tile = tile
								print(clicked_tile)
								break
				# create super-menu with available options what can be done to the clicked tile.
				self.get_node("SuperMenu").visible = true
				self.get_node("SuperMenu").is_open = true

func _process(delta):
    update()

func _draw():
		var sizex = tilemap_cell_size.x
		var sizey = tilemap_cell_size.y
		var x = highlighted_coord.x * sizex + 12
		var y = highlighted_coord.y * sizey + 16
		# first horizontal line
		draw_line( Vector2( x, y ), Vector2( x + sizex, y ), color )
		# second horizontal line
		draw_line( Vector2( x, y + sizey ), Vector2( x + sizex, y + sizey ) , color )
		# first vertical line
		draw_line( Vector2( x, y ), Vector2( x, y + sizey ), color )
		# second horizontal line
		draw_line( Vector2( x + sizex, y ), Vector2( x + sizex, y + sizey ), color )
		 