General
=======

Create an empty GLTF2 object
----------------------------

.. code-block:: python

    from pygltflib import GLTF2

    gltf = GLTF2()

Create a GLTF2 object from an existing GLTF2 object
---------------------------------------------------

.. code-block:: python

    from pygltflib import GLTF2

    gltf = GLTF2()
    gltf_copy = GLTF2(
        JSON=gltf.JSON,
        BIN=gltf.BIN,
        CHUNKS=gltf.CHUNKS,
        path_dir=gltf.path_dir
    )

Add a scene
-----------

.. code-block:: python

    from pygltflib import GLTF2, Scene

    gltf = GLTF2()
    scene = Scene()
    gltf.scenes.append(scene)  # scene available at gltf.scenes[0]


Access the first node (the objects comprising the scene) of a scene
-------------------------------------------------------------------

.. code-block:: python

    gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
    current_scene = gltf.scenes[gltf.scene]
    node_index = current_scene.nodes[0]  # scene.nodes is the indices, not the objects 
    box = gltf.nodes[node_index]
    box.matrix  # will output vertices for the box object

Access an extension
-------------------

.. code-block:: python

    # on a primitve
    gltf.meshes[0].primitives[0].extensions['KHR_draco_mesh_compression']

    # on a material
    gltf.materials[0].extensions['ADOBE_materials_thin_transparency']

Add a custom attribute to Attributes
------------------------------------

.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.v2.schema import (
        Attributes,
        Mesh,
        MeshPrimitive
    )

    # Application-specific semantics must start with an underscore, e.g., _TEMPERATURE.
    a = Attributes()
    a._MYCUSTOMATTRIBUTE = 123

    gltf = GLTF2()
    
    primitive = MeshPrimitive()
    primitive.attributes = a  # Add an attribute
    mesh = Mesh()
    mesh.primitives.append(primitive)

    gltf.meshes.append(mesh)
    gltf.meshes[0].primitives[0].attributes._MYOTHERATTRIBUTE = 456  # Add another attribute

Remove a bufferView
-------------------

This will update all accessors, images and sparse accessors to remove the first bufferView.

.. code-block:: python

    gltf.remove_bufferView(0)

Create a simple mesh
--------------------

Create a gltf object and file containing a scene with a primitive triangle with indexed geometry.

.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.v2.schema import (
        Accessor,
        Accessor_componentType,
        Accessor_type,
        Attributes,
        Buffer,
        BufferView,
        BufferView_target,
        Mesh,
        MeshPrimitive,
        Node,
        Scene
    )

    # Create a gltf object
    gltf = GLTF2()

    # Create data
    accessor1 = Accessor(
        bufferView = 0,
        byteOffset = 0,
        componentType = Accessor_componentType.UNSIGNED_SHORT.value,
        count = 3,
        type = Accessor_type.SCALAR.value,
        max = [2],
        min = [0]
    )
    accessor2 = Accessor(
        bufferView = 1,
        byteOffset = 0,
        componentType = Accessor_componentType.FLOAT.value,
        count = 3,
        type = Accessor_type.VEC3.value,
        max = [1.0, 1.0, 0.0],
        min = [0.0, 0.0, 0.0]
    )
    buffer = Buffer(
        uri = "data:application/octet-stream;base64,AAABAAIAAAAAAAAAAAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAACAPwAAAAA=",
        byteLength = 44
    )
    bufferView1 = BufferView(
        buffer = 0,
        byteOffset = 0,
        byteLength = 6,
        target = BufferView_target.ELEMENT_ARRAY_BUFFER.value
    )
    bufferView2 = BufferView(
        buffer = 0,
        byteOffset = 8,
        byteLength = 36,
        target = BufferView_target.ARRAY_BUFFER.value
    )
    primitive = MeshPrimitive(
        attributes = Attributes(POSITION = 1)
    )
    mesh = Mesh()
    mesh.primitives.append(primitive)
    node = Node(mesh = 0)
    scene = Scene(nodes = [0])

    # Assemble into a gltf structure
    gltf.accessors.append(accessor1)
    gltf.accessors.append(accessor2)
    gltf.buffers.append(buffer)
    gltf.bufferViews.append(bufferView1)
    gltf.bufferViews.append(bufferView2)
    gltf.meshes.append(mesh)
    gltf.nodes.append(node)
    gltf.scene = 0
    gltf.scenes.append(scene)

    # Save to file
    gltf.save("triangle.gltf")

Reading vertex data from a primitive and/or getting bounding sphere
-------------------------------------------------------------------

This code is not up to date and needs to be updated.

.. code-block:: python

    import pathlib
    import struct

    import miniball
    import numpy
    from pygltflib import GLTF2

    # load an example gltf file from the khronos collection
    fname = pathlib.Path("glTF-Sample-Models/2.0/Box/glTF-Embedded/Box.gltf")
    gltf = GLTF2().load(fname)

    # get the first mesh in the current scene (in this example there is only one scene and one mesh)
    mesh = gltf.meshes[gltf.scenes[gltf.scene].nodes[0]]

    # get the vertices for each primitive in the mesh (in this example there is only one)
    for primitive in mesh.primitives:

        # get the binary data for this mesh primitive from the buffer
        accessor = gltf.accessors[primitive.attributes.POSITION]
        bufferView = gltf.bufferViews[accessor.bufferView]
        buffer = gltf.buffers[bufferView.buffer]
        data = gltf.get_data_from_uri(buffer.uri)

        # pull each vertex from the binary buffer and convert it into a tuple of python floats
        vertices = []
        for i in range(accessor.count):
            index = bufferView.byteOffset + accessor.byteOffset + i*12  # the location in the buffer of this vertex
            d = data[index:index+12]  # the vertex data
            v = struct.unpack("<fff", d)   # convert from base64 to three floats
            vertices.append(v)
            print(i, v)

    # convert a numpy array for some manipulation
    S = numpy.array(vertices)

    # use a third party library to perform Ritter's algorithm for finding smallest bounding sphere
    C, radius_squared = miniball.get_bounding_ball(S)

    # output the results
    print(f"center of bounding sphere: {C}\nradius squared of bounding sphere: {radius_squared}")


