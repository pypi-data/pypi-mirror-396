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
"""This module provides base data structures to represent the model specification of a CZANN."""
import json
from typing import Optional, Generic, Union, TypeVar
from dataclasses import dataclass
from czmodel.core.model_metadata import ModelMetadata

T = TypeVar("T")


@dataclass
class ModelSpec(Generic[T]):
    """Data structure of model specification.

    Attributes:
        model: Either the path to a model on disk or the model object itself.
        model_metadata: The metadata of the model.
        license_file: The path to a license file that is added to the generated CZANN. Can be absolute or
            relative to the JSON file.
    """

    model: Union[str, T]
    model_metadata: ModelMetadata
    license_file: Optional[str] = None

    @staticmethod
    def from_json(model_spec_path: str) -> "ModelSpec":
        """This function parses a model specification JSON file to a ModelSpec object.

        Args:
            model_spec_path: The path to the JSON file containing the model specification.

        Returns:
            A ModelMetadata instance carrying all information to generate a CZANN file.
        """
        with open(model_spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        return ModelSpec(
            model=spec["ModelPath"],
            license_file=spec.get("LicenseFile"),
            model_metadata=ModelMetadata.from_json(spec["ModelMetadata"]),
        )
