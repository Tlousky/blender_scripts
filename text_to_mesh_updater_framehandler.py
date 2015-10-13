import bpy

def update_text( scene ):
    if 'TextMesh' not in scene.objects:
         m = bpy.data.meshes.new_from_object( 
            scene, scene.objects['Text'], True, 'RENDER', True, True 
         )

         o = bpy.data.objects.new( 'TextMesh', m )
         scene.objects.link( o )

    o = scene.objects['TextMesh']
    t = scene.objects['Text']

    t.hide = True
    o.location = t.location

    o.data = t.to_mesh( scene, True, 'RENDER', True, True )

bpy.app.handlers.frame_change_pre.append( update_text )