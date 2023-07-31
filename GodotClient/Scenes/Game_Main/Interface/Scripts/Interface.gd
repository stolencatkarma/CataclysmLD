extends Node2D

var clicked_tile = null

func _ready():
	# if not impassable -> move, build, 
	# if creature -> submenu - attack, trade,
	# if items -> mini loot window
	# if furniture -> grab, bash, deconstruct, activate (activate a sofa to sit, activate a door to open/close, lock/unlock, peek)
	# if vehicle -> enter, ride on top, other (to be implemented chapter 2)
	# if trap -> disarm, trigger,
	$SuperMenu.get_node("Terrain").connect("button_down", Callable(self, "terrain_pressed")) 
	$SuperMenu.get_node("Furniture").connect("button_down", Callable(self, "furniture_pressed")) 

func terrain_pressed():
	# create instance of SuperMenu_Terrain and give it what it needs.
	$SuperMenu_Terrain.visible = true
	$SuperMenu.visible = false
	
func furniture_pressed():
	# create instance of SuperMenu_Terrain and give it what it needs.
	$SuperMenu_Furniture.visible = true
	$SuperMenu.visible = false


func _input(event):
	if event is InputEventMouseButton:
		var mousepos = get_parent().get_node("SubViewport/node_window_main/terrain_tilemap").get_global_mouse_position()
		var coordpos = get_parent().get_node("SubViewport/node_window_main/terrain_tilemap").local_to_map( mousepos )
		if event.is_pressed(): # button pressed.
			if event.button_index == 2: # right click
				if self.get_node("SuperMenu").visible:
					self.get_node("SuperMenu").visible = false
					self.get_node("SuperMenu_Furniture").visible = false
					self.get_node("SuperMenu_Terrain").visible = false
				else:
					print("Tile right clicked at: ", coordpos)
					for chunk in manager_connection.localmap_chunks:
						for tile in chunk['tiles']:
							if tile['position']['x'] == coordpos.x:
								if tile['position']['y'] == coordpos.y:
									clicked_tile = tile
									break
					self.get_node("SuperMenu").visible = true
