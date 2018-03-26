import bpy
import pandas as pd
from os.path import basename
from datetime import datetime as dt

def create_parent( scn, x, y, name ):
    p = bpy.data.objects.new( name, None )
    p.location = ( x, y, 0 )
    scn.objects.link( p )

    return p

class timecode():
    ''' Convert from timecode string to time object, seconds and frames '''
    def __init__( self, timeString, fps ):
        self.tc_string = timeString
        self.tc_object = tc = dt.strptime( timeString, '%M:%S.%f' ).time()
        self.seconds   = (tc.minute) * 60 + tc.second + tc.microsecond / 1000000
        self.frame     = int( round( self.seconds * fps ) )

class TextLine():
    def __init__( self, slide, scn, x, y, lineIndex, fadeInDuration = 10 ):
        self.slide          = slide
        self.text_objects   = []
        self.fadeInDuration = fadeInDuration
        self.create_parent( scn, x, y, lineIndex )

    def create_parent( self, scn, x, y, i ):
        name = "{}_line_{}".format( self.slide.parent.name, i )
        self.parent = create_parent( scn, x, y, name )
        scn.update()
        self.parent.parent = self.slide.parent
        self.parent.matrix_parent_inverse = self.slide.parent.matrix_world.inverted()

    def create_text( self, text, start, end, x, y, scn, channel, fontsize, baseMat, background ):
        # Generate text curve data
        t = bpy.data.curves.new( text, "FONT" )
        t.body    = text
        t.align_x = 'LEFT'
        t.align_y = 'CENTER'

        # Text object
        o = bpy.data.objects.new( text, t )
        baseMat
        scn.objects.link( o )

        o.location = (x, y, 0)
        o.scale    = (fontsize, fontsize, 1)

        # Text material and animation
        m                 = baseMat.copy()
        o.active_material = m

        m.use_shadeless    = True
        m.use_transparency = True

        # Insert alpha keyframes at start and end
        for frm, val in zip( [ start, start + self.fadeInDuration ], [ 0, 1 ] ):
            m.alpha = val
            m.keyframe_insert( 'alpha', frame = frm )

        #t.color = (0.5, 0.5, 0.5, 0.5) if background else (1,1,1,1)

        return o

    def add_text( self, text, start, end, scn, baseMat, xInterval, y = 0, channel = 3, fontsize = 1, background = False ):
        # Place next word right after the last one
        x = 0 # First word x is 0
        if len( self.text_objects ):
            last = self.text_objects[-1]
            scn.update()
            x    = last.location.x + last.dimensions.x + xInterval

        textObj = self.create_text( text, start, end, x, y, scn, channel, fontsize, baseMat, background )
        scn.update()
        textObj.parent = self.parent
        textObj.matrix_parent_inverse = self.parent.matrix_world.inverted()

        self.text_objects.append( textObj )

class Slide():
    def __init__( self, vid, frame_start, frame_end, scn, x, y, slideIndex, camera_height, animateCamera = False, cameraMovementTime = 10 ):
        self.vid         = vid
        self.frame_start = frame_start
        self.frame_end   = frame_end
        self.lines       = []
        self.create_parent( scn, x, y, slideIndex )
        self.index       = slideIndex

        if animateCamera:
            scn.camera.keyframe_insert( 'location', 1, frame_start - cameraMovementTime )
            scn.camera.location.y -= camera_height
            scn.camera.keyframe_insert( 'location', 1, frame_start )

    def create_parent( self, scn, x, y, i ):
        self.parent = create_parent( scn, x, y, "slide_{}".format( i ) )

    def add_line( self, line ):
        self.lines.append( line )

