# stuff commonly used by sectorgen.py and and shex.py

import configparser, math, random, re, sys, uuid
from glyph import Glyph
import wand
from wand.color import Color
from wand.image import Image
from wand.drawing import Drawing

def d6():
    return random.randint(1,6)

def d10():
    return random.randint(1,10)

def d100():
    return random.randint(1,100)

def debug(message):
    if config.getboolean('development','debug') == True:
        print (message)

def trace(section,message):
    trace_section = "trace_{0:s}".format(section)
    if config.getboolean('development',trace_section) == True:
        print (message)

def load_glyph_file(file_name):
    glyphs = []
    debug("loading glyph file: {0:s}".format(file_name))
    lines = [line.rstrip() for line in open(file_name, "r")]
    debug("there are {0:d} lines in {1:s}".format(len(lines), file_name))
    for line in lines:
        line = line.rstrip()
        if (re.match('#', line)):
            trace("glyphs",'skipping comments line: {0:s}'.format(line))
            continue
        if (re.match('^$', line)):
            trace("glyphs","skipping blank line")
            continue
        ( font , rest ) = line.split ( '.',maxsplit=1)
        rest_parts = rest.split(' ')
        font = "{0:s}.{1:s}".format( font, rest_parts[0] )
        character = rest_parts[1]
        if ( len(character) > 1 ):
            character = chr( int ( character, 16) )
        glyphs.append ( Glyph ( font, character ) )
        trace('glyphs','adding glyph: {0:s} {1:s}'.format(font, character))
    debug('loaded {0:d} glyphs'.format(len(glyphs)))
    return glyphs

config = configparser.ConfigParser()
config.read('etc/sectorgen.ini')

# we need to immediately process the random seed here before any use
# of python's random module.

# random seed
random_seed = config.get('options','random_seed')
if random_seed != '':
    random.seed(random_seed)
else:
    random_seed = str ( uuid.uuid4() )
    random.seed(random_seed)

img_height = 9000
img_width = 6400

hex_height = 780
half_hex_height = int ( hex_height / 2 )
quarter_hex_height = int ( math.ceil (( half_hex_height / 2 ) ) )
hex_line_width = 450
half_hex_line_width = int ( hex_line_width / 2 )

# tlhex = "top left hex"
tlhex_center_x = 840
tlhex_center_y = 800

debug_slider = 0

comets = []
features = []
planet_names = []

debug("sector init")

# load planet names

planet_names = [line.rstrip() for line in open(config['files']['planet_names'], "r")]
random.shuffle(planet_names)
debug('loaded {0:d} planet names'.format(len(planet_names)))

# load glyphs

debug('loading comets')
comets = load_glyph_file ( config['glyph_files']['comets'] )
debug('loaded {0:d} comets'.format(len(comets)))

debug('loading features')
features = load_glyph_file ( config['glyph_files']['features'] )
debug('loaded {0:d} features'.format(len(features)))

if config.getboolean('options','turn_on_wackiness'):
    debug('loading wacky features')
    features.extend ( load_glyph_file ( config['glyph_files']['wacky_features'] ) )
    debug('features now has {0:d} glyphs'.format(len(features)))

    debug('loading wacky comets')
    comets.extend ( load_glyph_file ( config['glyph_files']['wacky_comets'] ) )
    debug('comets now has {0:d} glyphs'.format(len(comets)))

# shuffle comets

random.shuffle(comets)

# shuffle features

if config.getboolean('development','use_features_in_order'):
    debug('not shuffling features because use_features_in_reverse_order is set')
elif config.getboolean('development','use_features_in_reverse_order'):
    debug('reversing and not shuffling features because use_features_in_reverse_order is set')
    features.reverse()
else:
    random.shuffle(features)


img = Image ( 
    height = img_height , 
    width = img_width , 
    background = Color('black') ) 
# this is set explicitly because displey() bombs without it
img.format = 'png'
