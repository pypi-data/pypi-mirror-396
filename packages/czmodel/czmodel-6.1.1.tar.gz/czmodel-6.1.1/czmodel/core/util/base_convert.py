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
"""Provides base conversion utility functions for models."""
from typing import TypeVar, Generic, Callable, Union, Optional, List

from czmodel.core.model_metadata import ModelMetadata
from czmodel.core.legacy_model_metadata import ModelMetadata as LegacyModelMetadata

T = TypeVar("T", ModelMetadata, LegacyModelMetadata)
S = TypeVar("S")


class BaseConverter(Generic[T, S]):
    """Base class for converting models to an export format of the czmodel library."""

    def __init__(
        self,
        conversion_fn: Callable[[Union[str, bytes, memoryview], T, str, Optional[str]], None],
        validate_metadata_fn: Callable[[T, List[int], List[int]], None],
    ):
        """Initializes the converter and stores the conversion and metadata validation function.

        Arguments:
            conversion_fn: The function to convert a given model, metadata, output path and license file
                to the desired export format.
            validate_metadata_fn: Function that validates a given model metadata, model input shape
                and model output shape. This function raises a ValueError if the the provided values
                do not comply with the specification.
        """
        super().__init__()
        self._conversion_fn: Callable[[Union[str, bytes, memoryview], T, str, Optional[str]], None] = conversion_fn
        self._validate_metadata: Callable[[T, List[int], List[int]], None] = validate_metadata_fn
