import time
### Globals #########################################################
CORE_VERSION = 1
seed = time.time()
test_mode = False
verifyexit = False
check_mods = False
GAME_WIDTH, GAME_HEIGHT = 800, 600
TILESETS = [] # All found tilesets: <name, tileset_dir>
SOUNDPACKS = [] # All found soundpacks: <name, soundpack_dir>
OPTIONS = {} # the dict containing all the options.
HP_HEIGHT = 14
HP_WIDTH = 7
MINIMAP_HEIGHT = 7
MINIMAP_WIDTH = 7
MONINFO_HEIGHT = 12
MONINFO_WIDTH = 48
MESSAGES_HEIGHT = 8
MESSAGES_WIDTH = 48
LOCATION_HEIGHT = 1
LOCATION_WIDTH = 48
STATUS_HEIGHT = 4
STATUS_WIDTH = 55
EXPLOSION_MULTIPLIER = 7
MAPSIZE = 12
SEEX = 12
SEEY = 12
SEEZ = 12
MAX_VIEW_DISTANCE = SEEX * int(MAPSIZE / 2)
OMAPX = 256
OMAPY = 256
OMAPZ = 10
CORE_VERSION = 6
DANGEROUS_PROXIMITY = 5
PICKUP_RANGE = 6
# Number of z-levels below 0 (not including 0). */
OVERMAP_DEPTH = 10
# Number of z-levels above 0 (not including 0). */
OVERMAP_HEIGHT = 10
# Total number of z-levels */
OVERMAP_LAYERS = 1 + OVERMAP_DEPTH + OVERMAP_HEIGHT
# Maximum move cost when handling an item */
MAX_HANDLING_COST = 400
# Move cost of accessing an item in inventory. */
INVENTORY_HANDLING_PENALTY = 100
# Move cost of accessing an item lying on the map. @todo Less if player is crouching */
MAP_HANDLING_PENALTY = 80
# Move cost of accessing an item lying on a vehicle. */
VEHICLE_HANDLING_PENALTY = 80
# Amount by which to charge an item for each unit of plutonium cell */
PLUTONIUM_CHARGES = 500
# EFFECT_STR allows lifting of heavier objects */
STR_LIFT_FACTOR = 50 # measured in kg
# Weight per level of LIFT/JACK tool quality */
TOOL_LIFT_FACTOR = 500
# Cap JACK requirements to support arbitrarily large vehicles */
JACK_LIMIT = 8500
# Maximum density of a map field */
MAX_FIELD_DENSITY = 3
# Slowest speed at which a gun can be aimed */
MAX_AIM_COST = 10
# Maximum (effective) level for a skill */
MAX_SKILL = 10
# Maximum (effective) level for a stat */
MAX_STAT = 20
# Maximum range at which ranged attacks can be executed */
RANGE_HARD_CAP = 60
# Accuracy levels which a shots tangent must be below */
accuracy_headshot = 0.1
accuracy_critical = 0.2
accuracy_goodhit  = 0.5
accuracy_standard = 0.8
accuracy_grazing  = 1.0
# Minimum item damage output of relevant type to allow using with relevant weapon skill */
MELEE_STAT = 5
# Effective lower bound to combat skill levels when CQB bionic is active */
BIO_CQB_LEVEL = 5
MAX_RECOIL = 3000
