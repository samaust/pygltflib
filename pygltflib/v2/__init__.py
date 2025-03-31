from pathlib import Path
import warnings

from pygltflib.exceptions import SaveDestinationEmptyError
from pygltflib.v2.schema import BufferFormat, GLTF2JSON, GLTF2Data

from pygltflib.v2.actions.load.files import GLTF2Load
from pygltflib.v2.actions.load.files.gltf import GLTF2LoadFileGltf
from pygltflib.v2.actions.load.files.glb import GLTF2LoadBinary

from pygltflib.v2.actions.save.files import GLTF2Save
from pygltflib.v2.actions.save.files.gltf import GLTF2SaveFileGltf
from pygltflib.v2.actions.save.files.glb import GLTF2SaveFileGlb

from pygltflib.v2.actions.convert.buffers import GLTF2ConvertBuffers
from pygltflib.v2.actions.convert.images import GLTF2ConvertImages
from pygltflib.v2.actions.convert.utils import _identify_uri, _get_data_from_uri

from pygltflib.v2.actions.export.images import GLTF2ExportImage


class GLTF2:
    """
    Class to process .gltf, .glb and .bin files.
    """
    # =========================================================================
    # Data
    # =========================================================================
    def __init__(
            self,
            JSON: GLTF2JSON | None = None,
            BIN: bytes | None = None,
            CHUNKS: list[bytes | None] | None = None,
            path_dir: Path = Path()):
        """
        Initialize attributes
        """
        JSON_init = JSON
        if JSON_init is None:
            JSON_init = GLTF2JSON()

        CHUNKS_init = CHUNKS
        if CHUNKS_init is None:
            CHUNKS_init = []

        # Store in data to easily share with other classes
        self.data: GLTF2Data = GLTF2Data(
            JSON=JSON_init,
            BIN=BIN,
            CHUNKS=CHUNKS_init,
            path_dir=path_dir)

    # =========================================================================
    # Properties
    # =========================================================================

    # GLTF2Data properties

    @property
    def JSON(self):
        return self.data.JSON

    @JSON.setter
    def JSON(self, value):
        self.data.JSON = value

    @property
    def BIN(self):
        return self.data.BIN

    @BIN.setter
    def BIN(self, value):
        self.data.BIN = value

    @property
    def CHUNKS(self):
        return self.data.CHUNKS

    @CHUNKS.setter
    def CHUNKS(self, value):
        self.data.CHUNKS = value

    @property
    def path_dir(self):
        return self.data.path_dir

    @path_dir.setter
    def path_dir(self, value):
        self.data.path_dir = value

    # GLTF2JSON properties

    @property
    def extensionsUsed(self):
        return self.data.JSON.extensionsUsed

    @extensionsUsed.setter
    def extensionsUsed(self, value):
        self.data.JSON.extensionsUsed = value

    @property
    def extensionsRequired(self):
        return self.data.JSON.extensionsRequired

    @extensionsRequired.setter
    def extensionsRequired(self, value):
        self.data.JSON.extensionsRequired = value

    @property
    def accessors(self):
        return self.data.JSON.accessors

    @accessors.setter
    def accessors(self, value):
        self.data.JSON.accessors = value

    @property
    def animations(self):
        return self.data.JSON.animations

    @animations.setter
    def animations(self, value):
        self.data.JSON.animations = value

    @property
    def asset(self):
        return self.data.JSON.asset

    @asset.setter
    def asset(self, value):
        self.data.JSON.asset = value

    @property
    def buffers(self):
        return self.data.JSON.buffers

    @buffers.setter
    def buffers(self, value):
        self.data.JSON.buffers = value

    @property
    def bufferViews(self):
        return self.data.JSON.bufferViews

    @bufferViews.setter
    def bufferViews(self, value):
        self.data.JSON.bufferViews = value

    @property
    def cameras(self):
        return self.data.JSON.cameras

    @cameras.setter
    def cameras(self, value):
        self.data.JSON.cameras = value

    @property
    def images(self):
        return self.data.JSON.images

    @images.setter
    def images(self, value):
        self.data.JSON.images = value

    @property
    def materials(self):
        return self.data.JSON.materials

    @materials.setter
    def materials(self, value):
        self.data.JSON.materials = value

    @property
    def meshes(self):
        return self.data.JSON.meshes

    @meshes.setter
    def meshes(self, value):
        self.data.JSON.meshes = value

    @property
    def nodes(self):
        return self.data.JSON.nodes

    @nodes.setter
    def nodes(self, value):
        self.data.JSON.nodes = value

    @property
    def samplers(self):
        return self.data.JSON.samplers

    @samplers.setter
    def samplers(self, value):
        self.data.JSON.samplers = value

    @property
    def scene(self):
        return self.data.JSON.scene

    @scene.setter
    def scene(self, value):
        self.data.JSON.scene = value

    @property
    def scenes(self):
        return self.data.JSON.scenes

    @scenes.setter
    def scenes(self, value):
        self.data.JSON.scenes = value

    @property
    def skins(self):
        return self.data.JSON.skins

    @skins.setter
    def skins(self, value):
        self.data.JSON.skins = value

    @property
    def textures(self):
        return self.data.JSON.textures

    @textures.setter
    def textures(self, value):
        self.data.JSON.textures = value

    @property
    def extensions(self):
        return self.data.JSON.extensions

    @extensions.setter
    def extensions(self, value):
        self.data.JSON.extensions = value

    @property
    def extras(self):
        return self.data.JSON.extras

    @extras.setter
    def extras(self, value):
        self.data.JSON.extras = value

    # =========================================================================
    # Low-level
    # =========================================================================

    def identify_uri(self, uri):
        """
        Identify the format of the requested buffer. File, data or binary blob.

        :param uri: Either a data URI that embeds binary resources in the glTF
            JSON, a relative path or None.
        :type uri: str, optional.
        :return: Buffer format. None if failed to identify buffer format.
        :rtype: BufferFormat or None
        """
        return _identify_uri(
            path_dir=self.path_dir,
            buffers_len=len(self.data.JSON.buffers),
            uri=uri)

    def get_data_from_buffer_uri(self, uri: str):
        current_buffer_format = self.identify_uri(uri=uri)
        return _get_data_from_uri(uri, current_buffer_format)

    def get_data_from_buffer_index(self, bufferIndex):
        """
        bufferIndex = bufferView.buffer
        """
        return self.get_data_from_buffer_uri(
            self.data.JSON.buffers[bufferIndex].uri)

    def gltf_from_json(self, json_data):
        JSON_data = GLTF2LoadFileGltf._gltf_from_json(
            json_data, infer_missing=True)
        return JSON_data

    def gltf_to_json(self, separators=None, indent: str | None = "  ") -> str:
        json_data = GLTF2SaveFileGltf._gltf_to_json(
            json_data=self.data.JSON,
            separators=separators,
            indent=indent
        )
        return json_data

    def get_bin_name_from_path(self, path: Path):
        """
        Remove an extension and path and return a bin filename (sans path)
        """
        return str(Path(path.stem)) + ".bin"

    def remove_bufferView(self, buffer_view_id):
        GLTF2ConvertImages(data=self.data)._remove_bufferView(buffer_view_id)

    @classmethod
    def load_binary(cls, source):
        gltf2_data = GLTF2Load(source=source).load()
        gltf2 = GLTF2(JSON=gltf2_data.JSON, BIN=gltf2_data.BIN,
                      CHUNKS=gltf2_data.CHUNKS, path_dir=gltf2_data.path_dir)
        return gltf2

    @staticmethod
    def load_from_bytes(bytes_read):
        gltf2_data = GLTF2LoadBinary._load_from_bytes(bytes_read=bytes_read)
        gltf2 = GLTF2(JSON=gltf2_data.JSON, BIN=gltf2_data.BIN,
                      CHUNKS=gltf2_data.CHUNKS, path_dir=gltf2_data.path_dir)
        return gltf2

    def save_binary(self, destination, min_alignment: int = 4):
        GLTF2SaveFileGlb(
            data=self.data,
            min_alignment=min_alignment).save(destination=destination)

    def save_to_bytes(self):
        return GLTF2SaveFileGlb(data=self.data)._save_to_bytes()

    # =========================================================================
    # High-level
    # =========================================================================

    def convert_buffers(
            self,
            buffer_format: BufferFormat,
            overwrite: bool = False):
        return GLTF2ConvertBuffers(
            self.data, self.path_dir)._convert_buffers(buffer_format,
                                                       overwrite)

    def convert_images(
            self,
            image_format,
            destination_dir=None,
            overwrite=False):
        """
        Convert images to an image format

        GLTF files can store the image data in three different formats:
        In the buffers, as a data uri string and as external images files.
        This converts the images between the formats.

        :param image_format: Destination Image format.
        :type image_format: ImageFormat
        :param destination_dir: Destination path, optional.
            Must be a directory. If None, will use load directory.
        :type destination_dir: str
        :param overwrite: Default = False. Set to True to overwrite a file if
            it exists.
        :type overwrite: bool
        """
        GLTF2ConvertImages(
            data=self.data,
            overwrite=overwrite
        ).convert_images(
            image_format=image_format,
            destination_dir=destination_dir)

    def export_image(
            self,
            image_index: int,
            destination: str = '',
            overwrite: bool = False):
        """
        Export an image to a file

        :param image_index: Image index
        :type image_index: int
        :param destination: Destination path. Can be a directory or a file.
        :type destination: str
        :param overwrite: Default = False. Set to True to overwrite a file if
            it exists.
        :type overwrite: bool
        """
        # path_dir is set after a successful load
        if self.path_dir:
            file_name = GLTF2ExportImage(
                data=self.data,
                images=self.images,
                image_index=image_index,
                path_dir=self.path_dir,
                destination=Path(destination),
                overwrite=overwrite).export_image()
            return file_name
        else:
            warnings.warn("No data loaded. Nothing to export.")

    @classmethod
    def load(cls, source):
        """
        Load a .gltf, .glb or .bin file from a file or file-like binary object.

        :param source: Path of file to load or file-like binary object
        :type source: str or Any
        :return: pygltflib.v2.schema.GLTF2Data instance
        :rtype: pygltflib.v2.schema.GLTF2Data
        """
        gltf2_data = GLTF2Load(source=source).load()
        gltf2 = GLTF2(JSON=gltf2_data.JSON, BIN=gltf2_data.BIN,
                      CHUNKS=gltf2_data.CHUNKS, path_dir=gltf2_data.path_dir)
        return gltf2

    def save(self, destination: str | Path, min_alignment: int = 4):
        """
        Save a .gltf or .glb file and optionnally a .bin file

        :param destination: Path of file to save. Use .gltf or .glb extension.
        :type destination: str or Path
        :param min_alignment: minimum alignment, optional.
            Set the minimum alignment for chunks.
            A larger alignment may still be used if necessary.
            Only power-of-two alignments are supported.
        :type min_alignment: int
        """
        # Raise DestinationEmptyError if source is None
        if destination is None:
            raise SaveDestinationEmptyError("Save destination is empty.")

        GLTF2Save(
            data=self.data,
            destination=Path(destination),
            min_alignment=min_alignment).save()
