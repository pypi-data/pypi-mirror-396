import numpy as np
import os
import pickle
from typing import Tuple
import urllib.request
import tarfile
from tqdm import tqdm

class CIFAR10:
    """
    Pure Python/NumPy CIFAR-10 loader with tqdm progress bars.
    Downloads data automatically on first use.
    """

    URL = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    TRAIN_FILES = [f"data_batch_{i}" for i in range(1, 6)]
    TEST_FILE = "test_batch"

    def __init__(self, folder: str = "/tmp/cifar10_data", show_progress: bool = True):
        """
        Args:
            folder: Directory to store/download the dataset
            show_progress: Whether to display tqdm progress bars
        """
        self.folder = folder
        self.show_progress = show_progress
        self._train_data = None
        self._train_labels = None
        self._test_data = None
        self._test_labels = None

    def _download_and_extract(self) -> None:
        """Download and extract CIFAR-10 dataset with progress bars."""
        os.makedirs(self.folder, exist_ok=True)

        # Download with progress bar
        tar_path = os.path.join(self.folder, "cifar-10-python.tar.gz")

        if self.show_progress:
            print("Downloading CIFAR-10 dataset...")

            class DownloadProgressBar(tqdm):
                def update_to(self, b=1, bsize=1, tsize=None):
                    if tsize is not None:
                        self.total = tsize
                    self.update(b * bsize - self.n)

            # Use tqdm for download progress
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1) as t:
                urllib.request.urlretrieve(
                    self.URL,
                    tar_path,
                    reporthook=t.update_to
                )
        else:
            urllib.request.urlretrieve(self.URL, tar_path)

        # Extract with progress bar
        if self.show_progress:
            print("Extracting files...")
            with tarfile.open(tar_path, 'r:gz') as tar:
                members = tar.getmembers()
                # Show progress for extraction
                for member in tqdm(members, desc="Extracting"):
                    tar.extract(member, self.folder)
        else:
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(self.folder)

        # Clean up
        os.remove(tar_path)

    def _get_extracted_path(self) -> str:
        return os.path.join(self.folder, "cifar-10-batches-py")

    def _load_batch(self, filename: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load a single batch file."""
        path = os.path.join(self._get_extracted_path(), filename)

        with open(path, 'rb') as f:
            batch = pickle.load(f, encoding='bytes')

        data = batch[b'data'].astype(np.float32)
        labels = np.array(batch[b'labels'], dtype=np.int64)

        return data, labels

    @property
    def train_data(self) -> np.ndarray:
        """Get training data (50000, 3, 32, 32) with loading progress bar."""
        if self._train_data is None:
            if not os.path.exists(self._get_extracted_path()):
                self._download_and_extract()

            all_data = []
            all_labels = []

            # Use tqdm for batch loading progress
            if self.show_progress:
                batch_iterator = tqdm(self.TRAIN_FILES, desc="Loading training batches")
            else:
                batch_iterator = self.TRAIN_FILES

            for batch_file in batch_iterator:
                data, labels = self._load_batch(batch_file)
                all_data.append(data)
                all_labels.append(labels)

            self._train_data = np.vstack(all_data)
            self._train_labels = np.concatenate(all_labels)

            # Reshape with progress if desired
            if self.show_progress:
                print("Reshaping training data...")

            self._train_data = self._train_data.reshape(-1, 3, 32, 32)

            if self.show_progress:
                print(f"✓ Training data loaded: {self._train_data.shape}")

        return self._train_data

    @property
    def train_labels(self) -> np.ndarray:
        _ = self.train_data  # Trigger loading if needed
        return self._train_labels

    @property
    def test_data(self) -> np.ndarray:
        if self._test_data is None:
            if not os.path.exists(self._get_extracted_path()):
                self._download_and_extract()

            if self.show_progress:
                print("Loading test batch...")

            self._test_data, self._test_labels = self._load_batch(self.TEST_FILE)
            self._test_data = self._test_data.reshape(-1, 3, 32, 32)

            if self.show_progress:
                print(f"✓ Test data loaded: {self._test_data.shape}")

        return self._test_data

    @property
    def test_labels(self) -> np.ndarray:
        _ = self.test_data  # Trigger loading if needed
        return self._test_labels

    @property
    def class_names(self) -> Tuple[str, ...]:
        return ('airplane', 'automobile', 'bird', 'cat', 'deer',
                'dog', 'frog', 'horse', 'ship', 'truck')

    def load(self, train: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load CIFAR-10 data with progress visualization.

        Args:
            train: If True, returns training data; else returns test data.

        Returns:
            Tuple of (data, labels).
        """
        if train:
            return (self.train_data, self.train_labels)
        else:
            return (self.test_data, self.test_labels)

    def load_all(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Load all CIFAR-10 data at once with unified progress.

        Returns:
            (train_data, train_labels, test_data, test_labels)
        """
        if self.show_progress:
            print("Loading CIFAR-10 dataset...")

        train_data, train_labels = self.load(train=True)
        test_data, test_labels = self.load(train=False)

        if self.show_progress:
            print(f"✓ Complete! Loaded {len(train_data)} train, {len(test_data)} test samples")

        return train_data, train_labels, test_data, test_labels
