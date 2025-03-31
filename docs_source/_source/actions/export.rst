Export
======

Export images from the GLTF file to any location (ie outside the GLTF file)

.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.utils import ImageFormat
    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)
    gltf.export_image(0, "output/cube.png", override=True)  # There is now an image file at output/cube.png
