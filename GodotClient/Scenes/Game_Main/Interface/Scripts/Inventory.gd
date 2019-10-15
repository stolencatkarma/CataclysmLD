extends Node2D

onready var items_tilemap = get_parent().get_parent().get_node("Viewport/node_window_main/items_tilemap")


# Called when the node enters the scene tree for the first time.
func _ready():
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if self.visible and manager_connection.should_update_inventory:
		$inventory_tilemap.clear()
		# update inventory screen from latest update.
		manager_connection.should_update_inventory = false
		for body_part in manager_connection.controlled_character['body_parts']:
			if(body_part['slot0'] != null):
				# need dict and Texture
				var _contained = get_node(body_part['ident']).get_node('slot0').contained
				_contained = body_part['slot0']
				
				var _tileset = items_tilemap.get_tileset()
				var item_index = _tileset.find_tile_by_name(_contained["ident"])
				
				var slot_pos = get_node(body_part['ident']).get_node('slot0').position
				
				var xy = Vector2(slot_pos.x/32,slot_pos.y/32)
				print(xy)
				$inventory_tilemap.set_cellv( xy, item_index )
