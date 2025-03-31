"""
glTF 2.0 Schema

Contains enums and dataclasses for glTF 2.0.

About the GLTF2 file format:

glTF uses a right-handed coordinate system, that is, 
the cross product of +X and +Y yields +Z. glTF defines +Y as up.
The front of a glTF asset faces +Z.
The units for all linear distances are meters.
All angles are in radians.
Positive rotation is counterclockwise.
"""
import copy
from dataclasses import (
    dataclass,
    field,
)
from dataclasses_json import dataclass_json as dataclass_json
from enum import Enum
import json
from pathlib import Path
from typing import Any
import warnings


__version__ = "1.16.3"


GLTF_MIN_VERSION = 2  # minimum version this library can load
GLTF_MAX_VERSION = 2  # maximum supported version this library can load

# glTF 2.0 Enums

# glTF 2.0, 2.6. File Extensions and Media Types
# glTF 2.0, 3.6. Binary Data Storage
#           3.6.1. Buffers and Buffer Views
#           3.6.1.1. Overview
DATA_URI_HEADER = "data:application/octet-stream;base64,"

# glTF 2.0, 4.4. Binary glTF Layout, 4.4.2. Header
BINARY_GLTF_MAGIC = b'glTF'
BINARY_GLTF_VERSION = 2  # version this library exports


# glTF 2.0, 4.4. Binary glTF Layout
#           4.4.3. Chunks
#           4.4.3.1. Overview
class Binary_gLTF_ChunkType(Enum):
    JSON = "JSON"
    BIN = "BIN\x00"


# glTF 2.0, 5.1.3. accessor.componentType
class Accessor_componentType(Enum):
    BYTE = 5120
    UNSIGNED_BYTE = 5121
    SHORT = 5122
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125
    FLOAT = 5126


ACCESSOR_COMPONENT_TYPES = [
    Accessor_componentType.BYTE.value,
    Accessor_componentType.UNSIGNED_BYTE.value,
    Accessor_componentType.SHORT.value,
    Accessor_componentType.UNSIGNED_SHORT.value,
    Accessor_componentType.UNSIGNED_INT.value,
    Accessor_componentType.FLOAT.value
]

ACCESSOR_SPARSE_INDICES_COMPONENT_TYPES = [
    Accessor_componentType.UNSIGNED_BYTE.value,
    Accessor_componentType.UNSIGNED_SHORT.value,
    Accessor_componentType.UNSIGNED_INT.value
]


# glTF 2.0, 5.1.6. accessor.type
class Accessor_type(Enum):
    SCALAR = "SCALAR"
    VEC2 = "VEC2"
    VEC3 = "VEC3"
    VEC4 = "VEC4"
    MAT2 = "MAT2"
    MAT3 = "MAT3"
    MAT4 = "MAT4"


# glTF 2.0, 5.7.2. animation.channel.target.path
class Animation_channel_target_path(Enum):
    TRANSLATION = "translation"
    ROTATION = "rotation"
    SCALE = "scale"
    WEIGHTS = "weights"


ANIMATION_CHANNEL_TARGET_PATHS = [
    Animation_channel_target_path.TRANSLATION.value,
    Animation_channel_target_path.ROTATION.value,
    Animation_channel_target_path.SCALE.value,
    Animation_channel_target_path.WEIGHTS.value
]


# glTF 2.0, 5.8.2. animation.sampler.interpolation
class Animation_sampler_interpolation(Enum):
    LINEAR = "LINEAR"
    STEP = "STEP"
    CUBICSPLINE = "CUBICSPLINE"


# glTF 2.0, 5.11.5. bufferView.target
class BufferView_target(Enum):
    ARRAY_BUFFER = 34962  # eg vertex data
    ELEMENT_ARRAY_BUFFER = 34963  # eg index data


BUFFERVIEW_TARGETS = [
    BufferView_target.ARRAY_BUFFER.value,
    BufferView_target.ELEMENT_ARRAY_BUFFER.value
]


# glTF 2.0, 5.12.3. camera.type
class Camera_type(Enum):
    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"


CAMERA_TYPES = [
    Camera_type.PERSPECTIVE.value,
    Camera_type.ORTHOGRAPHIC.value
]


# glTF 2.0, 5.18.2. image.mimeType
class Image_mimeType(Enum):
    IMAGEJPEG = 'image/jpeg'
    IMAGEPNG = "image/png"


IMAGE_MIMETYPES = [
    Image_mimeType.IMAGEJPEG.value,
    Image_mimeType.IMAGEPNG.value
]


# glTF 2.0, 5.19.9. material.alphaMode
class Material_alphaMode(Enum):
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"


