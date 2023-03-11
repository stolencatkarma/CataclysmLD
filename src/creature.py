# defines base creature in the base. all monsters, Characters, npcs, and critters derive from this.
from .bodypart import Bodypart


class Creature(dict):
    def __init__(self):
        self['strength'] = 8
        self['dexterity'] = 8
        self['intelligence'] = 8
        self['perception'] = 8
        self['constitution'] = 8

        # known_recipes[0] = Recipe(ident) -  pull full recipe info from RecipeManager['ident'] - NPCs may know recipes that's why its in Creature
        self['known_recipes'] = list()

        # what each creature wants to do this turn and the upcoming turns. contains a list of Action(s) that are processed by the server.
        self['command_queue'] = list()
        self['gender'] = 'male'
        self['radiation'] = 0  # radiation level. hurts some helps others.

        # name is optional here. characters and most NPCs would have a name.
        self['name'] = None

        self['in_vehicle'] = False  # otherwise have a reference to the vehicle it's in.
        self['controlling_vehicle'] = False

        # what is this creature able to do?
        self['possible_actions'] = [
            'move',
            'attack',
            'sneak',
            'craft',
            'activate',
            'wear',
            'remove',
            'reload',
        ]

        # actions per turn (per second). (moving 5 ft a second is average walking speed)
        self['actions_per_turn'] = 1

        # how many turns until we can take an action. if this is greater than 0 subtract 1 per turn until 0. add to this per action.
        self['next_action_available'] = 0

        # set True for no_clip, does_no_damage, chase_creature
        self['hallucination'] = False
        self['tile_ident'] = 'player_male'  # base ident for new creatures.
        self['dodges_per_turn'] = 0
        self['blocks_per_turn'] = 0
        self['move_mode'] = 'walk'  # 'walk', 'run', 'sneak'

        # list of body parts this creature has. normal human has 2 arms, 2 hands, 2 legs, torso, head, and 2 feet. head and torso are both vital organs.
        # body_parts are where items get equipped.
        self['body_parts'] = [
            Bodypart('HEAD', True),
            Bodypart('TORSO', True),
            Bodypart('ARM_LEFT'),
            Bodypart('ARM_RIGHT'),
            Bodypart('LEG_LEFT'),
            Bodypart('LEG_RIGHT'),
            Bodypart('FOOT_LEFT'),
            Bodypart('FOOT_RIGHT'),
            Bodypart('HAND_LEFT'),
            Bodypart('HAND_RIGHT'),
        ]
        self['grabbed'] = None
