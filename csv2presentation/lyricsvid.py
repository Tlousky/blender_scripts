import bpy
import pandas as pd
from os.path import basename
from datetime import datetime as dt

class timecode():
    ''' Convert from timecode string to time object, seconds and frames '''
    def __init__( self, timeString, fps ):
        self.tc_string = timeString
        self.tc_object = tc = dt.strptime( timeString, '%M:%S.%f' ).time()
        self.seconds   = (tc.minute) * 60 + tc.second + tc.microsecond / 1000000
        self.frame     = int( round( self.seconds * fps ) )

class TextLine():
    def __init__( self ):
        self.text_objects = []

    def create_text( self, text, start, end, x, y, seq, channel, fontsize, background ):
        t = seq.new_effect( text, 'TEXT', channel, start, end )
        t.text        = text
        t.color       = (0.5, 0.5, 0.5, 0.5) if background else (1,1,1,1)
        t.align_x     = 'LEFT'
        t.align_y     = 'CENTER'
        t.blend_type  = 'ADD' if background else 'ALPHA_OVER'
        t.font_size   = fontsize
        t.location[0] = x
        t.location[1] = y
        
        return t
        
    def add_text( self, text, start, end, x, y, seq, channel = 3, fontsize = 40, background = False ):
        self.text_objects.append(
            self.create_text( text, start, end, x, y, seq, channel, fontsize, background ) 
        )
        
class Slide():
    def __init__( self, frame_start, frame_end ):
        self.frame_start = frame_start
        self.frame_end   = frame_end
        self.lines       = []
        
    def add_line( self, line ):
        self.lines.append( line )

class LyricsVideo():
    def __init__( self, audioFile, markersFile, vseSequences, scn, audioChannel = 1, backgroundFile = None ):
        self.slides        = []
        self.audio_file    = audioFile
        self.markers_file  = markersFile
        self.audio_channel = audioChannel
        self.audio = vseSequences.new_sound( 
            basename( audioFile ), audioFile, audioChannel, 1
        )
        self.fps = scn.render.fps
        
        # Set scene to match sound file
        scn.frame_start = self.audio.frame_start
        scn.frame_end   = self.audio.frame_final_end
        
        self.markers = pd.read_csv( markersFile, sep = '\t' )       
        
        # Create background
        if backgroundFile:
            bg = vseSequences.new_image( 'BG', backgroundFile, 2, 1 )
            bg.frame_final_end = scn.frame_end
        else:
            bg = vseSequences.new_effect( 'BG', 'COLOR', 2, 1, scn.frame_end ) 
            bg.color = (0,0,0)
        
        self.create_slides( vseSequences )

    def normalizedXloc( self, val, xlim ):
        ''' Normalize any value between 0-1 to the xlim provided range '''
        return xlim[0] + ( xlim[1] - xlim[0] ) * val 

    def create_slides( self, seq, yStart = 0.95, yInterval = 0.1, xlim = ( 0.025, 0.95 ) ):
        df = self.markers

        # Divide markers into slides and lines
        track_indices = list( df[ df['Type'] == 'Track' ].index )

        for i, slideIdx in enumerate( track_indices ):
            textChannel = self.audio_channel + 1
            slideStart   = slideIdx
            slideEnd     = track_indices[i+1] if i < len( track_indices ) - 1 else df.index[-1]
            slideMarkers = df.loc[ slideStart : slideEnd ]
            lineIndices  = [slideStart] + list( slideMarkers[ slideMarkers['Type'] == 'Subclip' ].index )

            slideFrameStart = timecode( df.loc[ slideStart, 'Start' ], self.fps ).frame
            slideFrameEnd   = timecode( df.loc[ slideEnd,   'Start' ], self.fps ).frame if i < len( track_indices ) - 1 else self.audio.frame_final_end
            slide = Slide( slideFrameStart, slideFrameEnd )

            for j, lineIdx in enumerate( lineIndices ):
                lineStart = lineIdx
                lineEnd   = lineIndices[j+1] - 1 if j < len( lineIndices ) - 1 else slideEnd - 1 if i < len( track_indices ) - 1 else df.index[-1]
                lineMarkers = df.loc[ lineStart : lineEnd ]

                line = TextLine()
                textSoFar = ''
                textChannel += 1
                for k, markerIndex in enumerate( lineMarkers.index ):
                    spacer  = ' ' if markerIndex != lineMarkers.index[-1] else ''
                    text    = lineMarkers.loc[ markerIndex, df.columns[0] ] + spacer
                    textEnd = slide.frame_end
                    textSoFar += text
                    if k < len( lineMarkers ) - 1:
                        nextMarkerIdx = lineMarkers.index[ k + 1 ]
                        textEnd = timecode( lineMarkers.loc[ nextMarkerIdx, 'Start' ], self.fps ).frame - 1
                    line.add_text( 
                        text    = textSoFar,
                        start   = timecode( lineMarkers.loc[ markerIndex, 'Start' ], self.fps ).frame - 1,
                        end     = textEnd,
                        x       = xlim[0],
                        y       = yStart - yInterval * j,
                        seq     = seq,
                        channel = textChannel
                    )
                    
                slide.add_line( line )
            
            # Maximize font size
            maxTextLen    = max( [ len( t.text ) for l in slide.lines for t in l.text_objects ] )
            slideFontSize = int( round( 3100 / maxTextLen ) )

            for l in slide.lines:
                for t in l.text_objects:
                    t.font_size = slideFontSize

            # Generate background text
            for lidx, l in enumerate( slide.lines ):
                t = l.text_objects[-1]

                l.add_text( 
                    t.text,
                    slide.frame_start if i != 0 else 1,
                    slide.frame_end,
                    t.location[0],
                    t.location[1],
                    seq,
                    len( slide.lines ) + 3 + lidx,
                    t.font_size,
                    background = True
                )
                
            self.slides.append( slide )
            

C = bpy.context
S = C.scene

if not S.sequence_editor: S.sequence_editor_create()

vse = S.sequence_editor
seq = vse.sequences

lv = LyricsVideo( 
    audioFile      = 'E:/Drive/Hellscore/Iron Maiden Medley/Iron Maiden Medley BASS.mp3',
    markersFile    = r'E:\Drive\Documents\Hellscore\Hellscore_songs\IronMaiden_Medely\Markers.csv',
    vseSequences   = seq,
    scn            = S,
    backgroundFile = r'E:\Drive\Documents\Hellscore\Hellscore_songs\BG.jpg'
)