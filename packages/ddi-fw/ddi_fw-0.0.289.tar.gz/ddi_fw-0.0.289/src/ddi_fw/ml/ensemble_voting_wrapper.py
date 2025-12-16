import numpy as np
from ddi_fw import utils
from ddi_fw.ml.model_wrapper import ModelWrapper
from ddi_fw.ml.evaluation_helper import Metrics, evaluate
import tensorflow as tf

def convert_to_categorical(arr, num_classes):
    """
    This function takes an array of labels and converts them to one-hot encoding 
    if they are not binary-encoded. If the array is already in a 
    compatible format, it returns the original array.

    Parameters:
    - arr: numpy array with label data (could be binary-encoded or label-encoded)
    - num_classes: number of classes to be used in one-hot encoding

    Returns:
    - The one-hot encoded array if the original array was binary or label encoded
    - The original array if it doesn't require any conversion
    """

    try:
        # First, check if the array is binary-encoded
        if not utils.is_binary_encoded(arr):
            # If the arr labels are binary-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(np.argmax(arr, axis=1), num_classes=num_classes)
        else:
            print("No conversion needed, returning original array.")
            return arr
    except Exception as e:
        # If binary encoding check raises an error, print it and continue to label encoding check
        print(f"Error while checking binary encoding: {e}")

    try:
        # Check if the array is label-encoded
        if utils.is_label_encoded(arr):
            # If the arr labels are label-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(arr, num_classes=num_classes)
    except Exception as e:
        # If label encoding check raises an error, print it
        print(f"Error while checking label encoding: {e}")
        # If the arr labels don't match any of the known encodings, raise an error
        raise ValueError("Unknown label encoding format.")

    # If no conversion was needed, return the original array

    return arr

class VotingWrapper(ModelWrapper):
    def __init__(self, wrappers, name="voting_ensemble"):
        self.wrappers = wrappers
        self.name = name
        self.individual_metrics = {}  # Store metrics for each wrapper
        self.ensemble_metrics = None   # Store ensemble metrics
        self.metrics_log = []         # List to collect metrics entries instead of printing

    def predict(self, X_test, y_test):
        """
        Generate predictions from all individual wrappers and the ensemble.
        Measure metrics for each wrapper and the ensemble. Metrics are stored
        in self.metrics_log and self.individual_metrics / self.ensemble_metrics.
        """
        individual_predictions = []
        individual_metrics_list = []

        # Get predictions and metrics from each wrapper
        for idx, wrapper in enumerate(self.wrappers):
            wrapper_name = wrapper.name if hasattr(wrapper, 'name') else f"wrapper_{idx}"

            # Get predictions from individual wrapper
            y_pred = wrapper.predict(X_test)
            individual_predictions.append(y_pred)

            # Evaluate individual wrapper
            wrapper_metrics = evaluate(y_test, y_pred)
            self.individual_metrics[wrapper_name] = wrapper_metrics
            individual_metrics_list.append(wrapper_metrics)

            # Append metrics to log as a structured dict
            self.metrics_log.append({
                "type": "individual",
                "name": wrapper_name,
                "metrics": self._metrics_to_dict(wrapper_metrics)
            })

        # Ensemble prediction (voting/averaging)
        ensemble_pred = self._ensemble_prediction(individual_predictions)

        # Evaluate ensemble
        self.ensemble_metrics = evaluate(y_test, ensemble_pred)

        # Append ensemble metrics to log
        self.metrics_log.append({
            "type": "ensemble",
            "name": self.name,
            "metrics": self._metrics_to_dict(self.ensemble_metrics)
        })

        return ensemble_pred

    def _ensemble_prediction(self, predictions):
        """
        Combine individual predictions using voting (for classification).
        Can be extended for regression or other aggregation strategies.
        """
        predictions_array = np.array(predictions)

        # For classification: majority voting
        if predictions_array.ndim == 2:  # Probabilities
            ensemble_pred = np.mean(predictions_array, axis=0)
        else:  # Class labels
            # Majority voting
            ensemble_pred = np.apply_along_axis(
                lambda x: np.bincount(x.astype(int)).argmax(),
                axis=0,
                arr=predictions_array
            )

        return ensemble_pred

    def _metrics_to_dict(self, metrics: Metrics):
        """
        Convert Metrics object or dict to plain dict for logging/serialization.
        """
        if isinstance(metrics, dict):
            return metrics
        result = {}
        for attr in dir(metrics):
            if not attr.startswith('_'):
                value = getattr(metrics, attr)
                if not callable(value):
                    try:
                        result[attr] = float(value)
                    except Exception:
                        result[attr] = value
        return result

    def _print_metrics(self, metrics: Metrics):
        """
        Legacy pretty-printer kept for compatibility; does not append to log.
        """
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                print(f"{key}: {value:.4f}")
        else:
            for attr in dir(metrics):
                if not attr.startswith('_'):
                    value = getattr(metrics, attr)
                    if not callable(value):
                        print(f"{attr}: {value:.4f}")

    def get_metrics_summary(self):
        """
        Return a summary of all metrics (individual + ensemble) and the metrics log list.
        """
        summary = {
            "individual": self.individual_metrics,
            "ensemble": self.ensemble_metrics,
            "log": self.metrics_log
        }
        return summary