"""
Interpylate-FLS: Neural Network Interpolation Package

A Python package for training neural networks on 5-dimensional datasets
for interpolation tasks.

Main Classes:
    - NeuralNetwork: PyTorch-based neural network for regression
    - DataLoader: Dataset loading and preprocessing utilities
    - Plotter: Visualization tools for model performance
    - Logger: Logging utilities

Example:
    >>> from interpylate_fls import NeuralNetwork, DataLoader
    >>> loader = DataLoader('data.pkl')
    >>> data = loader.load_dataset()
    >>> X_train, X_test, X_val, y_train, y_test, y_val, _, _, _ = loader.inspect_data(data)
    >>> nn = NeuralNetwork(X_train, y_train, X_val, y_val, X_test, y_test)
    >>> nn.train()
    >>> mse, r2 = nn.evaluate()
"""

__version__ = "0.1.0"
__author__ = "Funmi Looi-Somoye"
__email__ = "OL306@cam.ac.uk"
__license__ = "MIT"

from .neuralnetwork import NeuralNetwork
from .data import DataLoader
from .plotter import Plotter
from .logger import Logger

__all__ = [
    "NeuralNetwork",
    "DataLoader",
    "Plotter",
    "Logger",
]

