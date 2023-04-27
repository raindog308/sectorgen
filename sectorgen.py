#!/usr/bin/env python3

# sectorgen
# by andrew fabbro <andrew@fabbro.org> (raindog308)
# https://github.com/raindog308/sectorgen
# see LICENSE for license image (spoiler: MIT)

import os, random, sys, time
from wand.color  import Color
from wand.drawing import Drawing
from wand.display import display
sys.path.append('lib')
import common
from common import config, d10, d100, debug, planet_names, trace
from shex import Shex

# you may need these for macOS.  I admit I just googled them.
os.environ['WAND_MAGICK_LIBRARY_SUFFIX'] = "-7.Q16HDRI;-6.Q16HDRI"
os.environ['MAGICK_HOME'] = "/opt/homebrew"

def adjacent_hexes(col, row, criteria):
    col = int(col)
    row = int(row)
    trace('adjacent', "adjacent_hexes(): called for {0:d},{1:d}".format(col, row))
    adjacents = []

    if col % 2 == 0: # even
        hexes_to_check = {
            'N': (col, row - 1),
            'NE': (col + 1, row),
            'SE': (col + 1, row + 1),
            'S': (col, row + 1),
            'NW': (col - 1, row ),
            'SW': (col - 1, row + 1)
        }
    else:
        hexes_to_check = {
            'N': (col, row - 1),
            'NE': (col + 1, row - 1),
            'SE': (col + 1, row ),
            'S': (col, row + 1),
            'NW': (col - 1, row -  1),
            'SW': (col - 1, row )
        }

    trace('adjacent', 'here is the criteria:')
    trace('adjacent', criteria)

    for this_hex in hexes_to_check:
        (this_col, this_row) = (hexes_to_check[this_hex])
        if hexes_to_check[this_hex] in criteria:
            trace('adjacent', "adjacent_hexes():   {0:2s} is hex {1:02d}{2:02d}: yes".format(
                this_hex, this_col, this_row))
            adjacents.append(this_hex)
        else:
            trace('adjacent', "adjacent_hexes():   {0:2s} is hex {1:02d}{2:02d}: no".format(
                this_hex, this_col, this_row))
    trace('adjacent', 'adjacent_hexes(): here are the adjacent hexes:')
    trace('adjacent', adjacents)

    return sorted(adjacents)

# the adjacency test suite was something I used when
# checking my adjacency algorithm.  and once written, why remove it?
# see below under MAIN for instructions

def run_adjacency_test_suite():
    print ("\n\n>>>begin adjacency test suite\n\n")

    num_ok = 0
    num_failed = 0
    
    test_cases = {
        ( 1, 1 )  : [ 'SE' , 'S' ],
        ( 1, 6 )  : [ 'N' , 'NE', 'SE', 'S' ],
        ( 1, 10 ) : [ 'N', 'NE', 'SE' ],
        ( 2, 10 ) : [ 'NW', 'N', 'NE' ],
        ( 3, 10 ) : [ 'SW', 'NW', 'N', 'NE', 'SE' ],
        ( 4, 1  ) : [ 'SE', 'SW', 'S', 'NE', 'NW'],
        ( 4, 5  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 1  ) : [ 'SE', 'SW', 'S'],
        ( 5, 2  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 3  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 4  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 5  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 6  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 7  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 8  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 9  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 5, 10  ) : [ 'N', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 1  ) : [ 'SE', 'SW', 'S', 'NW', 'NE' ],
        ( 6, 2  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 3  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 4  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 5  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 6  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 7  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 8  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 9  ) : [ 'N', 'S', 'NE', 'SE', 'NW', 'SW'],
        ( 6, 10  ) : [ 'N', 'NE', 'NW'],
        ( 8 , 1 ) : [ 'NW', 'SW', 'S' ],
        ( 8 , 3 ) : [ 'N', 'S', 'NW', 'SW' ],
        ( 8 , 10 ) : [ 'N', 'NW' ]
    }

    for test_case in test_cases:
        ( col, row ) = test_case
        adjacents = adjacent_hexes(col, row, settled)

        correct_answer = sorted ( test_cases[test_case] )
        if adjacents == correct_answer:
            print ("{0:02d}{1:02d} ok".format(col,row))
            num_ok += 1
        else:
            print ("{0:02d}{1:02d} FAILED".format(col,row))
            print ("   expected: {0:s}".format(", ".join(correct_answer)))
            print ("        got: {0:s}".format(", ".join(adjacents)))
            num_failed += 1
    print ("completed {0:d} tests: {1:d} ok, {2:d} failed".format(len(test_cases),num_ok, num_failed))
    if num_failed > 0:
        print ("{0:s}".format(random.choice(["Forza!","I believe in you!","Excelsior!","You have the eye of the tiger!"])))
    sys.exit(1)