MATERIAL_ALPHAMODES = [
    Material_alphaMode.OPAQUE.value,
    Material_alphaMode.MASK.value,
    Material_alphaMode.BLEND.value
]


# glTF 2.0, 5.24.4. mesh.primitive.mode
class Mesh_primitive_mode(Enum):
    POINTS = 0
    LINES = 1
    LINE_LOOP = 2
    LINE_STRIP = 3
    TRIANGLES = 4
    TRIANGLE_STRIP = 5
    TRIANGLE_FAN = 6


MESH_PRIMITIVE_MODES = [
    Mesh_primitive_mode.POINTS.value,
    Mesh_primitive_mode.LINES.value,
    Mesh_primitive_mode.LINE_LOOP.value,
    Mesh_primitive_mode.LINE_STRIP.value,
    Mesh_primitive_mode.TRIANGLES.value,
    Mesh_primitive_mode.TRIANGLE_STRIP.value,
    Mesh_primitive_mode.TRIANGLE_FAN.value
]


# glTF 2.0, 5.26.1. sampler.magFilter
class Sampler_magFilter(Enum):
    NEAREST = 9728
    LINEAR = 9729


MAGNIFICATION_FILTERS = [
    Sampler_magFilter.NEAREST.value,
    Sampler_magFilter.LINEAR.value
]


# glTF 2.0, 5.26.2. sampler.minFilter
class Sampler_minFilter(Enum):
    NEAREST = 9728
    LINEAR = 9729
    NEAREST_MIPMAP_NEAREST = 9984
    LINEAR_MIPMAP_NEAREST = 9985
    NEAREST_MIPMAP_LINEAR = 9986
    LINEAR_MIPMAP_LINEAR = 9987


MINIFICATION_FILTERS = [
    Sampler_minFilter.NEAREST.value,
    Sampler_minFilter.LINEAR.value,
    Sampler_minFilter.NEAREST_MIPMAP_NEAREST.value,
    Sampler_minFilter.LINEAR_MIPMAP_NEAREST.value,
    Sampler_minFilter.NEAREST_MIPMAP_LINEAR.value,
    Sampler_minFilter.LINEAR_MIPMAP_LINEAR.value
]


# glTF 2.0, 5.26.3. sampler.wrapS
class Sampler_wrapS(Enum):
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    REPEAT = 10497


# glTF 2.0, 5.26.4. sampler.wrapT
class Sampler_wrapT(Enum):
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    REPEAT = 10497


WRAPPING_MODES = [
    Sampler_wrapS.CLAMP_TO_EDGE.value,
    Sampler_wrapS.MIRRORED_REPEAT.value,
    Sampler_wrapS.REPEAT.value
]


# Other Enums
class BufferFormat(Enum):
    DATAURI = "data uri"
    BINARYBLOB = "binary blob"
    BINFILE = "bin file"
    UNKNOWN = "unkown"


class ImageFormat(Enum):
    DATAURI = "data uri"
    FILE = "image file"
    BUFFERVIEW = "buffer view"


# glTF 2.0 dataclasses

@dataclass_json
@dataclass(kw_only=True)
class Property:
    extensions: dict[str, Any] | None = field(default_factory=dict)
    extras: dict[str, Any] | None = field(default_factory=dict)

    def to_json(self, *args, **kwargs) -> str:
        # Attributes objects can have custom attrs,
        # so use our own json conversion methods.
        data = copy.deepcopy(self.__dict__)
        return json.dumps(data)

# glTF 2.0, 5.3. Accessor Sparse Indices
@dataclass_json
@dataclass(kw_only=True)
class AccessorSparseIndices(Property):
    bufferView: int  # required
    byteOffset: int | None = None  # default = 0
    componentType: int  # required


# glTF 2.0, 5.4. Accessor Sparse Values
@dataclass_json
@dataclass(kw_only=True)
class AccessorSparseValues(Property):
    bufferView: int  # required
    byteOffset: int | None = None  # default = 0


# glTF 2.0, 5.2. Accessor Sparse
@dataclass_json
@dataclass(kw_only=True)
class AccessorSparse(Property):
    count: int  # required
    indices: AccessorSparseIndices  # required
    values: AccessorSparseValues  # required


# glTF 2.0, 5.1. Accessor
@dataclass_json
@dataclass(kw_only=True)
class Accessor(Property):
    bufferView: int | None = None
    byteOffset: int | None = None  # default = 0
    componentType: int  # required
    normalized: bool | None = None  # default = False
    count: int  # required
    type: str  # required. Accessor_type.name
    sparse: AccessorSparse | None = None
    max: list[float] | None = field(default_factory=list)
    min: list[float] | None = field(default_factory=list)
    name: str | None = None


