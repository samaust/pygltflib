Save
====

Save a .gltf file
-----------------

.. code-block:: python

    destination = "glTF-Sample-Models/2.0/Box/glTF/Box.gltf"
    gltf.save(destination)


Save a .glb file
----------------

.. code-block:: python

    from pygltflib import GLTF2

    destination = "glTF-Sample-Models/2.0/Box/glTF/Box.gltf"
    glb.save(destination)

Convert a glb to a gltf file
----------------------------

.. code-block:: python

    from pygltflib import GLTF2

    source = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
    glb = GLTF2().load(source)
    
    destination = "glTF-Sample-Models/2.0/Box/glTF/Box.gltf"
    glb.save(destination)

Convert a gltf to a glb file
----------------------------

.. code-block:: python

    from pygltflib import GLTF2

    source = "glTF-Sample-Models/2.0/Box/glTF/Box.gltf"
    gltf.load(source)

    destination = "glTF-Sample-Models/2.0/Box/glTF-Binary/Box.glb"
    gltf.save(destination)
    
