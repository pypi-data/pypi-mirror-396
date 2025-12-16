from typing import Type
from ddi_fw.datasets import BaseDataset
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import pandas as pd

from ddi_fw.datasets.dataset_splitter import DatasetSplitter


class IrisDataset(BaseDataset):
    dataset_name: str = "IrisDataset"
    columns: list[str] = ['sepal_length',
                          'sepal_width', 'petal_length', 'petal_width']
    index_path: str = "tests/datasets/iris/indexes"
    dataset_splitter_type: Type[DatasetSplitter] = DatasetSplitter

    def prep(self):
        print(self.columns)
        # Load the Iris dataset
        iris = load_iris()
        X = iris.data
        print(iris.target.shape)
        y = iris.target.reshape(-1, 1)
        print(y.shape)
        # # One-hot encode the target variable
        encoder = OneHotEncoder(sparse_output=False)
        y = encoder.fit_transform(y)
        replace_dict = {
            'sepal length (cm)': 'sepal_length',
            'sepal width (cm)': 'sepal_width',
            'petal length (cm)': 'petal_length',
            'petal width (cm)': 'petal_width'
        }

        # Replace the columns using the dictionary

        # # Create a DataFrame for the dataset
        self.dataframe = pd.DataFrame(
            X, columns=iris.feature_names, index=range(X.shape[0]))
        self.dataframe.rename(columns=replace_dict, inplace=True)
        self.dataframe['class'] = list(y)
        # self.dataframe['class'] = y.flatten()
