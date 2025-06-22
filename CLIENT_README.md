# Cataclysm: Looming Darkness Client

A Python-tcod client for the Cataclysm: Looming Darkness multiplayer survival game.

## Client Overview

- **File**: `client.py`
- **Description**: Full-featured client with modular UI components
- **Features**: Enhanced graphics, detailed UI panels, extensible architecture

## Quick Start

### Fastest Way to Play
```bash
# Start the server first
python server.py

# In another terminal, start the client
python client.py
```

### Windows Batch Files
```bash
# Start server
run_server.bat

# Start client
run_client.bat
```

## Controls

### Login/Character Selection
- **ENTER**: Login with default credentials or select character
- **C**: Create new character
- **ESC**: Quit

### In-Game Movement
- **Arrow Keys** or **Numpad**: Move character
  - 8/↑: North
  - 2/↓: South
  - 4/←: West
  - 6/→: East
  - 7: Northwest
  - 9: Northeast
  - 1: Southwest
  - 3: Southeast

### In-Game Commands
- **L**: Look around
- **C**: View character sheet
- **R**: View known recipes
- **H**: Show help
- **ESC**: Quit game

## Game Features

The client provides:
- Real-time multiplayer connection to the server
- Graphical map display using ASCII characters
- Character information panel
- Message log
- Command interface

### Map Symbols
- `@`: Your character
- `#`: Walls
- `.`: Floor/ground
- `+`: Closed door
- `/`: Open door
- `"`: Window
- `~`: Water
- `T`: Tree
- `!`: Items
- `B`: Blueprint
- `f`: Furniture
- `M`: Monster

## Technical Details

### Architecture
The client is built with:
- **tcod**: For graphics and input handling
- **threading**: For non-blocking network communication
- **json**: For server communication protocol

### Files
- `client.py`: Main client application (all logic is now unified here)
- `run_client.bat`: Launcher script with dependency checking

### Communication Protocol
The client communicates with the server using JSON messages over TCP:
- Commands are sent as JSON objects with `ident`, `command`, and `args` fields
- Server responses include game state updates, map data, and character information

## Troubleshooting

### Common Issues

1. **"tcod could not be resolved"**
   - Install tcod: `pip install tcod`
   - Ensure you're using Python 3.8+

2. **Connection errors**
   - Verify the server is running
   - Check the host/port settings
   - Ensure firewall allows the connection

3. **Font not found**
   - The client will work with default fonts
   - Download tcod fonts from the official repository if needed

4. **Graphics issues**
   - Try different renderers by modifying the tcod context setup in client.py
   - Update graphics drivers

### Development

To modify or extend the client:
- The main game loop and all UI logic are in `client.py`
- The code is designed to be modular and extensible for adding new features.

## Server Compatibility

This client is designed to work with the Cataclysm: Looming Darkness server. Ensure both client and server are using compatible versions of the communication protocol.
