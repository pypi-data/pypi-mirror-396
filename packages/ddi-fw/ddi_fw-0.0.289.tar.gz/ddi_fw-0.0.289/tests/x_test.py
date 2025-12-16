

# # import unittest

# from typing import Literal
# from unittest import TestCase
# import unittest

# # import pandas as pd
# from ddi_fw.datasets.dataset_splitter import DatasetSplitter
# from ddi_fw.vectorization import IDF
# from ddi_fw.langchain import MeanPoolingStrategy

 

# class TryTesting(TestCase):
    
#         # # idf_scores = calculate_idf(df['tui_description'])
#         # idf_scores_sorted_desc = sorted(
#         #     idf_scores.items(), key=lambda x: x[1], reverse=True)
#         # threshold = 1
#         # keys_over_threshold = [k for k,v in idf_scores.items() if v > threshold]


#     def test_dataset_split(self):
#         dataset_splitter = DatasetSplitter()
#         pooling_strategy = MeanPoolingStrategy()

#         d = DDIMDLDataset(
#             dataset_name="DDIMDLDataset",
#                         index_path="tests/ddi_index",
#                         embedding_size=1024,
#                         embedding_dict={},
#                         embeddings_pooling_strategy=pooling_strategy,
#                         dataset_splitter=dataset_splitter)
#         d.split_dataset(save_indexes=True)


#     def test_dataset_load(self):
#         dataset_splitter = DatasetSplitter()
#         pooling_strategy = MeanPoolingStrategy()

#         d = DDIMDLDataset(dataset_name="DDIMDLDataset",
#                         embedding_size=1024,
#                         embedding_dict={},
#                         embeddings_pooling_strategy=pooling_strategy,
#                         dataset_splitter=dataset_splitter)
#         d.load()
#         print(d.X_train.shape)
    
#     def test_always_passes(self):
#         self.assertTrue(True)

#     # def test_always_fails(self):
#     #     self.assertTrue(False)

# if __name__ == '__main__':
#     unittest.main()
