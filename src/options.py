import json # for reading and writing options for both global and world options
from collections import defaultdict
class Options:
    def translate_marker(self, text):
        return text

    def __init__(self):
        self.MAX_VIEW_DISTANCE = 10
        self.CORE_VERSION = '0.1'
        self.OPTIONS = defaultdict(dict)
        ##############GENERAL#############
        self.OPTIONS['DEF_CHAR_NAME'] = {}
        self.OPTIONS['DEF_CHAR_NAME']['VALUE'] = 'default'
        self.OPTIONS['DEF_CHAR_NAME']['TYPE'] = 'general'
        self.OPTIONS['DEF_CHAR_NAME']['HINT'] = self.translate_marker('Default character name')
        self.OPTIONS['DEF_CHAR_NAME']['HINTLONG'] = self.translate_marker('Set a default character name that will be used instead of a random name on character creation.' )

        self.OPTIONS['AUTO_PICKUP'] = {}
        self.OPTIONS['AUTO_PICKUP']['VALUE'] = False
        self.OPTIONS['AUTO_PICKUP']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PICKUP']['HINT'] = self.translate_marker('Auto pickup enabled')
        self.OPTIONS['AUTO_PICKUP']['HINTLONG'] = self.translate_marker( 'Enable item auto pickup.  Change pickup rules with the Auto Pickup Manager in the Help Menu ?3' )

        self.OPTIONS['AUTO_PICKUP_ADJACENT'] = {}
        self.OPTIONS['AUTO_PICKUP_ADJACENT']['VALUE'] = False
        self.OPTIONS['AUTO_PICKUP_ADJACENT']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PICKUP_ADJACENT']['HINT'] = self.translate_marker('Auto pickup adjacent')
        self.OPTIONS['AUTO_PICKUP_ADJACENT']['HINTLONG'] = self.translate_marker( 'If True, enable to pickup items one tile around to the player.  You can assign No Auto Pickup zones with the Zones Manager \'Y\' key for eg.  your homebase.' )

        self.OPTIONS['AUTO_PICKUP_WEIGHT_LIMIT'] = {}
        self.OPTIONS['AUTO_PICKUP_WEIGHT_LIMIT']['VALUE'] = 20
        self.OPTIONS['AUTO_PICKUP_WEIGHT_LIMIT']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PICKUP_WEIGHT_LIMIT']['HINT'] = self.translate_marker('Auto pickup light items')
        self.OPTIONS['AUTO_PICKUP_WEIGHT_LIMIT']['HINTLONG'] = self.translate_marker( 'Auto pickup items with weight less than or equal to [option] * 50 grams.  You must also set the small items option.  \'0\' disables self option'  )

        self.OPTIONS['AUTO_PICKUP_VOL_LIMIT'] = {}
        self.OPTIONS['AUTO_PICKUP_VOL_LIMIT']['VALUE'] = 50
        self.OPTIONS['AUTO_PICKUP_VOL_LIMIT']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PICKUP_VOL_LIMIT']['HINT'] = self.translate_marker('Auto pickup small volume items')
        self.OPTIONS['AUTO_PICKUP_VOL_LIMIT']['HINTLONG'] = self.translate_marker( 'Auto pickup items with volume less than or equal to [option] * 50 milliliters.  You must also set the light items option.  \'0\' disables self option' )

        self.OPTIONS['AUTO_PICKUP_SAFEMODE'] = {}
        self.OPTIONS['AUTO_PICKUP_SAFEMODE']['VALUE'] = False
        self.OPTIONS['AUTO_PICKUP_SAFEMODE']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PICKUP_SAFEMODE']['HINT'] = self.translate_marker('Auto pickup safe mode')
        self.OPTIONS['AUTO_PICKUP_SAFEMODE']['HINTLONG'] = self.translate_marker( 'Auto pickup is disabled as long as you can see monsters nearby.  This is affected by \'Safe Mode proximity distance\'.' )

        self.OPTIONS['AUTO_PULP_BUTCHER'] = {}
        self.OPTIONS['AUTO_PULP_BUTCHER']['VALUE'] = False
        self.OPTIONS['AUTO_PULP_BUTCHER']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PULP_BUTCHER']['HINT'] = self.translate_marker( 'Auto pulp or butcher' )
        self.OPTIONS['AUTO_PULP_BUTCHER']['HINTLONG'] = self.translate_marker( 'If True, auto pulping resurrecting corpses or auto butchering any corpse.  Never pulps acidic corpses.  Disabled as long as any enemy monster is seen.' )

        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION'] = {} # pulp_adjacent and pulp are also options.
        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION']['VALUE'] = 'butcher'
        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION']['TYPE'] = 'general'
        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION']['HINT'] = self.translate_marker( 'Auto pulp or butcher action' )
        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION']['HINTLONG'] = self.translate_marker( 'If True, auto pulping resurrecting corpses or auto butchering any corpse.  Never pulps acidic corpses.  Disabled as long as any enemy monster is seen.' )
        self.OPTIONS['AUTO_PULP_BUTCHER_ACTION']['VALUES'] = ['butcher', 'pulp', 'pulp_adjacent']

        self.OPTIONS['DANGEROUS_PICKUPS'] = {}
        self.OPTIONS['DANGEROUS_PICKUPS']['VALUE'] = False
        self.OPTIONS['DANGEROUS_PICKUPS']['TYPE'] = 'general'
        self.OPTIONS['DANGEROUS_PICKUPS']['HINT'] = self.translate_marker( 'Dangerous pickups' )
        self.OPTIONS['DANGEROUS_PICKUPS']['HINTLONG'] = self.translate_marker( 'If False, cause player to drop items that cause them to exceed the weight limit.' )

        self.OPTIONS['AUTOSAFEMODE'] = {}
        self.OPTIONS['AUTOSAFEMODE']['VALUE'] = False
        self.OPTIONS['AUTOSAFEMODE']['TYPE'] = 'general'
        self.OPTIONS['AUTOSAFEMODE']['HINT'] =  self.translate_marker( 'Auto-safe mode' )
        self.OPTIONS['AUTOSAFEMODE']['HINTLONG'] = self.translate_marker( 'If True, safemode automatically back on after it being disabled beforehand.  See option \'Turns to re-enable safe mode\'' )

        self.OPTIONS['AUTOSAFEMODETURNS'] = {}
        self.OPTIONS['AUTOSAFEMODETURNS']['VALUE'] = 10
        self.OPTIONS['AUTOSAFEMODETURNS']['TYPE'] = 'general'
        self.OPTIONS['AUTOSAFEMODETURNS']['HINT'] = self.translate_marker( 'Turns to re-enable safe mode' )
        self.OPTIONS['AUTOSAFEMODETURNS']['HINTLONG'] = self.translate_marker( 'Number of turns after safe mode is re-enabled if no hostiles are in \'Safe Mode proximity distance\'.' )

        self.OPTIONS['SAFEMODE'] = {}
        self.OPTIONS['SAFEMODE']['VALUE'] = False
        self.OPTIONS['SAFEMODE']['TYPE'] = 'general'
        self.OPTIONS['SAFEMODE']['HINT'] = self.translate_marker( 'Safe Mode' )
        self.OPTIONS['SAFEMODE']['HINTLONG'] = self.translate_marker( 'If True, hold the game and display a warning if a hostile monster/npc is approaching.' )

        self.OPTIONS['SAFEMODEPROXIMITY'] = {}
        self.OPTIONS['SAFEMODEPROXIMITY']['VALUE'] = 15
        self.OPTIONS['SAFEMODEPROXIMITY']['TYPE'] = 'general'
        self.OPTIONS['SAFEMODEPROXIMITY']['HINT'] =  self.translate_marker( 'Safe Mode proximity distance' )
        self.OPTIONS['SAFEMODEPROXIMITY']['HINTLONG'] = self.translate_marker( 'If safe mode is enabled, to hostiles at which safe mode should show a warning.  0 = Max player view distance.' )

        self.OPTIONS['SAFEMODEVEH'] = {}
        self.OPTIONS['SAFEMODEVEH']['VALUE'] = False
        self.OPTIONS['SAFEMODEVEH']['TYPE'] = 'general'
        self.OPTIONS['SAFEMODEVEH']['HINT'] = self.translate_marker( 'Safe Mode when driving' )
        self.OPTIONS['SAFEMODEVEH']['HINTLONG'] = self.translate_marker( 'When True, mode will alert you of hostiles while you are driving a vehicle.' )

        self.OPTIONS['TURN_DURATION'] = {}
        self.OPTIONS['TURN_DURATION']['VALUE'] = False
        self.OPTIONS['TURN_DURATION']['TYPE'] = 'general'
        self.OPTIONS['TURN_DURATION']['HINT'] = self.translate_marker( 'Realtime turn progression' )
        self.OPTIONS['TURN_DURATION']['HINTLONG'] = self.translate_marker( 'If enabled, will take periodic gameplay turns.  This value is the delay between each turn, seconds.  Works best with Safe Mode disabled.  0 = disabled.' )

        self.OPTIONS['AUTOSAVE'] = {}
        self.OPTIONS['AUTOSAVE']['VALUE'] = False
        self.OPTIONS['AUTOSAVE']['TYPE'] = 'general'
        self.OPTIONS['AUTOSAVE']['HINT'] = self.translate_marker( 'Periodically autosave' )
        self.OPTIONS['AUTOSAVE']['HINTLONG'] = self.translate_marker( 'If True, will periodically save the map.  Autosaves occur based on in-game turns or real-time minutes, is larger.' )

        self.OPTIONS['AUTOSAVE_TURNS'] = {}
        self.OPTIONS['AUTOSAVE_TURNS']['VALUE'] = 60
        self.OPTIONS['AUTOSAVE_TURNS']['TYPE'] = 'general'
        self.OPTIONS['AUTOSAVE_TURNS']['HINT'] = self.translate_marker( 'Game turns between autosaves' )
        self.OPTIONS['AUTOSAVE_TURNS']['HINTLONG'] = self.translate_marker( 'Number of game turns between autosaves' )

        self.OPTIONS['AUTOSAVE_MINUTES'] = {}
        self.OPTIONS['AUTOSAVE_MINUTES']['VALUE'] = 60
        self.OPTIONS['AUTOSAVE_MINUTES']['TYPE'] = 'general'
        self.OPTIONS['AUTOSAVE_MINUTES']['HINT'] = self.translate_marker( 'Real minutes between autosaves' )
        self.OPTIONS['AUTOSAVE_MINUTES']['HINTLONG'] = self.translate_marker( 'Number of real time minutes between autosaves' )

        self.OPTIONS['CIRCLEDIST'] = {}
        self.OPTIONS['CIRCLEDIST']['VALUE'] = False
        self.OPTIONS['CIRCLEDIST']['TYPE'] = 'general'
        self.OPTIONS['CIRCLEDIST']['HINT'] = self.translate_marker( 'Circular distances' )
        self.OPTIONS['CIRCLEDIST']['HINTLONG'] = self.translate_marker( 'If True, game will calculate range in a realistic way: light sources will be circles, movement will cover more ground and take longer.  If disabled, is square: moving to the northwest corner of a building takes as long as moving to the north wall.' )

        self.OPTIONS['DROP_EMPTY'] = {}
        self.OPTIONS['DROP_EMPTY']['VALUE'] = False
        self.OPTIONS['DROP_EMPTY']['TYPE'] = 'general'
        self.OPTIONS['DROP_EMPTY']['HINT'] = self.translate_marker( 'Drop empty containers' )
        self.OPTIONS['DROP_EMPTY']['HINTLONG'] = self.translate_marker( 'Set to drop empty containers after use.  No: Don\'t drop any. - Watertight: All except watertight containers. - All: Drop all containers.' )
        self.OPTIONS['DROP_EMPTY']['VALUES'] = ['no', 'watertight', 'all']

        self.OPTIONS['AUTO_NOTES'] = {}
        self.OPTIONS['AUTO_NOTES']['VALUE'] = False
        self.OPTIONS['AUTO_NOTES']['TYPE'] = 'general'
        self.OPTIONS['AUTO_NOTES']['HINT'] =  self.translate_marker( 'Auto notes' )
        self.OPTIONS['AUTO_NOTES']['HINTLONG'] = self.translate_marker( 'If True, sets notes on places that have stairs that go up or down' )

        self.OPTIONS['DEATHCAM'] = {}
        self.OPTIONS['DEATHCAM']['VALUE'] = False
        self.OPTIONS['DEATHCAM']['TYPE'] = 'general'
        self.OPTIONS['DEATHCAM']['HINT'] =  self.translate_marker( 'DeathCam' )
        self.OPTIONS['DEATHCAM']['HINTLONG'] = self.translate_marker( 'Always: Always start deathcam.  Ask: Query upon death.  Never: Never show deathcam.' )
        self.OPTIONS['DEATHCAM']['VALUES'] = ['Always', 'Ask', 'Never']

        ##############INTERFACE############
        '''
        add( 'USE_LANG', 'interface', self.translate_marker( 'Language' ), self.translate_marker( 'Switch Language.' ),
        {   { '', self.translate_marker( 'System language' ) },
            # Note: language names are in their own language and are *not* translated at all.
            # Note: Somewhere in github PR was better link to msdn.microsoft.com with language names.
            # http:#en.wikipedia.org/wiki/List_of_language_names
            { 'en', R'( English )' },
            { 'fr',  R'( Francais )' },
            { 'de', R'( Deutsch )' },
            { 'it_IT', R'( Italiano )' },
            { 'es_AR', R'( Espanol ( Argentina ) )' },
            { 'es_ES', R'( Espanol ( Espaia ) )' },
            { 'pl', R'( Polskie )' },
            { 'pt_BR', R'( Portuguis ( Brasil ) )' },
        }, '' )
        '''

        self.OPTIONS['USE_LANG'] = {}
        self.OPTIONS['USE_LANG']['VALUE'] = 'en'
        self.OPTIONS['USE_LANG']['TYPE'] = 'interface'
        self.OPTIONS['USE_LANG']['HINT'] = self.translate_marker( 'Language' )
        self.OPTIONS['USE_LANG']['HINTLONG'] = self.translate_marker( 'Switch Language.' )
        self.OPTIONS['USE_LANG']['VALUES'] = ['en', 'fr', 'de']

        self.OPTIONS['USE_CELSIUS'] = {}
        self.OPTIONS['USE_CELSIUS']['VALUE'] = True
        self.OPTIONS['USE_CELSIUS']['TYPE'] = 'interface'
        self.OPTIONS['USE_CELSIUS']['HINT'] = self.translate_marker( 'Temperature units' )
        self.OPTIONS['USE_CELSIUS']['HINTLONG'] = self.translate_marker( 'Switch between Celsius and Fahrenheit.' )

        self.OPTIONS['USE_METRIC'] = {}
        self.OPTIONS['USE_METRIC']['VALUE'] = True
        self.OPTIONS['USE_METRIC']['TYPE'] = 'interface'
        self.OPTIONS['USE_METRIC']['HINT'] = self.translate_marker( 'Use metric units' )
        self.OPTIONS['USE_METRIC']['HINTLONG'] = self.translate_marker( 'Switch between metric and Imperial.' )

        self.OPTIONS['USE_24_HOUR'] = {}
        self.OPTIONS['USE_24_HOUR']['VALUE'] = True
        self.OPTIONS['USE_24_HOUR']['TYPE'] = 'interface'
        self.OPTIONS['USE_24_HOUR']['HINT'] = self.translate_marker( 'Time format' )
        self.OPTIONS['USE_24_HOUR']['HINTLONG'] = self.translate_marker( '12h: AM/PM, 7:31 AM - Military: 24h Military, 0731 - 24h: Normal 24h, 7:31' )

        self.OPTIONS['FORCE_CAPITAL_YN'] = {}
        self.OPTIONS['FORCE_CAPITAL_YN']['VALUE'] = False
        self.OPTIONS['FORCE_CAPITAL_YN']['TYPE'] = 'interface'
        self.OPTIONS['FORCE_CAPITAL_YN']['HINT'] = self.translate_marker( 'Force Y/N in prompts' )
        self.OPTIONS['FORCE_CAPITAL_YN']['HINTLONG'] = self.translate_marker( 'If True, Y/N prompts are case-sensitive and y and n are not accepted.' )

        self.OPTIONS['SNAP_TO_TARGET'] = {}
        self.OPTIONS['SNAP_TO_TARGET']['VALUE'] = False
        self.OPTIONS['SNAP_TO_TARGET']['TYPE'] = 'interface'
        self.OPTIONS['SNAP_TO_TARGET']['HINT'] = self.translate_marker( 'Snap to target' )
        self.OPTIONS['SNAP_TO_TARGET']['HINTLONG'] = self.translate_marker( 'If True, follow the crosshair when firing/throwing.' )

        self.OPTIONS['SAVE_SLEEP'] = {}
        self.OPTIONS['SAVE_SLEEP']['VALUE'] = False
        self.OPTIONS['SAVE_SLEEP']['TYPE'] = 'interface'
        self.OPTIONS['SAVE_SLEEP']['HINT'] = self.translate_marker( 'Ask to save before sleeping' )
        self.OPTIONS['SAVE_SLEEP']['HINTLONG'] = self.translate_marker( 'If True, will ask to save the map before sleeping.' )

        self.OPTIONS['QUERY_DISASSEMBLE'] = {}
        self.OPTIONS['QUERY_DISASSEMBLE']['VALUE'] = False
        self.OPTIONS['QUERY_DISASSEMBLE']['TYPE'] = 'interface'
        self.OPTIONS['QUERY_DISASSEMBLE']['HINT'] = self.translate_marker( 'Query on disassembly' )
        self.OPTIONS['QUERY_DISASSEMBLE']['HINTLONG'] = self.translate_marker( 'If True, query before disassembling items.' )

        self.OPTIONS['QUERY_KEYBIND_REMOVAL'] = {}
        self.OPTIONS['QUERY_KEYBIND_REMOVAL']['VALUE'] = False
        self.OPTIONS['QUERY_KEYBIND_REMOVAL']['TYPE'] = 'interface'
        self.OPTIONS['QUERY_KEYBIND_REMOVAL']['HINT'] = self.translate_marker( 'Query on keybinding removal' )
        self.OPTIONS['QUERY_KEYBIND_REMOVAL']['HINTLONG'] = self.translate_marker( 'If True, query before removing a keybinding from a hotkey.' )

        self.OPTIONS['CLOSE_ADV_INV'] = {}
        self.OPTIONS['CLOSE_ADV_INV']['VALUE'] = False
        self.OPTIONS['CLOSE_ADV_INV']['TYPE'] = 'interface'
        self.OPTIONS['CLOSE_ADV_INV']['HINT'] = self.translate_marker( 'Close advanced inventory on move all' )
        self.OPTIONS['CLOSE_ADV_INV']['HINTLONG'] = self.translate_marker( 'If True, close the advanced inventory when the move all items command is used.' )

        self.OPTIONS['OPEN_DEFAULT_ADV_INV'] = {}
        self.OPTIONS['OPEN_DEFAULT_ADV_INV']['VALUE'] = False
        self.OPTIONS['OPEN_DEFAULT_ADV_INV']['TYPE'] = 'interface'
        self.OPTIONS['OPEN_DEFAULT_ADV_INV']['HINT'] = self.translate_marker( 'Open default advanced inventory layout' )
        self.OPTIONS['OPEN_DEFAULT_ADV_INV']['HINTLONG'] = self.translate_marker( 'Open default advanced inventory layout instead of last opened layout' )

        self.OPTIONS['INV_USE_ACTION_NAMES'] = {}
        self.OPTIONS['INV_USE_ACTION_NAMES']['VALUE'] = False
        self.OPTIONS['INV_USE_ACTION_NAMES']['TYPE'] = 'interface'
        self.OPTIONS['INV_USE_ACTION_NAMES']['HINT'] = self.translate_marker( 'Display actions in Use Item menu' )
        self.OPTIONS['INV_USE_ACTION_NAMES']['HINTLONG'] = self.translate_marker( 'If True, actions ( like \'Read\', \'Smoke\', \'Wrap tighter\' ) will be displayed next to the corresponding items.' ),

        self.OPTIONS['VEHICLE_ARMOR_COLOR'] = {}
        self.OPTIONS['VEHICLE_ARMOR_COLOR']['VALUE'] = False
        self.OPTIONS['VEHICLE_ARMOR_COLOR']['TYPE'] = 'interface'
        self.OPTIONS['VEHICLE_ARMOR_COLOR']['HINT'] =  self.translate_marker( 'Vehicle plating changes part color' )
        self.OPTIONS['VEHICLE_ARMOR_COLOR']['HINTLONG'] = self.translate_marker( 'If True, parts will change color if they are armor plated' )

        self.OPTIONS['DRIVING_VIEW_OFFSET'] = {}
        self.OPTIONS['DRIVING_VIEW_OFFSET']['VALUE'] = False
        self.OPTIONS['DRIVING_VIEW_OFFSET']['TYPE'] = 'interface'
        self.OPTIONS['DRIVING_VIEW_OFFSET']['HINT'] = self.translate_marker( 'Auto-shift the view while driving' )
        self.OPTIONS['DRIVING_VIEW_OFFSET']['HINTLONG'] = self.translate_marker( 'If True, will automatically shift towards the driving direction' )

        self.OPTIONS['VEHICLE_DIR_INDICATOR'] = {}
        self.OPTIONS['VEHICLE_DIR_INDICATOR']['VALUE'] = False
        self.OPTIONS['VEHICLE_DIR_INDICATOR']['TYPE'] = 'interface'
        self.OPTIONS['VEHICLE_DIR_INDICATOR']['HINT'] = self.translate_marker( 'Draw vehicle facing indicator' )
        self.OPTIONS['VEHICLE_DIR_INDICATOR']['HINTLONG'] = self.translate_marker( 'If True, controlling a vehicle, white \'X\' ( in curses version ) or a crosshair ( in tiles version ) at distance 10 from the center will display its current facing.' )

        self.OPTIONS['SIDEBAR_POSITION'] = {}
        self.OPTIONS['SIDEBAR_POSITION']['VALUE'] = False
        self.OPTIONS['SIDEBAR_POSITION']['TYPE'] = 'interface'
        self.OPTIONS['SIDEBAR_POSITION']['HINT'] = self.translate_marker( 'Sidebar position' )
        self.OPTIONS['SIDEBAR_POSITION']['HINTLONG'] =  self.translate_marker( 'Switch between sidebar on the left or on the right side.  Requires restart.' )
        self.OPTIONS['SIDEBAR_POSITION']['VALUES'] = ['left', 'right']

        self.OPTIONS['AUTO_INV_ASSIGN'] = {}
        self.OPTIONS['AUTO_INV_ASSIGN']['VALUE'] = True
        self.OPTIONS['AUTO_INV_ASSIGN']['TYPE'] = 'interface'
        self.OPTIONS['AUTO_INV_ASSIGN']['HINT'] = self.translate_marker( 'Auto inventory letters' )
        self.OPTIONS['AUTO_INV_ASSIGN']['HINTLONG'] = self.translate_marker( 'If False, inventory items will only get letters assigned if they had one before.' )

        self.OPTIONS['ITEM_SYMBOLS'] = {}
        self.OPTIONS['ITEM_SYMBOLS']['VALUE'] = False
        self.OPTIONS['ITEM_SYMBOLS']['TYPE'] = 'interface'
        self.OPTIONS['ITEM_SYMBOLS']['HINT'] = self.translate_marker( 'Show item symbols' )
        self.OPTIONS['ITEM_SYMBOLS']['HINTLONG'] =  self.translate_marker( 'If True, item symbols in inventory and pick up menu.' )

        self.OPTIONS['ENABLE_JOYSTICK'] = {}
        self.OPTIONS['ENABLE_JOYSTICK']['VALUE'] = False
        self.OPTIONS['ENABLE_JOYSTICK']['TYPE'] = 'interface'
        self.OPTIONS['ENABLE_JOYSTICK']['HINT'] = self.translate_marker( 'Enable Joystick' )
        self.OPTIONS['ENABLE_JOYSTICK']['HINTLONG'] = self.translate_marker( 'Enable input from joystick.' )

        self.OPTIONS['HIDE_CURSOR'] = {}
        self.OPTIONS['HIDE_CURSOR']['VALUE'] = False
        self.OPTIONS['HIDE_CURSOR']['TYPE'] = 'interface'
        self.OPTIONS['HIDE_CURSOR']['HINT'] = self.translate_marker( 'Hide mouse cursor' )
        self.OPTIONS['HIDE_CURSOR']['HINTLONG'] = self.translate_marker( 'Show: Cursor is always shown.  Hide: Cursor is hidden.  HideKB: Cursor is hidden on keyboard input and unhidden on mouse movement.' )
        self.OPTIONS['HIDE_CURSOR']['VALUES'] = ['show', 'hide', 'hidekb']

        ##############GRAPHICS############/
        self.OPTIONS['ANIMATIONS'] = {}
        self.OPTIONS['ANIMATIONS']['VALUE'] = True
        self.OPTIONS['ANIMATIONS']['TYPE'] = 'graphics'
        self.OPTIONS['ANIMATIONS']['HINT'] = self.translate_marker( 'Enable Animations' )
        self.OPTIONS['ANIMATIONS']['HINTLONG'] = self.translate_marker( 'If True, display enabled animations.' )

        #TODO: add the other tilesets
        self.OPTIONS['TILESET'] = {}
        self.OPTIONS['TILESET']['VALUE'] = False
        self.OPTIONS['TILESET']['TYPE'] = 'graphics'
        self.OPTIONS['TILESET']['HINT'] = self.translate_marker( 'Choose tileset' )
        self.OPTIONS['TILESET']['HINTLONG'] = self.translate_marker( 'Choose the tileset you want to use.' )
        self.OPTIONS['TILESET']['VALUES'] = ['ChestHole']

        self.OPTIONS['FULLSCREEN'] = {}
        self.OPTIONS['FULLSCREEN']['VALUE'] = False
        self.OPTIONS['FULLSCREEN']['TYPE'] = 'graphics'
        self.OPTIONS['FULLSCREEN']['HINT'] = self.translate_marker( 'Fullscreen' )
        self.OPTIONS['FULLSCREEN']['HINTLONG'] = self.translate_marker( 'Use Fullscreen.' )


        ##############DEBUG##############
        self.OPTIONS['DISTANCE_INITIAL_VISIBILITY'] = {}
        self.OPTIONS['DISTANCE_INITIAL_VISIBILITY']['VALUE'] = 15
        self.OPTIONS['DISTANCE_INITIAL_VISIBILITY']['TYPE'] = 'debug'
        self.OPTIONS['DISTANCE_INITIAL_VISIBILITY']['HINT'] = self.translate_marker( 'Distance initial visibility' )
        self.OPTIONS['DISTANCE_INITIAL_VISIBILITY']['HINTLONG'] = self.translate_marker( 'Determines the scope, is known in the beginning of the game.' )

        self.OPTIONS['INITIAL_STAT_POINTS'] = {}
        self.OPTIONS['INITIAL_STAT_POINTS']['VALUE'] = 2
        self.OPTIONS['INITIAL_STAT_POINTS']['TYPE'] = 'debug'
        self.OPTIONS['INITIAL_STAT_POINTS']['HINT'] = self.translate_marker( 'Initial stat points' )
        self.OPTIONS['INITIAL_STAT_POINTS']['HINTLONG'] = self.translate_marker( 'Initial points available to spend on stats on character generation.' )

        self.OPTIONS['INITIAL_TRAIT_POINTS'] = {}
        self.OPTIONS['INITIAL_TRAIT_POINTS']['VALUE'] = 6
        self.OPTIONS['INITIAL_TRAIT_POINTS']['TYPE'] = 'debug'
        self.OPTIONS['INITIAL_TRAIT_POINTS']['HINT'] = self.translate_marker( 'Initial trait points' )
        self.OPTIONS['INITIAL_TRAIT_POINTS']['HINTLONG'] = self.translate_marker( 'Initial points available to spend on traits on character generation.' )

        self.OPTIONS['INITIAL_SKILL_POINTS'] = {}
        self.OPTIONS['INITIAL_SKILL_POINTS']['VALUE'] = 6
        self.OPTIONS['INITIAL_SKILL_POINTS']['TYPE'] = 'debug'
        self.OPTIONS['INITIAL_SKILL_POINTS']['HINT'] =  self.translate_marker( 'Initial skill points' )
        self.OPTIONS['INITIAL_SKILL_POINTS']['HINTLONG'] =  self.translate_marker( 'Initial points available to spend on skills on character generation.' )

        self.OPTIONS['MAX_TRAIT_POINTS'] = {}
        self.OPTIONS['MAX_TRAIT_POINTS']['VALUE'] = 100
        self.OPTIONS['MAX_TRAIT_POINTS']['TYPE'] = 'debug'
        self.OPTIONS['MAX_TRAIT_POINTS']['HINT'] = self.translate_marker( 'Maximum trait points' )
        self.OPTIONS['MAX_TRAIT_POINTS']['HINTLONG'] =  self.translate_marker( 'Maximum trait points available for character generation.' )

        self.OPTIONS['SKILL_TRAINING_SPEED'] = {}
        self.OPTIONS['SKILL_TRAINING_SPEED']['VALUE'] = 1.0
        self.OPTIONS['SKILL_TRAINING_SPEED']['TYPE'] = 'debug'
        self.OPTIONS['SKILL_TRAINING_SPEED']['HINT'] = self.translate_marker( 'Skill training speed' )
        self.OPTIONS['SKILL_TRAINING_SPEED']['HINTLONG'] = self.translate_marker( 'Scales experience gained from practicing skills and reading books.  0.5 is half as fast as default, 2.0 is twice as fast, 0.0 disables skill training except for NPC training.' )

        self.OPTIONS['SKILL_RUST'] = {}
        self.OPTIONS['SKILL_RUST']['VALUE'] = 'vanilla'
        self.OPTIONS['SKILL_RUST']['TYPE'] = 'debug'
        self.OPTIONS['SKILL_RUST']['HINT'] = self.translate_marker( 'Skill rust' )
        self.OPTIONS['SKILL_RUST']['HINTLONG'] = self.translate_marker( 'Set the level of skill rust.  Vanilla: Vanilla Cataclysm - Capped: Capped at skill levels 2 - Int: Intelligence dependent - IntCap: Intelligence dependent, capped - Off: None at all.' )
        self.OPTIONS['SKILL_RUST']['VALUES'] = ['vanilla', 'capped', 'int', 'intcap', 'off']

        ##############WORLD DEFAULT##########

        self.OPTIONS['CORE_VERSION'] = {}
        self.OPTIONS['CORE_VERSION']['VALUE'] = False
        self.OPTIONS['CORE_VERSION']['TYPE'] = 'world_default'
        self.OPTIONS['CORE_VERSION']['HINT'] = self.translate_marker( 'Core version data' )
        self.OPTIONS['CORE_VERSION']['HINTLONG'] = self.translate_marker( 'Controls what migrations are applied for legacy worlds' )

        self.OPTIONS['DELETE_WORLD'] = {}
        self.OPTIONS['DELETE_WORLD']['VALUE'] = False
        self.OPTIONS['DELETE_WORLD']['TYPE'] = 'world_default'
        self.OPTIONS['DELETE_WORLD']['HINT'] =  self.translate_marker( 'Delete world' )
        self.OPTIONS['DELETE_WORLD']['HINTLONG'] = self.translate_marker( 'Delete the world when the last active character dies.' )
        self.OPTIONS['DELETE_WORLD']['VALUES'] = ['yes', 'no', 'query']

        self.OPTIONS['CITY_SIZE'] = {}
        self.OPTIONS['CITY_SIZE']['VALUE'] = 5
        self.OPTIONS['CITY_SIZE']['TYPE'] = 'world_default'
        self.OPTIONS['CITY_SIZE']['HINT'] = self.translate_marker( 'Size of cities' )
        self.OPTIONS['CITY_SIZE']['HINTLONG'] = self.translate_marker( 'A number determining how large cities are.  0 disables cities, and any scenario requiring a city start.' )

        self.OPTIONS['SPAWN_DENSITY'] = {}
        self.OPTIONS['SPAWN_DENSITY']['VALUE'] = 1.0
        self.OPTIONS['SPAWN_DENSITY']['TYPE'] = 'world_default'
        self.OPTIONS['SPAWN_DENSITY']['HINT'] = self.translate_marker( 'Spawn rate scaling factor' )
        self.OPTIONS['SPAWN_DENSITY']['HINTLONG'] = self.translate_marker( 'A scaling factor that determines density of monster spawns.' )

        self.OPTIONS['ITEM_SPAWNRATE'] = {}
        self.OPTIONS['ITEM_SPAWNRATE']['VALUE'] = 1.0
        self.OPTIONS['ITEM_SPAWNRATE']['TYPE'] = 'world_default'
        self.OPTIONS['ITEM_SPAWNRATE']['HINT'] =  self.translate_marker( 'Item spawn scaling factor' )
        self.OPTIONS['ITEM_SPAWNRATE']['HINTLONG'] =  self.translate_marker( 'A scaling factor that determines density of item spawns.' )

        self.OPTIONS['NPC_DENSITY'] = {}
        self.OPTIONS['NPC_DENSITY']['VALUE'] = 1.0
        self.OPTIONS['NPC_DENSITY']['TYPE'] = 'world_default'
        self.OPTIONS['NPC_DENSITY']['HINT'] = self.translate_marker( 'NPC spawn rate scaling factor' )
        self.OPTIONS['NPC_DENSITY']['HINTLONG'] =  self.translate_marker( 'A scaling factor that determines density of dynamic NPC spawns.' )

        self.OPTIONS['MONSTER_UPGRADE_FACTOR'] = {}
        self.OPTIONS['MONSTER_UPGRADE_FACTOR']['VALUE'] = 1.0
        self.OPTIONS['MONSTER_UPGRADE_FACTOR']['TYPE'] = 'world_default'
        self.OPTIONS['MONSTER_UPGRADE_FACTOR']['HINT'] = self.translate_marker( 'Monster evolution scaling factor' )
        self.OPTIONS['MONSTER_UPGRADE_FACTOR']['HINTLONG'] = self.translate_marker( 'A scaling factor that determines the time between monster upgrades.  A higher number means slower evolution.  Set to 0.00 to turn off monster upgrades.' ),

        self.OPTIONS['MONSTER_SPEED'] = {}
        self.OPTIONS['MONSTER_SPEED']['VALUE'] = 1.0
        self.OPTIONS['MONSTER_SPEED']['TYPE'] = 'world_default'
        self.OPTIONS['MONSTER_SPEED']['HINT'] = self.translate_marker( 'Monster speed' )
        self.OPTIONS['MONSTER_SPEED']['HINTLONG'] = self.translate_marker( 'Determines the movement rate of monsters.  A higher value increases monster speed and a lower reduces it.' )

        self.OPTIONS['MONSTER_RESILIENCE'] = {}
        self.OPTIONS['MONSTER_RESILIENCE']['VALUE'] = 1.0
        self.OPTIONS['MONSTER_RESILIENCE']['TYPE'] = 'world_default'
        self.OPTIONS['MONSTER_RESILIENCE']['HINT'] =  self.translate_marker( 'Monster resilience' )
        self.OPTIONS['MONSTER_RESILIENCE']['HINTLONG'] = self.translate_marker( 'Determines how much damage monsters can take.  A higher value makes monsters more resilient and a lower makes them more flimsy.' )

        self.OPTIONS['DEFAULT_REGION'] = {}
        self.OPTIONS['DEFAULT_REGION']['VALUE'] = 'default'
        self.OPTIONS['DEFAULT_REGION']['TYPE'] = 'world_default'
        self.OPTIONS['DEFAULT_REGION']['HINT'] = self.translate_marker( 'Default region type' )
        self.OPTIONS['DEFAULT_REGION']['HINTLONG'] = self.translate_marker( '( WIP feature ) Determines terrain, shops, plants, more.' )

        self.OPTIONS['INITIAL_TIME'] = {} # 0-23 hours
        self.OPTIONS['INITIAL_TIME']['VALUE'] = 8
        self.OPTIONS['INITIAL_TIME']['TYPE'] = 'world_default'
        self.OPTIONS['INITIAL_TIME']['HINT'] = self.translate_marker( 'Initial time' )
        self.OPTIONS['INITIAL_TIME']['HINTLONG'] = self.translate_marker( 'Initial starting time of day on character generation.' )
        self.OPTIONS['INITIAL_TIME']['VALUES'] = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

        self.OPTIONS['INITIAL_SEASON'] = {}
        self.OPTIONS['INITIAL_SEASON']['VALUE'] = 'spring'
        self.OPTIONS['INITIAL_SEASON']['TYPE'] = 'world_default'
        self.OPTIONS['INITIAL_SEASON']['HINT'] =  self.translate_marker( 'Initial season' )
        self.OPTIONS['INITIAL_SEASON']['HINTLONG'] = self.translate_marker( 'Season the player starts in.  Options other than the default delay spawn of the character, food decay and monster spawns will have advanced.' )
        self.OPTIONS['INITIAL_SEASON']['VALUES'] = ['spring', 'summer', 'autumn', 'winter']

        self.OPTIONS['SEASON_LENGTH'] = {} # default was 14 so only 60 days in a year.
        self.OPTIONS['SEASON_LENGTH']['VALUE'] = 90
        self.OPTIONS['SEASON_LENGTH']['TYPE'] = 'world_default'
        self.OPTIONS['SEASON_LENGTH']['HINT'] =  self.translate_marker( 'Season length' )
        self.OPTIONS['SEASON_LENGTH']['HINTLONG'] = self.translate_marker( 'Season length, days.' )

        self.OPTIONS['CONSTRUCTION_SCALING'] = {}
        self.OPTIONS['CONSTRUCTION_SCALING']['VALUE'] = 1.0
        self.OPTIONS['CONSTRUCTION_SCALING']['TYPE'] = 'world_default'
        self.OPTIONS['CONSTRUCTION_SCALING']['HINT'] = self.translate_marker( 'Construction scaling' )
        self.OPTIONS['CONSTRUCTION_SCALING']['HINTLONG'] =  self.translate_marker( 'Sets the time of construction in percents.  \'2.0\' is two times faster than default, \'0.5\' is two times longer.  \'0\' automatically scales construction time to match the world\'s season length.' )

        self.OPTIONS['WANDER_SPAWNS'] = {}
        self.OPTIONS['WANDER_SPAWNS']['VALUE'] = False
        self.OPTIONS['WANDER_SPAWNS']['TYPE'] = 'world_default'
        self.OPTIONS['WANDER_SPAWNS']['HINT'] = self.translate_marker( 'Wander spawns' )
        self.OPTIONS['WANDER_SPAWNS']['HINTLONG'] = self.translate_marker( 'Emulation of zombie hordes.  Zombie spawn points wander around cities and may go to noise.  Must reset world directory after changing for it to take effect.' )

        self.OPTIONS['CLASSIC_ZOMBIES'] = {}
        self.OPTIONS['CLASSIC_ZOMBIES']['VALUE'] = False
        self.OPTIONS['CLASSIC_ZOMBIES']['TYPE'] = 'world_default'
        self.OPTIONS['CLASSIC_ZOMBIES']['HINT'] =  self.translate_marker( 'Classic zombies' )
        self.OPTIONS['CLASSIC_ZOMBIES']['HINTLONG'] = self.translate_marker( 'Only spawn classic zombies and natural wildlife.  Requires a reset of save folder to take effect.  This disables certain buildings.' )

        self.OPTIONS['SURROUND_START'] = {}
        self.OPTIONS['SURROUND_START']['VALUE'] = False
        self.OPTIONS['SURROUND_START']['TYPE'] = 'world_default'
        self.OPTIONS['SURROUND_START']['HINT'] = self.translate_marker( 'Surrounded start' )
        self.OPTIONS['SURROUND_START']['HINTLONG'] = self.translate_marker( 'If True, zombies at shelters.  Makes the starting game a lot harder.' )

        self.OPTIONS['STATIC_NPC'] = {}
        self.OPTIONS['STATIC_NPC']['VALUE'] = False
        self.OPTIONS['STATIC_NPC']['TYPE'] = 'world_default'
        self.OPTIONS['STATIC_NPC']['HINT'] = self.translate_marker( 'Static npcs' )
        self.OPTIONS['STATIC_NPC']['HINTLONG'] = self.translate_marker( 'If True, game will spawn static NPC at the start of the game, world reset.' )

        self.OPTIONS['RANDOM_NPC'] = {}
        self.OPTIONS['RANDOM_NPC']['VALUE'] = False
        self.OPTIONS['RANDOM_NPC']['TYPE'] = 'world_default'
        self.OPTIONS['RANDOM_NPC']['HINT'] = self.translate_marker( 'Random npcs' )
        self.OPTIONS['RANDOM_NPC']['HINTLONG'] = self.translate_marker( 'If True, game will randomly spawn NPC during gameplay.' )

        self.OPTIONS['RAD_MUTATION'] = {}
        self.OPTIONS['RAD_MUTATION']['VALUE'] = False
        self.OPTIONS['RAD_MUTATION']['TYPE'] = 'world_default'
        self.OPTIONS['RAD_MUTATION']['HINT'] = self.translate_marker( 'Mutations by radiation' )
        self.OPTIONS['RAD_MUTATION']['HINTLONG'] = self.translate_marker( 'If True, causes the player to mutate.' )

        self.OPTIONS['ZLEVELS'] = {}
        self.OPTIONS['ZLEVELS']['VALUE'] = False
        self.OPTIONS['ZLEVELS']['TYPE'] = 'world_default'
        self.OPTIONS['ZLEVELS']['HINT'] = self.translate_marker( 'Experimental z-levels' )
        self.OPTIONS['ZLEVELS']['HINTLONG'] =  self.translate_marker( 'If True, z-level maps will be enabled.  This feature is not finished yet and turning it on will only slow the game down.' )

        self.OPTIONS['ALIGN_STAIRS'] = {}
        self.OPTIONS['ALIGN_STAIRS']['VALUE'] = False
        self.OPTIONS['ALIGN_STAIRS']['TYPE'] = 'world_default'
        self.OPTIONS['ALIGN_STAIRS']['HINT'] = self.translate_marker( 'Align up and down stairs' )
        self.OPTIONS['ALIGN_STAIRS']['HINTLONG'] = self.translate_marker( 'If True, will be placed directly above upstairs, if self results in uglier maps.' )

        self.OPTIONS['CHARACTER_POINT_POOLS'] = {}
        self.OPTIONS['CHARACTER_POINT_POOLS']['VALUE'] = 'any'
        self.OPTIONS['CHARACTER_POINT_POOLS']['TYPE'] = 'world_default'
        self.OPTIONS['CHARACTER_POINT_POOLS']['HINT'] =  self.translate_marker( 'Character point pools' )
        self.OPTIONS['CHARACTER_POINT_POOLS']['HINTLONG'] = self.translate_marker( 'Allowed point pools for character generation.' )
        self.OPTIONS['CHARACTER_POINT_POOLS']['VALUES'] = ['any', 'multi_pool', 'no_freeform']

        self.OPTIONS['NO_FAULTS'] = {}
        self.OPTIONS['NO_FAULTS']['VALUE'] = False
        self.OPTIONS['NO_FAULTS']['TYPE'] = 'world_default'
        self.OPTIONS['NO_FAULTS']['HINT'] = self.translate_marker( 'Disables vehicle part faults.' )
        self.OPTIONS['NO_FAULTS']['HINTLONG'] = self.translate_marker( 'If True, vehicle part faults, parts will be totally reliable unless destroyed, can only be repaired via replacement.' )

        self.OPTIONS['FILTHY_MORALE'] = {}
        self.OPTIONS['FILTHY_MORALE']['VALUE'] = False
        self.OPTIONS['FILTHY_MORALE']['TYPE'] = 'world_default'
        self.OPTIONS['FILTHY_MORALE']['HINT'] = self.translate_marker( 'Morale penalty for filthy clothing.' )
        self.OPTIONS['FILTHY_MORALE']['HINTLONG'] = self.translate_marker( 'If True, filthy clothing will cause morale penalties.' )

        self.OPTIONS['FILTHY_WOUNDS'] = {}
        self.OPTIONS['FILTHY_WOUNDS']['VALUE'] = False
        self.OPTIONS['FILTHY_WOUNDS']['TYPE'] = 'world_default'
        self.OPTIONS['FILTHY_WOUNDS']['HINT'] = self.translate_marker( 'Infected wounds from filthy clothing.' )
        self.OPTIONS['FILTHY_WOUNDS']['HINTLONG'] = self.translate_marker( 'If True, hit in a body part covered in filthy clothing may cause infections.' )

        self.OPTIONS['DISABLE_VITAMINS'] = {}
        self.OPTIONS['DISABLE_VITAMINS']['VALUE'] = False
        self.OPTIONS['DISABLE_VITAMINS']['TYPE'] = 'world_default'
        self.OPTIONS['DISABLE_VITAMINS']['HINT'] = self.translate_marker( 'Disables tracking vitamins in food items.' )
        self.OPTIONS['DISABLE_VITAMINS']['HINTLONG'] = self.translate_marker( 'If True, vitamin tracking and vitamin disorders.' )

        self.OPTIONS['NPCS_NEED_FOOD'] = {}
        self.OPTIONS['NPCS_NEED_FOOD']['VALUE'] = False
        self.OPTIONS['NPCS_NEED_FOOD']['TYPE'] = 'world_default'
        self.OPTIONS['NPCS_NEED_FOOD']['HINT'] = self.translate_marker( 'Disables tracking food, and ( partially ) fatigue for NPCs.' )
        self.OPTIONS['NPCS_NEED_FOOD']['HINTLONG'] = self.translate_marker( 'If True, won\'t need to eat or drink and will only get tired enough to sleep, to get penalties.' )

    def save(self):
        with open('./data/global_options.json', 'w') as json_file:
            json_data = self.OPTIONS
            json.dump(json_data, json_file, sort_keys = True, indent = 4, ensure_ascii = False)

    def load(self):
        with open('./data/global_options.json', 'r') as json_file:
            json_data = json.load(json_file)
            self.OPTIONS = json_data


    def get_option_value(self, option):
        if(option in self.OPTIONS):
            return option['VALUE']
        else:
            print('option not found: ' + str(option))


    def get_option(self, option):
        if(option in self.OPTIONS):
            return option
        else:
            print('option not found: ' + str(option))
            
