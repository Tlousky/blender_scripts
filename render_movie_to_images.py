import bpy, sys

# Take movie clip filepath and output directory as command line arguments
movieFilePath, OutputPath = sys.argv[-2:]

S  = bpy.context.scene
mc = bpy.data.movieclips.load( movieFilePath )

# Set render resolution to match movie clip
S.render.resolution_x          = mc.size[0]
S.render.resolution_y          = mc.size[1]
S.render.resolution_percentage = 100

# Set number of frames to match movie clip length
S.frame_start = 0
S.frame_end   = mc.frame_duration

# Set render format and output folder
S.render.image_settings.file_format = 'PNG'
S.render.filepath                   = OutputPath

# Load clip to sequencer
se = bpy.context.scene.sequence_editor_create()
se.sequences.new_clip( "MyClip", mc, 0, 0 )

# Render animation to create image sequence
bpy.ops.render.render( animation = True, write_still = True )