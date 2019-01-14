Cataclysm: Looming Darkness
===

A multiplayer re-imagining of Cataclysm: Dark Days Ahead.

Currently the pre-release of the client and server is available for download.
We are currently reworking the client to use pyglet and glooey as pygame was
not working for our needs.

----

A playable release is coming soon and will follow an episodic pattern, with each release adding more:

Episode 1 - Immediately after the cataclysm. This will be the minimum playable product.
Episode 2 - Vehicles. One of the more complex - and enjoyable - systems in C:DDA.
Episode 3 - Bionics and Mutations. The main sci-fi elements of the game brought to multiplayer.
Episode 4+ - Continued Expansion. Maps, graphics, and content on for as long as there are people willing to work on it.

Helping hands are always welcome, especially those familiar with pyglet and glooey. If you'd like to contribute follow the Discord link below.

----

Made with python 3.7.0 64 bit and pyglet+glooey using Mastermind for the TCP backend.

Discord: https://discord.gg/EqNQ784

Generic installation instructions

---

* install python 3.4+
* install pip3 - if on windows: https://pip.pypa.io/en/stable/installing/
* open a command shell and goto the Cataclysm:LD folder you downloaded and unzipped it to.
* `pip install pyglet glooey`

---

**Running a server**

* `python3 ./server.py [--host Host] [--port Port]`,
        Host and Port are optional (defaults are `localhost:6317`)

**Running a client**

* `python3 ./client.py [--host Host] [--port Port]`,
        where `Host` and `Port` are those of the server.
        By default `Host` is `localhost` and `Port` is 6317,
        so it's safe to omit them if you are running server locally.

