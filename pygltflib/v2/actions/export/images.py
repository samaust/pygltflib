import base64
import mimetypes
from pathlib import Path
from shutil import copyfile
from urllib.parse import unquote
import warnings

from pygltflib.v2.schema import GLTF2Data, Image, ImageFormat


class GLTF2ExportImage:
    def __init__(
        self,
        data: GLTF2Data,
        images: list[Image],
        image_index: int,
        path_dir: Path,
        destination: Path = Path(),
        overwrite: bool = False
    ):
        self.data = data
        self.image_index = image_index
        self.image: Image = images[image_index]
        self.path_dir = path_dir
        self.destination = destination
        self.overwrite = overwrite

    def _export_datauri_as_image_file(
            self,
            data_uri: str,
            name: str | None,
            destination: Path,
            overwrite: bool = False,
            index: int = 0) -> str | None:
        """ convert data uri to image file
            If destination is full path and file name, use that.
            If destination is just a directory, use the name of the data_uri
        """
        # Extract header and encoded
        header, encoded = data_uri.split(",", 1)

        # Assign file_name
        if name:
            # if image.name exists, use it as the filename
            file_name = name
        else:
            # Use the index and the extension as the filename
            mime = header.split(":")[1].split(";")[0]
            extension = mimetypes.guess_extension(mime)
            file_name = f"{index}{extension}"

        # Assign image_path
        destination_path = Path(destination)
        if destination_path.is_dir():
            # destination_path/file_name
            image_path = Path(destination_path, unquote(file_name))
        else:
            # assume filepath
            image_path = destination_path

        # Return with a warning if a file already exists
        if image_path.is_file() and not overwrite:
            warnings.warn("Unable to write image file, "
                          f"a file already exists at {image_path}")
            return None

        # Decode data
        image_buffer = base64.b64decode(encoded)

        # Write file to disk
        with open(image_path, "wb") as image_file:
            image_file.write(image_buffer)

        return file_name

    def _export_fileuri_as_image_file(
            self,
            file_uri: str,
            destination: Path,
            path_dir: Path,
            overwrite: bool = False):
        """
        Export file uri as another image file
        (ie copy out of GLTF into own location)
        """
        # Define image path from load directory and file uri
        image_path = Path(path_dir, unquote(file_uri))
        image_name = image_path.name

        # If destination is a dir, destination_path/image_name
        if destination.is_dir():
            destination = Path(destination, image_name)

        # Return with a warning is the file is not found
        if not image_path.exists():
            warnings.warn(f"Unable to find image {image_path} for export.")
            return None

        # Return with a warning if a file already exists
        if destination.is_file() and not overwrite:
            warnings.warn("Unable to write image file, "
                          f"a file already exists at {destination}")
            return None

        # Copy the file to the destination
        copyfile(image_path, destination)

        return file_uri

    def export_image(self):
        """
        Directly export an image to a file without affecting GLTF
        """
        file_name = None

        # Identify storage type
        has_image_in_fileuri = self.image.uri is not None and not self.image.uri.startswith('data:')
        has_image_in_datauri = self.image.uri is not None and self.image.uri.startswith('data:')
        has_image_in_bufferView = self.image.bufferView is not None

        # Export image
        if has_image_in_fileuri:
            # copy file to new location
            assert self.image.uri is not None
            file_name = self._export_fileuri_as_image_file(
                file_uri=self.image.uri,
                destination=self.destination,
                path_dir=self.path_dir,
                overwrite=self.overwrite)
        elif has_image_in_datauri:
            assert self.image.uri is not None
            file_name = self._export_datauri_as_image_file(
                data_uri=self.image.uri,
                name=self.image.name,
                destination=self.destination,
                overwrite=self.overwrite,
                index=self.image_index)
        elif has_image_in_bufferView:
            from pygltflib import GLTF2

            # Create copy
            gltf2 = GLTF2(JSON=self.data.JSON, BIN=self.data.BIN,
                          CHUNKS=self.data.CHUNKS, path_dir=self.data.path_dir)

            # Convert to DATAURI
            gltf2.convert_images(ImageFormat.DATAURI)

            # Export tofile
            uri = gltf2.images[self.image_index].uri
            if uri is not None:
                file_name = self._export_datauri_as_image_file(
                    data_uri=uri,
                    name=self.image.name,
                    destination=self.destination,
                    overwrite=self.overwrite,
                    index=self.image_index)
        else:
            warnings.warn("No images to export.")

        return file_name
