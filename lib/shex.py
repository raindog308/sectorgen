# shex = 'sector hex' (because 'hex' is a reserved word)

import random
from wand.drawing import Drawing
from wand.color import Color
import common
from common import comets, config, debug, d10, d100, features, planet_names, trace
from glyph import Glyph

class Comet:
	def __init__ ( self, glyph, color):
		self.glyph = glyph
		self.color = color

class Rating:
	def __init__ ( self, value, direction):
		self.value = value
		self.direction = direction

class Shex:
	debug_names = [ "A" , "Bp", "Cqq", "Dxx", "Ettt", "Flkor",
		"Gw3g56", "Hqpqpqp", "I234g678", "J234g6789",
		"K234q67q90", "L2g4p67q901", "M234gpq89012" ]
	
	def __init__ ( self, col, row ):
		self.col = col
		self.row = row
		self.even_col = False
		if ( col % 2 == 0):
			self.even_col = True
		self.hex_number = "{0:02d}{1:02d}".format(col,row)
		self.settled = False
		self.alert_color = None
		self.paths = set()

		# calc center point of this hex
		base_x = 840
		if self.even_col is False: # odd
			base_y = 800
		else:
			base_y = 800 + common.half_hex_height

		self.center_x = base_x +  ( ( self.col - 1 ) * (common.hex_line_width + common.half_hex_line_width))
		self.center_y = base_y +  ( ( self.row - 1 ) * common.hex_height )

	def add_path(self, path):
		self.paths.add(path)

	def turn_on_alert(self):
		roll = d100()
		if (roll <= 20):
			self.alert_color = 'red'
		elif (roll >= 21 and roll <= 40):
			self.alert_color = 'orange'
		else:
			self.alert_color = 'yellow'
		debug('{0:s} setting {1:s} alert'.format(self.hex_number,self.alert_color))

	def gen_planet(self, slot):
		if self.dyson: # then the dyson sphere is taking all the star's energy
			return ('Ice')

		pool = [ 
			'Desert' , 'Desert' , 'Desert' , 'Desert' , 'Desert' ,
			'Rocky', 'Rocky', 'Rocky', 'Rocky', 'Rocky',
			'Tainted', 'Tainted', 'Tainted', 
			'Jovian'
		]
		
		if slot < 3:
			pool.extend ( [ 'Furnace' , 'Furnace' , 'Furnace' , 'Furnace' , 'Furnace' ] )
			pool.extend ( [ 'Ocean', 'Ocean' ] )
		
		if slot >= 3 and slot <= 7:
			pool.extend ( [ 'Vibrant', 'Vibrant', 'Vibrant', 'Vibrant', 'Vibrant' ] )
			pool.extend ( [ 'Ice' ] )
			pool.extend ( [ 'Grave' ] )
			pool.extend ( [ 'Jungle', 'Jungle' ] )
			pool.extend ( [ 'Ocean', 'Ocean' ] )
		
		if slot > 7:
			pool.extend ( [ 'Ice', 'Ice', 'Ice', 'Ice', 'Ice' ] )

		return random.choice(pool)

	def settle(self):
		self.settled = True

		self.mainworld_name = planet_names.pop(0).rstrip().title()
		if config.getboolean('development','use_debug_names'):
			self.mainworld_name = random.choice([
				 "A" , "Bp", "Cqq", "Dxx", "Ettt", "Flkor",
				"Gw3456", "Hqpqpqp", "I2345678", "J23456789",
				"K234567890", "L2345678901", "M23456789012" 
			])

		self.starport = random.choice ([ 'A', 'B', 'B', 'C', 'C', 'C', 'D', 'D', 'E', 'E', 'X' ])
		debug("{0:s} {1:s} [{2:s}]".format(self.hex_number,self.mainworld_name, self.starport))

		# system map: star
		star_colors = config['stars']['colors'].split (',')
		this = random.choice(star_colors).lstrip().split(' ')
		self.star = { "fill" : this[0] , "stroke" : this[1] }

		# dyson sphere?
		self.dyson = False
		if ( random.randint(1,1000) < config.getint('tuning','chance_dyson_sphere')):
			self.dyson = True
			debug('{0:s} this hex is a dyson sphere'.format(self.hex_number))
			self.star['stroke'] = config['stars']['dyson_stroke']

		# system map
		self.system_map = {}
		for x in range ( 1, 12):
			self.system_map[x] = None
		
		slots = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ]
		random.shuffle(slots)

		# place mainworld
		self.mainworld_slot = slots.pop()
		self.system_map [ self.mainworld_slot ] = "mainworld"
		self.mainworld_type = self.gen_planet ( self.mainworld_slot )

		# place asteroid fields
		if ( config.getboolean('development','turn_it_to_eleven') or
			d100() <= config.getint('tuning','chance_asteroid_field') ):
			for x in range ( 0, random.choice([ 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]) ):
				while slots[0] <= 2:
					random.shuffle(slots)
				self.system_map [ slots.pop(0) ] = "asteroid field"

		# gas giants?
		num_gas_giants = 0
		if ( config.getboolean('development','turn_it_to_eleven') or
			d100() <= config.getint('tuning','chance_gas_giant') ):
			num_gas_giants = random.choice([ 1, 1, 1, 1, 1, 1, 1, 1, 2, 2 ])

		# place gas giants and other planets
		for remaining_slot in slots:
			if d100() <= config.getint('tuning','chance_orbit_has_planet'):
				# place gas giants first - but not in slot 11 otherwise it crowds the comet
				if num_gas_giants > 0 and remaining_slot != 11:
					self.system_map[remaining_slot] = "gas giant"
					num_gas_giants -= 1
				else:
					self.system_map[remaining_slot] = self.gen_planet(remaining_slot)

		# settlement type
		if ( d100() <= config.getint('tuning','chance_hex_is_space_station')):
			self.settlement = 'Station'
			self.mainworld_type = 'Station'
		else:
			if ( config.getboolean('development','turn_it_to_eleven') or
			     d100() >= config.getint('tuning','chance_settlement_is_planetary') ):
				self.settlement = "orbital"
			else:
				self.settlement = "planetary"
		if self.mainworld_slot > 7:
			self.settlement = "orbital"

		# these settlements must be orbital
		if self.dyson or self.mainworld_type == 'Jovian' :
			self.settlement = 'orbital'

		debug("{0:s} {1:s}".format(self.hex_number,self.settlement))
		debug("{0:s} {0:s}".format(self.hex_number,self.mainworld_type))

		# naval base or scout base
		# A, B can contain naval bases
		# C, D, E can contain scout bases
		# X has no base

		self.base = None
		if ( self.starport == 'A' or self.starport == 'B' ):
			if ( d100() <= 50 ):
					self.base = 'naval'
					debug("{0:s} base: naval".format(self.hex_number))
		elif self.starport in [ 'C', 'D', 'E' ]:
			roll = d100()
			if self.starport == 'C':	
				roll += 20
			if ( roll <= 50 ):
				self.base = 'scout'
				debug("{0:s} base: scout".format(self.hex_number))

		# if turning everything on, pick naval or scout randomly

		if ( config.getboolean('development','turn_it_to_eleven') ):
			if d100() <= 50:
				self.base = 'naval'
				debug("{0:s} base: naval".format(self.hex_number))
			else:
				self.base = 'scout'
				debug("{0:s} base: scout".format(self.hex_number))

		# ratings

		self.ratings = {}
		if config.getboolean("development","debug_sliders") == True:
			common.debug_slider += 1
			if common.debug_slider > 11:
				common.debug_slider = 1
			self.ratings['population']    = Rating ( common.debug_slider , 'up' )
			self.ratings['economy']   = Rating ( common.debug_slider , 'down' )
			self.ratings['equity'] = Rating ( common.debug_slider , 'up' )
		else:
			for name in [ 'population' , 'economy' , 'equity' ]:
				self.ratings[name] = Rating (
					random.randint ( 1, 11 ),
					random.choice  ( [ 'up' , 'down' ] )
				)

		# adj pop for base
		if ( self.base == 'A' and self.ratings['population'] < 6 ):
			self.ratings['population'] = 6
		if ( self.base == 'B' and self.ratings['population'] < 5 ):
			self.ratings['population'] = 5
		if ( self.base == 'C' and self.ratings['population'] < 4 ):
			self.ratings['population'] = 4

		# features
		self.features = [ features.pop(0) , features.pop(0) , features.pop(0) ]

		# comet
		self.comet = None
		if ( config.getboolean('development','turn_it_to_eleven') or d100() <= config.getint('tuning','chance_comet') ):
			self.comet = Comet ( 
				random.choice ( comets ),
				random.choice ( [ 'white', 'white', 'white', 'yellow', 'red', 'purple', 'blue', 'brown' ] )
			)
			
		if self.comet is None:
			debug("{0:s} Comet: no".format(self.hex_number))
		else:
			debug("{0:s} Comet color: {0:s}".format(self.hex_number,self.comet.color))

	def calc_path_centers(self):
		self.path_centers = {
			'N'  : ( self.center_x                               , self.center_y - common.half_hex_height    ),
			'NE' : ( self.center_x + common.hex_line_width - 112 , self.center_y - common.quarter_hex_height ),
			'SE' : ( self.center_x + common.hex_line_width - 112 , self.center_y + common.quarter_hex_height ),
			'S'  : ( self.center_x                               , self.center_y + common.half_hex_height    ),
			'SW' : ( self.center_x - common.hex_line_width + 112 , self.center_y + common.quarter_hex_height ),
			'NW' : ( self.center_x - common.hex_line_width + 112 , self.center_y - common.quarter_hex_height )
		}

	def draw_path_dots(self):
		path_dot_colors = {
			'N'  : 'red',
			'NE' : 'yellow',
			'SE' : 'purple',
			'S'  : 'blue',
			'NW' : 'orange',
			'SW' : 'pink'
		}

		self.calc_path_centers()

		mycanvas = Drawing()
		mycanvas.fill_opacity = 100
		mycanvas.stroke_opacity = 0
		for pc in [ 'N' , 'NE' , 'SE', 'S', 'SW', 'NW' ]:
			debug('   {0:2s}: {1:d} , {2:d}'.format(pc , self.path_centers[pc][0], self.path_centers[pc][1]))

			( x , y ) = self.path_centers[pc]

			mycanvas.fill_color = Color("white")
			mycanvas.circle ( 
				( x , y ),
				( x + 5, y + 5 )
			)
			mycanvas.fill_color = Color(path_dot_colors[pc])
			mycanvas.point ( x , y )

		mycanvas.fill_color = Color("white")
		mycanvas.circle ( 
			( self.center_x , self.center_y ),
			( self.center_x + 5, self.center_y + 5 )
		)
		mycanvas.fill_color = Color("cyan")
		mycanvas.point (self.center_x, self.center_y)

		mycanvas.draw(common.img)

	def draw_paths(self):
		self.calc_path_centers()
		mycanvas = Drawing()
		for path in self.paths:
			( path_center_x , path_center_y ) = self.path_centers[path]

			# determine what color the hex line is (there might be an alert)
			# just "what color is my alert" is insufficient because the alert
			# might have been overridden by an adjacent hex with a higher alert

			color_bytes = common.img.export_pixels ( path_center_x, path_center_y, width = 1 , height = 1, storage = "char" )
			if color_bytes == [ 0 , 0 , 0 , 255 ]:
				# it's black because a path has already been drawn
				trace('paths', '{0:s} NOT drawing path on {1:s} border because path dot is black'.format(self.hex_number,path))
				return
			if color_bytes == [ 255, 0, 0, 255 ]:
				path_color_name = "red"
			elif color_bytes == [ 0, 255, 255, 255 ]:
				path_color_name = "cyan"
			elif color_bytes == [ 255, 255, 0, 255 ]:
				path_color_name = "yellow"
			elif color_bytes == [255, 165, 0, 255]:
				path_color_name = "orange"

			trace('paths', '{0:s} drawing {1:s} path on {2:s} border'.format(self.hex_number,path_color_name,path))

			# first punch through the sector wall
			lower_left_x = path_center_x - 30
			lower_left_y = path_center_y - 30

			mycanvas.fill_color = Color("black")
			mycanvas.fill_opacity = 100
			mycanvas.stroke_opacity = 0
			mycanvas.polygon([
				( lower_left_x      , lower_left_y      ),
				( lower_left_x      , lower_left_y + 60 ),
				( lower_left_x + 60 , lower_left_y + 60 ),
				( lower_left_x + 60 , lower_left_y      )
			])

			# now draw the path sides
			# mycanvas.stroke_color = Color(config["paths"]["color"])
			# mycanvas.fill_color = Color(config["paths"]["color"])
			mycanvas.stroke_opacity = 100
			mycanvas.stroke_width = 5
			mycanvas.stroke_color = Color(path_color_name)
			mycanvas.fill_color = Color(path_color_name)
			if path == 'N' or path == 'S': # vertical line
				mycanvas.line(
					(lower_left_x , lower_left_y ),
					(lower_left_x, lower_left_y + 60 )
				)
				mycanvas.line(
					(lower_left_x + 60 , lower_left_y ),
					(lower_left_x + 60 , lower_left_y + 60 )
				)				
			else: # horizontal
				mycanvas.line(
					(lower_left_x      , lower_left_y ),
					(lower_left_x + 60 , lower_left_y)
				)
				mycanvas.line(
					(lower_left_x      , lower_left_y + 60 ),
					(lower_left_x + 60 , lower_left_y + 60 )
				)
		mycanvas.draw(common.img)

	def draw(self):

		# hex is center_y +/- 390 ( common.half_hex_height )
		# hex is center_x +- 450  ( common.hex_line_width )

		debug('{0:s} drawing hex'.format(self.hex_number))

		draw = Drawing()
		# hex number
		draw.font_size = 45
		draw.fill_color = Color('cyan')
		draw.font = 'fonts/roboto/Roboto-Regular.ttf'
		draw.text_antialias = True
		draw.text_alignment = "left"
		draw.stroke_opacity = 0
		draw.text( 
			self.center_x - common.half_hex_line_width + 10 ,
			self.center_y - common.half_hex_height + 45     ,
			self.hex_number
		)

		if self.settled == False:
			draw(common.img)
			return

		# planet name
		draw.fill_color = Color('white')
		draw.stroke_color = Color('white')
		draw.text_alignment = 'center'
		draw.font = 'fonts/roboto/Roboto-Regular.ttf'
		draw.font_size = 100
		if ( len (self.mainworld_name) > 9 ):
			draw.font_size = 72 
		draw.text_antialias = True
		draw.stroke_opacity = 0
		draw.text (self.center_x , self.center_y + 225 , self.mainworld_name)
		draw.text_decoration = 'no'

		# orbital settlement
		if self.settlement == 'orbital':
			draw.font = 'fonts/noto_sans_symbols_2/NotoSansSymbols2-Regular.ttf'
			draw.fill_opacity = 100
			draw.fill_color = Color('snow')
			draw.stroke_color = Color('snow')
			draw.stroke_opacity = 0
			draw.font_size = 100
			draw.text (self.center_x - 20 , self.center_y - 228, '⚆')
			draw.fill_opacity = 100

		# mainworld
		if self.settlement == "Station":
			draw.font = 'fonts/noto_sans_symbols_2/NotoSansSymbols2-Regular.ttf'
			draw.font_size = 200
			draw.stroke_opacity = 100 
			draw.stroke_width = 21
			draw.fill_color = config['Station']['planet_fill']
			draw.stroke_color = config['Station']['planet_stroke']
			draw.text(self.center_x-164,self.center_y-130,'◆')
		else:
			if self.dyson:
				draw.fill_color = Color(self.star['fill'])
				draw.stroke_color = Color(self.star['stroke'])
			else:
				draw.stroke_color = config[self.mainworld_type]['planet_stroke']
				draw.fill_color = config[self.mainworld_type]['planet_fill']
			draw.stroke_opacity = 100
			draw.stroke_width = 25
			draw.circle((self.center_x-164, self.center_y-188), 
						(self.center_x-108, self.center_y-108)) 
		
		# if dyson sphere, replace mainworld with the star
		if self.dyson:
			draw.stroke_color = Color('black')
			draw.fill_opacity = 0
			draw.stroke_width = 1
			for band in range(2, -80, -2):
				draw.circle((self.center_x-164, self.center_y-188), 
							(self.center_x-168+band, self.center_y-192+band)) 
			draw.fill_opacity = 100
			
		# starport
		draw.stroke_opacity = 0
		draw.font = 'fonts/roboto/Roboto-Regular.ttf'
		if self.dyson:
			draw.fill_color = Color('white')
		else:
			draw.fill_color = Color(config[self.mainworld_type]['port_color'])
		draw.font_size = 140
		draw.text_alignment = "center"
		if self.settlement == "Station":
			draw.text (self.center_x-164, self.center_y-153, self.starport)
		else:
			draw.text (self.center_x-164, self.center_y-143, self.starport)

		# planet type
		draw.font = 'fonts/roboto/Roboto-Regular.ttf'
		draw.font_size = 36
		draw.stroke_opacity = 0
		draw.stroke_color = '#efefef'
		draw.fill_color = '#efefef'
		if self.dyson:
			draw.text (self.center_x-164, self.center_y - 35, 'Dyson Sphere')
		elif self.mainworld_type == 'Station':
			draw.text (self.center_x-164, self.center_y - 35, self.mainworld_type)
		else:
			draw.text (self.center_x-164, self.center_y - 38, self.mainworld_type)

		# base 
		draw.font = 'fonts/noto_sans_symbols_2/NotoSansSymbols2-Regular.ttf'
		draw.fill_color = Color('snow')
		if self.base == 'naval':
			draw.font_size = 90
			draw.text (self.center_x - 320, self.center_y-60, '★')
		elif self.base == 'scout':
			draw.font_size = 200
			draw.text (self.center_x - 320, self.center_y-45, '▴')

		# ratings

		ratings_draw = {
			'population' : {
				'color'     : 'blue',
				'glyph'     : Glyph ( 'fonts/material/MaterialIcons-Regular.ttf', 'F233'),
				'x'         : 60,
				'y_adj'     : 10,
				'font_size' : 60
			},
			'equity' : {
				'color'     : 'red',
				'glyph'     : Glyph ( 'fonts/noto_sans_symbols_2/NotoSansSymbols2-Regular.ttf', '♔' ),
				'x'         : 133,
				'y_adj'     : 0,
				'font_size' : 75
			},
			'economy' : {
				'color'     : 'green2',
				'glyph'     : Glyph ( 'fonts/roboto/Roboto-Regular.ttf', '$' ), # or 💰
				'x'         : 206,
				'y_adj'     : 0,
				'font_size' : 60
			}
		}

		for rating in [ 'population' , 'equity', 'economy' ]:
			draw.font_size  = ratings_draw[rating]['font_size']
			draw.fill_color = ratings_draw[rating]['color']
			draw.font       = ratings_draw[rating]['glyph'].font
			draw.text(
				self.center_x + ratings_draw[rating]['x'], 
				self.center_y - 285 + ratings_draw[rating]['y_adj'], 
				ratings_draw[rating]['glyph'].character )

			draw.fill_color = Color('gray26')
			draw.polygon([
				( self.center_x + ratings_draw[rating]['x'] - 5 , self.center_y - 250 ),
				( self.center_x + ratings_draw[rating]['x'] - 5 , self.center_y -  50 ),
				( self.center_x + ratings_draw[rating]['x'] + 5 , self.center_y -  50 ),
				( self.center_x + ratings_draw[rating]['x'] + 5 , self.center_y - 250 )
				])
			
			lower_left_y = self.center_y - 50 - ( ( self.ratings[rating].value - 1) * 20 )
			lower_left_x = self.center_x + ratings_draw[rating]['x'] - 20

			draw.fill_color = Color( ratings_draw[rating]['color'] )
			
			if self.ratings[rating].direction == 'up':
				triangle_point_y = lower_left_y - 20
			else:
				triangle_point_y = lower_left_y + 20

			draw.polygon ([
				( lower_left_x        , lower_left_y  ),
				( lower_left_x + 40   , lower_left_y  ),
				( lower_left_x +  20  , triangle_point_y )
			])

		# features
		draw.fill_color = Color('white')
		draw.stroke_color = Color('white')
		draw.font_size = 100
		draw.text_alignment = 'left'
		x = 0
		for feature in self.features:
			draw.font = feature.font
			draw.text ( self.center_x - 200 + x , self.center_y + 345, feature.character )
			x += 150

		# comet
		if ( self.comet is not None):
			draw.font_size = 100
			draw.fill_color = Color(self.comet.color)
			draw.font = self.comet.glyph.font
			draw.text( self.center_x + 275, self.center_y - 30, self.comet.glyph.character )

		# system map or space station map
		if self.settlement != "Station":
			planet_diam = 22
			gas_giant_diam = 32
			debug_string = ""

			# line on which the planets sit
			draw.fill_color = Color('gray41')
			draw.stroke_opacity = 0
			draw.polygon ([
				(self.center_x - 350 , self.center_y + 73),
				(self.center_x + 300 , self.center_y + 73),
				(self.center_x + 300 , self.center_y + 77),
				(self.center_x - 350 , self.center_y + 77)
			])

			# indicate which slot is the mainworld with a blue triangle
			mw_x = self.center_x - 350 + ( ( self.mainworld_slot - 1 ) * 54 ) + 75
			draw.stroke_color = Color('blue')
			draw.stroke_opacity = 100
			draw.stroke_width = 5
			draw.fill_color = Color('black')
			draw.polygon ([
				( mw_x - 13       , self.center_y + 110 ),
				( mw_x            , self.center_y +  85 ),
				( mw_x + 13       , self.center_y + 110 )
			])

			# primary star
			draw.fill_color = Color(self.star['fill'])
			draw.stroke_color = Color(self.star['stroke'])
			draw.stroke_width = 20
			draw.stroke_opacity = 100
			draw.arc ( 
				( self.center_x - 424 , self.center_y - 30 ),
				( self.center_x - 315 , self.center_y + 80 ),
				( 210, 90 )
				)

			# slots
			draw.stroke_opacity = 100
			draw.stroke_width = 5
			for slot in range ( 1, 12 ):
				x = self.center_x - 350 + ( ( slot - 1 ) * 54 ) + 75

				# draw the hash mark
				draw.fill_color = Color('gray41')
				draw.stroke_color = Color('gray41')
				draw.polygon( [
					(x - 5, self.center_y + 73),
					(x - 5, self.center_y + 58),
					(x + 5, self.center_y + 58),
					(x + 5, self.center_y + 73)
				])

				# if this slot is empty, we're done
				if self.system_map[slot] is None:
					debug_string += "{0:d} ".format(slot)
					continue

				# main world?
				if self.system_map[slot] == 'mainworld':
					draw.stroke_color = config[self.mainworld_type]['planet_stroke']
					draw.fill_color = config[self.mainworld_type]['planet_fill']
					draw.stroke_width = 5
					draw.circle( ( x , self.center_y + planet_diam) , ( x + planet_diam  , self.center_y + planet_diam ) )
					debug_string += "{0:d}:mw ".format(slot)

				# asteroid field
				
				elif self.system_map[slot] == 'asteroid field':
					# debug('drawing asteroid field in {0:s} slot {1:d}'.format(self.hex_number, slot))
					debug_string += "{0:1}:as ".format(slot)
					for x_point in range ( x - 15 , x + 15):
						for y_point in range ( self.center_y - 5 , self.center_y + 43, 2):
							roll = d10()
							if ( roll <= 1):
								draw.fill_color = Color( "gray{0:d}".format(random.randint(25,60)) )
								draw.point ( x_point , y_point )

					as_y_bands = []
					for as_y_band in range ( 0 , 46, 5):
						as_y_bands.append(as_y_band)
						roll = d10()
						if roll <= 5:
							as_y_bands.append(as_y_band)

					for as_y_band in as_y_bands:
						as_y = self.center_y + as_y_band
						draw.fill_color = Color( "gray{0:d}".format(random.randint(25,60)) )
						as_x = x + random.randint ( 5 , 25 ) - 15

						for points in [ 
							(as_x     , as_y),
							(as_x + 1 , as_y),
							(as_x - 1 , as_y),
							(as_x     , as_y + 1),
							(as_x     , as_y - 1),
							(as_x + 1 , as_y + 1),
							(as_x + 1 , as_y - 1),
							(as_x - 1 , as_y + 1),
							(as_x - 1 , as_y - 1)
						]:
							draw.fill_color = Color( "gray{0:d}".format(random.randint(25,60)) )
							draw.point ( points[0], points[1] )

						for points in [ 
							(as_x - 1 , as_y - 2),
							(as_x     , as_y - 2),
							(as_x + 1 , as_y - 2),							
							(as_x - 2 , as_y - 1),
							(as_x + 2 , as_y - 1),
							(as_x - 2 , as_y    ),
							(as_x + 2 , as_y    ),
							(as_x - 2 , as_y + 1),
							(as_x + 2 , as_y + 1),
							(as_x - 1 , as_y + 2),
							(as_x     , as_y + 2),
							(as_x + 1 , as_y + 2),
						]:
							roll = d10()
							if ( roll <= 9 ):
								draw.fill_color = Color( "gray{0:d}".format(random.randint(25,60)) )
								draw.point ( points[0], points[1] )

				# gas giant
				elif self.system_map[slot] == 'gas giant':
					debug_string += "{0:d}:gg ".format(slot)
					(draw.stroke_color, draw.fill_color) = (random.choice(config['gas_giants']['colors'].split(','))).strip().split(' ')
					draw.circle( ( x , self.center_y + gas_giant_diam - 20 ) , ( x + gas_giant_diam , self.center_y + gas_giant_diam ) )
					if d10() <= 5: # has rings
							draw.stroke_opacity = 100
							draw.stroke_width = 10
							draw.line (
								( x - 35 , self.center_y + gas_giant_diam + 15 ),
								( x + 40 , self.center_y + gas_giant_diam - 55 )
							)

				# if we got here, it's a normal planet in this slot
				else:
					debug_string += "{0:d}:pl ".format(slot)
					draw.stroke_width = random.choice([ 5, 10 ])
					draw.stroke_color = config[self.system_map[slot]]['planet_stroke']
					draw.fill_color = config[self.system_map[slot]]['planet_fill']
					draw.circle( ( x , self.center_y + planet_diam) , ( x + planet_diam  , self.center_y + planet_diam ) )

			debug("{0:s} system map: {1:s}".format(self.hex_number, debug_string))

		else: # Station
				
				# draw "empty" space
				for x in range ( self.center_x - 350 , self.center_x + 350):
					for y in range ( self.center_y , self.center_y + 100):
						roll = random.randint(1, 1000)
						if roll <= 10:
							draw.fill_color = Color( "gray{0:d}".format(random.randint(25,60)) )
							draw.point ( x , y )

		# and update the image
		draw(common.img)






