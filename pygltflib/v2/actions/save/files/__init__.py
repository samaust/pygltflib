"""
glTF 2.0 Save .gltf or .glb file
"""
from pathlib import Path
import warnings

from pygltflib.v2.schema import (
    Asset,
    GLTF2Data
)
from pygltflib.v2.actions.save.files.gltf import GLTF2SaveFileGltf
from pygltflib.v2.actions.save.files.glb import GLTF2SaveFileGlb


class GLTF2SaveFile:
    """
    GLTF2SaveFile
    """
    def __init__(
            self,
            data: GLTF2Data,
            destination: Path,
            min_alignment: int):
        self.data = data
        self.destination = destination
        self.min_alignment = min_alignment

    # def _save_file_validations(self):
    #    ...

    def save(self):
        # Run validations
        # self._save_file_validations()

        # Set Asset
        self.data.JSON.asset = Asset()

        # Get file saver
        ext = self.destination.suffix
        if ext.lower() in [".glb"]:
            saver = GLTF2SaveFileGlb(
                data=self.data,
                min_alignment=self.min_alignment)
        else:
            if self.data.BIN is not None:
                warnings.warn(
                    f"This file ({self.destination}) contains a binary blob loaded from "
                    "a .glb file, and this will be saved to a .bin file next "
                    "to the json file.")
            saver = GLTF2SaveFileGltf(
                data=self.data,
            )

        saver.save(destination=self.destination)


class GLTF2Save:
    """
    GLTF2Save
    """
    def __init__(
            self,
            data: GLTF2Data,
            destination: Path,
            min_alignment: int) -> None:
        self.data = data
        self.destination = destination
        self.min_alignment = min_alignment

    def save(self):
        """
        Save a .gltf or .glb file and optionnally a .bin file
        """
        GLTF2SaveFile(
            data=self.data,
            destination=self.destination,
            min_alignment=self.min_alignment).save()
