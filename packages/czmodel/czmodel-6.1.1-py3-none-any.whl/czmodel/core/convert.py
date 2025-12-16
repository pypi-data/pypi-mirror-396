# CZModel provides simple-to-use conversion tools to generate a CZANN
# Copyright 2025 Carl Zeiss Microscopy GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To obtain a commercial version please contact Carl Zeiss Microscopy GmbH.
"""Provides base conversion functions to generate a CZANN from exported models."""
import os
from abc import abstractmethod
from typing import (
    Tuple,
    List,
    Any,
    TypeVar,
    Generic,
)
from pathlib import Path
from czmodel.core.util.argument_parsing import dir_file


S = TypeVar("S")


class UnpackModel(Generic[S]):
    """Base mixin class unpacking the model"""

    @abstractmethod
    def unpack_model(
        self,
        model_file: str,
        target_dir: Path,
    ) -> Tuple[S, os.PathLike]:
        """Unpack the model file.

        Args:
            model_file: Path of the model file
            target_dir: Target directory for the extraction

        Returns:
            Tuple containing the model metadata and the model itself in that order
        """


def parse_args(args: List[str]) -> Any:
    """Parses all arguments from a given collection of system arguments.

    Arguments:
        args: The system arguments to be parsed.

    Returns:
        The parsed system arguments.
    """
    # Import argument parser
    import argparse  # pylint: disable=import-outside-toplevel

    # Define expected arguments
    parser = argparse.ArgumentParser(
        description="Convert a PyTorch or ONNX model to a CZANN that can be executed inside ZEN."
    )
    parser.add_argument(
        "model_spec",
        type=dir_file,
        help="A JSON file containing the model specification.",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="The path where the generated czann model will be created.",
    )
    parser.add_argument("output_name", type=str, help="The name of the generated czann model.")

    # Parse arguments
    return parser.parse_args(args)


def main() -> None:
    """Console script to convert model to a CZANN."""


if __name__ == "__main__":
    main()
