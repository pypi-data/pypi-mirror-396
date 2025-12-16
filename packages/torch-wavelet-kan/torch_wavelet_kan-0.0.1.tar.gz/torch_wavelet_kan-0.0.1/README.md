

````markdown
# Torch Wavelet KAN

[![PyPI version](https://img.shields.io/pypi/v/torch-wavelet-kan.svg)](https://pypi.org/project/torch-wavelet-kan/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Torch Wavelet KAN** is a lightweight, efficient PyTorch implementation of Kolmogorov-Arnold Networks (KAN) using **Learnable Morlet Wavelets**.

While standard KANs rely on B-Splines (which require fixed grids and are computationally heavy), **Torch Wavelet KAN** uses continuous wavelet transforms to capture high-frequency components and local features more effectively.

## 🚀 Features
* **Grid-Free:** Unlike Spline-KANs, Wavelets do not require maintaining a grid, making them more adaptable to data distribution shifts.
* **Learnable Parameters:** Simultaneously learns the **Weights**, **Scale (Dilation)**, and **Translation (Shift)** of every wavelet.
* **PyTorch Native:** Fully compatible with `nn.Sequential`, standard optimizers (Adam/SGD), and GPU acceleration.

## 📦 Installation

```bash
pip install torch-wavelet-kan
````

## ⚡ Quick Start

Here is how to use `WaveletKANLayer` as a drop-in replacement for `nn.Linear`.

```python
import torch
import torch.nn as nn
from torch_wavelet_kan import WaveletKANLayer

# 1. Define the Model
# Input: 2 features -> Hidden: 5 neurons -> Output: 1 value
model = nn.Sequential(
    WaveletKANLayer(in_features=2, out_features=5, num_wavelets=3),
    nn.BatchNorm1d(5), # Optional: Batch Norm often helps KANs
    WaveletKANLayer(in_features=5, out_features=1, num_wavelets=3)
)

# 2. Forward Pass
x = torch.randn(16, 2) # Batch size 16
output = model(x)

print(output.shape) # torch.Size([16, 1])
```

## 📖 API Documentation

### `WaveletKANLayer`

```python
WaveletKANLayer(in_features, out_features, num_wavelets=5, epsilon=1e-5)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `in_features` | `int` | Required | Size of each input sample. |
| `out_features` | `int` | Required | Size of each output sample. |
| `num_wavelets` | `int` | `5` | The number of wavelets to superimpose for each connection. Higher values increase model capacity but cost more memory. |
| `epsilon` | `float` | `1e-5` | Small constant for numerical stability during division. |

## 🧠 The Math

The standard KAN decomposition theorem states that any multivariate continuous function can be represented as a superposition of univariate functions.

In **Wavelet KAN**, we approximate these univariate functions $\phi$ using a sum of Morlet Wavelets:

$$\phi(x) = \sum_{i=1}^{N} w_i \cdot \psi\left(\frac{x - \mu_i}{s_i}\right)$$

Where:

  * $w_i$: The learnable amplitude (weight).
  * $\mu_i$: The learnable translation (where the wavelet is centered).
  * $s_i$: The learnable scale (how wide/narrow the frequency is).
  * $\psi(t) = e^{-t^2/2} \cos(5t)$: The Morlet wavelet function.

## 🤝 Contributing

Contributions are welcome\! If you find a bug or have an idea for a new wavelet type (e.g., Mexican Hat), please open an issue or submit a Pull Request.

1.  Fork the repo
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📚 Acknowledgements

This library is inspired by the paper *"Wav-KAN: Wavelet Kolmogorov-Arnold Networks"* (2024).

```