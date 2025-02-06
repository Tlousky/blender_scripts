import cv2, bpy, bmesh
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

C = bpy.context
D = bpy.data
S = C.scene

IMAGE_SIZE_PX = 1000
SCALE = 1/100
SIZE_SCALED = IMAGE_SIZE_PX * SCALE

def context_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {
                            'window': window, 'screen': screen,
                            'area': area, 'region': region,
                            'scene': bpy.context.scene
                        }


def import_cutout(imgpath):
    n = Path(imgpath).name
    image = cv2.imread(imgpath, cv2.IMREAD_UNCHANGED)
    alpha = image[:,:,3]

    # Find contour from alpha channel
    _, binary_mask = cv2.threshold(alpha, 0, 255, cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the max size contour using OpenCV's functions
    max_area_contour = max(contours, key=lambda c: cv2.contourArea(c))
    contour_2d = IMAGE_SIZE_PX - max_area_contour[:,0,:]

    # Generate scaled mesh from contour
    verts = contour_2d * SCALE
    verts = np.insert(verts, 1, 0, axis=1)

    faces = [ np.arange(len(verts)) ]
    verts = np.vstack(( verts, [[0,0,0], [0,0,SIZE_SCALED], [SIZE_SCALED,0,SIZE_SCALED], [SIZE_SCALED,0,0] ]))

    # Add boundary face for UV projection
    faces.append( np.arange(len(verts)-4,len(verts) ) )

    m = D.meshes.new(n)
    m.from_pydata(verts, [], faces)

    o = D.objects.new(n, m)

    S.collection.objects.link(o)

    o.select_set(True)
    C.view_layer.objects.active = o

    bpy.ops.object.mode_set(mode='EDIT')
    # Go to front view and project UVs from view



    with bpy.context.temp_override(**context_override()):
        bpy.ops.view3d.view_axis(type='BACK')
        bpy.ops.uv.project_from_view(scale_to_bounds=True)
        
    # Remove redundant face
    bm = bmesh.from_edit_mesh(C.object.data)
    bm.faces.ensure_lookup_table()
    bm.faces.remove(bm.faces[1])
    bm.verts.ensure_lookup_table()

    for i in bm.verts[-4:]:
        bm.verts.remove(i)

    bmesh.update_edit_mesh(C.object.data)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Add material and set texture
    mat = D.materials.new(n)
    im = D.images.load(imgpath)
    #tex = D.textures.new(n, 'IMAGE')
    #tex.image = im

    mat.use_nodes = True
    t = mat.node_tree

    t.nodes.remove(t.nodes.get('Principled BSDF'))
    material_output = t.nodes.get('Material Output')
    emission = t.nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 1
    t.links.new( material_output.inputs[0], emission.outputs[0] )

    img_tex_node = t.nodes.new('ShaderNodeTexImage')
    img_tex_node.image = im

    t.links.new( emission.inputs[0], img_tex_node.outputs[0] )

    bpy.ops.object.material_slot_add()
    o.material_slots[0].material = mat
    

imgfolder = r'G:\My Drive\Documents\Music\Echolalia\art\Destination_Music_Video\Tests\danielle\layers'
pngs = list( Path(imgfolder).glob('*.png') )

for i in pngs:
    import_cutout(str(i))