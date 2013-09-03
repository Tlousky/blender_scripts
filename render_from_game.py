# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#  Author            : Tamir Lousky [ tlousky@gmail.com, tamir@pitchipoy.tv ]
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/
#  Studio (sponsor)  : Armobillo VFX (Armobillo.com)
#  Start of project  : 2013-03-09 by Tamir Lousky
#  Last modified     : 2013-03-09
#
#  Acknowledgements 
#  ================
#  Armobillo: Elad BarNess - who came up with the idea

bl_info = {    
    "name"       : "Render from Game Engine",
    "author"     : "Tamir Lousky",
    "version"    : (0, 0, 1),
    "blender"    : (2, 68, 0),
    "category"   : "Render",
    "location"   : "3D View >> Tools",
    "wiki_url"   : '',
    "tracker_url": '',
    "description": "Render frames and animations from the game engine"
}

import bpy

class render_from_game(bpy.types.Panel):
    bl_idname      = "RenderFromGame"
    bl_label       = "Render from Game Engine"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'objectmode'

    @classmethod
    def poll( self, context ):
        return context.scene.render.engine == 'BLENDER_GAME'

    def draw( self, context):
        layout = self.layout
        col    = layout.column()

        col.operator( 
            'logic.create_anim_logics',
            text = "Create Animation Logics",
            icon = 'LOGIC'
        )

class create_logics( bpy.types.Operator ):
    """ Render Animations from Game Engine """
    bl_idname      = "logic.create_anim_logics"
    bl_label       = "Create Animation Logics"
    bl_description = "Automatically create animation logics bricks"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        return context.scene.render.engine == 'BLENDER_GAME'

    def create_logics( self, context ):
        """ Goes over all objects in scene and creates game logic bricks
            to play their animations when the game engine runs """
       
        for o in context.scene.objects:
            emax = 0
            smin = context.scene.frame_end

            if 'action' in dir(o.animation_data):
                # Find start and end frames for action animations
                for fc in o.animation_data.action.fcurves:
                    start,end = fc.range()[:]
                    if start < smax:
                        smin = start
                    if end > emax:
                        emax = end

                # Add always sensor which will feed all animations
                bpy.ops.logic.sensor_add( 
                    type   = 'DELAY', 
                    name   = 'SensAnimation', 
                    object = o.name 
                )
                
                # Make sure always sensor is re-evaluated at each frame
                o.game.sensors[-1].delay = smin
                        
                # Add logic controller
                bpy.ops.logic.controller_add(
                    type   = 'LOGIC_AND', 
                    name   = 'ctrl_' + o.name,
                    object = o.name
                )

                # Add an action actuator
                bpy.ops.logic.actuator_add(
                    type   = 'ACTION', 
                    name   = 'act_' + o.name, 
                    object = o.name
                )
                o.game.actuators[-1].action      = o.animation_data.action
                o.game.actuators[-1].frame_start = smin
                o.game.actuators[-1].frame_end   = emax
                
                # Connect bricks
                e.game.controllers[-1].link(
                    sensor   = o.game.sensors[-1], 
                    actuator = o.game.actuators[-1]
                )
                
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
