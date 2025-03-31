.. pygltflib documentation master file

pygltflib documentation
=======================

This is a fork of pygltflib, a library for reading, writing and handling GLTF v2 files. It is compatible with Python 3.10 and above.

It supports the entire specification, including materials and animations. Main features are:

- GLB and GLTF support
- Buffer data conversion
- Extensions
- All attributes are type-hinted

About the fork
--------------
The GLTF2 class was split into multiple classes to separate the various actions done on the data to their own classes. The methods intended to be called by the users are on the class GLTF2. All other methods were moved to other files and classes.

This was done as a learning experience in refactoring a python package. I don't intend to provide long term support and improvements.

This package currently has the same name and version as the official pygltflib so only one of them can be installed at a time.

All the tests in test_pygltflib.py are PASSING.

glb binary files with data in chunks after the binary buffer are unsupported.

- Changes :
   - Not required attributes are initialized to None. The default values are shown in the comments of pygltflib.v2.schema.
   - Required attributes need to be set in the constructor.
   - Constants are moved into Enums.
   - Comments above the dataclasses in pygltflib.v2.schema give the references to the glTF™ 2.0 Specification.
   - There are some minor breaking changes that require code updates to work. The examples are not all updated and might not work.
   - Sphinx Documentation.

Overview of GLTF2 class
-----------------------

- GLTF2Data Properties
   - JSON
   - BIN
   - CHUNKS
   - path_dir

- GLTF2JSON Properties
   - extensionsUsed
   - extensionsRequired
   - accessors
   - animations
   - asset
   - buffers
   - bufferViews
   - cameras
   - images
   - materials
   - meshes
   - nodes
   - samplers
   - scene
   - scenes
   - skins
   - textures
   - extensions
   - extras

- High level methods
   - convert_buffers
   - convert_images
   - export_image
   - load
   - save

- Low level methods
   - identify_uri
   - get_data_from_buffer_uri
   - get_data_from_buffer_index
   - gltf_from_json
   - gltf_to_json
   - get_bin_name_from_path
   - remove_bufferView
   - load_binary
   - load_from_bytes
   - save_binary
   - save_to_bytes

.. toctree::
   :caption: Quickstart
   :maxdepth: 10
   
   Home <self>
   quickstart/installation

.. toctree::
   :caption: How-to guides
   :maxdepth: 10

   actions/general
   actions/load
   actions/save
   actions/convert
   actions/export
   actions/validate

.. toctree::
   :caption: Code documentation 
   :maxdepth: 3
   
   modules/modules

.. toctree::
   :caption: About
   :maxdepth: 10
   
   about

