"""
glTF2 Convert Images
"""
import base64
import copy
import mimetypes
from pathlib import Path
from urllib.parse import unquote
import warnings

from pygltflib.exceptions import InvalidImageFormat
from pygltflib.v2.schema import BufferView, GLTF2Data, ImageFormat
from pygltflib.v2.actions.convert.utils import _identify_uri, _get_data_from_uri


class GLTF2ConvertImages:
    def __init__(
            self,
            data: GLTF2Data,
            overwrite: bool = False):
        self.data = data
        self.overwrite = overwrite

    # =========================================================================
    # Helpers
    # =========================================================================

    def _remove_data_from_buffer(
            self,
            byteOffset: int,
            byteLength: int) -> None:
        if len(self.data.JSON.buffers) == 1:
            data = self.data.BIN

            if data is None:
                return

            data = data[:byteOffset] + data[byteOffset + byteLength:]
            self.data.BIN = data
            # setting buffer 0 length
            self.data.JSON.buffers[0].byteLength = len(data)
            # rearange bufferViews
            for item in self.data.JSON.bufferViews:
                if (item.byteOffset is not None and
                        item.byteOffset >= byteOffset + byteLength):
                    item.byteOffset -= byteLength

    def _remove_bufferView(self, buffer_view_id: int) -> BufferView | None:
        """
        Remove a bufferView and update all the bufferView pointers in the GLTF
        object

        :param buffer_view_id: BufferView id
        :type buffer_view_id: int
        :return: The BufferView that was removed.
        :rtype: BufferView or None
        """
        def update_obj(title, obj):
            if obj and obj.bufferView:
                if obj.bufferView == buffer_view_id:
                    warnings.warn(f"Removing bufferView {buffer_view_id} but "
                                  f"{title}.bufferView still points to it. "
                                  f"This may corrupt the GLTF.")
                if obj.bufferView >= buffer_view_id:
                    obj.bufferView -= 1
            else:
                print(f"{title} empty")

        if (buffer_view_id < 0 or
                buffer_view_id > len(self.data.JSON.bufferViews)):
            warnings.warn(f"Cannot remove bufferView {buffer_view_id}. "
                          f"bufferView index {buffer_view_id} is out of range")
            return

        bufferView = self.data.JSON.bufferViews.pop(buffer_view_id)

        for i, accessor in enumerate(self.data.JSON.accessors):
            update_obj(f"gltf.accessors[{i}]", accessor)
            if accessor and accessor.sparse:
                update_obj(f"gltf.accessors[{i}].sparse.indices",
                           accessor.sparse.indices)
                update_obj(f"gltf.accessors[{i}].sparse.values",
                           accessor.sparse.values)

        for i, obj in enumerate(self.data.JSON.images):
            update_obj(f"gltf.images[{i}]", obj)

        return bufferView

    # =========================================================================
    # Destination
    # =========================================================================
    def _to_DATAURI(self, image_bytes, image):
        # Encode image
        encoded_string = str(base64.b64encode(image_bytes).decode('utf-8'))

        # Save image
        image.name = copy.copy(image.uri) if not image.name else image.name
        image.uri = f'data:{image.mimeType};base64,{encoded_string}'

    def _to_BUFFERVIEW(self):
        warnings.warn("Conversion to BUFFERVIEW not implemented. Skipping...")

    def _to_FILE(
            self, image_bytes, image, image_index,
            destination_dir: str | None):
        # TODO : test implementation. There might be mistakes

        # if destination_dir is empty, use load dir as destination_dir
        if destination_dir is None:
            destination_path = self.data.path_dir
        else:
            destination_path = Path(destination_dir)

        # image source
        from_fileuri = image.uri is not None and not image.uri.startswith('data:')
        from_datauri = image.uri is not None and image.uri.startswith('data:')

        if from_fileuri:
            # Extract extension
            extension = image.uri.split(".")[-1]
        elif from_datauri:
            # Extract header and encoded
            header, encoded = image.uri.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            extension = mimetypes.guess_extension(mime)
        elif image.mimeType is not None:
            extension = mimetypes.guess_extension(image.mimeType)
        else:
            extension = ".unknown"

        # Assign file_name
        if image.name:
            # if image.name exists, use it as the filename
            file_name = image.name
        else:
            # Use the index and the extension as the filename
            file_name = f"{image_index}{extension}"

        image.uri = file_name

        # Assign image_path
        if destination_path.is_dir():
            # destination_path/file_name
            image_path = Path(destination_path, unquote(file_name))
        else:
            # assume filepath
            image_path = destination_path

        # Write file to disk
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)

        return file_name

    # ========================================================================= 
    # Source
    # =========================================================================
    def _from_fileuri(self, image, path_dir: Path) -> bytes | None:
        # not in target data format, so assume a file name
        # data is stored in a file, so load into data uri
        image_path = Path(path_dir, unquote(image.uri))
        if not image_path.exists():
            warnings.warn("Expected image file at "
                          f"{image_path} not found. Skipping...")
            return None

        mime, _ = mimetypes.guess_type(str(image_path))
        if mime is None:
            warnings.warn("the mime type can't be guessed.")
        else:
            image.mimeType = mime  # TODO : test if valid

        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        return image_bytes

    def _from_datauri(self, image_index, image) -> bytes | None:
        # TODO : to test, There might be errors, missing checks

        # Extract header and encoded
        header, encoded = image.uri.split(",", 1)

        # Assign file_name
        if image.name:
            # if image.name exists, use it as the filename
            file_name = image.name
        else:
            # Use the index and the extension as the filename
            mime = header.split(":")[1].split(";")[0]
            extension = mimetypes.guess_extension(mime)
            file_name = f"{image_index}{extension}"

        image.name = file_name

        # Decode data
        image_buffer = base64.b64decode(encoded)

        return image_buffer

    def _from_bufferView(self, image) -> bytes | None:
        bufferViewIndex = image.bufferView
        bufferView = self.data.JSON.bufferViews[bufferViewIndex]
        bufferIndex = bufferView.buffer
        removeFromBuffer = True
        if self.data.BIN is None:
            # if BIN is none search for buffer as uri
            # Get data from buffer
            if bufferIndex < 0 or bufferIndex >= len(self.data.JSON.buffers):
                warnings.warn(f"Cannot read buffers[{bufferIndex}]."
                              f"buffers index {bufferIndex} out of range.")
                return
            current_buffer_format = _identify_uri(
                path_dir=self.data.path_dir,
                buffers_len=len(self.data.JSON.buffers),
                uri=self.data.JSON.buffers[bufferIndex].uri)
            data = _get_data_from_uri(
                self.data.JSON.buffers[bufferIndex].uri,
                current_buffer_format)
            removeFromBuffer = False
            if data is None:
                warnings.warn(f"Expected image data in Buffer {bufferIndex} not found.")
                return
        else:
            # Get data from BIN
            data = self.data.BIN

        # Read image
        start = bufferView.byteOffset
        end = bufferView.byteOffset + bufferView.byteLength
        image_data = data[start:end]

        # Remove data from buffer
        if removeFromBuffer:
            self._remove_data_from_buffer(
                bufferView.byteOffset,
                bufferView.byteLength)

        # Remove bufferview
        # Because uri and bufferview in one image element is invalid
        self._remove_bufferView(bufferViewIndex)
        image.bufferView = None

        return image_data

    # =========================================================================
    # Entry point
    # =========================================================================
    def convert_images(
            self,
            image_format: ImageFormat,
            destination_dir: str | None):
        # validate ImageFormat
        if image_format not in ImageFormat:
            raise InvalidImageFormat(f"{image_format} is not a valid ImageFormat. The valid choices are ImageFormat.DATAURI, ImageFormat.FILE or ImageFormat.BUFFERVIEW")

        # Iterate over all images
        for image_index, image in enumerate(self.data.JSON.images):
            # Identify source storage type
            from_fileuri = image.uri is not None and not image.uri.startswith('data:')
            from_datauri = image.uri is not None and image.uri.startswith('data:')
            from_bufferView = image.bufferView is not None

            To_FILE = image_format == ImageFormat.FILE
            to_DATAURI = image_format == ImageFormat.DATAURI
            to_BUFFERVIEW = image_format == ImageFormat.BUFFERVIEW

            # from_fileuri is encoded in uri
            # to file is a file
            # Not the same

            if from_datauri is True and to_DATAURI is True:
                continue  # Same format. Skip

            if from_bufferView is True and to_BUFFERVIEW is True:
                continue  # Same format. Skip

            # Read data
            # TODO : it might be necessary to return name and uri, or path
            if from_fileuri:
                image_bytes = self._from_fileuri(image, self.data.path_dir)
            elif from_datauri:
                image_bytes = self._from_datauri(image_index, image)
            elif from_bufferView:
                image_bytes = self._from_bufferView(image)
            else:
                image_bytes = None
                warnings.warn("No image to read.")

            # Write data
            if image_bytes is not None:
                if to_DATAURI:
                    self._to_DATAURI(image_bytes, image)
                elif to_BUFFERVIEW:
                    self._to_BUFFERVIEW()  # Not implemented
                elif To_FILE:
                    self._to_FILE(
                        image_bytes, image, image_index, destination_dir)
                else:
                    warnings.warn("Invalid ImageFormat")
            else:
                warnings.warn("No image converted.")
