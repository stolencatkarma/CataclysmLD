#!/usr/bin/env python3

"""
Simple client launcher script that checks for dependencies
and provides instructions for setting up the client.
"""

import sys
import os
import subprocess


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True


def check_tcod():
    """Check if tcod is installed"""
    try:
        import tcod
        print(f"tcod version: {tcod.__version__}")
        return True
    except ImportError:
        print("tcod is not installed")
        return False


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "client_requirements.txt"
        ])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return False
    except FileNotFoundError:
        print("pip not found. Please install pip first.")
        return False


def create_font_directory():
    """Create font directory and download font if needed"""
    font_dir = "data/fonts"
    font_file = "data/fonts/dejavu10x10_gs_tc.png"
    
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
        print(f"Created directory: {font_dir}")
    
    if not os.path.exists(font_file):
        print(f"Font file not found: {font_file}")
        print("You can download tcod fonts from:")
        print("https://github.com/libtcod/libtcod/tree/main/data/fonts")
        print("Or the client will use the default font.")
        return False
    
    return True


def main():
    """Main launcher function"""
    print("Cataclysm: Looming Darkness Client Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check if tcod is available
    if not check_tcod():
        print("\nAttempting to install requirements...")
        if not install_requirements():
            print("Please install tcod manually:")
            print("  pip install tcod")
            return 1
        
        # Check again after installation
        if not check_tcod():
            print("Installation failed. Please install tcod manually.")
            return 1
    
    # Create font directory
    create_font_directory()
      # Import and run the client
    try:
        print("\nStarting simple client...")
        from simple_client import main as client_main
        client_main()
    except ImportError as e:
        print(f"Failed to import client: {e}")
        print("Trying original client...")
        try:
            from client import main as client_main
            client_main()
        except Exception as e2:
            print(f"Both clients failed: {e2}")
            return 1
    except Exception as e:
        print(f"Client error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
