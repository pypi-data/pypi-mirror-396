from typing import Any, Dict, List, Optional, Type
from ddi_fw.datasets.dataset_splitter import DatasetSplitter

from pydantic import BaseModel
from ddi_fw.datasets.core import TextDatasetMixin
from ddi_fw.langchain.faiss_storage import BaseVectorStoreManager
from ddi_fw.ml.ensemble_stacking_wrapper import StackingWrapper
from ddi_fw.ml.ensemble_strategy import AveragingStrategy, GenericEnsembleWrapper, StackingStrategy, VotingStrategy
from ddi_fw.ml.model_wrapper import Result
from ddi_fw.ml.tracking_service import TrackingService
from ddi_fw.langchain.embeddings import PoolingStrategy
from ddi_fw.datasets import BaseDataset
from ddi_fw.ml import MultiModalRunner
import logging
from ddi_fw.ml.pytorch_wrapper import PTModelWrapper
from ddi_fw.ml.tensorflow_wrapper import TFModelWrapper
from ddi_fw.utils import utils
from ddi_fw.utils.package_helper import get_import

class EnsemblePipeline(BaseModel):

    library: str = 'tensorflow'
    ensemble_strategy: str = 'voting'  # 'voting', 'averaging', 'stacking'
    experiment_name: str
    experiment_description: str
    tracking_library: str
    tracking_params: Optional[Dict[str, Any]] = None
    dataset_type: Type[BaseDataset]
    dataset_additional_config: Optional[Dict[str, Any]] = None
    dataset_splitter_type: Type[DatasetSplitter] = DatasetSplitter
    columns: Optional[List[str]] = None
    input_processing: Optional[List[Dict[str, Any]]] = None
    embedding_dict: Optional[Dict[str, Any]] = None
    column_embedding_configs: Optional[List] = None
    vector_db_persist_directory: Optional[str] = None
    vector_db_collection_name: Optional[str] = None
    embedding_pooling_strategy_type: Type[PoolingStrategy] | None = None
    vector_store_manager_type: Type[BaseVectorStoreManager] | None = None
    combinations: Optional[List[tuple]] = None
    model: Optional[Any] = None
    default_model:  Optional[Any] = None
    multi_modal:  Optional[Any] = None
    _tracking_service: TrackingService | None = None
    _dataset: BaseDataset | None = None
    _items: List = []
    _train_idx_arr: List | None = []
    _val_idx_arr: List | None = []

    @property
    def tracking_service(self) -> TrackingService | None:
        return self._tracking_service

    @property
    def dataset(self) -> BaseDataset | None:
        return self._dataset

    @property
    def items(self) -> List:
        return self._items

    @property
    def train_idx_arr(self) -> List | None:
        return self._train_idx_arr

    @property
    def val_idx_arr(self) -> List | None:
        return self._val_idx_arr

    class Config:
        arbitrary_types_allowed = True

    # TODO embedding'leri set etme kimin görevi
    def build(self):
        self._tracking_service = TrackingService(self.experiment_name,
                                                 backend=self.tracking_library, tracking_params=self.tracking_params)

        if self.embedding_pooling_strategy_type is not None and not isinstance(self.embedding_pooling_strategy_type, type):
            raise TypeError(
                "self.embedding_pooling_strategy_type must be a class, not an instance")
        if not isinstance(self.dataset_type, type):
            raise TypeError(
                "self.dataset_type must be a class, not an instance")

        # 'enzyme','target','pathway','smile','all_text','indication', 'description','mechanism_of_action','pharmacodynamics', 'tui', 'cui', 'entities'
        kwargs = {"columns": self.columns,
                  "additional_config": self.dataset_additional_config}

        dataset_splitter = self.dataset_splitter_type()
        pooling_strategy = self.embedding_pooling_strategy_type(
        ) if self.embedding_pooling_strategy_type else None

        params = {}

        if self.embedding_dict is not None:
            params["embedding_dict"] = self.embedding_dict
        if self.vector_db_persist_directory is not None:
            params["persist_directory"] = self.vector_db_persist_directory
        if self.vector_db_collection_name is not None:
            params["collection_name"] = self.vector_db_collection_name

        vector_store_manager = self.vector_store_manager_type(
            **params) if self.vector_store_manager_type else None
        if issubclass(self.dataset_type, TextDatasetMixin):

            dataset = self.dataset_type(
                vector_store_manager=vector_store_manager,
                embedding_dict=self.embedding_dict,
                pooling_strategy=pooling_strategy,
                column_embedding_configs=self.column_embedding_configs,
                vector_db_persist_directory=self.vector_db_persist_directory,
                vector_db_collection_name=self.vector_db_collection_name,
                dataset_splitter_type=self.dataset_splitter_type,
                **kwargs)

        elif self.dataset_type == BaseDataset: ## !!! check it
            dataset = self.dataset_type(
                dataset_splitter_type=self.dataset_splitter_type,
                **kwargs)
        else:
            dataset = self.dataset_type(
                dataset_splitter_type=self.dataset_splitter_type, **kwargs)
            
        dataset.input_processing = self.input_processing

        # X_train, X_test, y_train, y_test, train_indexes, test_indexes, train_idx_arr, val_idx_arr = dataset.load()

        dataset.load()

        self._dataset = dataset
        self._train_idx_arr = dataset.train_idx_arr
        self._val_idx_arr = dataset.val_idx_arr

        dataframe = dataset.dataframe

        # Check if any of the arrays are None or empty
        is_data_valid = (dataset.X_train is not None and dataset.X_train.size > 0 and
                         dataset.y_train is not None and dataset.y_train.size > 0 and
                         dataset.X_test is not None and dataset.X_test.size > 0 and
                         dataset.y_test is not None and dataset.y_test.size > 0)

        # Check if the dataframe is None or empty
        is_dataframe_valid = dataframe is not None and not dataframe.empty

        if not (is_data_valid or is_dataframe_valid):
            raise ValueError("The dataset is not loaded")

        # column name, train data, train label, test data, test label
        self._items = dataset.produce_inputs()

        print(f"Building the experiment: {self.experiment_name}")
        # print(
        #     f"Name: {self.experiment_name}, Dataset: {dataset}, Model: {self.model}")
        # Implement additional build logic as needed
        return self
    
    def __create_wrapper(self, library):
        if library == 'tensorflow':
            return TFModelWrapper
        elif library == 'pytorch':
            return PTModelWrapper
        try:
            lib = get_import(library)
            return lib
        except Exception:
            raise ValueError(
                "Unsupported library type. Supported types are 'tensorflow', 'pytorch' or custom model wrapper class path.")


    def run(self):
        if self.default_model is None:
            raise ValueError("default_model cannot be None")
        if self._tracking_service is None:
            logging.warning("Tracking service is not initialized.")
        else:
            self._tracking_service.setup()


        date = utils.utc_time_as_string_simple_format()
        
        
        name = self.default_model.get('name')
        library = self.default_model.get('library', self.library)
        model_type = get_import(self.default_model.get("model_type"))
        kwargs = self.default_model.get('params')
        T = self.__create_wrapper(library)
        meta_learner_wrapper = T(date, name, model_type,
                                    tracking_service=self.tracking_service,  **kwargs)
        
        wrappers=[]
        if self.multi_modal:
            for m in self.multi_modal:
                name = m.get('name')
                library = m.get('library', self.library)
                model_type = get_import(m.get("model_type"))
                kwargs = m.get('params')
                
                input = m.get('input')
                inputs = m.get('inputs')

                if model_type is None:
                    raise Exception(
                        "model_type cannot be None, it should be defined in multi_modal or default_model")
                    
                if input and inputs:
                    raise ValueError(
                        "Only one of 'input' or 'inputs' should be defined.")
                if not input and not inputs:
                    raise ValueError(
                        "At least one of 'input' or 'inputs' must be defined.")
                    
                if input and not isinstance(input, str):
                    raise ValueError(
                        "'input' should be a single string. For multiple inputs, use 'inputs'.")
                    
                                # Get stacking and reshaping config
                processor_type = m.get("processor", "ddi_fw.datasets.processor.DefaultInputProcessor")
                processor = get_import(processor_type)  # Ensure the processor type is valid
                force_stack = m.get("force_stack", True)
                reshape_dims = m.get("reshape")
                train_data, train_label, test_data, test_label = None, None, None, None
                
                # Prepare processing config with all context
                processing_config = {
                    "force_stack": force_stack,
                    "reshape": reshape_dims
                }
                item_dict = {t[0]: t for t in self.items}
                # --- SINGLE INPUT CASE ---
                if input:
                    item = item_dict[input]
                    train_data = item[1]
                    train_label = item[2]
                    test_data = item[3]
                    test_label = item[4]
                elif inputs:
                    filtered_dict = {k: item_dict[k]
                                     for k in inputs if k in item_dict}
                    if not filtered_dict:
                        raise ValueError(
                            f"No matching inputs found in item_dict for: {inputs}")

                    first_input = next(iter(filtered_dict.values()))
                    train_data = [f[1] for f in filtered_dict.values()]
                    test_data = [f[3] for f in filtered_dict.values()]
                    train_label = first_input[2]
                    test_label = first_input[4]
                    
                train_data = processor().process2(train_data, processing_config)
                test_data = processor().process2(test_data, processing_config)

                T = self.__create_wrapper(library)
                wrapper = T(date, name, model_type,
                                    tracking_service=self.tracking_service,  **kwargs)
                wrapper.set_data(
                    self.train_idx_arr, self.val_idx_arr,
                    train_data, train_label,
                    test_data, test_label
                )
                wrappers.append(wrapper)
        
        # Get ensemble strategy from config (default: voting)
            ensemble_strategies = self.ensemble_strategy  # e.g. "voting,stacking"

            # Prepare meta learner only if stacking is included
            meta_learner_wrapper = None
            if "stacking" in ensemble_strategies.replace(" ", "").lower():
                name = self.default_model.get('name')
                library = self.default_model.get('library', self.library)
                model_type = get_import(self.default_model.get("model_type"))
                meta_kwargs = self.default_model.get('params')

                T_meta = self.__create_wrapper(library)
                meta_learner_wrapper = T_meta(
                    date,
                    name,
                    model_type,
                    tracking_service=self.tracking_service,
                    **meta_kwargs
                )

            # Instantiate ensemble wrapper (supports multiple strategies)
            ensemble = GenericEnsembleWrapper(
                base_wrappers=wrappers,
                ensemble_strategies=ensemble_strategies,
                meta_learner=meta_learner_wrapper,
                name="ensemble",
                tracking_service=self.tracking_service,
                date=date
            )
            
            # Train and evaluate
            logs, result, pred = ensemble.fit_and_evaluate()
            
            # result = Result()
            # result.add_metric(ensemble.name, metrics)
            return result