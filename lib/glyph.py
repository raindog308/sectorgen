class Glyph:
    def __init__ ( self , font, character ):
        self.font = font 
        if ( len(character) > 1 ):
            self.character = chr( int ( character, 16) )
        else:
            self.character = character
