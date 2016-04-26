import bpy
import numpy as np
from mathutils import Vector

p = bpy.context.active_object.particle_systems['ParticleSystem'].particles

locations = 10 * np.random.random((len(p),3)) - 5
locations = [ Vector(co) for co in locations ]

for pp, loc in zip( p, locations ):
    pp.location = loc

bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
