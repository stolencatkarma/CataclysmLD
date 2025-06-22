# Cataclysm: Looming Darkness - Setup Guide

This guide will help you set up both the server and client for Cataclysm: Looming Darkness.

## Prerequisites

- **Python 3.8 or higher** (Download from [python.org](https://python.org))
- **Windows 10/11** (or Linux/macOS with appropriate modifications to scripts)

## Quick Setup (Windows)

### 1. Install Python
Download and install Python from python.org. Make sure to check "Add Python to PATH" during installation.

### 2. Set Up the Server
1. Open Command Prompt or PowerShell in the game directory
2. Run: `run_server.bat`
   - This will create necessary directories and start the server
   - The server will listen on port 6317 by default

### 3. Set Up the Client
1. Open a **new** Command Prompt or PowerShell window
2. Run: `run_client.bat`
   - This will install required Python packages and start the client
   - The client will connect to localhost:6317 by default

## Manual Setup

### Server Setup
```bash
# Create required directories
mkdir accounts world log

# Start the server
python server.py
```

### Client Setup
```bash
# Install client dependencies
pip install -r client_requirements.txt

# Start the client
python client.py
```

## Configuration

### Server Configuration
Edit `server.cfg` to modify server settings:
- `listen_address`: Server IP address (default: 127.0.0.1)
- `listen_port`: Server port (default: 6317)
- `city_size`: Size of generated cities (default: 1)
- `time_per_turn`: Game turn speed in seconds (default: 1)

### Client Configuration
The client accepts command-line arguments:
```bash
python client.py --host 192.168.1.100 --port 6317
```

## Gameplay

### First Time Playing
1. Start the server first
2. Start the client
3. Press ENTER to login with default credentials
4. Create a new character (press C) or select an existing one
5. Use arrow keys or numpad to move around

### Controls
- **Movement**: Arrow keys or numpad (8=north, 2=south, 4=west, 6=east, etc.)
- **Look**: L
- **Character sheet**: C
- **Recipes**: R
- **Help**: H
- **Quit**: ESC

### Basic Gameplay Loop
1. Move around and explore the generated city
2. Look around (L) to see items and terrain
3. Bash furniture to get materials
4. Craft items using known recipes
5. Take items and put them in containers
6. Work on blueprints to build structures

## Multiplayer

To play with friends:

### Host (Server)
1. Configure `server.cfg` with your external IP address
2. Forward port 6317 in your router/firewall
3. Start the server with `run_server.bat`
4. Share your external IP address with friends

### Join (Client)
1. Run: `python client.py --host <friend's-ip> --port 6317`
2. Create your character and start playing

## Troubleshooting

### Common Issues

**"Python is not recognized"**
- Reinstall Python and check "Add Python to PATH"
- Or use the full path: `C:\Python39\python.exe`

**"tcod could not be resolved"**
- Run: `pip install tcod`
- If that fails, try: `pip install --upgrade pip` then retry

**"Connection refused"**
- Make sure the server is running first
- Check that the IP address and port are correct
- Verify firewall settings

**Server crashes on startup**
- Check that all required files are present in the data/ directory
- Ensure accounts/ and world/ directories exist

**Client shows black screen**
- Try running with different renderer by modifying client.py
- Update graphics drivers
- Try the default tcod font by not placing any custom fonts

**Character creation fails**
- Check server console for error messages
- Ensure the data/json/ directory contains profession and recipe files

### Performance Issues
- Reduce city_size in server.cfg
- Increase time_per_turn for slower gameplay
- Close unnecessary programs

### Development/Debugging
- Check server console for detailed error messages
- Enable additional logging in server code if needed
- Use print statements for debugging client issues

## File Structure

```
CataclysmLD/
├── server.py              # Main server
├── server.cfg             # Server configuration
├── client.py              # Main client
├── client_ui.py           # Client UI components
├── client_map.py          # Map rendering
├── client_character.py    # Character management
├── run_client.py          # Client launcher
├── run_server.bat         # Windows server launcher
├── run_client.bat         # Windows client launcher
├── client_requirements.txt # Python dependencies
├── src/                   # Server source code
├── data/                  # Game data files
├── accounts/              # Player accounts (created automatically)
├── world/                 # World save files (created automatically)
└── log/                   # Log files (created automatically)
```

## Next Steps

Once you have the game running:
1. Explore the generated city
2. Learn the crafting system
3. Try multiplayer with friends
4. Modify the code to add new features
5. Create custom content in the data/ directory

The game is designed to be moddable and extensible. Check the source code for examples of how to add new items, recipes, monsters, and map generation.
