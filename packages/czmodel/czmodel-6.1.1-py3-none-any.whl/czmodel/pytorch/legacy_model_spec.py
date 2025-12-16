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
"""This module provides data structures to represent the meta-data of a CZModel containing a PyTorch model."""
from typing import Union, Optional, TYPE_CHECKING
from czmodel.core.legacy_model_metadata import ModelMetadata
from czmodel.core.legacy_model_spec import ModelSpec as CoreModelSpec

# Ignore flake8 imported but unused warnings (does not recognize non-runtime check). Checked by mypy
if TYPE_CHECKING:
    from torch.nn import Module


class ModelSpec(CoreModelSpec["Module"]):
    """Data structure of model specification."""

    model: Union[str, "Module"]
    model_metadata: ModelMetadata
    license_file: Optional[str] = None
