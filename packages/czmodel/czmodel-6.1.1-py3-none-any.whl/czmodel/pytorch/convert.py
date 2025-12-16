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
"""Provides conversion functions to generate a CZANN from exported PyTorch models."""
import os
import sys
from typing import (
    Type,
    Tuple,
    Optional,
    Callable,
    Generic,
    TypeVar,
)
from pathlib import Path

import torch
from torch.nn import Module

from czmodel.core.convert import UnpackModel, parse_args
from czmodel.core.model_metadata import ModelMetadata
from czmodel.pytorch.model_spec import ModelSpec as PyTorchModelSpec
from czmodel.core.legacy_model_metadata import ModelMetadata as LegacyModelMetadata
from czmodel.pytorch.legacy_model_spec import ModelSpec as LegacyModelSpec

from czmodel.pytorch.util import torch_export
from czmodel.core.util._extract_model import extract_czann_model, extract_czseg_model


T = TypeVar("T", PyTorchModelSpec, LegacyModelSpec)
S = TypeVar("S", ModelMetadata, LegacyModelMetadata)


class PyTorchBaseConverter(Generic[T, S]):
    """Base class for converting models to an export format supported by the czmodel library."""

    def __init__(
        self,
        spec_type: Type[T],
        conversion_fn: Callable[
            [
                Module,
                S,
                str,
                Tuple[int, ...],
                Optional[str],
            ],
            None,
        ],
    ):
        """Initializes the converter.

        Arguments:
            spec_type: The type of the specification object.
            conversion_fn: A function to convert a model, its model specification, model meta-data, an output path,
                the input shape and a license file to the target format.
        """
        self._spec_type: Type[T] = spec_type
        self.conversion_fn: Callable[
            [
                Module,
                S,
                str,
                Tuple[int, ...],
                Optional[str],
            ],
            None,
        ] = conversion_fn

    def convert_from_model_spec(
        self,
        model_spec: T,
        output_path: str,
        input_shape: Tuple[int, ...],
        output_name: str = "DNNModel",
    ) -> None:
        """Convert a PyTorch model to a .czann model usable in ZEN Intellesis.

        Args:
            model_spec: A ModelSpec object describing the specification of the CZANN to be generated.
            output_path: A folder to store the generated CZANN file.
            input_shape: The input shape of the model.
            output_name: The name of the generated .czann file.
        """
        # Create output directory
        os.makedirs(output_path, exist_ok=True)

        # Load model if necessary
        if isinstance(model_spec.model, Module):
            model = model_spec.model
        else:
            # because of: https://bandit.readthedocs.io/en/1.8.3/plugins/b614_pytorch_load.html
            # Add PyTorch modules to safe globals for weights_only=True loading
            # This is needed for PyTorch 2.6+ compatibility
            safe_globals = [
                torch.nn.modules.container.Sequential,
                torch.nn.modules.conv.Conv2d,
                torch.nn.modules.activation.ReLU,
                torch.nn.modules.activation.Softmax,
                torch.nn.modules.linear.Linear,
                torch.nn.modules.batchnorm.BatchNorm2d,
                torch.nn.modules.dropout.Dropout,
                torch.nn.modules.pooling.MaxPool2d,
                torch.nn.modules.pooling.AdaptiveAvgPool2d,
            ]

            with torch.serialization.safe_globals(safe_globals):
                model = torch.load(model_spec.model, weights_only=True)

        # Convert model
        self.conversion_fn(
            model,
            model_spec.model_metadata,  # type: ignore # Invalid combination must be taken care of manually
            os.path.join(output_path, output_name),
            input_shape,
            model_spec.license_file,
        )

    def convert_from_json_spec(
        self,
        model_spec_path: str,
        output_path: str,
        input_shape: Tuple[int, ...],
        output_name: str = "DNNModel",
    ) -> None:
        """Converts a PyTorch model specified in a JSON metadata file to a czann model.

        Args:
            model_spec_path: The path to the JSON specification file.
            output_path: A folder to store the generated CZANN file.
            input_shape: The input shape of the model.
            output_name: The name of the generated .czann file.
        """
        # Parse the specification JSON file
        parsed_spec = self._spec_type.from_json(model_spec_path)

        # Write czann model to disk
        self.convert_from_model_spec(parsed_spec, output_path, input_shape, output_name)  # type: ignore


class DefaultConverter(PyTorchBaseConverter[PyTorchModelSpec, ModelMetadata], UnpackModel[ModelMetadata]):
    """Converter for czann models."""

    def __init__(self) -> None:
        """Initializes the converter for czann models."""
        super().__init__(
            spec_type=PyTorchModelSpec,
            conversion_fn=torch_export.DefaultPyTorchConverter().convert,
        )

    def unpack_model(
        self,
        model_file: str,
        target_dir: Path,
    ) -> Tuple[ModelMetadata, os.PathLike]:
        """Unpack the .czann file.

        Args:
            model_file: Path of the .czann file
            target_dir: Target directory for the extraction

        Returns:
            Tuple containing the model metadata and the model itself in that order
        """
        model_metadata, model_path = extract_czann_model(model_file, target_dir)
        return model_metadata, model_path


class LegacyConverter(
    PyTorchBaseConverter[LegacyModelSpec, LegacyModelMetadata],
    UnpackModel[LegacyModelMetadata],
):
    """Converter for legacy czmodel models."""

    def __init__(self) -> None:
        """Initializes the converter for legacy czmodel models."""
        super().__init__(
            spec_type=LegacyModelSpec,
            conversion_fn=torch_export.LegacyPyTorchConverter().convert,
        )

    def unpack_model(
        self,
        model_file: str,
        target_dir: Path,
    ) -> Tuple[LegacyModelMetadata, os.PathLike]:
        """Unpack .czseg or .czmodel file.

        Args:
            model_file: Path of the .czseg/.czmodel file
            target_dir: Target directory for the extraction

        Returns:
            Tuple containing the model metadata and the model itself in that order
        """
        model_metadata, model_path = extract_czseg_model(model_file, target_dir)
        return model_metadata, model_path


def main() -> None:
    """Console script to convert a PyTorch model to a CZANN."""
    args = parse_args(sys.argv[1:])

    # Run conversion
    DefaultConverter().convert_from_json_spec(args.model_spec, args.output_path, args.output_name)


if __name__ == "__main__":
    main()