def count_adjacent_by_criteria(col, row, criteria):
    return len(adjacent_hexes(col, row, criteria))

def draw_hexagon ( center_x , center_y, color ):
    draw = Drawing()
    draw.fill_color = Color(color)
    draw.stroke_color = Color(color)
    draw.stroke_width = 5
    draw.stroke_opacity = 100

    # top line
    draw.line ( 
        (center_x - common.half_hex_line_width, center_y - common.half_hex_height),
        (center_x + common.half_hex_line_width, center_y - common.half_hex_height)
    )

    # left top
    draw.line ( 
        (center_x - common.half_hex_line_width, center_y - common.half_hex_height),
        (center_x - common.hex_line_width , center_y )
    )

    # right top
    draw.line ( 
        (center_x + common.half_hex_line_width, center_y - common.half_hex_height),
        (center_x + common.hex_line_width , center_y )
    )

    # bottom line
    draw.line ( 
        (center_x - common.half_hex_line_width, center_y + common.half_hex_height),
        (center_x + common.half_hex_line_width, center_y + common.half_hex_height)
    )

    # left bottom
    draw.line ( 
        (center_x - common.hex_line_width, center_y ),
        (center_x - common.half_hex_line_width, center_y + common.half_hex_height)
    )

    # right bottom
    draw.line ( 
        (center_x + common.hex_line_width, center_y ),
        (center_x + common.half_hex_line_width, center_y + common.half_hex_height)
    )

    draw(common.img)

def init_sector_map ( ):
    for col in range ( 0, 8 ):
        x = common.tlhex_center_x + ( col * ( common.hex_line_width + common.half_hex_line_width) )
        
        if ( col % 2 ) != 0: # odd
            y_start = common.tlhex_center_y + common.half_hex_height
        else:
            y_start = common.tlhex_center_y

        for row in range ( 0, 10 ):
            y = y_start + ( row * 780 )
            draw_hexagon ( x, y, "cyan" )

    draw = Drawing()
    draw.fill_color = Color("cyan")
    draw.stroke_color = Color("cyan")
    draw.stroke_width = 5

    # fix up lower left and upper right hexes

    # lower left
    start_y = common.tlhex_center_y + ( 10 * common.hex_height ) - common.half_hex_height
    start_x = common.tlhex_center_x - common.half_hex_line_width
    end_y  = common.tlhex_center_y + ( 10 * common.hex_height ) 
    end_x = common.tlhex_center_x - common.hex_line_width
    draw.line ( 
        ( start_x, start_y ),
        ( end_x, end_y )
    )
    # upper right

    # up right point is start_x, start_y
    start_x = common.tlhex_center_x + ( 7 * ( common.hex_line_width + common.half_hex_line_width) ) + common.hex_line_width
    start_y = common.tlhex_center_y - common.half_hex_height
    end_x = common.tlhex_center_x + ( 6 * ( common.hex_line_width + common.half_hex_line_width) ) + ( common.hex_line_width * 2 )
    end_y = common.tlhex_center_y 
    draw.line ( 
        ( start_x, start_y ),
        ( end_x, end_y )
    )

    # bounding line around hexes

    draw.fill_opacity = 0
    draw.stroke_color = Color("cyan")
    draw.stroke_width = 5

    draw.polyline([ 
        # top left
        ( common.tlhex_center_x - common.hex_line_width , common.tlhex_center_y - common.half_hex_height ),
        # top right
        ( common.tlhex_center_x + common.hex_line_width + ( 7 * ( common.hex_line_width + common.half_hex_line_width) ) , common.tlhex_center_y - common.half_hex_height ),
        # bottom right
        ( common.tlhex_center_x + common.hex_line_width + ( 7 * ( common.hex_line_width + common.half_hex_line_width) ) , common.tlhex_center_y + ( 9 * common.hex_height ) + common.hex_height ),
        # bottom left
        ( common.tlhex_center_x - common.hex_line_width , common.tlhex_center_y + ( 9 * common.hex_height ) + common.hex_height ),
        # top left
        ( common.tlhex_center_x - common.hex_line_width , common.tlhex_center_y - common.half_hex_height )
    ])

    # bold line

    draw.stroke_width = 50
    draw.polyline([ 
        ( 200 , 200 ), 
        ( common.img_width - 200 , 200  ),
        ( common.img_width - 200 , common.img_height - 200 ),
        ( 200 , common.img_height - 200),
        ( 200 , 200 )
    ])

    # outside "edge of paper" line

    draw.stroke_width = 20
    draw.polyline([ 
        ( 0 , 0 ), 
        ( common.img_width, 0 ),
        ( common.img_width , common.img_height ),
        ( 0 , common.img_height ),
        ( 0 , 0 )
    ])

    draw(common.img)

