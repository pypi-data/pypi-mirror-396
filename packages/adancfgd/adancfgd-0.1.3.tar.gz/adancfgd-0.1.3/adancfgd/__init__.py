from .adancfgd import AdaFGD, AdaNCFGD
from .snn import *
from .snn_cnn import *

__version__ = "0.1.3"
__author__ = "Yihe Zhu"
__email__ = "zhu.yihe@qq.com"
__description__ = "Adaptive Fractional Gradient Descent Optimizers (AdaFGD & AdaNCFGD)"
__url__ = "https://github.com/HunLuanZhiZhu/AdaNCFGD"

# Export main classes and functions
__all__ = [
    # Optimizers
    "AdaFGD",
    "AdaNCFGD",
    # SNN components
    "SNNDropout",
    "SNNBatchNorm1d",
    "SNNLinear",
    "SNNConv2d",
    "SNNMaxPool2d",
    "SNNReLU",
    "SNNSequential",
    "LIFNeuron",
    "SNN",
    "SNNCNN",
]