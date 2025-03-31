"""
glTF2 Convert Buffers
"""
import base64
from pathlib import Path
import warnings

from pygltflib.exceptions import InvalidBufferFormat
from pygltflib.v2.schema import BufferFormat, DATA_URI_HEADER, GLTF2Data
from pygltflib.v2.actions.convert.utils import _identify_uri, _get_data_from_uri


class GLTF2ConvertBuffers:
    def __init__(
            self,
            data: GLTF2Data,
            path_dir: Path):
        self.data = data
        self.path_dir = path_dir

    def _convert_buffers(self, buffer_format: BufferFormat, overwrite: bool = False):
        """
        GLTF files can store the buffer data in three different formats:
        As a binary blob ready for glb, as a data uri string and as external
        bin files. This converts the buffers between the formats.

        buffer_format (BufferFormat.ENUM)
        override (bool): Override a bin file if it already exists and is about
            to be replaced
        """
        # validate BufferFormat
        if buffer_format not in BufferFormat:
            raise InvalidBufferFormat(f"{buffer_format} is not a valid BufferFormat. The valid choices are BufferFormat.DATAURI, BufferFormat.BINARYBLOB or BufferFormat.BINFILE")

        for buffer_index, buffer in enumerate(self.data.JSON.buffers):
            # Identify Current Buffer format
            current_buffer_format = _identify_uri(
                path_dir=self.path_dir,
                buffers_len=len(self.data.JSON.buffers),
                uri=buffer.uri)
            if current_buffer_format == buffer_format:  # already in the format
                continue
            if current_buffer_format is BufferFormat.BINFILE:
                warnings.warn(f"Conversion will leave {buffer.uri} file "
                              "orphaned since data is now in the GLTF object.")

            # Get current data
            if (current_buffer_format == BufferFormat.BINFILE or
                    current_buffer_format == BufferFormat.DATAURI):
                buffer_data = _get_data_from_uri(
                    buffer.uri, current_buffer_format, self.path_dir)
            elif (current_buffer_format == BufferFormat.BINARYBLOB):
                buffer_data = self.data.BIN

            if buffer_data is None:
                return

            # Convert data
            if buffer_format is BufferFormat.BINARYBLOB:
                if len(self.data.JSON.buffers) > 1:
                    warnings.warn(
                        "pygltflib currently unable to convert "
                        "multiple buffers to a single binary blob. "
                        "Please open an issue at "
                        "https://gitlab.com/dodgyville/pygltflib/issues")
                    return
                self.data.BIN = buffer_data
                buffer.uri = None
            elif buffer_format is BufferFormat.DATAURI:
                # convert buffer to a data uri
                buffer_data_encoded = base64.b64encode(buffer_data).decode('utf-8')
                buffer.uri = f'{DATA_URI_HEADER}{buffer_data_encoded}'
            elif buffer_format is BufferFormat.BINFILE:
                filename = Path(f"{buffer_index}").with_suffix(".bin")
                binfile_path = Path(self.path_dir, filename)
                if binfile_path.is_file() and not overwrite:
                    warnings.warn("Unable to write buffer file, a file "
                                  f"already exists at {binfile_path}")
                    continue
                with open(binfile_path, "wb") as f:
                    # save bin file with the gltf file
                    f.write(buffer_data)
                buffer.uri = str(filename)

            # free up any binary blob floating around
            if (buffer_format != BufferFormat.BINARYBLOB):
                self.data.BIN = None
