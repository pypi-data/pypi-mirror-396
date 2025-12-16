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
"""Provides conversion utility functions for PyTorch models."""
import os
import tempfile
from abc import abstractmethod
from io import BytesIO
from typing import TypeVar, Optional, TYPE_CHECKING, Dict, Tuple, Any

import torch
import torch.nn as nn
import onnx

from czmodel.core.model_metadata import ModelMetadata, ModelType
from czmodel.core.legacy_model_metadata import ModelMetadata as LegacyModelMetadata
from czmodel.core.util.base_convert import BaseConverter

from czmodel.core.util.model_packing import (
    create_model_zip,
    create_legacy_model_zip,
)
from czmodel.core.util.common import (
    validate_metadata as common_validate_metadata,
    validate_legacy_metadata as common_validate_legacy_metadata,
)

if TYPE_CHECKING:
    from torch.nn import Module

T = TypeVar("T", ModelMetadata, LegacyModelMetadata)

_ONNX_OPSET = 12
NEED_POSTPROCESSING = [
    ModelType.SINGLE_CLASS_INSTANCE_SEGMENTATION,
    ModelType.MULTI_CLASS_INSTANCE_SEGMENTATION,
    ModelType.SINGLE_CLASS_SEMANTIC_SEGMENTATION,
    ModelType.MULTI_CLASS_SEMANTIC_SEGMENTATION,
    ModelType.REGRESSION,
]


def switch_shape(shape: Tuple[int, ...]) -> Tuple[int, ...]:
    """Switch the dimension of Tuple presenting shape.

    Arguments:
        shape: The shape whose dimension would be switched.

    Raises:
        ValueError: If the input shape does not have three dimensions.
    """
    # Support both 2D and 3D shapes:
    # - 2D: input shape is (C, H, W) -> metadata expects (H, W, C)
    # - 3D: input shape is (C, Z, H, W) -> metadata expects (Z, H, W, C)
    if len(shape) == 3:
        return shape[1], shape[2], shape[0]
    if len(shape) == 4:
        return shape[1], shape[2], shape[3], shape[0]
    raise ValueError(f"The provided shape ({list(shape)}) should have three or four dimensions.")


class Permute(nn.Module):
    """Defining an extra torch.permute layer for PyTorch model."""

    def __init__(self, order: Tuple[int, ...]):
        """Initializes the Permute class.

        Arguments:
            order: The desired order of the dimension.
        """
        super().__init__()
        self.order = order

    def forward(self, x: torch.Tensor) -> Any:
        """Forward pass of the torch.permute layer.

        Arguments:
            x: The input that needs switch of dimensions.
        """
        return torch.permute(x, self.order)


def convert_pytorch_to_onnx(
    saved_model_dir: str,
    output_file: str,
    input_shape: Tuple[int, ...],
    post: Optional[bool] = True,
    custom_op_handlers: Optional[Dict] = None,
) -> None:
    """Exports a PyTorch on disk to an ONNX file.

    Arguments:
        saved_model_dir: The directory containing the model in PyTorch format.
        output_file: The path to the file to be created for the ONNX model.
        input_shape: The input shape of the model.
        post: If one extra permute layer is needed at the end of model.
        custom_op_handlers: Handlers for custom operations.
    """
    # Using weights_only=False because czmodel loads models that it itself just saved.
    # The weights_only=True security feature is meant to protect against untrusted pickle
    # files, not for internal model conversion workflows.
    model = torch.load(saved_model_dir, weights_only=False)  # nosec B614

    model.eval()
    # Build permute wrappers depending on whether input is 2D or 3D
    if len(input_shape) == 3:
        # Input to ONNX will be [N, H, W, C] and model expects [N, C, H, W]
        pre_permute = Permute((0, 3, 1, 2))
        post_permute = Permute((0, 2, 3, 1)) if post else None
        if post:
            new_model = nn.Sequential(pre_permute, model, post_permute)
        else:
            new_model = nn.Sequential(pre_permute, model)
    elif len(input_shape) == 4:
        # Input to ONNX will be [N, Z, H, W, C] and model expects [N, C, Z, H, W]
        pre_permute = Permute((0, 4, 1, 2, 3))
        post_permute = Permute((0, 2, 3, 4, 1)) if post else None
        if post:
            new_model = nn.Sequential(pre_permute, model, post_permute)
        else:
            new_model = nn.Sequential(pre_permute, model)
    else:
        raise ValueError("input_shape must be a 3- or 4-tuple for 2D or 3D models respectively")

    x = torch.randn([1, *switch_shape(input_shape)], requires_grad=True)

    torch.onnx.export(
        model=new_model,  # model being run
        args=x,  # model input (or a tuple for multiple inputs)
        f=output_file,  # where to save the model (can be a file or file-like object)
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=_ONNX_OPSET,  # the ONNX version to export the model to
        custom_opsets=custom_op_handlers,  # custom opset domain
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names=["input"],  # the model's input names
        output_names=["output"],  # the model's output names
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        },  # variable length axes
    )

    # Verify model's structure and check for valid model schema
    onnx.checker.check_model(output_file)


