extends Node2D

# inventory screen uses the same tilemap as items.
@onready var items_tilemap = get_parent().get_parent().get_node("SubViewport/node_window_main/items_tilemap")

var container_slot = load('res://Scenes/Game_Main/Interface/container_slot.tscn')

var atlas_texture = AtlasTexture.new()



# Called when the node enters the scene tree for the first time.
func _ready():
	atlas_texture.set_atlas(items_tilemap.get_tileset().tile_get_texture(creature_index))

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if self.visible and manager_connection.should_update_inventory:
		# vars for items in containers.
		var startx = 0
		var starty = 320
		# clear screen before redraw.
		$inventory_tilemap.clear()
		for child in $container_slots.get_children():
			child.queue_free()
			
		# update inventory screen from latest update.
		manager_connection.should_update_inventory = false
		for body_part in manager_connection.controlled_character['body_parts']:
			if(body_part['slot0'] != null):
				# need dict and Texture
				var _contained = body_part['slot0'].duplicate()
				get_node(body_part['ident']).get_node('slot0').contained = _contained
				# print(_contained)
				var _tileset = items_tilemap.get_tileset()
				var item_index = _tileset.find_tile_by_name(_contained["ident"])
				
				var slot_pos = get_node(body_part['ident']).get_node('slot0').position
				
				if('opened' in body_part['slot0']):
					if(body_part['slot0']['opened'] == 'yes'):
						for item in body_part['slot0']['contained_items']:
							if(startx >= 320):
								startx = 0
								starty = starty + 32
							if(starty >= 64):
								break
							startx = startx + 32
							var _slot = container_slot.instantiate()
							$container_slots.add_child(_slot)
							_slot.set_position(Vector2(startx, starty))
							_slot.contained = item.duplicate()


			
			if(body_part['slot1'] != null):
				# need dict and Texture
				var _contained = body_part['slot1'].duplicate()
				get_node(body_part['ident']).get_node('slot1').contained = _contained
				# print(_contained)
				var _tileset = items_tilemap.get_tileset()
				var item_index = _tileset.find_tile_by_name(_contained["ident"])
				
				var slot_pos = get_node(body_part['ident']).get_node('slot1').position
				
				var xy = Vector2(slot_pos.x/32,slot_pos.y/32)
				$inventory_tilemap.set_cellv( xy, item_index )
