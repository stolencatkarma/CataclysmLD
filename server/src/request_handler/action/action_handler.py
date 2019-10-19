from src.blueprint import Blueprint
from src.model.action import Action
from src.model.manager.item import Container
from src.position import Position, Direction


class ActionHandler:
    def __init__(self, logger, recipe_manager):
        self.logger = logger
        self.recipe_manager = recipe_manager
        self.action_handlers = {
            "move": self.simple_hander,
            "bash": self.bash_handler,
            "create_blueprint": self.blueprint_handler,
            "calculated_move": self.calculated_move_handler,
            "move_item_to_character_storage": self.move_item_to_character_storage_handler,
            "move_item": self.move_item_handler
        }

    def handle_request(self, command, world_state):
        self.action_handlers[command.command_name](command, world_state)

    def can_handle(self, action_name):
        return action_name in self.action_handlers

    def simple_hander(self, command, world_state):
        action = Action("bash", [command.args[0]])
        world_state.characters[command.ident]["command_queue"].append(action)

    def bash_handler(self, command, world_state):
        position = Position(command.args[0], command.args[1], command.args[2])
        action = Action('bash', position)
        world_state.characters[command.ident]["command_queue"].append(action)

    def blueprint_handler(self, command, world_state):
        blueprint_ident = command.args[0]
        direction = command.args[1]
        print(f"creating blueprint {blueprint_ident} for character {world_state.characters[command.ident]}")
        # blueprint rules
        # * there should be blueprints for terrain, furniture, items, and anything else that takes a slot up in the Worldmap.
        # * they act as placeholders and then "transform" into the type they are once completed.
        # Blueprint(type, recipe)
        dy = 1 if direction == "south" else -1 if direction == "north" else 0
        dx = 1 if direction == "east" else -1 if direction == "west" else 0
        bpposition = Position(
            world_state.characters[command.ident]["position"]["x"] + dx,
            world_state.characters[command.ident]["position"]["y"] + dy,
            world_state.characters[command.ident]["position"]["z"],
        )

        recipe = self.recipe_manager.RECIPE_TYPES[blueprint_ident]
        recipe_type = recipe["type_of"]
        bp_to_create = Blueprint(recipe_type, recipe)

        world_state.worldmap.put_object_atposition(bp_to_create, bpposition)
        
    def move_item_to_character_storage_handler(self, command, world_state):
        character = world_state.characters[command.ident["name"]]
        from_pos = Position(command.args[0], command.args[1], command.args[2])
        item_ident = command.args[3]
        from_item = None
        open_containers = []
        # find the item that the character is requesting.
        for item in world_state.worldmap.get_tile_by_position(from_pos)["items"]:
            if item["ident"] == item_ident:
                # this is the item or at least the first one that matches the same ident.
                from_item = item  # save a reference to it to use.
                break

        # we didn't find one, character sent bad information (possible hack?)
        if from_item is None:
            return

        # make a list of open_containers the character has to see if they can pick it up.
        for bodyPart in character["body_parts"]:
            if (
                    bodyPart["slot0"] is not None
                    and isinstance(bodyPart["slot0"], Container)
                    and bodyPart["slot0"].opened
            ):
                open_containers.append(bodyPart["slot0"])
            if (
                    bodyPart["slot1"] is not None
                    and isinstance(bodyPart["slot1"], Container)
                    and bodyPart["slot1"].opened
            ):
                open_containers.append(bodyPart["slot1"])

        if len(open_containers) <= 0:
            return  # no open containers.

        # check if the character can carry that item.
        for container in open_containers:
            # then find a spot for it to go (open_containers)
            if container.add_item(item):  # if it added it sucessfully.
                # remove it from the worlds.
                for item in world_state.worldmap.get_tile_by_position(from_pos)["items"][:]:  # iterate a copy to remove properly.
                    if item["ident"] == item_ident:
                        world_state.worldmap.get_tile_by_position(from_pos)["items"].remove(item)
                        break
                return
            else:
                print("could not add item to character inventory.")
            # then send the character the updated version of themselves so they can refresh.

    def move_item_handler(self, command, world_state):
        # client sends "hey server. can you move this item from this to that?"
        character_requesting = world_state.characters[command.ident]
        item = command.args[0]  # the item we are moving.
        from_type = command.args[1]

        # the list the item will end up. passed from command.
        to_list = command.args[2]

        # pass the position even if we may not need it.
        position = Position(command.args[3], command.args[4], command.args[5])

        # need to parse where it's coming from and where it's going.
        if from_type == "bodypart.equipped":
            for bodypart in character_requesting["body_parts"][:]:  # iterate a copy to remove properly.
                if item in bodypart.equipped:
                    from_list = bodypart.equipped
                    from_list.remove(item)
                    to_list.append(item)
                    return
        elif from_type == "bodypart.equipped.container":
            for bodypart in character_requesting["body_parts"][:]:  # iterate a copy to remove properly.
                for item in bodypart.equipped:  # could be a container or not.
                    # if it's a container.
                    if isinstance(item, Container):
                        for item2 in item.contained_items[:]:  # check every item in the container.
                            if item2 is item:
                                from_list = item.contained_items
                                from_list.remove(item)
                                to_list.append(item)
                                return
        elif from_type == "position":
            from_list = world_state.worldmap.get_tile_by_position(position)["items"]
            if item in from_list:
                from_list.remove(item)
                to_list.append(item)
                return
        # a blueprint is a type of container but can't be moved from it's worlds position.
        elif from_type == "blueprint":
            for item in world_state.worldmap.get_tile_by_position(position)["items"]:
                # only one blueprint allowed per space.
                if isinstance(item, Blueprint):
                    from_list = item.contained_items
                    from_list.remove(item)
                    to_list.append(item)
                    return
    
    def calculated_move_handler(self, command, world_state):
        """Load a series of move actions into the action queue that will deliver the requesting character to the target tile"""
        print(f"Recieved calculated_move action. Building a path for {command.ident}")
        position = Position(command.args[0], command.args[1], command.args[2])
        route = self.calculate_route(world_state.characters[command.ident]["position"], position, world_state, False)
        print(
            "Calculated route for Character {}: {}".format(
                world_state.characters[command.ident]["name"], route
            )
        )
        world_state.characters[command.ident]["command_queue"].clear()
        # fill the queue with move commands to reach the tile.
        # pprint.pprint(self.characters[command.ident])
        x = world_state.characters[command.ident]["position"]["x"]
        y = world_state.characters[command.ident]["position"]["y"]
        z = world_state.characters[command.ident]["position"]["z"]
        if route is None:
            print("No route possible.")
            return
        for step in route:
            next_x = step["x"]
            next_y = step["y"]
            next_z = step["z"]
            if x > next_x:
                direction = Direction.WEST
            elif x < next_x:
                direction = Direction.EAST
            elif y > next_y:
                direction = Direction.NORTH
            elif y < next_y:
                direction = Direction.SOUTH
            elif z < next_z:
                direction = Direction.UP
            elif z > next_z:
                direction = Direction.DOWN
            else:
                x = next_x
                y = next_y
                z = next_z
                self.logger.info(f"Repeated step in route at position: ({x}, {y}, {z})")
                continue  # we are at the same position as the character

            action = Action("move", [direction.name.lower()])
            world_state.characters[command.ident]["command_queue"].append(action)
            # pretend as if we are in the next position.
            x = next_x
            y = next_y
            z = next_z

    def calculate_route(self, start, goal, world_state, consider_impassable=True):
        """Returns a route from start to goal as a series of Position(s)"""
        path = [start]

        # normally we will not want to consider impassable terrain in movement calculations. Creatures that can walk through walls don't need to though.
        # TODO: Create more granularity in what is considered "passable" and what is not.  Open air may be passable to birds, but not to humans, etc.
        adjacency_retriever = world_state.worldmap.get_adjacent_tiles if consider_impassable else world_state.worldmap.get_adjacent_tiles_non_impassable

        # Do a DFS without backtracking to calculate the route.  This will generate an unbroken path to the goal tile.
        while path[-1] != goal:
            # get reachable positions from the last point on the map.
            adjacent_tiles = adjacency_retriever(path[len(path) - 1])

            # get the tile in those that is closest to the goal.
            current_best = path[-1]
            for adjacent in [adjacent_tile['position'] for adjacent_tile in adjacent_tiles]:
                # Get the Manhattan distance between the current pos and the next pos
                next_distance = abs(adjacent["x"] - goal["x"]) + abs(adjacent["y"] - goal["y"])
                current_best_pos = abs(current_best["x"] - goal["x"]) + abs(current_best["y"] - goal["y"])
                if next_distance < current_best_pos:
                    current_best = adjacent
            # print(path[len(path) - 1])
            path.append(current_best)

            if len(path) > 9:
                break

        return path