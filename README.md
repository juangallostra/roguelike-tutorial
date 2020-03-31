# roguelike-tutorial
So, after a week of confinement due to COVID-19, I have decided to follow the Python tutorial at [roguebasin](http://www.roguebasin.com/index.php?title=Main_Page). 

The tutorial can be found [here](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod). 


## Development status

I'm currently on [Part 13](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_13).


#### 22/03/2020

* [Part 0](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_0)
* [Part 1](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_1)
* [Part 2](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_2)
* [Part 3](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_3)

#### 23/03/2020

* [Part 4](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_4)

#### 24/03/2020

* [Part 5](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_5)

#### 25/03/2020

* [Part 6](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_6)

#### 26/03/2020

* [Part 7](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_7)

#### 27/03/2020

* [Part 8](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_8)
* [Part 9](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_9)

#### 28/03/2020

* [Part 10](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_10)

#### 29/03/2020

* [Part 11](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_11)

#### 31/03/2020

* [Part 12](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_12)


## List of modifications

Below you can find a list of things that I have done, up to he point were I am currently, different from the tutorial:

- Avoid the use of global variables.
- Console message logging system is a component of the objects that log messages.
- Instead of each object drawing and clearing itself, rendering is handled by an independent class (`Renderer`).
- The player class is in charge of handling its key events. It receives the key pressed and decides how to act.
- The game map is a class instead of a list of lists.
- The dungeon levels are all created when the game starts instead of generating them on the go when the player changes level. This allows the user to move freely between levels, although it comes at the cost of using more memory.
- Enable loading custom tilesets. This is covered in the extras section.

## TODO List

- [ ] Move strings to constants (key codes, object names, etc.).
- [ ] Add method in objects to relocate them in array so that they are drawn in the correct order.
- [ ] Check real time combat.
- [ ] Check if `libtcod` can load both a font and a tileset from diferent files. 
- [ ] Create a tileset loader that handles all the required operations. (retro/no retro, only chars/chars and colors, etc.)
- [ ] Document code.
- [ ] Change color palette.
- [ ] Add option to play with alphanumeric chars instead of colors/tilesets.
- [x] Bug in message log order when killing monsters.
- [x] Investigate how to use custom tilesets.
- [x] Add stairs to move between dungeon levels.
- [x] Fix field of view.
- [x] Only show objects that are in the current level.
