extends Node2D



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