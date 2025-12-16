# read from json
# programatic pipeline

import unittest
import json
from pathlib import Path
from ddi_fw.datasets.dataset_splitter import DatasetSplitter
from ddi_fw.pipeline import Pipeline, MultiPipeline
from ddi_fw.datasets import BaseDataset
from ddi_fw.langchain.embeddings import MeanPoolingStrategy, PoolingStrategy
from config.iris_dataset import IrisDataset
from tests.config.mnist_dataset import MNISTDataset

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read the JSON configuration file
       
        
        config_path = Path('./tests/config/pipeline_test.json')
        with open(config_path, 'r') as f:
            cls.config = json.load(f)
            # print(cls.config)

    def test_pipeline_creation(self):
        dataset_splitter = DatasetSplitter()
        pooling_strategy = MeanPoolingStrategy()
        # dataset = IrisDataset(dataset_name="IrisDataset",
        #                       dataset_splitter_type = DatasetSplitter ,
        #                       index_path="tests/datasets/iris/indexes"
        #                    )
        # dataset.load()
        # dataset.split_dataset(save_indexes=True)
        
        cfg = self.config['experiments'][0]
        # Create a Pipeline object using the configuration
        mp = MultiPipeline(experiments_config=self.config).build()
        mp.run()
        print(f'name\t accuracy\tf-score\tprecision\trecall')
        for key in mp.results().keys():
            for m in mp.results()[key].metric_dict:
                accuracy = mp.results()[key].metric_dict[m].accuracy
                macro_f_score = mp.results()[key].metric_dict[m].f1_score['macro']
                macro_precision = mp.results()[key].metric_dict[m].precision['macro']
                macro_recall = mp.results()[key].metric_dict[m].recall['macro']
                print(f'{m}: {accuracy}\t{macro_f_score}\t{macro_precision}\t{macro_recall}')
            
    
    def test_pipeline_creation_mnist(self):
            
            x_config_path = Path('./tests/config/pipeline_test_mnist.json')
            with open(x_config_path, 'r') as f:
                config = json.load(f)
                print(config)
            
            dataset_splitter = DatasetSplitter()
            pooling_strategy = MeanPoolingStrategy()
            # dataset = MNISTDataset(dataset_name="MNISTDataset",
            #                     dataset_splitter_type = DatasetSplitter ,
            #                     index_path="tests/datasets/mnist/indexes"
            #                 )
            # dataset.load()
            # dataset.split_dataset(save_indexes=True)
            
            # cfg = self.config['experiments'][0]
            # # Create a Pipeline object using the configuration
            mp = MultiPipeline(experiments_config=config).build()
            mp.run()
            print(f'name\t accuracy\tf-score\tprecision\trecall')
            for key in mp.results().keys():
                for m in mp.results()[key].metric_dict:
                    accuracy = mp.results()[key].metric_dict[m].accuracy
                    macro_f_score = mp.results()[key].metric_dict[m].f1_score['macro']
                    macro_precision = mp.results()[key].metric_dict[m].precision['macro']
                    macro_recall = mp.results()[key].metric_dict[m].recall['macro']
                    print(f'{m}: {accuracy}\t{macro_f_score}\t{macro_precision}\t{macro_recall}')

 
    def test_pipeline_creation_openfda(self):
        import os
        from dotenv import load_dotenv
        import tensorflow as tf

        print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))

        # Load variables from .env file into environment
        load_dotenv()

        # Set Kaggle credentials from environment
        os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
        os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

        # !kaggle datasets download -d kivancbayraktar/c8c6ab09-dbbd-4a57-8241-c81209bcbfcd --unzip -p /content/new_work/embeddings/all-embeddings
        # import kagglehub

        # # Download latest version
        # path = kagglehub.dataset_download("kivancbayraktar/c8c6ab09-dbbd-4a57-8241-c81209bcbfcd")

        # print("Path to dataset files:", path)
        # from ddi_fw.langchain import ChromaVectorStoreManager,BaseVectorStoreManager, FaissVectorStoreManager

        
        # faiss_vector_store_manager  = FaissVectorStoreManager(persist_directory=f"{path}/faiss/openfda-deneme-all-mpnet-base-v2/no_op")
        # # faiss_vector_store_manager  = FaissVectorStoreManager(persist_directory=f"{path}/embeddings/all-embeddings/faiss/openfda-deneme-all-mpnet-base-v2/no_op")

        # d = faiss_vector_store_manager.initialize_embedding_dict()
        # faiss_vector_store_manager.vector_store.index.ntotal
        x_config_path = Path('./tests/config/pipeline_test_openfda_2.json')
        with open(x_config_path, 'r') as f:
            config = json.load(f)
            # print(config)
        
        dataset_splitter = DatasetSplitter()
        pooling_strategy = MeanPoolingStrategy()
        # dataset = MNISTDataset(dataset_name="MNISTDataset",
        #                     dataset_splitter_type = DatasetSplitter ,
        #                     index_path="tests/datasets/mnist/indexes"
        #                 )
        # dataset.load()
        # dataset.split_dataset(save_indexes=True)
        
        # cfg = self.config['experiments'][0]
        # # Create a Pipeline object using the configuration
        mp = MultiPipeline(experiments_config=config).build()
        mp.run()
        print(f'name\t accuracy\tf-score\tprecision\trecall')
        for key in mp.results().keys():
            for m in mp.results()[key].metric_dict:
                accuracy = mp.results()[key].metric_dict[m].accuracy
                macro_f_score = mp.results()[key].metric_dict[m].f1_score['macro']
                macro_precision = mp.results()[key].metric_dict[m].precision['macro']
                macro_recall = mp.results()[key].metric_dict[m].recall['macro']
                print(f'{m}: {accuracy}\t{macro_f_score}\t{macro_precision}\t{macro_recall}')
                            
 
if __name__ == '__main__':
    unittest.main()