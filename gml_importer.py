bl_info = {
    "name": "GML Importer",
    "author": "batFINGER",
    "version": (0, 1),
    "blender": (2, 76, 0),
    "location": "Menu",
    "description": "Importer for city GML files",
    "warning": "",
    "wiki_url": "",
    "category": "Import",
}

import bpy

from mathutils import Vector

##### Refactor to own file citygml.py
class Texture:
    def __init__(self, id=None, path="", map=""):
        def unflatten(coords):
            return [Vector(float(x) for x in coords[i:i+2]) for i in range(0, len(coords), 2)]        
        self.id = id
        self.path = path
        self.map = unflatten(map.split())

class PolyGon:
    def __init__(self, id=None, pts=""):
        def unflatten(coords):
            return [Vector(float(x) for x in coords[i:i+3]) for i in range(0, len(coords), 3)]
        self.id = id
        self.verts = unflatten(pts.split())

class Building:
    def __init__(self, id="", name="", surfaces={}, textures={}):
        self.id = id
        self.name = name
        self.surfaces = {s.id: s for s in surfaces}
        self.textures = {t.id: t for t in textures}

class CityModel:

    def __init__(self, name="", upper_corner="", lower_corner=""):
        self.lower_corner = Vector(float(x) for x in lower_corner.split())
        self.upper_corner = Vector(float(x) for x in upper_corner.split())
        self.name = name
        self.buildings = {}
        self.images = {}

    def add_building(self, building):
        self.buildings[building.id] = building

    def build(self, scene, filepath, scale):
        import bmesh
        import os

        for k, b in self.buildings.items():
            keep_verts = []
            bm = bmesh.new()
            bm.verts.ensure_lookup_table()
            mesh = bpy.data.meshes.new(b.id)

            for sid, s in b.surfaces.items():
                verts = [bm.verts.new(scale * (v - self.lower_corner)) for v in s.verts]
                face = bm.faces.new(verts)
                texture = b.textures.get("#%s" % s.id)

                if texture:                    
                    uv_layer = bm.loops.layers.uv.verify()
                    tex = bm.faces.layers.tex.verify()
                    bm.faces.ensure_lookup_table()
                    for i,l in enumerate(bm.faces[-1].loops):
                        uv = l[uv_layer].uv
                        (uv.x, uv.y) = texture.map[i]

                    path = os.path.join(filepath, texture.path).replace("\\", "/")
                    image = bpy.data.images.get(os.path.basename(path))
                    if not image:
                        image = bpy.data.images.load(path)
                        image.use_fake_user = True  

                    bm.faces[-1][tex].image = image  
                    dubs = bmesh.ops.find_doubles(bm,
                              verts=verts,
                              dist=0.001)['targetmap']
                    if len(dubs.keys()) > 2:
                        keep_verts.extend(dubs.values())
            verts = list(set(bm.verts) - set(keep_verts))
            bmesh.ops.remove_doubles(bm, verts=verts, dist=0.001)
            #bmesh.ops.automerge(bm, verts=bm.verts, dist=0.000001)
            bm.to_mesh(mesh)
            building = bpy.data.objects.new("building", mesh)
            scene.objects.link(building)
            bm.free()

def read_some_data2(context, filepath, directory, use_some_setting, scale):
    scene = context.scene
    from xml.etree import ElementTree as ET
    cityxml = ET.parse(filepath)
    citymodelnode = cityxml.getroot()
    print("Importing citygml city")
    namespaces = {
           "citygml":"http://www.opengis.net/citygml/1.0",
           "core":"http://www.opengis.net/citygml/base/1.0" ,
           "tex":"http://www.opengis.net/citygml/textures/1.0",
           "gml":"http://www.opengis.net/gml",
           "bldg":"http://www.opengis.net/citygml/building/1.0", 
           "app":"http://www.opengis.net/citygml/appearance/1.0", 
           "dem":"http://www.opengis.net/citygml/relief/1.0",
           "tran":"http://www.opengis.net/citygml/transportation/1.0",
           "gen":"http://www.opengis.net/citygml/generics/1.0",
           "frn":"http://www.opengis.net/citygml/cityfurniture/1.0", 
           "wtr":"http://www.opengis.net/citygml/waterbody/1.0", 
           "luse":"http://www.opengis.net/citygml/landuse/1.0", 
           "veg":"http://www.opengis.net/citygml/vegetation/1.0", 
           "xAL":"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
           }
    '''
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)            
    '''
    bbox = cityxml.find("gml:boundedBy", namespaces=namespaces)

    name = bbox.find(".//gml:Envelope", namespaces=namespaces).attrib["srsName"]
    print("name: %s" % name)
    uc = bbox.find(".//gml:upperCorner", namespaces=namespaces).text
    lc = bbox.find(".//gml:lowerCorner", namespaces=namespaces).text

    city = CityModel(name=name, upper_corner=uc, lower_corner=lc)

    cityobjects = cityxml.findall("citygml:cityObjectMember",
                                namespaces=namespaces)

    print("importing %d city objects (#:buildings, X:non-building)" % len(cityobjects))

    for cityobject in cityobjects:

        building = cityobject.find("bldg:Building", namespaces=namespaces)
        if building is None:
            # ugly hack do for now.
            groundsurface = cityobject.find("bldg:GroundSurface", namespaces=namespaces)
            print("X", end="")
            if groundsurface is None:
                continue
            building = groundsurface
        else:

            print("#", end="")
        building_id = building.attrib["{%s}id" % namespaces["gml"]]

        rings = cityobject.findall(".//gml:Polygon//gml:LinearRing", namespaces=namespaces)
        surfaces = []
        for ring in rings:
            ring_id = ring.attrib["{%s}id" % namespaces["gml"]]
            poslist = ring.find("gml:posList", namespaces=namespaces).text
            surfaces.append(PolyGon(id=ring_id, pts=poslist))

        textures = []
        sdms = cityobject.findall(".//app:surfaceDataMember", namespaces=namespaces)
        for sdm in sdms:
            coords = sdm.find(".//app:textureCoordinates", namespaces=namespaces)
            if coords is None:
                continue
            sdm_ring = coords.attrib["ring"]
            path = r"%s" % sdm.find(".//app:imageURI", namespaces=namespaces).text
            textures.append(Texture(id=sdm_ring, map=coords.text, path=path))

        building = Building(id=building_id, surfaces=surfaces, textures=textures)
        city.add_building(building)
    print()
    print("finished importing, building...")
    city.build(scene, directory, scale)
    print("done")
    return {'FINISHED'}    

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Operator

class ImportCityGML(Operator, ImportHelper):
    """Import CityGML"""
    bl_idname = "import_dem.city_gml"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Load City"

    # ImportHelper mixin class uses this
    filename_ext = ".gml" #".xml"

    filter_glob = StringProperty(
            default = ".gml", #".xml"
            options = {'HIDDEN'},
    )
    directory = StringProperty()
    filepath = StringProperty(name="File Path", description="Filepath used for importing txt files", maxlen= 1024, default= "")

    use_setting = BoolProperty(
            name="Save to Text Editor",
            description="Make a copy of generated script in text editor",
            default=False,
            )
    scale = FloatProperty(
            name="Scale",
            description="Scale the model",
            default=0.05,
            min=0.01,
            max=10.0
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scale")

    def execute(self, context):
        return read_some_data2(context, self.filepath, self.directory, self.use_setting, self.scale)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportCityGML.bl_idname, text="Import CityGML")


def register():
    bpy.utils.register_class(ImportCityGML)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportCityGML)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_dem.city_gml('INVOKE_DEFAULT')