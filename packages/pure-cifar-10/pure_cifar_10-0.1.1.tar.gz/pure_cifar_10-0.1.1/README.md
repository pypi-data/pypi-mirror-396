# pure_cifar_10

A pure Python, minimal-dependency loader for the CIFAR-10 dataset. This package provides the CIFAR-10 images and labels as NumPy arrays, with automatic downloading and caching, requiring only `numpy` and `tqdm`.

## Features
*   **Minimal Dependencies**: Only requires `numpy` and `tqdm`. No heavy machine learning frameworks like PyTorch or TensorFlow.
*   **Automatic Handling**: Downloads the CIFAR-10 dataset automatically on first use and caches it locally.
*   **Pure NumPy**: Returns standard `numpy.ndarray` objects for easy integration into any pipeline.
*   **Progress Visualization**: Uses `tqdm` to show download and loading progress bars.
*   **Simple API**: Mirrors the clean, functional style of the `mnist_datasets` package.

## Installation
You can install the package directly from PyPI using pip:

```bash
pip install pure_cifar_10
```
## Usage
```python
from pure_cifar_10 import CIFAR10
loader = CIFAR10() 
train_data, train_labels, test_data, test_labels = loader.load_all()
```
### Optionally specify a custom folder and load train and test data as required.
```python
loader = CIFAR10(folder="/tmp/data) 
train_data, train_labels = loader.load() # train=True by default 
test_data, test_labels = loader.load(train=False)
print(train_data.shape, train_labels.shape)
print(test_data.shape, test_labels.shape)

(50000, 3, 32, 32) (50000,)
(10000, 3, 32, 32) (10000,)

classes = loader.class_names
print(classes)
('airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
```

## Data Format
- Images: The data arrays have shape (N, 3, 32, 32), where N is the number of samples. This is a channels-first format (3 color channels, Red-Green-Blue). Pixel values are float32 in the range [0, 255], as stored in the original dataset.
- Labels: The labels are 1D numpy arrays of dtype int64, containing integers from 0 to 9.

## Class Names
The dataset contains 10 mutually exclusive classes:
  0. airplane
  1. automobile
  2. bird
  3. cat
  4. deer
  5. dog
  6. frog
  7. horse
  8. ship
  9. truck