# ###########################################################################
# MAIN
# ###########################################################################

# you could run the adjacency test suite here, but it's only
# useful if you were developing the adjacency algorithm.
# needs to have tuning.chance_hex_is_settled set to 100 for it to work.
# the suite will run and then exit.
# s.run_adjacency_test_suite()

start_time = time.time()

map = {}
settled = []
alerts = {}
comm_icons = []
alert_colors = [ 'yellow', 'orange', 'red']

for alert_color in alert_colors:
    alerts[alert_color] = []

# sector name
# we'll pick one of the first 8 planet names, because
# that way the name will show up in the sector 
# itself.  if chance_settled is set very low, no problem.  
# shex.settle() using pop(0) to select planet names

which_name = random.randint(0, 18)
which_name2 = random.randint(6, 12)
sector_name = planet_names[which_name].rstrip().title()
roll = d10()
if roll <= 3:
    sector_name = planet_names[which_name].rstrip().title()
elif roll >= 4 and roll <= 7:
    sector_name = "{0:s}-{1:s}".format ( 
        planet_names[which_name].rstrip().title() , 
        planet_names[which_name2].rstrip().title()
    )
else:
    sector_name = "{0:s} {1:s}".format (
        planet_names[which_name].rstrip().title(),
        random.choice([ 'Alpha', 'Beta', 'Gamma', 'Delta', 'Omicron', 'Epsilon',
                        'Zeta', 'Theta', 'Kappa', 'Omni', 'Sigma', 'Tau', 'Omega'])
    )
sector_name = "{0:s} Sector".format(sector_name)

# gen hexes

debug('creating sector map')
init_sector_map()

# initialize hexes and settle sector

debug('generating settled map')
for col in range(1, 9):
    for row in range(1, 11):

        # init hex
        map[ ( col , row) ] = Shex(col,row)

        # roll to see if it should be settled
        roll = d100()
        if (roll <= config.getint('tuning','chance_hex_is_settled')):
            trace('settled', "{0:02d}{1:02d} yes".format(col, row))
            settled.append((col , row))
            map[ ( col , row) ].settle()
        else:
            trace('settled', "{0:02d}{1:02d} not settled (rolled {2:d})".format(col, row, roll))
debug("there are {0:d} settled hexes".format(len(settled)))

# paths

trace('paths','generating paths')
for col in range(1, 9):
    for row in range(1, 11):
        if ( col, row ) in settled:
            for adj in adjacent_hexes ( col , row , settled):
                trace ("paths","{0:d},{1:d} considering adjacent {2:s}".format(col, row, adj))
                if d100() < config.getint('tuning','chance_path'):
                    trace('paths','added path at {0:s}: {1:s}'.format (
                        map[ ( col, row )].hex_number,
                        adj
                    ))
                    map[ ( col, row )].add_path(adj)
                    trace ("paths","{0:d},{1:d} added {2:s}".format(col, row, adj))

# generate alerts

debug("generating alerts map")
trace('alerts', 'alerts 1st pass: starting')
num_alerts = 0
for col in range(1, 9):
    for row in range(1, 11):
        if (col, row) not in settled:
            continue
        if (d100() <= config.getint('tuning','chance_alert')):
            map[(col,row)].turn_on_alert()
            alerts[ map[(col,row)].alert_color ].append((col, row))
            num_alerts += 1
            trace('alerts', "alerts 1st: {0:s} alert on ( {1:d}, {2:d} )".format(
                map[(col,row)].alert_color, col, row ) )
        else:
            trace('alerts', 'alerts 1st: {0:02d}{1:02d} no'.format(col, row))
trace('alerts',"after 1st pass there are {0:d} alerts".format(num_alerts))
for alert_color in alert_colors:
    trace("alerts", "{0:8s}: {1:d}".format(alert_color, len(alerts[alert_color])))
