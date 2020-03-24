# roguelike-tutorial
So, after a week of confinement due to COVID-19, I have decided to follow the Python tutorial at [roguebasin](http://www.roguebasin.com/index.php?title=Main_Page).


## Development status

I'm currently [here](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_5).


#### 22/03/2020

* [Part 0](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_0)
* [Part 1](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_1)
* [Part 2](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_2)
* [Part 3](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_3)

#### 23/03/2020

* [Part 4](http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python3%2Blibtcod,_part_4)

#### 24/03/2020

## List of modifications

Below you can find a list of things that I have done, up to he point were I am currently, different from the tutorial:

- Instead of each object drawing and clearing itself, rendering is handled by an independent class (`Renderer`).
- The player class is in charge of handling its key events. It receives the key pressed and decides how to act.
- The game map is a class instead of a list of lists.
- The dungeon has more than one level (it enables having `N` levels). Change level by using `z` to go up and `x` to go down when on a stair tile.

## TODO List

- [ ] Document code.
- [ ] Only show objects that are in the current level.
- [ ] Change color palette.
- [ ] Add option to play with alphanumeric chars instead of colours.
- [x] Add stairs to move between dungeon levels.
- [x] Fix field of view.
