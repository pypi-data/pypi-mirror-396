#This module implements a neural network for interpolating 5-dimensional data using Pytorch
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import mean_squared_error, r2_score
from .interpylate_fls.logger import Logger 
import numpy as np
from typing import List, Union, Tuple

log = Logger()

class NeuralNetwork:
    """PyTorch-based neural network for interpolating 5-dimensional datasets.
    
    Purpose:
        This class implements a customisable neural network using PyTorch
        for interpolating 5-dimensional data.
    
    Attributes:
        device (torch.device): Device where tensors and model are stored (CPU)
        X_train (torch.Tensor): Training feature data
        X_val (torch.Tensor): Validation feature data
        X_test (torch.Tensor): Test feature data
        y_train (torch.Tensor): Training target data
        y_val (torch.Tensor): Validation target data
        y_test (torch.Tensor): Test target data
        input_size (int): Number of input features
        output_size (int): Number of output neurons
        num_hidden_layers (int): Number of hidden layers
        hidden_layer_sizes (List[int]): List of neurons per hidden layer
        learning_rate (float): Learning rate for Adam optimizer
        epochs (int): Number of training epochs
        seed (int): Random seed for reproducibility
        model (torch.nn.Sequential): The PyTorch neural network model
        criterion (torch.nn.MSELoss): Loss function (Mean Squared Error)
        optimizer (torch.optim.Adam): Optimizer for training
        train_losses (List[float]): Training loss values per epoch
        val_losses (List[float]): Validation loss values per epoch
        y_pred_test (torch.Tensor): Predicted values on test set (after evaluation)
    
    Methods:
        __init__: Initialize the neural network with data and hyperparameters
        _build_model: Build the PyTorch model architecture
        train: Train the neural network on training data
        evaluate: Evaluate the model on test data and return metrics
        predict: Make a prediction for a single input
    """
    
    def __init__(self, X_train: Union[np.ndarray, List[List[float]]], 
                 y_train: Union[np.ndarray, List[float]], 
                 X_val: Union[np.ndarray, List[List[float]]], 
                 y_val: Union[np.ndarray, List[float]], 
                 X_test: Union[np.ndarray, List[List[float]]], 
                 y_test: Union[np.ndarray, List[float]],
                 input_size: int = 5,               
                 num_hidden_layers: int = 2,
                 hidden_layer_sizes: List[int] = [64, 32],
                 output_size: int = 1,              
                 learning_rate: float = 0.001,
                 epochs: int = 100,
                 seed: int = 42) -> None: #using seeds for reproducibility
        """Initialize a neural network for regression tasks.
        
        Parameters:
            X_train (array-like): Training feature data
            y_train (array-like): Training target data
            X_val (array-like): Validation feature data
            y_val (array-like): Validation target data
            X_test (array-like): Test feature data
            y_test (array-like): Test target data
            input_size (int): Number of input features (default: 5)
            num_hidden_layers (int): Number of hidden layers (default: 2)
            hidden_layer_sizes (List[int]): List of neurons per hidden layer (default: [64, 32])
            output_size (int): Number of output neurons (default: 1)
            learning_rate (float): Learning rate for Adam optimizer (default: 0.001)
            epochs (int): Number of training epochs (default: 100)
            seed (int): Random seed for reproducibility (default: 42)
        
        Returns:
            None
        """
        
        # Ensure all tensors are on CPU python library compatibility e.g. NumPy, Pandas, Scikit-learn
        self.device = torch.device('cpu')
        try:
            self.X_train = torch.tensor(X_train, dtype=torch.float32, device=self.device)
            self.X_val   = torch.tensor(X_val, dtype=torch.float32, device=self.device)
            self.X_test  = torch.tensor(X_test, dtype=torch.float32, device=self.device)
            self.y_train = torch.tensor(y_train, dtype=torch.float32, device=self.device)
            self.y_val   = torch.tensor(y_val, dtype=torch.float32, device=self.device)
            self.y_test  = torch.tensor(y_test, dtype=torch.float32, device=self.device)
        except Exception as e:
            log.error(f"Failed to convert data to tensors: {e}")
            raise ValueError(f"Failed to convert input data to PyTorch tensors: {e}")

        self.input_size = input_size
        self.output_size = output_size
        self.num_hidden_layers = num_hidden_layers
        self.hidden_layer_sizes = hidden_layer_sizes
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.seed = seed

        try:
            torch.manual_seed(seed)
            self.model = self._build_model()

            # Ensure model is on CPU
            self.model = self.model.to(self.device)
            self.criterion = nn.MSELoss()
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        except Exception as e:
            log.error(f"Failed to initialize model components: {e}")
            raise RuntimeError(f"Failed to initialize neural network model: {e}")

        self.train_losses = []
        self.val_losses = []

    #Build model based on user inputs
    def _build_model(self) -> nn.Sequential:
        """Builds a simple PyTorch neural network model based on the number of hidden layers and their sizes.
        
        Parameters:
            None (uses instance attributes)
        
        Returns:
            torch.nn.Sequential: A PyTorch sequential model with linear layers and ReLU activations.
        
        Raises:
            ValueError: If model architecture parameters are invalid
        """
        try:
            layers = []
            in_size = self.input_size
            for i, h_size in enumerate(self.hidden_layer_sizes):
                if h_size <= 0:
                    raise ValueError(f"Invalid hidden layer size: {h_size}. Must be positive.")
                layers.append(nn.Linear(in_size, h_size))
                
                if i % 2 == 0: # ReLU for even layers
                    layers.append(nn.ReLU())
                in_size = h_size
            layers.append(nn.Linear(in_size, self.output_size))
            log.info("Model built successfully. Input Size: {}, Hidden Layers: {}, Output Size: {}".format(
                self.input_size, self.hidden_layer_sizes, self.output_size))
            
            return nn.Sequential(*layers)
        except Exception as e:
            log.error(f"Failed to build model: {e}")
            raise ValueError(f"Model building failed: {e}")

    #train model based on user's dataset
    def train(self, verbose: bool = True) -> None:
        """Trains the neural network using the inputted training data.
        
        Parameters:
            verbose (bool): If True, prints training progress every 10% of epochs (default: True)
        
        Returns:
            None (updates model weights and stores losses in self.train_losses and self.val_losses)
        
        Raises:
            RuntimeError: If training fails due to model or data issues
        """
        log.info("Training started!")
        try:
            for epoch in range(self.epochs):
                self.model.train()
                self.optimizer.zero_grad()
                y_pred_train = self.model(self.X_train)
                loss_train = self.criterion(y_pred_train, self.y_train)
                loss_train.backward()
                self.optimizer.step()

                # Validation
                self.model.eval()
                with torch.no_grad():
                    y_pred_val = self.model(self.X_val)
                    loss_val = self.criterion(y_pred_val, self.y_val)

                self.train_losses.append(loss_train.item())
                self.val_losses.append(loss_val.item())

                if verbose and (epoch + 1) % max(1, self.epochs // 10) == 0:
                    log.info(f"Epoch {epoch+1}/{self.epochs}, "
                          f"Train Loss={loss_train.item():.4f}, "
                          f"Val Loss={loss_val.item():.4f}")
            log.info("Training complete!")
        except Exception as e:
            log.error(f"Training failed at epoch {epoch+1}: {e}")
            raise RuntimeError(f"Training failed: {e}")

    #Find the MSE and R² on the test set
    def evaluate(self) -> Tuple[float, float]:
        """Evaluates the neural network on the test data.
        
        Parameters:
            None (uses self.X_test and self.y_test)
        
        Returns:
            tuple: A tuple containing:
                - mse (float): Mean squared error on test set
                - r2 (float): R² score on test set
        """
        log.info("Evaluation started!")
        self.model.eval()
        with torch.no_grad():
            try:
                y_pred_test = self.model(self.X_test)
                
                # Ensure y_pred_test is on CPU, detached, and contiguous before converting to numpy
                y_pred_test = y_pred_test.cpu().detach().contiguous()
                self.y_pred_test = y_pred_test  # Store for plotting results
                
                # Convert tensors to numpy arrays
                y_test_np = self.y_test.cpu().detach().contiguous().numpy()
                y_pred_np = y_pred_test.numpy()
                
                mse = mean_squared_error(y_test_np, y_pred_np)
                r2 = r2_score(y_test_np, y_pred_np)
                log.info(f"Test MSE: {mse:.4f}")
                log.info(f"Test R²: {r2:.4f}")
                log.info("Evaluation Complete!")
                return mse, r2
            except Exception as e:
                log.error(f"Error during evaluation: {e}")
                import traceback
                log.error(traceback.format_exc())
                raise
    
    
    def predict(self, x_input: Union[List[float], np.ndarray]) -> float:
        """Makes a prediction for a single input.
        
        Parameters:
            x_input (List[float] or array-like): Input features for prediction (should match input_size)
        
        Returns:
            float: Predicted output value rounded to 2 decimal places.
        
        Raises:
            ValueError: If input shape doesn't match expected input_size
            RuntimeError: If prediction fails
        """
        log.info("Prediction started!")
        try:
            # Validate input shape
            if isinstance(x_input, list):
                if len(x_input) != self.input_size:
                    raise ValueError(f"Input length {len(x_input)} does not match expected input size {self.input_size}")
            elif isinstance(x_input, np.ndarray):
                if x_input.shape[-1] != self.input_size:
                    raise ValueError(f"Input shape {x_input.shape} does not match expected input size {self.input_size}")
            
            self.model.eval()
            x_vals = torch.tensor(x_input, dtype=torch.float32, device=self.device).unsqueeze(0)
            with torch.no_grad():
                y_new = round(self.model(x_vals).item(), 2) #round answer to 2 decimal places
            log.info(f"Prediction for input {x_input}: {y_new}")
            log.info("Prediction complete!")
            return y_new
        except ValueError:
            raise
        except Exception as e:
            log.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")