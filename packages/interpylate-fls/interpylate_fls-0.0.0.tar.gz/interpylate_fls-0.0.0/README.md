# Interpylate-FLS

A Python package for training neural networks on 5 dimensional datasets for interpolation tasks.


## Features

- **NeuralNetwork**: PyTorch-based neural network for regression tasks
- **DataLoader**: Dataset loading and preprocessing utilities
- **Plotter**: Visualization tools for model performance
- **Logger**: Logging utilities

## Installation

### PYPI
```bash
pip install interpylate-fls
```


### Local Installation
```bash
pip install -e .
```

## Example Usage

```python
from interpylate_fls import NeuralNetwork, DataLoader

# Load and preprocess data
loader = DataLoader('data.pkl')
data = loader.load_dataset()
X_train, X_test, X_val, y_train, y_test, y_val, _, _, _ = loader.inspect_data(data)

# Create and train neural network
nn = NeuralNetwork(
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val,
    X_test=X_test,
    y_test=y_test,
    hidden_layer_sizes=[64, 32],
    learning_rate=0.001,
    epochs=100
)

# Train the model
nn.train(verbose=True)

# Evaluate
mse, r2 = nn.evaluate()
print(f"MSE: {mse:.4f}, R²: {r2:.4f}")

# Make predictions
prediction = nn.predict([0.5, 0.5, 0.5, 0.5, 0.5])
print(f"Prediction: {prediction}")
```

## Requirements

- Python >= 3.9
- PyTorch >= 2.2.0
- scikit-learn >= 1.6.0
- pandas >= 2.3.0
- numpy >= 1.26.0, < 2.0.0
- matplotlib >= 3.9.0
- seaborn >= 0.13.0

## License

MIT License

## Author

Funmi Looi-Somoye  

