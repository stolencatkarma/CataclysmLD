Cataclysm: Looming Darkness
===

A multiplayer reimagining of Cataclysm Dark Days Ahead.

Currently only the WYSIWYG building editor has been released.

----

Made with python 3.6 and pygame using Mastermind for the TCP backend.

The current release date for Chapter 1 is May 13th and will include the base game and level 1 difficulty areas and monsters.

You can follow along on discord at https://discord.gg/EqNQ784.

Generic installation instructions
---

* install python 3.6
* install pip - if on windows - https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation
* open a command shell and goto the Cataclysm:LD folder you downloaded and unzipped it to.
* `pip install pygame`
* `python ./WYSIWYG.py`

Usage

---

* Left clicking a tile will apply the terrain or furniture at the location.
* Right clicking a tile will clear the tile and set it to fill terrain.
* Scroll wheel (mouse buttons 4 & 5) scrolls the terrain, furniture, and item list.

Exports and imports work but only for a single file called `buildingeditortest.json` in the root directory.

---

* Running a server.
* edit server.py for your specific setup for IP and port.
* note: disable city gen after the first time you start it. This is a known issue.
* `python ./server.py`

* Running a client.
* edit client.py to point to the server ip and address.
* `python ./client.py`
