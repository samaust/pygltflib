"""
glTF 2.0 Load .gltf file
"""
from dataclasses_json.core import _decode_dataclass
import json
from pathlib import Path
import warnings

from pygltflib.v2.schema import (
    Attributes,
    GLTF2JSON,
    GLTF2Data
)


class GLTF2LoadFileGltf:
    """
    GLTF2LoadJson
    """
    @staticmethod
    def _gltf_from_json(
        s: str,
        *,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        infer_missing=False,
            **kw) -> GLTF2JSON:
        """
        Load a .gltf file.
        """
        init_kwargs = json.loads(
            s,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            **kw)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = _decode_dataclass(GLTF2JSON, init_kwargs, infer_missing)
        for mesh in result.meshes:
            for primitive in mesh.primitives:
                raw_attributes = primitive.attributes
                if raw_attributes:
                    attributes = Attributes(**raw_attributes)
                    primitive.attributes = attributes
        return result

    def load(self, source: Path) -> GLTF2Data:
        """
        Load a .gltf file.
        """
        with source.open(mode="r") as f:
            read_data = f.read()
            JSON_data = GLTF2LoadFileGltf._gltf_from_json(read_data,
                                                          infer_missing=True)
            gltf2_data = GLTF2Data(
                JSON=JSON_data, BIN=None, CHUNKS=[], path_dir=source.parent)

        return gltf2_data
