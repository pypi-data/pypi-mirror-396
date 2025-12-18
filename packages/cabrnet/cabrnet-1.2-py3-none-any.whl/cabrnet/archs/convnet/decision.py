from __future__ import annotations

from typing import Any
from torch import Tensor
from cabrnet.archs.generic.decision import CaBRNetClassifier


class DummyClassifier(CaBRNetClassifier):
    r"""Dummy classifier."""

    def prototype_is_active(self, proto_id: int) -> bool:
        r"""Is the prototype *proto_idx* active or disabled?

        Args:
            proto_id (int): Prototype index.
        """
        return False

    def forward(self, features: Tensor, **kwargs) -> Tensor:
        r"""Returns the features unchanged.

        Args:
            features (tensor): Input features.
        """
        return features
