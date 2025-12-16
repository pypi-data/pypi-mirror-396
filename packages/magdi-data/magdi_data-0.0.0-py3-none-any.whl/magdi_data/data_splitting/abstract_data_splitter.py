"""
Contains an abstract class to create modified copies of a dataset metadata file
(AbstractOccInstDatasetMeta) to create different data splits.
"""

import os
from sklearn.model_selection import train_test_split
import copy
from magdi_data.dataset.abstract_occ_inst_dataset_meta import AbstractOccInstDatasetMeta


class AbstractDataSplitter:
    """
    This abstract class and its subclasses are responsible to create modified copies of
    a dataset metadata file to create different data splits.
    The class contains multiple functions for multiple types or methods of data
    splitting.
    """

    def load_dataset_meta_file(
        self,
    ) -> AbstractOccInstDatasetMeta:
        """
        Load an instance of AbstractOccInstDatasetMeta from a source.
        Must be implemented by subclasses.

        Returns:
            Instance of AbstractOccInstDatasetMeta
        """

        raise NotImplementedError("This method is not implemented.")

    def data_split_train_val(
        self,
        val_size=0.2,
        seed=0,
        result_dataset_meta_path: str | None = None,
    ) -> AbstractOccInstDatasetMeta:
        dataset_meta: AbstractOccInstDatasetMeta = self.load_dataset_meta_file()

        split_meta: AbstractOccInstDatasetMeta = self.create_dataset_meta_train_val(
            dataset_meta, val_size=val_size, random_seed=seed
        )

        if result_dataset_meta_path is not None:
            os.makedirs(os.path.dirname(result_dataset_meta_path), exist_ok=True)
            with open(
                result_dataset_meta_path, mode="w", encoding="utf-8"
            ) as json_file:
                json_file.write(split_meta.model_dump_json(indent=4))

        return split_meta

    def create_dataset_meta_train_val(
        self, dataset_meta: AbstractOccInstDatasetMeta, val_size=0.2, random_seed=0
    ) -> AbstractOccInstDatasetMeta:
        """
        Make a deep copy of the given AbstractOccInstDatasetMeta to create a new one
        that contains training and validation subsets made of the original training
        subset of data.
        Args:
            dataset_meta: any valid instance of AbstractOccInstDatasetMeta
            val_size: validation split ratio (e.g. 0.2 splits training into 20%
            validation and 80% training data)
            random_seed: random state for the data splitting

        Returns:
            Instance of AbstractOccInstDatasetMeta
        """

        if dataset_meta.validation is not None and len(dataset_meta.validation) != 0:
            raise ValueError(
                'Splitting not possible, because the "validation" split is not empty.'
            )

        x_y_train, x_y_val = train_test_split(
            dataset_meta.training, test_size=val_size, random_state=random_seed
        )
        new_dataset_meta = copy.deepcopy(dataset_meta)
        new_dataset_meta.training = x_y_train
        new_dataset_meta.validation = x_y_val
        new_dataset_meta.update_counters()

        return new_dataset_meta

    @staticmethod
    def validate_dataset_meta_path(
        dataset_path: str, custom_dataset_meta_path: str | None = None
    ) -> str:
        if custom_dataset_meta_path is None:
            return os.path.join(dataset_path, "dataset_meta.json")
        return custom_dataset_meta_path
