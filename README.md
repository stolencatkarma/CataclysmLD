Cataclysm: Looming Darkness
===

A multiplayer re-imagining of Cataclysm: Dark Days Ahead.

Currently the pre-release of the client and server is available for download.
We are currently reworking the client to use pyglet and glooey as pygame was
not working for our needs.

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

