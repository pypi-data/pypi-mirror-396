# pure_cifar_10

A pure Python, minimal-dependency loader for the CIFAR-10 dataset. This package provides the CIFAR-10 images and labels as NumPy arrays, with automatic downloading and caching, requiring only `numpy` and `tqdm`[citation:1][citation:2].

## Features
*   **Minimal Dependencies**: Only requires `numpy` and `tqdm`. No heavy machine learning frameworks like PyTorch or TensorFlow[citation:4].
*   **Automatic Handling**: Downloads the CIFAR-10 dataset automatically on first use and caches it locally.
*   **Pure NumPy**: Returns standard `numpy.ndarray` objects for easy integration into any pipeline.
*   **Progress Visualization**: Uses `tqdm` to show download and loading progress bars.
*   **Simple API**: Mirrors the clean, functional style of the `mnist_datasets` package.

## Installation
You can install the package directly from PyPI using pip:

```bash
pip install pure_cifar_10
