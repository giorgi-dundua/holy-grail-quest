# Holy Grail Quest

A small terminal adventure inspired by Monty Python and the Holy Grail.

You play as King Arthur. Your goal is to defeat the Black Knight,
cross his bridge, and reach Witch Trial Village.

This version covers the first chapter of the adventure.

## What you can do

- Move between three locations.
- Look around and check your health and inventory.
- Collect items and use a biscuit to restore health.
- Talk to Patsy and invite him to join you.
- Fight the Black Knight and open the blocked path.

Reaching the village completes the chapter.
Losing all your health ends the game.

## How to run

You need Python 3.10 or newer. No extra packages are needed.

Open a terminal in this folder and run:

```bash
python main.py
```

Enter the number shown beside an option.
In selection menus, enter `0` to go back.

## Project files

- `main.py` starts the program.
- `game.py` creates the world and rules.
- `terminal.py` handles loop, menus and rendering. 
- `models.py` contains the character, item, and location classes.

The terminal chapter was completed for the Lexicon Python Fundamentals assignment.
Further development is a learning-led hobby project toward a retro browser version.
The browser version is planned and has not been implemented yet.
