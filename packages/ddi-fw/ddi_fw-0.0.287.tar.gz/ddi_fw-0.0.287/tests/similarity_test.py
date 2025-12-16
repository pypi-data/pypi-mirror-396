import unittest
import pandas as pd
from ddi_fw.vectorization import SimilarityMatrixGenerator, VectorGenerator
 
 ## TODO: Complete the test case below

from sklearn.preprocessing import MultiLabelBinarizer

 

class TestSimilarityMatrixGenerator(unittest.TestCase):
    def setUp(self):
        # Create a sample dataframe
        data = {
            'column1': [[1, 0, 1], [1, 1, 0], [0, 0, 1]],
            'column2': [[0, 1, 0], [1, 0, 1], [1, 1, 1]]
        }
        self.dataframe = pd.DataFrame(data)

    def test_compute_jaccard_similarity(self):
        
        # Create an instance of SimilarityMatrixGenerator
        generator = SimilarityMatrixGenerator()

        # Compute the Jaccard similarity matrix
        columns = ['column1', 'column2']
        
        vector_generator = VectorGenerator(self.dataframe)
        generated_vectors = vector_generator.generate_feature_vectors(
        columns)
        

        # Print the similarity matrices
        for column, matrix in zip(columns, generated_vectors.values()):
            print(f"Jaccard similarity matrix for {column}:")
            print(matrix)
            sm = generator.create_jaccard_similarity_matrices(matrix)
            print(sm)

        # # Assertions to verify the results
        # self.assertIn('column1', similarity_matrices)
        # self.assertIn('column2', similarity_matrices)
        # self.assertIsInstance(similarity_matrices['column1'], pd.DataFrame)
        # self.assertIsInstance(similarity_matrices['column2'], pd.DataFrame)

if __name__ == '__main__':
    unittest.main()