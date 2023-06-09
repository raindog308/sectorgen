![sectorgen logo](https://github.com/raindog308/sectorgen/blob/main/art/sectorgen_github.png "sectorgen")

## full-featured sector maps for roleplaying games

sectorgen generates 8x10 space sector hex maps.  These are similar to the classic Traveller-style maps we all know and love, but with a different emphasis.

- All information is easily readable on the map. You don't need to look up hex 0506 to see generated data. Everything is represented in the hex itself.

- More narrative focus than simulationist. So instead of telling you the hydrosphere score, sectorgen gives you an icon representing a lighthouse icon. Does that mean that the mainworld has a strong seafaring culture, or that it's a warning point for interstellar danger, or that it's a beacon of hope?

sectorgen is a Python script is tunable on many dimensions. It produces a 6400x9000 PNG file. On a Macbook M1 Max, it takes between 8-10 seconds depending on how many hexes are settled.

The generated maps are finely detailed but are perfect for use on a tablet or computer where you can zoom in to focus on where you're adventuring.

# Example

This example is scaled down to 1200x1800.  The actual sectorgen output is 6400x9000.  You can [download the full example.png here](https://github.com/raindog308/sectorgen/blob/main/example.png) (example.png in the repo), though you should probably save it and open it locally as GitHub will cut off much of the image.

![sectorgen logo](https://github.com/raindog308/sectorgen/blob/main/example-1200x1800.png "sectorgen example.png scaled down")

# Just Want Some Maps?

If you just want to use some maps rather than generate your own, look in the 'maps' directory, which contains

- 100 maps in maps/normal
- 100 maps in maps/wacky with turn_on_wackiness set to True.  This adds fun icons (Taco Bell, superheroes, Star Wars, and more)

# Instructions

sectorgen is a Python 3 script.  It requires wand: http://docs.wand-py.org

Review etc/sectorgen.ini.  Then run sectorgen.py

# Status

sectorgen works.  Documentation is coming.

# Credits

Various ideas taken from Traveller and Ironsworn: Starforged.

Planet names were generated from: https://github.com/sayamqazi/planet-name-generator

All fonts come from two sources and all are listed as "public domain", "GPL", "OFL", "100% Free", or "Free for personal use":

- dafont.com
- 1001freefonts.com
