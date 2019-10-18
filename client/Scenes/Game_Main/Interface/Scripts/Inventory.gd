extends Node2D

# inventory screen uses the same tilemap as items.
onready var items_tilemap = get_parent().get_parent().get_node("Viewport/node_window_main/items_tilemap")
var container_slot = load('res://Scenes/Game_Main/Interface/container_slot.tscn')


# Called when the node enters the scene tree for the first time.
func _ready():
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if self.visible and manager_connection.should_update_inventory:
		# update inventory screen from latest update.
		manager_connection.should_update_inventory = false
		for child in $container_slots.get_children():
			child.queue_free()
		# vars for items in containers.
		var startx = 0
		var starty = 384
		for body_part in manager_connection.controlled_character['body_parts']:
			if(body_part['slot0'] != null):
				var _contained = body_part['slot0'].duplicate()

				get_node(body_part['ident']).get_node('slot0').contained = _contained

				var _tileset = items_tilemap.get_tileset()
				var item_index = _tileset.find_tile_by_name(_contained["ident"])
				var region = items_tilemap.get_tileset().tile_get_region ( item_index )
				var at = AtlasTexture.new()
				at.set_atlas(items_tilemap.get_tileset().tile_get_texture( item_index ))
				at.set_region(region)
				get_node(body_part['ident']).get_node('slot0').button.icon = at
				
				if('opened' in body_part['slot0']):
					if(body_part['slot0']['opened'] == 'yes'):
						for item in body_part['slot0']['contained_items']:
							var _slot = container_slot.instance() 
							var _contained_in = item.duplicate()
							var at2 = AtlasTexture.new()
							var item_index2 = _tileset.find_tile_by_name(item["ident"])
							var region2 = items_tilemap.get_tileset().tile_get_region ( item_index2 )
							at2.set_atlas(items_tilemap.get_tileset().tile_get_texture( item_index2 ))
							at2.set_region(region2)
							$container_slots.add_child(_slot)
							_slot.contained = _contained_in
							_slot.button.set_button_icon(at2)
							if(startx > 320):
								startx = 0
								starty = starty + 32
							startx = startx + 32
							
							_slot.position = Vector2(startx, starty)
							

			
			