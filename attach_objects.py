# Go over a list of objects, and attatch them to another object via shrinkwrap constraint

import bpy
objs = [ o for o in bpy.context.scene.objects if 'House' in o.name ]
counter = 1
for o in objs:
    bpy.ops.object.select_all(action='DESELECT')
    o.select = True
    bpy.context.scene.objects.active = o
    bpy.context.scene.cursor_location = bpy.context.object.location
    bpy.ops.object.empty_add()
    e = bpy.context.scene.objects[ bpy.context.object.name ]

    bpy.ops.object.select_all(action='DESELECT')
    o.select = True
    e.select = True
    bpy.context.scene.objects.active = e
    bpy.ops.object.parent_set(keep_transform=True)

    bpy.ops.object.select_all(action='DESELECT')
    e.select = True
    bpy.context.scene.objects.active = e    
    
    const = bpy.context.object.constraints.new('SHRINKWRAP')
    const.target = bpy.context.scene.objects['Sphere']
    print( "done with object %s of %s" % (counter, len(objs) ) )  
    counter += 1  
