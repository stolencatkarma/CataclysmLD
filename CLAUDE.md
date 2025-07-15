# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cataclysm: Looming Darkness is a multiplayer rewrite of Cataclysm: Dark Days Ahead in Python. It's a survival game with client-server architecture using TCP networking and tcod for client rendering.

## Development Commands

### Server
```bash
# Start server (Windows)
run_server.bat

# Start server (manual)
python server.py

# Server configuration
# Edit server.cfg for settings like port (6317), max_players, city_size, etc.
```

### Client
```bash
# Start client (Windows)
run_client.bat

# Start client (manual)
pip install -r client_requirements.txt
python client.py

# Connect to remote server
python client.py --host <ip> --port 6317
```

### Dependencies
- Client requires: `tcod>=13.8.0`, `numpy>=1.20.0`
- No automated testing framework is currently set up
- No linting tools are configured

## Architecture

### Server Architecture (`server.py`)
- **MastermindServerTCP**: Custom TCP server handling client connections
- **Worldmap**: Chunk-based world storage system with JSON persistence
- **Managers**: Separate managers for recipes, professions, monsters, items, furniture, tiles
- **Game Loop**: Turn-based system with `compute_turn()` processing all character/monster command queues
- **Calendar System**: Game time tracking via GameCalendar

### Client Architecture (`client.py`)
- **CataclysmClient**: Main client class with threading for network communication
- **GameState Enum**: LOGIN → CHARACTER_SELECT → CHARACTER_CREATION → PLAYING
- **Modular UI**: Separated into UIManager, MapRenderer, CharacterManager in `src/client/`
- **tcod Integration**: Console-based rendering with ASCII graphics

### Core Systems

#### World Management
- **Chunks**: World divided into chunks stored as `x_y.chunk` files in `/world/`
- **Position System**: Absolute coordinates with chunk loading/unloading
- **Persistence**: JSON-based saving of world state, characters, and game data

#### Data-Driven Design
- **JSON Configuration**: Items, recipes, professions, monsters in `/data/json/`
- **Mapgen**: Template-based map generation in `/data/json/mapgen/`
- **Localization**: Multi-language support in `/data/names/` and `/data/credits/`

#### Network Protocol
- **JSON Messages**: All client-server communication via JSON over TCP
- **Command Pattern**: Commands sent as objects with `ident`, `command`, `args`
- **Mastermind Framework**: Custom networking layer in `src/mastermind/`

### Key Files
- `server.py`: Main server entry point and game logic
- `client.py`: Complete client implementation
- `src/worldmap.py`: World chunk management and persistence
- `src/character.py`: Character class inheriting from Creature
- `src/mastermind/`: Custom TCP networking framework
- `src/client/`: Modular client UI components

## Working with the Codebase

### Character System
Characters inherit from Creature class and use dict-like access patterns. Account data stored in `/accounts/` with hashed passwords.

### World Modification
Add new content via JSON files in `/data/json/`. The server loads these automatically on startup.

### Client Extensions
UI components are modular. Add new features by extending UIManager, MapRenderer, or CharacterManager classes.

### Debugging
Server logs to console and `/log/server.log` with configurable logging levels in `server.cfg`.