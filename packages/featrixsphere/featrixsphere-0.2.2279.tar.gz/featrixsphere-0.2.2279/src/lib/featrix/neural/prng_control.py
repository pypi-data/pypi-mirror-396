import random

import numpy as np
import torch

from featrix.neural.gpu_utils import set_gpu_seed

# Based on https://pytorch.org/docs/stable/notes/randomness.html

# NOTE in particular: Completely reproducible results are not guaranteed across PyTorch releases,
# individual commits, or different platforms. Furthermore, results may not be reproducible between
# CPU and GPU executions, even when using identical seeds.


def set_seed(seed):
    # Python
    random.seed(seed)

    # PyTorch
    torch.manual_seed(seed)
    # set seed for GPU operations (CUDA or MPS)
    set_gpu_seed(seed)
    # to ensure that you're using the same CUDNN algorithm each time.
    torch.backends.cudnn.deterministic = True

    # NumPy
    np.random.seed(seed)
