extends Control

func _ready():
	self.get_node("GridContainer/Move").connect("button_down", self, "move_pressed") 

func move_pressed():
	self.visible = false
	get_parent().is_open = false