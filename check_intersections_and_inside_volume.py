    import bpy, bmesh
    from mathutils import Vector
    
    def check_raycast(ray_origin, ray_destination, obj):
        ''' This function casts a virtual ray from "ray_origin" to
            "ray_destination", and finds any intersections along
            the ray's path with the mesh object referenced in the "obj" param.
            If there are any intersections, it will return True, else False.
        '''
        mat = obj.matrix_local.inverted()
        f   = obj.ray_cast(mat * ray_origin, mat * ray_destination)
        loc, normal, face_idx = f
    
        if face_idx == -1:
            return False
    
        return True
    
    c = bpy.data.objects['Cube']
    o = bpy.data.objects['Suzanne']
    
    # Generate bmesh object from cube mesh data
    bm = bmesh.new()
    bm.from_mesh( c.data )
    
    bm.edges.ensure_lookup_table() # Generates edge   index table
    bm.verts.ensure_lookup_table() # Generates vertex index table
    
    # Check if cube intersects with mesh
    ''' The intersection algorithm iterates of the cube's edges and uses
        each edge's two vertices as ray casting source and origin points.
        In other words, a ray is cast from the first --> 2nd verts of each edge.
        If the cube intersects with the object, one of the edges of this cube
        must also intersect with the object, thus the cast ray will bump into
        on of the object's faces.
    '''
    
    intersectsMesh = False
    # Iterate over the cube's edges
    for e in bm.edges:
        # Find the global coordinates of each edge's two vertices
        coos = [ c.matrix_world * v.co for v in e.verts ]
        
        # Set these verts as ray casting origin and destination
        ray_origin, ray_destination = coos
        
        # Check whether this edge intersects with the object's mesh
        if check_raycast(ray_origin, ray_destination, o):
            intersectsMesh = True
            break
    
    # Check if cube center is inside the mesh volume
    ''' This test sends a ray from the cube's center (location) straight up,
        towards an arbitrary point at XYZ 0,0,1000.
        If the cube's center is within the mesh of the object, the ray will hit
        the engulfing mesh somewhere along its way up, and the function will
        return True.
    '''
    insideMesh = check_raycast( c.location, Vector( (0,0,1000) ),  o )
       
    print( "Intersects: ", intersectsMesh )
    print( "Inside Mesh: ", insideMesh )