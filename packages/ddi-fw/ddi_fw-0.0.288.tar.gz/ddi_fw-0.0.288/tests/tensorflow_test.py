import unittest
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from ddi_fw.ml import TFModelWrapper

import os

from ddi_fw.ml.evaluation_helper import Metrics

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import keras

class TestTFModelWrapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the Iris dataset
        iris = load_iris()
        cls.X = iris.data
        cls.y = iris.target.reshape(-1, 1)

        # One-hot encode the target variable
        encoder = OneHotEncoder(sparse_output=False)
        cls.y = encoder.fit_transform(cls.y)

        # Split the dataset into training and testing sets
        cls.X_train, cls.X_temp, cls.y_train, cls.y_temp = train_test_split(cls.X, cls.y, test_size=0.4, random_state=42)
        cls.X_valid, cls.X_test, cls.y_valid, cls.y_test = train_test_split(cls.X_temp, cls.y_temp, test_size=0.5, random_state=42)

        # Define a simple neural network model
        # cls.model = cls.create_model((cls.X_train.shape[1],))

    @staticmethod
    def create_model(input_shape):
        model = Sequential([
            Dense(128, activation='relu', input_shape=(input_shape[1],)),
            Dense(64, activation='relu'),
            Dense(3, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def test_fit_and_evaluate(self):
        # Create an instance of TFModelWrapper
        tf_model_wrapper = TFModelWrapper(
            date='2021-09-01',
            model_func=self.create_model,
            descriptor='iris_test',
            use_mlflow=False
        )
        #train_idx_arr, val_idx_arr, train_data, train_label, test_data, test_label
        tf_model_wrapper.set_data(
            None,
            None,
            self.X_train,
            self.y_train,
            self.X_test,
            self.y_test
        )
        # # Fit the model
        # best_model, best_model_key = tf_model_wrapper.fit()


        # # Predict using the best model
        # predictions = tf_model_wrapper.predict()

        # Evaluate the model
        logs, metrics, pred = tf_model_wrapper.fit_and_evaluate(print_detail=True)

        # Assertions to verify the results
        # self.assertIsNotNone(best_model)
        # self.assertIsInstance(best_model_key, str)
        # self.assertIsNotNone(predictions)
        self.assertIsInstance(logs, dict)
        self.assertIsInstance(metrics, Metrics)
        self.assertIsNotNone(pred)
        print(metrics)

if __name__ == '__main__':
    unittest.main()