"""
Load valid gltf files, save them and compare to the original file

Uses the files provided by
https://github.com/KhronosGroup/glTF-Validator

To run, execute the following command from the pygltflib root directory :
python pygltflib/v2/actions/validate/base/gltf.py

This does not work for a few reasons:
- This scripts does a naive comparison (files identical) and
does not compare de JSON content of the .gltf files.
- The JSON elements are not ordered in the same order.
- bufferViews[0].byteOffset is removed if it is equal to zero in the validator files.
"""
import filecmp
import json
from pathlib import Path

from pygltflib import GLTF2


def main():
    assets_dir = "submodules/KhronosGroup/glTF-Validator/test/base"
    assets_file = "assets.json"
    assets_path = Path(assets_dir, assets_file)

    validation_dir = "validation"

    with assets_path.open() as f:
        assets = json.load(f)
        # list gltf valid files
        valid_gltf_files = []
        for category, category_value in assets.items():
            for file_name, test_name in category_value["tests"].items():
                if (file_name.startswith("valid") and
                        file_name.endswith(".gltf")):
                    validation_file_name = f"{category}__{file_name}"
                    valid_gltf_files.append({
                        "category": category,
                        "file_name": file_name,
                        "test_name": test_name,
                        "load_file_path": Path(assets_dir, "data", category, file_name).absolute().as_posix(),
                        "save_file_path": Path(validation_dir, validation_file_name).absolute().as_posix()
                    })
        # print(valid_gltf_files)

    # Load and save valid gltf files
    for file in valid_gltf_files:
        # Load gltf file
        gltf = GLTF2().load(file["load_file_path"])

        # Save gltf file
        gltf.save(file["save_file_path"])

        # Compare the files
        files_equals = filecmp.cmp(
            file["load_file_path"],
            file["save_file_path"]
        )

        # Print result of comparison
        if files_equals:
            print(f"{file['category']} - {file['file_name']} - {file['test_name']} - FILES ARE EQUALS - VALIDATION SUCCESS")
        else:
            print(f"{file['category']} - {file['file_name']} - {file['test_name']} - FILES ARE DIFFERENTS - VALIDATION FAILED")

        # Cleanup
        # delete the files manually


if __name__ == "__main__":
    main()
