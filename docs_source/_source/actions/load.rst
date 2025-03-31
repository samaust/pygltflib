Load
====

For .gltf and .glb files, load method auto detects based on extension.

Load a .gltf file
-----------------

.. code-block:: python

    from pygltflib import GLTF2

    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)

Load a binary .glb file
-----------------------

.. code-block:: python

    from pygltflib import GLTF2

    glb_filename = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
    glb = GLTF2().load(glb_filename)


Load a binary file with an unusual extension
--------------------------------------------

Helper methods:
- load_json
- load_binary 

.. code-block:: python

    from pygltflib import GLTF2

    glb = GLTF2().load_binary("BinaryGLTF.glk")   


Load a B3DM file
----------------

.B3DM files are a deprecated format used by CesiumJS. They are a wrapper around a GLTF1 file. pygltflib only supports
GLTF2 files. Please open an issue if this is important to you!
