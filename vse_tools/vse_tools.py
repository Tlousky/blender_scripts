bl_info = {
    "name"        : "Video Editing Tools",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 1),
    "blender"     : (2, 78, 0),
    "category"    : "Object",
    "location"    : "3D View > Tools",
    "description" : "Set of tools for efficient video editing"
}

import bpy

def sort_sequqnces( vse, typeFilter = [] ):
    ''' Return a sorted list of VSE sequence names '''
    if not vse or not vse.sequences: return []

    seqSorted = sorted( vse.sequences[:], key = lambda s: s.frame_final_start )

    if typeFilter:
        return [ s.name for s in seqSorted if s.type in typeFilter ]
    else:
        return [ s.name for s in seqSorted ]

class video_editing_tools_panel( bpy.types.Panel ):
    bl_idname      = "PANEL_vse_tools"
    bl_label       = "Video editing tools"
    bl_category    = "VSE TOOLS"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll( self, context ):
        return context.scene.sequence_editor

    def draw( self, context):
        layout = self.layout
        col    = layout.column()

        row = col.row()

        row.operator(
            'sequencer.set_frame_to_clip_start',
            text = "",
            icon = 'TRIA_LEFT_BAR'
        )

        row.operator(
            'sequencer.set_frame_to_clip_end',
            text = "",
            icon = 'TRIA_RIGHT_BAR'
        )

        row.operator(
            'sequencer.snap_two_sequences',
            text = "",
            icon = 'SNAP_ON'
        )

        row.operator(
            'sequencer.snap_to_next',
            text = "",
            icon = 'FF'
        )

class setFrameToClipStart( bpy.types.Operator ):
    bl_idname      = "sequencer.set_frame_to_clip_start"
    bl_label       = "Snap to Start"
    bl_description = "Set frame current to active clip's start position"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        return context.scene.sequence_editor and context.scene.sequence_editor.active_strip

    def execute( self, context ):
        context.scene.frame_set(
            context.scene.sequence_editor.active_strip.frame_final_start
        )

        return {'FINISHED'}

class setFrameToClipEnd( bpy.types.Operator ):
    bl_idname      = "sequencer.set_frame_to_clip_end"
    bl_label       = "Snap to End"
    bl_description = "Set frame current to active clip's end position"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        return context.scene.sequence_editor and context.scene.sequence_editor.active_strip

    def execute( self, context ):
        context.scene.frame_set(
            context.scene.sequence_editor.active_strip.frame_final_end
        )

        return {'FINISHED'}

class snapSelectedSeqToActiveSeq( bpy.types.Operator ):
    """ Snaps the selected sequence to the active sequence.
        If the active is ahead of the selected seq, will snap sel.end to active.start
        If the active is behind the selected, snaps sel.start to active.end
    """
    bl_idname      = "sequencer.snap_two_sequences"
    bl_label       = "Snap Sequences"
    bl_description = "Snap selected sequence to active sequence"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        vse               = context.scene.sequence_editor
        act               = vse.active_strip
        selectedSequences = [ s for s in vse.sequences if s.select ]
        return vse and act and len( selectedSequences ) == 2

    def execute( self, context ):
        vse = context.scene.sequence_editor
        act = vse.active_strip
        sel = [ s for s in vse.sequences if s.select and s.name != act.name ][0]

        if act.frame_final_end < sel.frame_final_end:
            # Active is behind selected. Move sel.end to act.start.
            sel.frame_start = act.frame_final_end
        else:
            # Active is ahead of selected. Move sel.start to act.end.
            sel.frame_start = act.frame_final_end - sel.frame_final_duration - act.frame_final_duration

            context.scene.frame_set(
                context.scene.sequence_editor.active_strip.frame_final_end
            )

        return {'FINISHED'}

class snapToClosest( bpy.types.Operator ):
    bl_idname      = "sequencer.snap_to_next"
    bl_label       = "Snap next"
    bl_description = "Snap the active sequence to the next sequence"
    bl_options     = {'REGISTER', 'UNDO'}

    mode = bpy.props.StringProperty( default = "NEXT" )

    @classmethod
    def poll( self, context ):
        vse               = context.scene.sequence_editor
        act               = vse.active_strip
        return vse and act

    def execute( self, context ):
        vse            = context.scene.sequence_editor
        act            = vse.active_strip
        seqNamesSorted = sort_sequqnces( vse )

        actIdx  = seqNamesSorted.index( act.name )

        if actIdx == len( seqNamesSorted ) - 1:
            return {'CANCELLED'}

        nextSeq = vse.sequences[ seqNamesSorted[ actIdx + 1] ]

        act.frame_start = nextSeq.frame_final_end - act.frame_final_duration - nextSeq.frame_final_duration

        context.scene.frame_set(
            context.scene.sequence_editor.active_strip.frame_final_end
        )

        return {'FINISHED'}

class crossFadeToBlack( bpy.types.Operator ):
    bl_idname      = "sequencer.cross_fade_to_black"
    bl_label       = "Fade to black"
    bl_description = "Add a fade to black transition between the two selected sequences"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        vse               = context.scene.sequence_editor
        act               = vse.active_strip
        selectedSequences = [ s for s in vse.sequences if s.select ]
        return vse and act and len( selectedSequences ) == 2

    def execute( self, context ):
        pass

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)