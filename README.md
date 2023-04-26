# sectorgen: full-featured sector maps for roleplaying games

copyright (c) 2023 Andrew Fabbro (raindog308) - MIT License

sectorgen generates 8x10 space sector hex maps.

These are similar to the classic Traveller-style maps we all know and love, but with a different emphasis.

- All information is easily readable on the map. You don't need to look up hex 0506 to see generated data. Everything is represented in the hex itself.

- More narrative focus than simulationist. So instead of telling you the hydrosphere score, sectorgen gives you an icon representing a lighthouse icon. Does that mean that the mainworld has a strong seafaring culture, or that it's a warning point for interstellar danger, or that it's a beacon of hope?

sectorgen is a Python script is tunable on many dimensions. It produces a 6400x9000 PNG file. On a Macbook M1 Max, it takes between 8-10 seconds depending on how many hexes are settled.

The generated maps are finely detailed but are perfect for use on a tablet or computer where you can zoom in to focus on where you're adventuring.

# Just Want Some Maps?

A set of 100 generated maps are provided in the "maps" sub direectory. All were created using the default parameters.

25 have "wackiness" turned on, which means you may see icons for Taco Bell, Star Wars, unicorns, burger and fries, and such.

# Credits

Various ideas taken from Traveller and Ironsworn: Starforged.

Planet names were generated from: https://github.com/sayamqazi/planet-name-generator

All fonts come from two sources and all are listed as "public domain", "GPL", "OFL", "100% Free", or "Free for personal use":

- dafont.com
- 1001freefonts.com
