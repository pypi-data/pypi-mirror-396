#This module implements a class for loading and preprocessing 5-dimensional datasets, to answer Question 3 (Data Handling)


#Required Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import logging
from typing import Tuple

log = logging.getLogger(__name__)


class DataLoader:
    """Utility class for loading and preprocessing 5-dimensional datasets.
    
    Purpose:
        This class handles loading pickle files containing 5D datasets, validating
        data structure, handling missing values, splitting data into train/validation/test
        sets, and standardizing features for neural network training.
    
    Attributes:
        PATH (str): Path to the pickle file containing the dataset
        scaler (sklearn.preprocessing.StandardScaler): StandardScaler instance for feature normalization
    
    Methods:
        __init__: Initialize the DataLoader with a file path
        load_dataset: Load a dataset from a pickle file
        inspect_data: Validate, preprocess, and split the dataset
    """
    
    def __init__(self, PATH: str) -> None:
        """Initialize a DataLoader for loading and preprocessing datasets.
        
        Parameters:
            PATH (str): Path to the pickle file containing the dataset
        
        Returns:
            None
        
        Raises:
            ValueError: If PATH is empty or invalid
        """
        if not PATH or not isinstance(PATH, str):
            raise ValueError(f"Invalid file path provided: {PATH}")
        self.PATH = PATH
        try:
            self.scaler = StandardScaler()
        except Exception as e:
            log.error(f"Failed to initialize StandardScaler: {e}")
            raise
    
    def load_dataset(self) -> pd.DataFrame:
        """Load a dataset from a pickle file.
        
        Parameters:
            None (uses self.PATH)
        
        Returns:
            pandas.DataFrame: The loaded dataset from the pickle file.
        
        Raises:
            FileNotFoundError: If the pickle file does not exist
            KeyError: If the pickle file is missing required keys ("X", "y", "metadata")
            ValueError: If the data structure is invalid
        """
        try:
            data = pd.read_pickle(self.PATH)
        except FileNotFoundError:
            log.error(f"File not found: {self.PATH}")
            raise FileNotFoundError(f"Dataset file not found: {self.PATH}")
        except Exception as e:
            log.error(f"Failed to load pickle file {self.PATH}: {e}")
            raise ValueError(f"Failed to load pickle file: {e}")
        
        try:
            X = data["X"]              # numpy array
            y = data["y"]              # numpy array
            meta = data["metadata"]    # metadata dict
        except KeyError as e:
            log.error(f"Missing required key in dataset: {e}")
            raise KeyError(f"Dataset is missing required key: {e}. Expected keys: 'X', 'y', 'metadata'")

        try:
            # Build DataFrame
            df = pd.DataFrame(X, columns=meta["feature_names"])
            df[meta["target_name"]] = y
        except Exception as e:
            log.error(f"Failed to build DataFrame: {e}")
            raise ValueError(f"Failed to build DataFrame from loaded data: {e}")

        log.info("Pickle data loaded successfully")
        return df

    def inspect_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int, Tuple[float, float]]:
        """Inspect, validate, and preprocess the dataset.
        
        Validates required columns (x1, x2, x3, x4, x5, y), handles missing values,
        splits data into train/validation/test sets, and standardizes features.
        
        Parameters:
            data (pandas.DataFrame): The dataset to inspect and preprocess
        
        Returns:
            tuple: A tuple containing:
                - X_train (numpy.ndarray): Training features
                - X_test (numpy.ndarray): Test features
                - X_val (numpy.ndarray): Validation features
                - y_train (numpy.ndarray): Training targets
                - y_test (numpy.ndarray): Test targets
                - y_val (numpy.ndarray): Validation targets
                - num_features (int): Number of features
                - num_samples (int): Total number of samples
                - target_range (tuple): (min, max) values of target variable
        """

        # Validate required columns exist
        required_features = ["x1", "x2", "x3", "x4", "x5"]
        required_target = "y"
        
        missing_features = [col for col in required_features if col not in data.columns]
        if missing_features:
            raise KeyError(f"Dataset is missing required feature columns: {missing_features}")

        if required_target not in data.columns:
            raise KeyError(f"Dataset must contain target column '{required_target}'.")

        # Extract features and target
        X = data[required_features].to_numpy()
        y = data[required_target].to_numpy().reshape(-1, 1)

        # Validate shapes
        if X.ndim != 2 or X.shape[1] != 5: #check if X has 2 dimensions and 5 features
            raise ValueError(f"X must have shape (n_samples, 5). Got {X.shape}")

        if y.ndim != 2 or y.shape[0] != X.shape[0]: #check if y has 2 dimensions and matches X rows
            raise ValueError("y must be shape (n_samples, 1) and match X rows.")

    
        # Handle missing values - replace NaNs with the column means
        # For features (x1, x2, x3, x4, x5)
        if np.isnan(X).any():
            col_means = np.nanmean(X, axis=0)
            inds = np.where(np.isnan(X))
            X[inds] = np.take(col_means, inds[1])
            log.info("Missing values in X replaced with column means")

        # For target (y)
        if np.isnan(y).any():
            y_mean = np.nanmean(y)
            y[np.isnan(y)] = y_mean
            log.info("Missing values in y replaced with mean target value")

        
        # Extract dataset characteristics for frontend display
        num_samples = X.shape[0]
        num_features = X.shape[1]
        target_range = (round(float(y.min()), 2), round(float(y.max()), 2)) #round to 2 decimal places

        log.info(f"Dataset characteristics:")
        log.info(f" → Samples: {num_samples}")
        log.info(f" → Features: {num_features}")
        log.info(f" → Target range: {target_range}")

        # Split data - 70% train, 15% val, 15% test
        try:
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=0.3, random_state=42
            )

            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42
            )
        except Exception as e:
            log.error(f"Failed to split data: {e}")
            raise ValueError(f"Data splitting failed: {e}")

        log.info("Data split into training, validation and test sets")

  
        # Standardise features using StandardScaler (fit only on train) 
        try:
            X_train = self.scaler.fit_transform(X_train)
            X_val = self.scaler.transform(X_val)
            X_test = self.scaler.transform(X_test)
        except Exception as e:
            log.error(f"Failed to standardize features: {e}")
            raise ValueError(f"Feature standardization failed: {e}")

        log.info("Features standardised using StandardScaler")

        return (
            X_train,
            X_test,
            X_val,
            y_train,
            y_test,
            y_val,
            num_features,
            num_samples,
            target_range,
        )