from typing import Any

import torch
from cabrnet.archs.generic.model import CaBRNet


class ConvNet(CaBRNet):
    r"""CNN model that returns the extracted "features" as the model output.

    Attributes:
        extractor: Model used to extract convolutional features from the input image.
        classifier: Empty shell.
    """

    def loss(self, model_output: Any, label: torch.Tensor, **kwargs) -> tuple[torch.Tensor, dict[str, float]]:
        r"""Loss function.

        Args:
            model_output (Any): Model output, in this case a tuple containing the prediction and the minimum distances.
            label (tensor): Batch labels.

        Returns:
            Loss tensor and batch statistics.
        """
        # Cross-entropy loss
        cross_entropy = torch.nn.functional.cross_entropy(model_output, label)
        batch_accuracy = torch.sum(torch.eq(torch.argmax(model_output, dim=1), label)).item() / len(label)
        return cross_entropy, {"loss": cross_entropy.item(), "accuracy": batch_accuracy}
