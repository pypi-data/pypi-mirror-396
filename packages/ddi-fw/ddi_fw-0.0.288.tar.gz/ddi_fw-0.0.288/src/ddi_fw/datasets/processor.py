from typing import Optional
import numpy as np


class BaseInputProcessor:
    def process1(self, data, processing_config=None):
        raise NotImplementedError("Input processors must implement the process method.")
    def process2(self, data, processing_config=None):
        raise NotImplementedError("Input processors must implement the process method.")

class DefaultInputProcessor(BaseInputProcessor):
    def __init__(self):
        pass

    def process2(self, data, processing_config=None):
        """
        Processes input data according to the provided config.
        Supports stacking, reshaping, and can use item_dict for advanced logic.
        """
        if processing_config is None:
            raise ValueError("processing_config must be provided.")

        force_stack = processing_config.get("force_stack", False)
        reshape_dims = processing_config.get("reshape")
        if type(data) is not list:
        
            # Optional: force stack single input to simulate extra dimension
            if force_stack:
                data = np.expand_dims(data, axis=1)
        else:
        # --- MULTIPLE INPUTS CASE ---
            # Stack across inputs
            if len(data) == 1:
                data = data[0]
            
            if force_stack:
                data = np.stack(data, axis=1)
                
            else: #TODO check this
                data = np.array(data).T
         

        # --- OPTIONAL: Reshape if needed ---
        if reshape_dims:
            data = data.reshape((-1, *reshape_dims))
        
        return data


    def process1(self, data, processing_config=None):
        if not processing_config:
            return data
        if processing_config.get("flatten", False):
            print("Flattening data...")
            data = np.array(data).flatten()
            print(f"Data shape after flattening: {data.shape}")
        
        if processing_config.get("stack", False):
            print("Stacking data...")
            data = np.stack(data)
            print(f"Data shape after stacking: {data.shape}")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        # if processing_config.get("flatten", False):
        #     data = np.stack(data.flatten().tolist())
        # Ensure we start with a NumPy array
       

        # Normalize input
        if processing_config.get("normalize", False):
            data = data.astype(np.float32)
            max_val = np.max(data)
            if max_val > 1:
                data /= max_val

        # Reshape input (for images etc.)
        if "reshape" in processing_config:
            try:
                target_shape = tuple(processing_config["reshape"])
                data = data.reshape((-1, *target_shape))
            except Exception as e:
                raise ValueError(f"Reshape failed for data with shape {data.shape}: {e}")


        return data
    
    
    
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class ConcatInputProcessor(BaseInputProcessor):
    def __init__(self):
        self.embeddings_array = None
        self.id_list = None
        self.id_to_idx = None
        self.similarity_matrix = None
        self.top_k_similar_df = None

     
    def _compute_similarity_matrix(self,data):
        similarity_matrix = cosine_similarity(data)
        return similarity_matrix

    def get_top_k_similar(self, similarity_matrix:np.ndarray, top_k=1):
        arr = similarity_matrix.copy()
        np.fill_diagonal(arr, -np.inf)
        top_k_idx = np.argpartition(arr, -top_k, axis=1)[:, -top_k:]
        sorted_top_k_idx = np.argsort(arr[np.arange(arr.shape[0])[:, None], top_k_idx], axis=1)[:, ::-1]
        final_top_k_idx = np.take_along_axis(top_k_idx, sorted_top_k_idx, axis=1)
        top_k_ids_list = [[self.id_list[idx] for idx in row] for row in final_top_k_idx]
        return pd.DataFrame({"drug_id": self.id_list, "top_similar_ids": top_k_ids_list}).set_index("drug_id")

    def process2(self, data, processing_config=None):
        """
        For each input vector, concatenate it with its top-k most similar vectors.
        Assumes 'data' is a DataFrame with an id column and an embedding column.
        """
        # Prepare embeddings and similarity matrix if not already done
        if self.embeddings_array is None or self.similarity_matrix is None:
            similarity_matrix = self._compute_similarity_matrix(data)
            self.top_k_similar_df = self.get_top_k_similar(similarity_matrix,1)

        if self.top_k_similar_df is None:
            raise ValueError("Top-k similar DataFrame not computed.")
        # For each row in data, concatenate its embedding with its top-k similar embeddings
        result = []
        for idx, row in data.iterrows():
            drug_id = row[self.id_column]
            embedding = row[self.embedding_column]
            similar_ids = self.top_k_similar_df.loc[drug_id, "top_similar_ids"]
            similar_embeddings = []
            for sim_id in similar_ids:
                sim_idx = self.id_to_idx.get(sim_id)
                if sim_idx is not None:
                    similar_embeddings.append(self.embeddings_array[sim_idx])
            concat_embedding = np.concatenate([embedding] + similar_embeddings)
            result.append(concat_embedding)
        return np.stack(result)