Cataclysm: Looming Darkness
===

A multiplayer rewrite of Cataclysm: Dark Days Ahead in python. 

1-24-19 update - This codebase is moving to a more mud-style clientless telnet system where player's will connect
                 to the game using a telnet or MUD client.

----

A playable release is coming soon and will follow an episodic pattern, with each release adding more:

* Chapter 1 - Immediately after the cataclysm. This will be the minimum playable product.
* Chapter 2 - Vehicles. One of the more complex - and enjoyable - systems in C:DDA.
* Chapter 3 - Bionics and Mutations. The main sci-fi elements of the game brought to multiplayer.
* Chapter 4+ - Continued Expansion. Maps, graphics, and content on for as long as there are people willing to work on it.


----

Made with python 3.7.0 64 bit and Mastermind for the TCP backend.

Generic installation instructions

---

* install python 3.4 64bit or greater on any OS that supports it. (python 2 not supported at this time.)

---

**Running a server**

* `python3 ./server.py` - the first time you start the server a world is generated automatically using default settings. This does take a few minutes or longer on older hardware.

**connecting to a server.**

* `telnet 127.0.0.1 6317` from a command-line. default port is 6317 but can be changed in server.cfg
       

