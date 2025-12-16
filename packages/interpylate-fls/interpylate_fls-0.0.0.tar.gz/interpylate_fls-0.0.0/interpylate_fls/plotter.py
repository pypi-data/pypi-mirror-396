#This module provides plotting functionality to visualise model performance to display on frontend

import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional

#Use dark theme to match app UI
sns.set_theme(style="darkgrid", palette="deep")
plt.style.use("dark_background")

class Plotter:
    """Utility class for visualising neural network model performance.
    
    Purpose:
        This class provides static methods for generating visualisations of model
        performance, including learning curves and predictions vs actual values plots.
        All methods use a dark theme to match the application UI.
    
    Attributes:
        None (all methods are static)
    
    Methods:
        save_learning_curve: Save learning curves to a file
        save_predictions_vs_actual: Save predictions vs actual plot to a file
    """
    
    @staticmethod
    def save_learning_curve(training_history: List[float], 
                           val_history: Optional[List[float]] = None, 
                           save_path: Optional[str] = None) -> None:
        """Saves training and validation learning curves to a file.
        
        Parameters:
            training_history (List[float]): List of training loss values per epoch
            val_history (List[float], optional): List of validation loss values per epoch (default: None)
            save_path (str, optional): Path to save the plot image (default: None)
        
        Returns:
            None (saves the plot to file if save_path is provided)
        
        Raises:
            ValueError: If training_history is empty or invalid
            IOError: If file saving fails
        """
        #create learning curve plot
        try:
            if not training_history or len(training_history) == 0:
                raise ValueError("Training history cannot be empty")
            
            plt.figure(figsize=(9, 5))
            
            epochs = np.arange(len(training_history))
            sns.lineplot(x=epochs, y=training_history, label="Training Loss", linewidth=2.2, color="#4A9EFF")
            
            if val_history is not None:
                if len(val_history) != len(training_history):
                    raise ValueError(f"Validation history length {len(val_history)} does not match training history length {len(training_history)}")
                sns.lineplot(x=np.arange(len(val_history)), y=val_history, label="Validation Loss", linewidth=2.2, color="#FF6B9D")
            
            
            plt.xlabel("Epochs", fontsize=12)
            plt.ylabel("Mean Squared Error (MSE)", fontsize=12)
            plt.grid(alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            #save plot to uploads folder
            if save_path:
                try:
                    plt.savefig(save_path, dpi=100, bbox_inches='tight')
                except Exception as e:
                    raise IOError(f"Failed to save learning curve to {save_path}: {e}")
            plt.close()
        except ValueError:
            raise
        except IOError:
            raise
        except Exception as e:
            plt.close()
            raise RuntimeError(f"Failed to create learning curve plot: {e}")

    @staticmethod
    def save_predictions_vs_actual(y_true: np.ndarray, 
                                  y_pred: np.ndarray, 
                                  save_path: Optional[str] = None) -> None:
        """Saves predicted vs actual values plot to a file.
        
        Parameters:
            y_true (numpy.ndarray): True target values
            y_pred (numpy.ndarray): Predicted target values
            save_path (str, optional): Path to save the plot image (default: None)
        
        Returns:
            None (saves the plot to file if save_path is provided)
        
        Raises:
            ValueError: If input arrays are empty or have mismatched shapes
            IOError: If file saving fails
        """
        #create predictions vs actual plot
        try:
            if y_true.size == 0 or y_pred.size == 0:
                raise ValueError("Input arrays cannot be empty")
            
            if y_true.shape != y_pred.shape:
                raise ValueError(f"Shape mismatch: y_true shape {y_true.shape} does not match y_pred shape {y_pred.shape}")
            
            y_true = y_true.flatten()
            y_pred = y_pred.flatten()
            
            plt.figure(figsize=(9, 6))
            sns.scatterplot(x=y_true, y=y_pred, s=60, alpha=0.65, edgecolor=None, color="#5A9")
            
            # Reference line for perfect predictions
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            plt.plot([min_val, max_val], [min_val, max_val], linestyle="--", linewidth=2, color="gold", label="Perfect Prediction")
            
            plt.title("Predictions vs True Values", fontsize=14, fontweight="bold")
            plt.xlabel("True Value", fontsize=12)
            plt.ylabel("Predicted Value", fontsize=12)
            plt.legend()
            plt.grid(alpha=0.25)
            plt.tight_layout()
            
            #save plot to uploads folder
            if save_path:
                try:
                    plt.savefig(save_path, dpi=100, bbox_inches='tight')
                except Exception as e:
                    raise IOError(f"Failed to save predictions plot to {save_path}: {e}")
            plt.close()
        except ValueError:
            raise
        except IOError:
            raise
        except Exception as e:
            plt.close()
            raise RuntimeError(f"Failed to create predictions vs actual plot: {e}")