# glTF 2.0, 5.7. Animation Channel Target
@dataclass_json
@dataclass(kw_only=True)
class AnimationChannelTarget(Property):
    node: int | None = None
    path: str  # required


# glTF 2.0, 5.6. Animation Channel
@dataclass_json
@dataclass(kw_only=True)
class AnimationChannel(Property):
    sampler: int  # required
    target: AnimationChannelTarget  # required


# glTF 2.0, 5.8. Animation Sampler
@dataclass_json
@dataclass(kw_only=True)
class AnimationSampler(Property):
    input: int  # required
    interpolation: str | None = None  # default = Animation_sampler_interpolation.LINEAR.value
    output: int  # required


# glTF 2.0, 5.5. Animation
@dataclass_json
@dataclass(kw_only=True)
class Animation(Property):
    channels: list[AnimationChannel] = field(default_factory=list)
    samplers: list[AnimationSampler] = field(default_factory=list)
    name: str | None = None


# glTF 2.0, 5.9. Asset
@dataclass_json
@dataclass(kw_only=True)
class Asset(Property):
    copyright: str | None = None
    generator: str | None = f"pygltflib@v{__version__}"
    version: str = "2.0"  # required
    minVersion: str | None = None


# glTF 2.0, 5.10. Buffer
@dataclass_json
@dataclass(kw_only=True)
class Buffer(Property):
    uri: str | None = None
    byteLength: int
    name: str | None = None


# glTF 2.0, 5.11. Buffer View
@dataclass_json
@dataclass(kw_only=True)
class BufferView(Property):
    buffer: int
    byteOffset: int = 0
    byteLength: int
    byteStride: int | None = None
    target: int | None = None
    name: str | None = None


# glTF 2.0, 5.13. Camera Orthographic
@dataclass_json
@dataclass(kw_only=True)
class CameraOrthographic(Property):
    xmag: float  # required
    ymag: float  # required
    zfar: float  # required
    znear: float  # required


# glTF 2.0, 5.14. Camera Perspective
@dataclass_json
@dataclass(kw_only=True)
class CameraPerspective(Property):
    aspectRatio: float | None = None
    yfov: float  # required
    zfar: float | None = None
    znear: float  # required


# glTF 2.0, 5.12. Camera
@dataclass_json
@dataclass(kw_only=True)
class Camera(Property):
    orthographic: CameraOrthographic | None = None
    perspective: CameraPerspective | None = None
    type: str
    name: str | None = None


# 5.15. Extension - JSON object with extension-specific objects.


# 5.16. Extras - Application-specific data.


# glTF 2.0, 5.18. Image
@dataclass_json
@dataclass(kw_only=True)
class Image(Property):
    uri: str | None = None
    mimeType: str | None = None
    bufferView: int | None = None
    name: str | None = None


# glTF 2.0, 5.30. Texture Info
@dataclass_json
@dataclass(kw_only=True)
class TextureInfo(Property):
    index: int  # required
    texCoord: int | None = None  # default = 0


# glTF 2.0, 5.22. Material PBR Metallic Roughness
@dataclass_json
@dataclass(kw_only=True)
class MaterialPbrMetallicRoughness(Property):
    baseColorFactor: list[float] | None = None  # field(default_factory=list)  # default = [1.0, 1.0, 1.0, 1.0]
    baseColorTexture: TextureInfo | None = None
    metallicFactor: float | None = None  # default = 1.0
    roughnessFactor: float | None = None  # default = 1.0
    metallicRoughnessTexture: TextureInfo | None = None


# glTF 2.0, 5.20. Material Normal Texture Info
@dataclass_json
@dataclass(kw_only=True)
class MaterialNormalTextureInfo(Property):
    index: int  # required
    texCoord: int | None = None  # default = 0
    scale: float | None = None  # default = 1.0


# glTF 2.0, 5.21. Material Occlusion Texture Info
@dataclass_json
@dataclass(kw_only=True)
class MaterialOcclusionTextureInfo(Property):
    index: int  # required
    texCoord: int | None = None  # default = 0
    strength: float | None = None  # default = 1.0


# glTF 2.0, 5.19. Material
@dataclass_json
@dataclass(kw_only=True)
class Material(Property):
    name: str | None = None
    pbrMetallicRoughness: MaterialPbrMetallicRoughness | None = None
    normalTexture: MaterialNormalTextureInfo | None = None
    occlusionTexture: MaterialOcclusionTextureInfo | None = None
    emissiveTexture: TextureInfo | None = None
    emissiveFactor: list[float] | None = None  # field(default_factory=list)  # default = [0.0, 0.0, 0.0]
    alphaMode: str | None = None  # default = Material_alphaMode.OPAQUE.value
    alphaCutoff: float | None = None  # default = 0.5
    doubleSided: bool | None = None  # default = False


