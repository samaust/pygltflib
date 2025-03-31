"""
glTF 2.0 Save .gltf file
"""
import copy
from dataclasses import (
    _is_dataclass_instance,
    fields,
)
from dataclasses_json.core import _ExtendedEncoder as JsonEncoder
from datetime import date, datetime
import json
from pathlib import Path
from typing import Any, Callable
import warnings

from pygltflib.v2.schema import (
    Attributes,
    Buffer,
    GLTF2Data,
    GLTF2JSON
)


class GLTF2SaveFileGltf:
    """
    GLTF2SaveFileGltf
    """
    def __init__(
            self,
            data: GLTF2Data):
        self.data = data

    @staticmethod
    def _save_gltf_json(path, gltf2_data):
        """
        Save gltf data to a .glb file
        """
        with open(path, "w") as f:
            f.write(gltf2_data)

    @staticmethod
    def _asdict_inner(obj, dict_factory) -> Any:
        # return the same result as dataclass _asdict_inner
        # except for Attributes, which can have custom specifiers.
        if type(obj) is Attributes:
            return copy.deepcopy(obj.__dict__)
        if _is_dataclass_instance(obj):
            result = []
            for f in fields(obj):
                value = GLTF2SaveFileGltf._asdict_inner(getattr(obj, f.name), dict_factory)
                result.append((f.name, value))
            return dict_factory(result)
        elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
            return type(obj)(*[GLTF2SaveFileGltf._asdict_inner(v, dict_factory) for v in obj])
        elif isinstance(obj, (list, tuple)):

            return type(obj)(GLTF2SaveFileGltf._asdict_inner(v, dict_factory) for v in obj)
        elif isinstance(obj, dict):
            return type(obj)((GLTF2SaveFileGltf._asdict_inner(k, dict_factory),
                              GLTF2SaveFileGltf._asdict_inner(v, dict_factory))
                             for k, v in obj.items())
        else:
            return copy.deepcopy(obj)

    @staticmethod
    def _delete_empty_keys(dictionary: dict) -> dict:
        """
        Delete keys with the value ``None`` in a dictionary, recursively.

        This alters the input so you may wish to ``copy`` the dict first.

        Courtesy Chris Morgan and modified from:
        https://stackoverflow.com/questions/4255400/exclude-empty-null-values-from-json-serialization
        """
        for key, value in list(dictionary.items()):
            if value is None or (hasattr(value, '__iter__') and len(value) == 0):
                del dictionary[key]
            elif isinstance(value, dict) and key != "extensions":
                # delete empty dicts except when the dictionary
                # is an extension inside "extensions".
                # The extension exemption is because we use dicts
                # for extensions instead of dataclass objects
                GLTF2SaveFileGltf._delete_empty_keys(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        GLTF2SaveFileGltf._delete_empty_keys(item)
        return dictionary  # For convenience

    @staticmethod
    def _gltf_asdict(obj, *, dict_factory=dict) -> dict:
        # convert a dataclass object to a dict
        if not _is_dataclass_instance(obj):
            raise TypeError("asdict() should be called on dataclass instances")
        return GLTF2SaveFileGltf._asdict_inner(obj, dict_factory)

    @staticmethod
    def _json_serial(obj) -> str:
        """
        JSON serializer for objects not serializable by default json code
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    @staticmethod
    def _to_json(
            *,
            json_data: GLTF2JSON,
            skipkeys: bool = False,
            ensure_ascii: bool = True,
            check_circular: bool = True,
            allow_nan: bool = True,
            indent: int | str | None = None,
            separators: tuple[str, str] | None = None,
            default: Callable | None = None,
            sort_keys: bool = False,
            **kw) -> str:
        """
        to_json and from_json from dataclasses_json
        courtesy https://github.com/lidatong/dataclasses-json
        """

        data_dict = GLTF2SaveFileGltf._gltf_asdict(json_data)
        data_dict = GLTF2SaveFileGltf._delete_empty_keys(data_dict)
        return json.dumps(data_dict,
                          cls=JsonEncoder,
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan,
                          indent=indent,
                          separators=separators,
                          default=default,
                          sort_keys=sort_keys,
                          **kw)

    @staticmethod
    def _gltf_to_json(
            json_data: GLTF2JSON,
            separators: tuple | None = None,
            indent: int | str | None = "  ") -> str:
        """
        gltf_to_json
        """
        return GLTF2SaveFileGltf._to_json(
            json_data=json_data,
            default=GLTF2SaveFileGltf._json_serial,
            indent=indent,
            allow_nan=False,
            skipkeys=True,
            separators=separators
        )

    @staticmethod
    def _save_gltf_buffer(
            file_path: Path,
            buffer: Buffer,
            binary_payload: bytes):
        """
        Save a buffer to a file.
        """
        with open(file_path, "wb") as f:
            f.write(binary_payload)  # save bin file

    @staticmethod
    def _save_gltf_buffer_bin(
            path: Path,
            binary_buffer: Buffer,
            binary_blob: bytes) -> None:
        """
        Save a buffer with data provided by the GLB-stored BIN chunk
        to a .bin file.
        """
        if binary_buffer.uri is None:  # assume loaded from glb binary file
            if binary_blob is None:
                warnings.warn(f"binary buffer is empty: {binary_buffer}")
                return
            # Save .bin file
            file_path = path.with_suffix(".bin")
            GLTF2SaveFileGltf._save_gltf_buffer(
                file_path, binary_buffer, binary_blob)
            # update the buffer uri to point to our new local bin file
            binary_buffer.uri = file_path.name

    def save(self, destination: Path):
        """
        save_gltf
        """
        # Save binary_blob as bin file
        if self.data.BIN is not None:  # Binary buffer
            # binary buffer MUST be the first element of buffers
            binary_buffer = self.data.JSON.buffers[0]
            self._save_gltf_buffer_bin(
                destination, binary_buffer, self.data.BIN)

        # NOT IMPLEMENTED
        # Save other buffers payloads to files
        #for i, buffer in enumerate(data.buffers):
        #    if i == 0: continue  # skip first buffer
        #    file_path = Path(path.parent, buffer.uri) if buffer.uri is not None else Path(path.parent, f"{i}".unknown)
        #    binary_payload = NOTIMPLEMENTED
        #    self._save_gltf_buffer(file_path, buffer, binary_payload)

        # Save json
        data_json = self._gltf_to_json(self.data.JSON)
        self._save_gltf_json(destination, data_json)
