"""
Contains a subclass of AbstractDataSplitter to split a dataset whose metadata file is
located in a Minio bucket.
"""

from typing_extensions import override
from anhaltai_commons_minio.io_utils import download_json
from minio import Minio
from pydantic_core import from_json
from magdi_data.data_splitting.abstract_data_splitter import AbstractDataSplitter
from magdi_data.dataset.abstract_occ_inst_dataset_meta import AbstractOccInstDatasetMeta


class MinioDataSplitter(AbstractDataSplitter):

    def __init__(
        self,
        minio_dataset_path: str,
        minio_client: Minio,
        minio_bucket_name: str,
        custom_dataset_meta_path: str | None = None,
    ):
        self.minio_client = minio_client
        self.minio_bucket_name = minio_bucket_name
        self.dataset_path = minio_dataset_path
        self.dataset_meta_path = self.validate_dataset_meta_path(
            self.dataset_path, custom_dataset_meta_path
        )

    @override
    def load_dataset_meta_file(self):
        """
        Read the addressed dataset meta JSON file on minio to create an instance of
        AbstractOccInstDatasetMeta.

        Returns:
            Instance of AbstractOccInstDatasetMeta
        """

        dataset_meta_json_str = download_json(
            minio_client=self.minio_client,
            bucket_name=self.minio_bucket_name,
            object_name=self.dataset_meta_path,
        )
        return AbstractOccInstDatasetMeta.model_validate(
            from_json(dataset_meta_json_str)
        )