# Attributes is a special case so we provide our own json handling
class Attributes:
    """
    glTF 2.0
    3.7. Geometry
    3.7.1. Overview
    3.7.2. Meshes
    3.7.2.1. Overview
    kwargs :
        POSITION
        NORMAL
        TANGENT
        TEXCOORD_n
        COLOR_n
        JOINTS_n
        WEIGHTS_n
    """
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return self.__class__.__qualname__ + '(' + ', '.join(
            [f"{f}={v}" for f, v in self.__dict__.items()]) + ')'

    def to_json(self, *args, **kwargs) -> str:
        # Attributes objects can have custom attrs,
        # so use our own json conversion methods.
        data = copy.deepcopy(self.__dict__)
        return json.dumps(data)

    @staticmethod
    def from_json() -> None:
        warnings.warn("To allow custom attributes on Attributes, "
                      "we don't use dataclasses-json on this class. "
                      "Please open an issue at https://gitlab.com/dodgyville/pygltflib/issues")


# glTF 2.0, 5.24. Mesh Primitive
@dataclass_json
@dataclass(kw_only=True)
class MeshPrimitive(Property):
    attributes: Attributes = field(default_factory=Attributes)  # required
    indices: int | None = None
    mode: int | None = None  # default = Mesh_primitive_mode.TRIANGLES.value
    material: int | None = None
    targets: list[Attributes] | None = field(default_factory=list)


# glTF 2.0, 5.23. Mesh
@dataclass_json
@dataclass(kw_only=True)
class Mesh(Property):
    primitives: list[MeshPrimitive] = field(default_factory=list)  # required
    weights: list[float] | None = field(default_factory=list)
    name: str | None = None


# glTF 2.0, 5.25. Node
@dataclass_json
@dataclass(kw_only=True)
class Node(Property):
    camera: int | None = None
    children: list[int] | None = field(default_factory=list)
    skin: int | None = None
    matrix: list[float] | None = None  # field(default_factory=list)  # default = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    mesh: int | None = None
    rotation: list[float] | None = None  # field(default_factory=list)  # default = [0,0,0,1]
    scale: list[float] | None = None  # field(default_factory=list)  # default = [1,1,1]
    translation: list[float] | None = None  # field(default_factory=list)  # default = [0,0,0]
    weights: list[float] | None = field(default_factory=list)
    name: str | None = None


# glTF 2.0, 5.26. Sampler
@dataclass_json
@dataclass(kw_only=True)
class Sampler(Property):
    """
    Samplers are stored in the samplers array of the asset.
    Each sampler specifies filter and wrapping options
    correspondingto the GL types
    """
    magFilter: int | None = None
    minFilter: int | None = None
    wrapS: int | None = None  # default = Sampler_wrapS.REPEAT.value
    wrapT: int | None = None  # default = Sampler_wrapT.REPEAT.value
    name: str | None = None


# glTF 2.0, 5.27. Scene
@dataclass_json
@dataclass(kw_only=True)
class Scene(Property):
    nodes: list[int] | None = field(default_factory=list)
    name: str | None = None


# glTF 2.0, 5.28. Skin
@dataclass_json
@dataclass(kw_only=True)
class Skin(Property):
    inverseBindMatrices: int | None = None
    skeleton: int | None = None
    joints: list[int] = field(default_factory=list)  # required
    name: str | None = None


# glTF 2.0, 5.29. Texture
@dataclass_json
@dataclass(kw_only=True)
class Texture(Property):
    sampler: int | None = None
    source: int | None = None
    name: str | None = None


# glTF 2.0, 5.17. glTF
@dataclass(kw_only=True)
class GLTF2JSON(Property):
    extensionsUsed: list[str] = field(default_factory=list)
    extensionsRequired: list[str] = field(default_factory=list)
    accessors: list[Accessor] = field(default_factory=list)
    animations: list[Animation] = field(default_factory=list)
    asset: Asset = field(default_factory=Asset)  # required
    buffers: list[Buffer] = field(default_factory=list)
    bufferViews: list[BufferView] = field(default_factory=list)
    cameras: list[Camera] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    meshes: list[Mesh] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    samplers: list[Sampler] = field(default_factory=list)
    scene: int | None = None
    scenes: list[Scene] = field(default_factory=list)
    skins: list[Skin] = field(default_factory=list)
    textures: list[Texture] = field(default_factory=list)


@dataclass(kw_only=True)
class GLTF2Data:
    JSON: GLTF2JSON
    BIN: bytes | None
    CHUNKS: list[bytes | None]
    path_dir: Path