trace('alerts', 'alerts 2nd pass: starting')
num_first_pass_alerts = num_alerts
for col in range(1, 9):
    for row in range(1, 11):
        if (col, row) not in settled:
            continue
        if (count_adjacent_by_criteria(col, row, alerts) >= 1):
            if (d100() <= config.getint('tuning','chance_alert')):
                trace('alerts', "alerts 2nd: {0:s} alert on ( {1:d}, {2:d} )".format(
                    map[(col,row)].alert_color, col, row ) )
                map[(col,row)].turn_on_alert()
                alerts[ map[(col,row)].alert_color ].append((col, row))
                num_alerts += 1
            else:
                trace('alerts', 'alerts 2nd: {0:02d}{0:02d} no'.format(col, row))
trace("alerts","after 2nd pass there are {0:d} alerts".format(num_alerts))
for alert_color in alert_colors:
    trace("alerts", "{0:8s}: {1:d}".format(alert_color, len(alerts[alert_color])))
trace("alerts","we picked up {0:d} alerts in the 2nd pass".format(num_alerts - num_first_pass_alerts))

# draw the hexes

for shex in map:
    map[shex].draw()

# draw sector name and random seed

draw = Drawing()
for info in [
    { 'name' : 'sector name' , 'text' : sector_name        , 'y' : 230 },
    { 'name' : 'random seed' , 'text' : common.random_seed , 'y' : common.img_height - 180  } ]:

    # compute font size
    draw.font = 'fonts/roboto/Roboto-Thin.ttf'
    ok = False
    font_size = 100
    while ok is False and font_size > 10:
        draw.font_size = font_size
        font_metrics = draw.get_font_metrics (common.img, info['text'])
        if font_metrics.text_width > 4000:
            font_size -= 1
        else:
            ok = True
    debug ("selected font size {0:d} for {1:s}".format(font_size, info['name']) )
    x_pos = int ( ( common.img_width - int(font_metrics.text_width) ) / 2 )

    # erase the bold blue
    # draw.stroke_color = Color('black')
    # draw.stroke_width = 50
    draw.fill_opacity = 100
    draw.fill_color = Color('black')
    draw.stroke_opacity = 0    
    draw.polygon ([
        ( x_pos - 100 , info['y'] - 150 ), 
        ( x_pos - 100 , info['y'] + 150 ), 
        ( x_pos + font_metrics.text_width + 100 , info['y'] + 150 ), 
        ( x_pos + font_metrics.text_width + 100 , info['y'] - 150 )
    ])

    # draw the sector name
    draw.fill_opacity = 100
    draw.fill_color = Color('cyan')
    draw.font = 'fonts/roboto/Roboto-Thin.ttf'
    draw.text ( x_pos, info['y'], info['text'] )

# draw the random seed

font_metrics = draw.get_font_metrics (common.img, common.random_seed)
x_pos = int ( ( common.img_width - int(font_metrics.text_width) ) / 2 )
draw.text( x_pos, common.img_height - 180 , common.random_seed )

# update sector edges with colored alerts
# do these in ascendaning urgency so red edges override orange, etc.
for alert_color in [ "yellow" , "orange" , "red"]:
    trace("alerts","processing {0:s} alerts".format(alert_color))
    for alert_coords in alerts[alert_color]:
        trace('alerts',"drawing {0:s} alert for {1:s} at {2:d}, {3:d}".format(
            alert_color, 
            map[alert_coords].hex_number,
            map[alert_coords].center_x,
            map[alert_coords].center_y
        ))
        draw_hexagon (
            map[alert_coords].center_x,
            map[alert_coords].center_y,
            alert_color
        )

# draw everything we've done up to now
draw(common.img)

# draw paths
for shex in map:
    map[shex].draw_paths()

# overlay path location dots (for development)
if config.getboolean('development','draw_path_location_dots'):
    for col in range(1, 9):
        for row in range(1, 11):
            debug('drawing dots for {0:s}'.format(map[(col,row)].hex_number))
            map[(col,row)].draw_path_dots()

# display if wanted
if config.getboolean('options','display'):
    display(common.img)

# and save
if config['options']['save_file_name'] != '':
    save_to = config['options']['save_file_name']
else:
    save_to = "{0:s}.png".format( str(common.random_seed) )
common.img.save( filename = save_to )
print ("sector generated and saved to {0:s} in {1:.2f}s".format(save_to, time.time() - start_time))




