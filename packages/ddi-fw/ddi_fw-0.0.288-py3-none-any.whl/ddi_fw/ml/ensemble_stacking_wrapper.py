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


class StackingWrapper(ModelWrapper):
    def __init__(self, date, descriptor, base_wrappers, meta_model_wrapper, tracking_service=None):
        """
        Args:
            base_wrappers (list): list of instantiated base model wrappers (TF or XGBoost)
            meta_model_wrapper (ModelWrapper): instantiated meta model wrapper
            tracking_service: optional tracking service
        """
        super().__init__(date, descriptor, None)
        self.base_wrappers = base_wrappers
        self.meta_model_wrapper = meta_model_wrapper
        self.tracking_service = tracking_service

    def fit(self):
        # Step 1: Train base models and collect softmax outputs
        inputs = []
        train_label, test_label = None, None
        train_idx_arr, val_idx_arr = None, None
        num_classes = None
        for wrapper in self.base_wrappers:
            train_label = wrapper.train_label
            test_label = wrapper.test_label
            
            # wrapper.train_data = self.train_data
            # wrapper.train_label = self.train_label
            train_idx_arr = wrapper.train_idx_arr
            val_idx_arr = wrapper.val_idx_arr
            # wrapper.train_idx_arr = self.train_idx_arr
            # wrapper.test_data = self.test_data
            # wrapper.test_label = self.test_label

            print(f"Training base model: {wrapper.descriptor}")
            best_model, _, val_preds_dict = wrapper.fit()
            num_classes = wrapper.num_classes
            wrapper.best_model = best_model
            # pred_train = wrapper.predict()
            # if val_preds_dict is not None:
            print("val_preds_dict")
            print(val_preds_dict)
            stacked_values = np.concatenate(list(val_preds_dict.values()))
            # Use validation predictions for training meta-model
            inputs.append(stacked_values)

            # pred_val = wrapper.predict()
            # base_test_outputs.append(pred_val)

        # Step 2: Prepare meta-model input
        # shape: (n_samples, num_classes * num_base_models)
        # X_meta_train = np.hstack(inputs)
        X_meta_train = np.stack(inputs, axis=1)
        y_meta_train = train_label

        # Step 3: Train meta-model
        self.meta_model_wrapper.train_data = X_meta_train
        self.meta_model_wrapper.train_label = y_meta_train
        self.meta_model_wrapper.train_idx_arr = train_idx_arr
        self.meta_model_wrapper.val_idx_arr = val_idx_arr
        self.num_classes = num_classes
        # self.meta_model_wrapper.val_idx_arr = None
        preds = [b.predict() for b in self.base_wrappers]
        self.meta_model_wrapper.test_data = np.stack(preds, axis=1) 
        
        # self.meta_model_wrapper.test_data = np.hstack(
        #     [b.predict() for b in self.base_wrappers])
        
        self.meta_model_wrapper.test_label = test_label

        print("Training meta-learner...")
        best_meta_model, best_meta_key, _ = self.meta_model_wrapper.fit()
        self.meta_model_wrapper.best_model = best_meta_model
        # self.best_model = best_meta_model

        return best_meta_model, best_meta_key

    def predict(self):
        # Step 3: Feed into meta-model
        pred = self.meta_model_wrapper.predict()
        return pred

    def fit_and_evaluate(self, print_detail=False):
        best_model, best_key = self.fit()
        pred = self.predict()
        pred_as_cat = convert_to_categorical(pred, self.num_classes)
        logs, metrics = evaluate(
            self.meta_model_wrapper.test_label, pred_as_cat, info=self.descriptor, print_detail=print_detail)
        metrics.format_float()
        return logs, metrics, pred
