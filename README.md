Cataclysm: Looming Darkness
===

A multiplayer rewrite of Cataclysm: Dark Days Ahead in python. 

Made with python 3.9.0 64 bit and Mastermind for the TCP backend.

----

A playable release is coming soon and will follow an episodic pattern, with each release adding more:

* Chapter 1 - Immediately after the cataclysm. This will be the minimum playable product.
* Chapter 2 - Vehicles. One of the more complex - and enjoyable - systems in C:DDA.
* Chapter 3 - Bionics and Mutations. The main sci-fi elements of the game brought to multiplayer.
* Chapter 4+ - Continued expansion, maps, and content.

----

Generic installation instructions

---

* install python 3.9 64bit or greater on any OS that supports it. (python 2 not supported at this time.)

**Running a server**

* execute `python3 ./server.py` from a command line - the first time you start the server a world is generated automatically using default settings. This does take a few minutes or longer on older hardware. Newer hardware should be less than 10 seconds.

**connecting to a server.**

* The current recommendation is to use a MUD client to connect to the server until a proper client can be made. Mudlet is my preferred method.
* `127.0.0.1:6317` is the default IP and port you will need to connect to it.
       