class BasePyTorchConverter(BaseConverter[T, "Module"]):
    """Base class for converting PyTorch models to an export format of the czmodel library."""

    @abstractmethod
    def convert_to_onnx(
        self,
        tmpdir_pytorch: str,
        model_metadata: T,
        onnx_path: str,
        input_shape: Tuple[int, ...],
    ) -> None:
        """Abstract method of converting PyTorch model to ONNX.

        Arguments:
                tmpdir_pytorch: The directory containing the model in PyTorch format.
                model_metadata: The metadata required to generate a model in export format.
                onnx_path: The path to the file to be created for the ONNX model.
                input_shape: The input shape of the model.
        """

    def convert(
        self,
        model: "Module",
        model_metadata: T,
        output_path: str,
        input_shape: Tuple[int, ...],
        license_file: Optional[str] = None,
    ) -> None:
        """Converts a given PyTorch model to an ONNX model.
        The exported model is optimized for inference.

        Args:
            model: PyTorch model to be converted. The model must have a separate InputLayer as input node.
            model_metadata: The metadata required to generate a model in export format.
            output_path: Destination path to the model file that will be generated.
            input_shape: The input shape of the PyTorch model, should be in order [N,C,H,W].
            license_file: The path to a license file to be included in the model.

        Raises:
            ValueError: If the input or output shapes of the model and the meta-data do not match.
        """
        # Check if model input and output shape is consistent with provided metadata
        try:
            model_output_shape = model(torch.randn((1,) + input_shape)).shape[1:]
        except RuntimeError as error:
            raise ValueError(
                "The input shape of the provided model is not consistent with the provided model."
            ) from error
        self._validate_metadata(
            model_metadata,
            list(switch_shape(input_shape)),
            list(switch_shape(model_output_shape)),
        )
        with tempfile.TemporaryDirectory() as tmpdir_pytorch:
            with tempfile.TemporaryDirectory() as tmpdir_onnx_name:
                # Export PyTorch model in PyTorch format
                tmpdir_pytorch = os.path.join(tmpdir_pytorch, "model.pt")
                torch.save(model, tmpdir_pytorch)

                # Convert to ONNX
                onnx_path = os.path.join(tmpdir_onnx_name, "model.onnx")
                self.convert_to_onnx(tmpdir_pytorch, model_metadata, onnx_path, input_shape)
                with open(onnx_path, "rb") as f:
                    buffer = BytesIO(f.read())

                # Pack model into export format
                self._conversion_fn(buffer.getbuffer(), model_metadata, output_path, license_file)


class DefaultPyTorchConverter(BasePyTorchConverter[ModelMetadata]):
    """Converts PyTorch models to the czann format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_model_zip,
            validate_metadata_fn=common_validate_metadata,
        )

    def convert_to_onnx(
        self,
        tmpdir_pytorch: str,
        model_metadata: ModelMetadata,
        onnx_path: str,
        input_shape: Tuple[int, ...],
    ) -> None:
        """Abstract method of converting PyTorch model to ONNX.

        Arguments:
                tmpdir_pytorch: The directory containing the model in PyTorch format.
                model_metadata: The metadata required to generate a model in export format.
                onnx_path: The path to the file to be created for the ONNX model.
                input_shape: The input shape of the model.
        """
        convert_pytorch_to_onnx(
            tmpdir_pytorch,
            onnx_path,
            input_shape,
            model_metadata.model_type in NEED_POSTPROCESSING,
        )


class LegacyPyTorchConverter(BasePyTorchConverter[LegacyModelMetadata]):
    """Converts PyTorch models to the czmodel format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_legacy_model_zip,
            validate_metadata_fn=common_validate_legacy_metadata,
        )

    def convert_to_onnx(
        self,
        tmpdir_pytorch: str,
        model_metadata: LegacyModelMetadata,
        onnx_path: str,
        input_shape: Tuple[int, ...],
    ) -> None:
        """Abstract method of converting PyTorch model to ONNX.

        Arguments:
                tmpdir_pytorch: The directory containing the model in PyTorch format.
                model_metadata: The metadata required to generate a model in export format.
                onnx_path: The path to the file to be created for the ONNX model.
                input_shape: The input shape of the model.
        """
        convert_pytorch_to_onnx(tmpdir_pytorch, onnx_path, input_shape)
