"""
glTF2 Convert Utils
"""
import base64
from pathlib import Path
import warnings

from pygltflib.v2.schema import BufferFormat, DATA_URI_HEADER


def _identify_uri(path_dir: Path, buffers_len: int, uri: str | None) -> BufferFormat | None:
    absolute_path = path_dir.absolute().as_posix()
    if uri is None:  # assume loaded from glb binary file
        uri_format = BufferFormat.BINARYBLOB
        if buffers_len > 1:
            warnings.warn("GLTF has multiple buffers but only one buffer "
                          "binary blob, pygltflib might corrupt data. "
                          "Please open an issue at "
                          "https://gitlab.com/dodgyville/pygltflib/issues")
    elif uri.startswith("data:"):
        uri_format = BufferFormat.DATAURI
    elif Path(absolute_path, uri).is_file():
        uri_format = BufferFormat.BINFILE
    else:
        uri_format = BufferFormat.UNKNOWN
        warnings.warn("pygltf.GLTF.identify_buffer_format can not "
                      "identify buffer. Please open an issue at "
                      "https://gitlab.com/dodgyville/pygltflib/issues")
    return uri_format


def _load_file_uri(path_dir: Path, uri: str) -> bytes:
    """
    Load a file pointed to by a URI.

    :param uri: A relative path to a file.
    :type uri: str
    :return: Binary data.
    :rtype: bytes
    """
    if uri is None:
        return None

    with open(Path(path_dir, uri), 'rb') as fb:
        data = fb.read()
    return data


def _decode_data_uri(uri: str) -> bytes | None:
    """
    Decodes the binary portion of a data URI.

    :param uri: Either a data URI that embeds binary resources in the
    glTF JSON.
    :type uri: str
    :return: Binary data.
    :rtype: bytes
    """
    if uri is None:
        return None

    data = uri.split(DATA_URI_HEADER)[1]
    data = base64.decodebytes(bytes(data, "utf8"))
    return data


def _get_data_from_uri(
        uri: str | None,
        current_buffer_format,
        path_dir: Path = Path()) -> bytes | None:
    """
    Strip off any headers and do any conversions and return a universal
    binary blob for manipulation.

    Supports two data sources:
    - from a file using
    - a data URI that embeds binary resources in the glTF JSON

    A binary blob is not data from uri.

    Called by convert_buffers and convert_images.

    :param uri: Either a data URI that embeds binary resources in the glTF
        JSON, a relative path or None.
    :type uri: str, optional
    :param current_buffer_format: Current buffer format
    :type current_buffer_format: BufferFormat
    :return: Binary data.
    :rtype: bytes or None.
    """
    if uri is not None and current_buffer_format is BufferFormat.BINFILE:
        data = _load_file_uri(path_dir, uri)
    elif uri is not None and current_buffer_format is BufferFormat.DATAURI:
        data = _decode_data_uri(uri)
    elif current_buffer_format is BufferFormat.BINARYBLOB:
        # Not data from a uri. Return nothing
        return None
    else:
        return None

    return data
