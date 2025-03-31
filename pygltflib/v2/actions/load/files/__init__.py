from enum import Enum
import errno
import os
from pathlib import Path
from typing import Any
import warnings

from pygltflib.exceptions import FileEmptyError, LoadSourceEmptyError
from pygltflib.v2.schema import GLTF2Data, GLTF2JSON
from pygltflib.v2.actions.load.files.gltf import GLTF2LoadFileGltf
from pygltflib.v2.actions.load.files.glb import (
    GLTF2LoadFileGlb,
    GLTF2LoadBinaryObject
)


class GLTF2LoadFile:
    """
    GLTF2LoadFile
    """
    def __init__(self, source: Path):
        self.source = source

    def _load_file_validations(self):
        # Raise FileNotFoundError if the file is not found
        if not self.source.is_file():
            source_str = self.source.absolute().as_posix
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), source_str)

        # Raise FileEmptyError is the file is empty
        size = self.source.stat().st_size
        if size == 0:
            absolute_path = self.source.absolute().as_posix()
            raise FileEmptyError(f"File empty: {absolute_path}")

    def load(self) -> GLTF2Data:
        """
        load
        """
        # Run validations
        self._load_file_validations()

        # Get file loader
        ext = self.source.suffix
        if ext.lower() in [".glb"]:
            loader = GLTF2LoadFileGlb()
        elif ext.lower() in [".gltf"]:
            loader = GLTF2LoadFileGltf()
        else:
            warnings.warn(
                "Unknown file type. "
                "pygltflib supports loading .gltf and .glb files.")
            JSON_data = GLTF2JSON()
            gltf2_data = GLTF2Data(
                JSON=JSON_data, BIN=None,
                CHUNKS=[], path_dir=Path())
            return gltf2_data

        # Load data
        gltf2_data = loader.load(source=self.source)

        return gltf2_data


class GLTF2LoadObject:
    """
    GLTF2LoadObject
    """
    def __init__(self, fileObject: Any):
        self.fileObject = fileObject

    def _load_file_binaryObject(self) -> GLTF2Data:
        # Load from a file-like binary object
        loader = GLTF2LoadBinaryObject(fileObject=self.fileObject)
        gltf2_data = loader.load()
        return gltf2_data

    def load(self) -> GLTF2Data:
        """
        load
        """
        gltf2_data = self._load_file_binaryObject()
        return gltf2_data


class LoadMode(Enum):
    FILE = 1
    OBJECT = 2


class GLTF2Load:
    """
    GLTF2Load
    """
    def __init__(self, source: str | Path):
        # Raise SourceEmptyError if source is None
        if source is None:
            raise LoadSourceEmptyError("Load source is empty.")

        if isinstance(source, str | Path):
            self.mode: LoadMode = LoadMode.FILE
            self.source = Path(source)
        else:
            self.mode: LoadMode = LoadMode.OBJECT
            self.fileObject = self.source

    def load(self) -> GLTF2Data:
        """
        load
        """
        if self.mode is LoadMode.FILE:
            gltf2_data = GLTF2LoadFile(
                source=self.source).load()
            return gltf2_data
        else:  # self.mode is LoadMode.OBJECT
            gltf2_data = GLTF2LoadObject(fileObject=self.fileObject).load()
            return gltf2_data
