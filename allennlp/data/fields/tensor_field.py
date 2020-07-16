from typing import Dict, Any

import torch
from overrides import overrides

from allennlp.data.fields.field import Field


class TensorField(Field[torch.Tensor]):
    """
    A class representing a tensor, which could have arbitrary dimensions.
    A batch of these tensors are padded to the max dimension length in the batch
    for each dimension.
    """

    __slots__ = ["tensor", "padding_value"]

    def __init__(self, tensor: torch.Tensor, padding_value: Any = 0.0) -> None:
        self.tensor = tensor
        self.padding_value = padding_value

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:
        return {"dimension_" + str(i): shape for i, shape in enumerate(self.tensor.size())}

    @overrides
    def as_tensor(self, padding_lengths: Dict[str, int]) -> torch.Tensor:
        pad = [
            padding
            for i, dimension_size in reversed(list(enumerate(padding_lengths.values())))
            for padding in [0, dimension_size - self.tensor.size(i)]
        ]
        return torch.nn.functional.pad(self.tensor, pad, value=self.padding_value)

    @overrides
    def empty_field(self):
        # Pass the padding_value, so that any outer field, e.g., `ListField[TensorField]` uses the
        # same padding_value in the padded TensorFields
        return TensorField(torch.tensor([], dtype=self.tensor.dtype), padding_value=self.padding_value)

    def __str__(self) -> str:
        return f"TensorField with shape: {self.tensor.size()} and dtype: {self.tensor.dtype}."

    def __len__(self):
        return 1 if len(self.tensor.size()) <= 0 else self.tensor.size(0)

    def __eq__(self, other: "TensorField") -> bool:
        return torch.equal(self.tensor, other.tensor)