Cataclysm: Looming Darkness
===

A multiplayer re-imagining of Cataclysm: Dark Days Ahead.

Currently the WYSIWYG building editor and pre-release of the client and server have been released.

----

Made with python 3.6 and pygame using Mastermind for the TCP backend.

The current release date for Chapter 1 is May 13th and will include the base game and level 1 difficulty areas and monsters.

You can follow along on discord at https://discord.gg/EqNQ784.

Generic installation instructions
---

* install python 3.6
* install pip - if on windows: https://pip.pypa.io/en/stable/installing/
* open a command shell and goto the Cataclysm:LD folder you downloaded and unzipped it to.
* `pip install pygame`

---
Usage for the Building Editor.

* `python ./WYSIWYG.py`
* Left clicking a tile will apply the terrain or furniture at the location.
* Right clicking a tile will clear the tile and set it to fill terrain.
* Scroll wheel (mouse buttons 4 & 5) scrolls the terrain, furniture, and item list.

Exports and imports work but only for a single file called `buildingeditortest.json` in the root directory.

---

**Running a server**

* note: disable city gen after the first time you start it. This is a known issue.
* `python server.py [--host Host] [-p Port]`,
        Host and Port are optional (defaults are `0.0.0.0:6317`)
* `python server.py --help` for detailed usage


**Running a client**

* `python client.py [--host Host] [-p Port] first_name last_name`,
        where `Host` and `Port` are those of the server.
        By default `Host` is `localhost`, `Port` is 6317,
        so it's safe to ommit them if you're running server locally.
* type `python client.py --help` for detailed usage information.