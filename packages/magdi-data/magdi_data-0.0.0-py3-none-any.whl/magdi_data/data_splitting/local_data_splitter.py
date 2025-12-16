"""
Contains a subclass of AbstractDataSplitter to split a dataset whose metadata file is
located locally.
"""

from typing_extensions import override
from pydantic_core import from_json
from magdi_data.data_splitting.abstract_data_splitter import AbstractDataSplitter
from magdi_data.dataset.abstract_occ_inst_dataset_meta import AbstractOccInstDatasetMeta


class LocalDataSplitter(AbstractDataSplitter):
    def __init__(
        self,
        local_dataset_path: str,
        custom_dataset_meta_path: str | None = None,
    ):
        self.dataset_path = local_dataset_path
        self.dataset_meta_path = self.validate_dataset_meta_path(
            self.dataset_path, custom_dataset_meta_path
        )

    @override
    def load_dataset_meta_file(self):
        """
        Read the addressed dataset meta JSON file on disk to create an instance of
        AbstractOccInstDatasetMeta.

        Returns:
            Instance of AbstractOccInstDatasetMeta
        """

        with open(self.dataset_meta_path, mode="r", encoding="utf-8") as file:
            json_str_input = file.read()

        return AbstractOccInstDatasetMeta.model_validate(from_json(json_str_input))
