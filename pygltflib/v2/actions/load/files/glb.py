"""
glTF 2.0 Load .glb file
"""
from pathlib import Path
import struct
from typing import Any
import warnings

from pygltflib.exceptions import ValidationError
from pygltflib.v2.actions.load.files.gltf import GLTF2LoadFileGltf
from pygltflib.v2.schema import (
    BINARY_GLTF_MAGIC,
    GLTF_MIN_VERSION,
    GLTF_MAX_VERSION,
    Binary_gLTF_ChunkType,
    GLTF2Data
)


class GLTF2LoadBinary:
    """
    GLTF2LoadBinary
    """
    @staticmethod
    def _load_binary_chunk_info(
            data: bytes, byte_index: int) -> tuple[int, int, str]:
        chunk_length = struct.unpack("<I", data[byte_index:byte_index + 4])[0]
        byte_index += 4
        chunk_type = bytes(struct.unpack(
            "<BBBB", data[byte_index:byte_index + 4])).decode()
        byte_index += 4
        return (byte_index, chunk_length, chunk_type,)

    @staticmethod
    def _load_binary_chunk_JSON(
            data: bytes, byte_index: int, chunk_length: int):
        start = byte_index
        end = byte_index + chunk_length
        raw_json = data[start:end].decode("utf-8")
        return GLTF2LoadFileGltf._gltf_from_json(raw_json, infer_missing=True)

    @staticmethod
    def _load_binary_chunk_BIN(data, byte_index, chunk_length) -> bytes:
        start = byte_index
        end = byte_index + chunk_length
        return data[start:end]

    @staticmethod
    def _load_from_bytes(bytes_read) -> GLTF2Data:
        # glTF 2.0, 4.4.2 Header (12 bytes)
        # Load Header

        # magic (4 bytes)
        magic = struct.unpack("<BBBB", bytes_read[:4])
        if bytearray(magic) != BINARY_GLTF_MAGIC:
            raise IOError("Unable to load binary gltf file. Header does not "
                          "appear to be valid glb format.")

        # version (4 bytes), length (4 bytes)
        version, length = struct.unpack("<II", bytes_read[4:12])
        if version > GLTF_MAX_VERSION or version < GLTF_MIN_VERSION:
            warnings.warn(
                "pygltflib does not support version strictly smaller than "
                f"v{GLTF_MIN_VERSION} or strictly larger than "
                f"v{GLTF_MAX_VERSION} of the binary gltf format, this file is "
                "version {version}, it may not import correctly. "
                "Please open an issue at "
                "https://gitlab.com/dodgyville/pygltflib/issues")

        # glTF 2.0, 4.4.3. Chunks
        # Load Binary Chunks
        chunk_index = 0
        byte_index = 12  # Start of Chunk 0

        # Load Chunk 0 Informations
        byte_index, chunk_length, chunk_type = GLTF2LoadBinary._load_binary_chunk_info(
            bytes_read, byte_index)

        if chunk_type != Binary_gLTF_ChunkType.JSON.value:
            raise ValidationError("Chunk 0 is not of type JSON.")

        # Load Binary Chunk 0 (JSON) data
        JSON_data = GLTF2LoadBinary._load_binary_chunk_JSON(
            bytes_read, byte_index, chunk_length)
        chunk_index += 1
        byte_index += chunk_length

        BIN_data = None
        while byte_index < length:
            # Load Binary Chunk Informations
            byte_index, chunk_length, chunk_type = GLTF2LoadBinary._load_binary_chunk_info(
                bytes_read, byte_index)
            match chunk_type:
                case Binary_gLTF_ChunkType.BIN.value:
                    # Load Binary Chunk (BIN) data
                    BIN_data = GLTF2LoadBinary._load_binary_chunk_BIN(
                        bytes_read, byte_index, chunk_length)
                case _:
                    # Ignore other chunk types
                    warnings.warn(
                        f"Ignoring chunk {chunk_index} with unknown type "
                        f"'{chunk_type}', probably glTF extensions. "
                        "Please open an issue at "
                        "https://gitlab.com/dodgyville/pygltflib/issues")

            chunk_index += 1
            byte_index += chunk_length

        gltf2_data = GLTF2Data(
            JSON=JSON_data, BIN=BIN_data, CHUNKS=[], path_dir=Path())

        return gltf2_data


class GLTF2LoadFileGlb:
    """
    GLTF2LoadGlb
    """
    def load(self, source: Path) -> GLTF2Data:
        """
        Load a .glb file.
        """
        with source.open(mode="rb") as f:
            bytes_read = f.read()
        gltf2_data = GLTF2LoadBinary._load_from_bytes(bytes_read)
        gltf2_data.path_dir = source.parent

        return gltf2_data


class GLTF2LoadBinaryObject:
    """
    GLTF2LoadBinaryObject
    """
    def __init__(self, fileObject: Any):
        self.fileObject = fileObject

    def load(self) -> GLTF2Data:
        """
        Load binary from a file-like object.

        It is the responsability of the caller to open and close the file-like
        object.
        """
        bytes_read = self.fileObject.read()
        gltf2_data = GLTF2LoadBinary._load_from_bytes(bytes_read)
        return gltf2_data