Create a mesh, convert to bytes, convert back to mesh
-----------------------------------------------------

The geometry is derived from [glTF 2.0 Box Sample](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0/Box), but point normals were removed and points were reused where it was possible in order to reduce the size of the example. Be aware that some parts are hard-coded (types and shapes for en- and decoding of arrays, no bytes padding).

This code is not up to date and needs to be updated.

.. code-block:: python

    import numpy as np
    import pygltflib

    # Define mesh using `numpy`
    points = np.array(
    [
        [-0.5, -0.5, 0.5],
        [0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5],
        [0.5, -0.5, -0.5],
        [-0.5, -0.5, -0.5],
        [0.5, 0.5, -0.5],
        [-0.5, 0.5, -0.5],
    ],
    dtype="float32",
    )
    triangles = np.array(
        [
            [0, 1, 2],
            [3, 2, 1],
            [1, 0, 4],
            [5, 4, 0],
            [3, 1, 6],
            [4, 6, 1],
            [2, 3, 7],
            [6, 7, 3],
            [0, 2, 5],
            [7, 5, 2],
            [5, 7, 4],
            [6, 4, 7],
        ],
        dtype="uint8",
    )

    # Create glb-style `GLTF2` with single scene, single node and single mesh from arrays of points and triangles:
    triangles_binary_blob = triangles.flatten().tobytes()
    points_binary_blob = points.tobytes()
    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1), indices=0
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.UNSIGNED_BYTE,
                count=triangles.size,
                type=pygltflib.SCALAR,
                max=[int(triangles.max())],
                min=[int(triangles.min())],
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=len(points),
                type=pygltflib.VEC3,
                max=points.max(axis=0).tolist(),
                min=points.min(axis=0).tolist(),
            ),
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0,
                byteLength=len(triangles_binary_blob),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(triangles_binary_blob),
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=len(triangles_binary_blob) + len(points_binary_blob)
            )
        ],
    )
    gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)

    # Write `GLTF2` to bytes:
    glb = b"".join(gltf.save_to_bytes())  # save_to_bytes returns an array of the components of a glb

    # Load `GLTF2` from bytes:
    gltf = pygltflib.GLTF2.load_from_bytes(glb)

    # Decode `numpy` arrays from `GLTF2`:
    binary_blob = gltf.binary_blob()

    triangles_accessor = gltf.accessors[gltf.meshes[0].primitives[0].indices]
    triangles_buffer_view = gltf.bufferViews[triangles_accessor.bufferView]
    triangles = np.frombuffer(
        binary_blob[
            triangles_buffer_view.byteOffset
            + triangles_accessor.byteOffset : triangles_buffer_view.byteOffset
            + triangles_buffer_view.byteLength
        ],
        dtype="uint8",
        count=triangles_accessor.count,
    ).reshape((-1, 3))

    points_accessor = gltf.accessors[gltf.meshes[0].primitives[0].attributes.POSITION]
    points_buffer_view = gltf.bufferViews[points_accessor.bufferView]
    points = np.frombuffer(
        binary_blob[
            points_buffer_view.byteOffset
            + points_accessor.byteOffset : points_buffer_view.byteOffset
            + points_buffer_view.byteLength
        ],
        dtype="float32",
        count=points_accessor.count * 3,
    ).reshape((-1, 3))

    **P.S.**: If you'd like to use "compiled" version of mesh writing:
    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1), indices=0
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.UNSIGNED_BYTE,
                count=36,
                type=pygltflib.SCALAR,
                max=[7],
                min=[0],
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=8,
                type=pygltflib.VEC3,
                max=[0.5, 0.5, 0.5],
                min=[-0.5, -0.5, -0.5],
            ),
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0, byteLength=36, target=pygltflib.ELEMENT_ARRAY_BUFFER
            ),
            pygltflib.BufferView(
                buffer=0, byteOffset=36, byteLength=96, target=pygltflib.ARRAY_BUFFER
            ),
        ],
        buffers=[pygltflib.Buffer(byteLength=132)],
    )
    gltf.set_binary_blob(
        b"\x00\x01\x02\x03\x02\x01\x01\x00\x04\x05\x04\x00\x03\x01\x06\x04\x06\x01"
        b"\x02\x03\x07\x06\x07\x03\x00\x02\x05\x07\x05\x02\x05\x07\x04\x06\x04\x07"
        b"\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00?\x00\x00\x00"
        b"\xbf\x00\x00\x00?\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?"
        b"\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?\x00\x00\x00\xbf\x00\x00\x00\xbf"
        b"\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00"
        b"\x00?\x00\x00\x00\xbf\x00\x00\x00\xbf\x00\x00\x00?\x00\x00\x00\xbf"
    )
