Convert
=======

Convert buffers to GLB binary buffers

.. code-block:: python

    from pygltflib import GLTF2, BufferFormat

    gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
    
    gltf.convert_buffers(BufferFormat.BINARYBLOB)   # convert buffers to GLB blob


Convert buffer to data uri (embedded) buffer


.. code-block:: python

    from pygltflib import GLTF2, BufferFormat

    gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
    
    gltf.convert_buffers(BufferFormat.DATAURI)  # convert buffer URIs to data.


Convert buffers to binary file (external) buffers

.. code-block:: python

    from pygltflib import GLTF2, BufferFormat

    gltf = GLTF2().load("glTF-Sample-Models/2.0/Box/glTF/Box.gltf")
    
    gltf.convert_buffers(BufferFormat.BINFILE)   # convert buffers to files
    gltf.save("test.gltf")  # all the buffers are saved in 0.bin, 1.bin, 2.bin.


Convert texture images inside a GLTF file to their own PNG files


.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.utils import ImageFormat
    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)
    gltf.convert_images(ImageFormat.FILE)
    gltf.images[0].uri  # will now be 0.png and the texture image will be saved in 0.png



Convert texture images from a GLTF file to their own PNG files using custom file names


.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.utils import ImageFormat
    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)
    gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
    gltf.convert_images(ImageFormat.FILE)
    gltf.images[0].uri  # will now be cube.png and the texture image will be saved in cube.png



Specify a path to my images when converting to files

By default pygltflib will load images from the same location as the GLTF file.

It will also try and save image files to the that location when converting image buffers or data uris.

.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.utils import ImageFormat
    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)
    gltf.images[0].name = "cube.png"  # will save the data uri to this file (regardless of data format)
    gltf.convert_images(ImageFormat.FILE, path='/destination/') 
    gltf.images[0].uri  # will now be cube.png and the texture image will be saved in /destination/cube.png


Import PNG files as textures into a GLTF

.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.utils import ImageFormat, Image
    gltf = GLTF2()
    image = Image()
    image.uri = "myfile.png"
    gltf.images.append(image)
    gltf.convert_images(ImageFormat.DATAURI)
    gltf.images[0].uri  # will now be something like "data:image/png;base64,iVBORw0KGg..."
    gltf.images[0].name  # will be myfile.png