class LyricsVideo():
    def __init__( self, audioFile, markersFile, vseSequences, scn, audioChannel = 1, backgroundFile = None, baseMat = None ):
        self.slides        = []
        self.audio_file    = audioFile
        self.markers_file  = markersFile
        self.audio_channel = audioChannel
        self.audio = vseSequences.new_sound(
            basename( audioFile ), audioFile, audioChannel, 1
        )
        self.fps = scn.render.fps

        if baseMat:
            self.baseMat = baseMat
        else:
            m = bpy.data.materials.new("baseMat")
            m.use_shadeless = True
            m.use_transparency = True
            self.baseMat = m

        # Set scene to match sound file
        scn.frame_start = self.audio.frame_start
        scn.frame_end   = self.audio.frame_final_end

        self.markers = pd.read_csv( markersFile, sep = '\t' )

        # Set scene background to transparent
        scn.render.alpha_mode           = 'TRANSPARENT'
        scn.render.sequencer_gl_preview = 'MATERIAL'

        # Create background
        if backgroundFile:
            bg = vseSequences.new_image( 'BG', backgroundFile, 2, 1 )
            bg.frame_final_end = scn.frame_end
        else:
            bg = vseSequences.new_effect( 'BG', 'COLOR', 2, 1, scn.frame_end )
            bg.color = (0,0,0)

        bg.blend_type = 'REPLACE'

        # Add scene to vse
        vseScn = vse.sequences.new_scene( name = 'Scene', scene = scn, channel = 5, frame_start = scn.frame_start )
        vseScn.blend_type = 'ALPHA_OVER'

        self.create_slides( vseSequences, scn )

    def normalizedXloc( self, val, xlim ):
        ''' Normalize any value between 0-1 to the xlim provided range '''
        return xlim[0] + ( xlim[1] - xlim[0] ) * val

    def create_slides( self, seq, scn, yStart = 0.95, yInterval = 0.1 ):
        df = self.markers

        # Divide markers into slides and lines
        track_indices = list( df[ df['Type'] == 'Track' ].index )

        # Maximize font size - TODO: Need to revise and adapt to camera viewsize
        xy_ratio      = scn.render.resolution_x / scn.render.resolution_y
        line_width    = scn.camera.data.ortho_scale
        camera_height = line_width / xy_ratio
        x             = 0
        for i, slideIdx in enumerate( track_indices ):
            textChannel = self.audio_channel + 1
            slideStart   = slideIdx
            slideEnd     = track_indices[i+1] if i < len( track_indices ) - 1 else df.index[-1]
            slideMarkers = df.loc[ slideStart : slideEnd ]
            lineIndices  = [slideStart] + list( slideMarkers[ slideMarkers['Type'] == 'Subclip' ].index )

            x = 0
            slideFrameStart = timecode( df.loc[ slideStart, 'Start' ], self.fps ).frame
            slideFrameEnd   = timecode( df.loc[ slideEnd,   'Start' ], self.fps ).frame if i < len( track_indices ) - 1 else self.audio.frame_final_end
            slideY          = -i * camera_height
            slide           = Slide( self, slideFrameStart, slideFrameEnd, scn, x, slideY, i, camera_height, animateCamera = (i > 0) )

            textLines = []
            for j, lineIdx in enumerate( lineIndices ):
                lineStart = lineIdx
                lineEnd   = lineIndices[j+1] - 1 if j < len( lineIndices ) - 1 else slideEnd - 1 if i < len( track_indices ) - 1 else df.index[-1]
                lineMarkers = df.loc[ lineStart : lineEnd ]

                # Calculate y for this line
                lineY = slideY
                if len( slide.lines ):
                    lastLine = slide.lines[-1]
                    if len( lastLine.text_objects ):
                        scn.update()
                        maxYtextObj = max( lastLine.text_objects, key = lambda o: o.dimensions.y )
                        lineY = maxYtextObj.location.y - maxYtextObj.dimensions.y - yInterval

                line = TextLine( slide, scn, x, lineY, j )
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
                        text      = text,
                        start     = timecode( lineMarkers.loc[ markerIndex, 'Start' ], self.fps ).frame - 1,
                        end       = textEnd,
                        scn       = scn,
                        baseMat   = self.baseMat,
                        xInterval = line_width / 50,
                        y         = lineY,
                        fontsize  = 0.65
                    )

                slide.add_line( line )
                textLines.append( textSoFar )

            maxTextLen = max([
                    ( o.location.x + o.dimensions.x ) for l in slide.lines for o in l.text_objects
            ])
            slideFontSize = int( round( line_width / ( maxTextLen * 1.1 ) ) ) # Kinda makes sense?

            '''
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
            '''

            self.slides.append( slide )

C = bpy.context
S = C.scene

if not S.sequence_editor: S.sequence_editor_create()

vse = S.sequence_editor
seq = vse.sequences

lv = LyricsVideo(
    audioFile      = r'C:\Users\TLOUSKY\Google Drive\Documents\Hellscore\Hellscore_songs\Afterlife\int + v1+ pc1 + c1 + v2 + pc2 + c2 + cpart + c3- Bariton.mp3',
    markersFile    = r'C:\Users\TLOUSKY\Google Drive\Documents\Hellscore\Hellscore_songs\Afterlife\Afterlife_baritone_All.csv',
    vseSequences   = seq,
    scn            = S,
    backgroundFile = r'C:\Users\TLOUSKY\Google Drive\Documents\Hellscore\Hellscore_songs\BG.jpg'
)