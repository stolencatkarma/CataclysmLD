extends Node2D

# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if self.visible and manager_connection.should_update_inventory:
		# update inventory screen from latest update.
		manager_connection.should_update_inventory = false
		for body_part in manager_connection.controlled_character['body_parts']:
			if(body_part['slot0'] != null):
				print(body_part['slot0'])
			if(body_part['slot1'] != null):
				print(body_part['slot1'])
			