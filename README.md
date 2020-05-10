
This project is centralized around 2 main components:
- An arduino board manager. 
This component control the connextion/deconection of boards.
Using an arduino-cli wrapper, it can compile and upload sketches to connected boards
- A program registery.
This registry recursively looks inside of a directory for the ino programs.
When a boad is connected the registery can tell the last program that was uploaded to it.