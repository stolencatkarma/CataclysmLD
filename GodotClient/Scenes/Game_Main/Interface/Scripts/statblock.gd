extends NinePatchRect

var should_update = false

# Called every frame. 'delta' is the elapsed time since the previous frame.
# warning-ignore:unused_argument
func _process(delta):
	if should_update:
		# stats come in as a float
		$strength.text = String(manager_connection.controlled_character['strength'])
		$dexterity.text = String(manager_connection.controlled_character['dexterity'])
		$intelligence.text = String(manager_connection.controlled_character['intelligence'])
		$perception.text = String(manager_connection.controlled_character['perception'])
		
		should_update = false