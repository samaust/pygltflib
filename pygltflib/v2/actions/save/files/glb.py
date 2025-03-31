"""
glTF 2.0 Save .glb file
"""
from pathlib import Path
import struct
from typing import Any
import warnings

from pygltflib.v2.schema import (
    BINARY_GLTF_MAGIC,
    BINARY_GLTF_VERSION,
    Binary_gLTF_ChunkType,
    GLTF2Data
)
from pygltflib.v2.actions.save.files import GLTF2SaveFileGltf
from pygltflib.v2.actions.convert.utils import _decode_data_uri


class GLTF2SaveFileGlb:
    """
    GLTF2SaveFileGlb
    """
    def __init__(
            self,
            data: GLTF2Data,
            min_alignment: int = 4):
        self.data = data

        # Binary glTF has alignment requirements
        self.alignment: int = self._calculate_alignment(
            min_alignment=min_alignment,
            extensionsUsed=data.JSON.extensionsUsed,
            extensionsRequired=data.JSON.extensionsRequired,
            extensions=data.JSON.extensions
        )

    @staticmethod
    def _calculate_alignment(
            min_alignment: int,
            extensionsUsed: list[str],
            extensionsRequired: list[str],
            extensions: dict[str, Any] | None) -> int:
        """
        Get the required alignment for chunks.

        By default this is 4, unless a larger alignment is requested or
        required by an extension.

        To support the EXT_structural_metadata extension, pygltflib will pad
        chunks using 8-bytes instead of 4 when it detects the presence of this
        extension in a GLTF2 object (if EXT_structural_metadata is in
        self.extensionsUsed, self.extensionsRequired or self.extensions)

        :return: The required alignment.
        :rtype: int
        """
        # Calculate minimum data aligment
        if (min_alignment is None or min_alignment < 4):
            min_alignment = 4

        # round up to next power-of-two
        min_alignment = 1 << (min_alignment - 1).bit_length()

        required_min_alignment = min_alignment

        # Adjust alignement based on extensions requirements
        if ("EXT_structural_metadata" in extensionsUsed or
            "EXT_structural_metadata" in extensionsRequired or
            (extensions is not None and
                "EXT_structural_metadata" in extensions)):
            # EXT_structural_metadata requires an 8 byte alignment.
            required_alignment = max(required_min_alignment, 8)
        else:
            required_alignment = required_min_alignment

        return required_alignment

    def _buffers_to_binary_blob(self) -> bytes:
        """
        Flatten all buffers into a single buffer
        """
        buffer_blob = bytearray()
        offset = 0
        path_dir = self.data.path_dir
        assert path_dir is not None
        for i, bufferView in enumerate(self.data.JSON.bufferViews):
            buffer = self.data.JSON.buffers[bufferView.buffer]
            if buffer.uri is None:  # assume loaded from glb binary file
                binary_payload = self.data.BIN
            elif buffer.uri.startswith("data:"):
                binary_payload = _decode_data_uri(buffer.uri)
            elif Path(path_dir, buffer.uri).is_file():
                with open(Path(path_dir, buffer.uri), 'rb') as fb:
                    binary_payload = fb.read()
            else:
                warnings.warn(f"Unable to save bufferView {buffer.uri[:20]} "
                              "to glb, skipping. "
                              "Please open an issue at "
                              "https://gitlab.com/dodgyville/pygltflib/issues")
                continue
            byte_offset = bufferView.byteOffset if bufferView.byteOffset is not None else 0
            byte_length = bufferView.byteLength

            bufferView.byteOffset = offset
            bufferView.byteLength = byte_length
            bufferView.buffer = 0

            if binary_payload is not None:
                start = byte_offset
                end = byte_offset + byte_length
                buffer_blob += binary_payload[start:end]

            # Pad each buffer to the required alignment (usually 4 bytes)
            # to make following data happy
            padding = -byte_length % self.alignment
            buffer_blob += b'\0' * padding
            offset += padding

            offset += byte_length

        return bytes(buffer_blob)

    def _save_to_bytes(self) -> list[bytes]:
        # Flatten all buffers into a single buffer
        buffer_blob = self._buffers_to_binary_blob()

        # Serialize GLTF2Data class instance to json
        json_blob = GLTF2SaveFileGltf._gltf_to_json(
            json_data=self.data.JSON,
            separators=(',', ':'),
            indent=None).encode("utf-8")

        # Prepare header
        version = struct.pack('<I', BINARY_GLTF_VERSION)
        chunk_header_len = 8
        gltf_header_len = len(BINARY_GLTF_MAGIC) + len(version) + 4

        # Pad each blob if needed; include the whole length before the json
        # too, to reach global alignment. We subtract one chunk header length,
        # so the start of the binary blob is aligned (otherwise the header
        # would be aligned, instead of the data).
        padding = -(gltf_header_len
                    + chunk_header_len
                    + len(json_blob)
                    - chunk_header_len) % self.alignment
        if padding != 0:
            json_blob += b' ' * padding

        length = (gltf_header_len
                  + chunk_header_len * 2
                  + len(json_blob)
                  + len(buffer_blob))

        # header is MAGIC, version, length
        # json chunk is json_blob length, JSON, json_blob
        # buffer chunk is length of buffer_blob, utf-8, buffer_blob
        return [
            # Header
            BINARY_GLTF_MAGIC,
            version,
            struct.pack('<I', length),
            # Chunk 0 (JSON)
            struct.pack('<I', len(json_blob)),
            bytes(Binary_gLTF_ChunkType.JSON.value, 'utf-8'),
            json_blob,
            # Chunk 1 (Binary Buffer)
            struct.pack('<I', len(buffer_blob)),
            bytes(Binary_gLTF_ChunkType.BIN.value, 'utf-8'),
            buffer_blob
        ]

    def save(self, destination: Path):
        with open(destination, 'wb') as f:
            glb_structure = self._save_to_bytes()
            if not glb_structure:
                return False
            for data in glb_structure:
                f.write(data)
