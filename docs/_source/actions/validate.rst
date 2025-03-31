Validate
========

For a more complete validator, visit:

- Hosted validator : https://github.khronos.org/glTF-Validator/
- Source code : https://github.com/KhronosGroup/glTF-Validator

pyglftlib validator
-------------------

Validate a gltf object.

This experimental validator only validates a few rules about GLTF2 objects.


.. code-block:: python

    from pygltflib import GLTF2
    from pygltflib.validator import validate, summary

    filename = "glTF-Sample-Models/2.0/AnimatedCube/glTF/AnimatedCube.gltf"
    gltf = GLTF2().load(filename)
    validate(gltf)  # will throw an error depending on the problem
    summary(gltf)  # will pretty print human readable summary of errors
