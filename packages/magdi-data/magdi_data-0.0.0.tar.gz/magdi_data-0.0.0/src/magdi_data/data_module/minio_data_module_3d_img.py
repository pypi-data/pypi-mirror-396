"""
Contains a subclass of AbstractDataModule3dImgSeg to download data from minio.
"""

import os
from anhaltai_commons_minio.io_utils import download_directory
from minio import Minio
from magdi_data.data_module.abstract_data_module_3d_img import (
    AbstractDataModule3dImgSeg,
)
import json
import os.path
from pydantic_core import from_json
from monai.data import CacheDataset
from magdi_data.dataset.nifti_occ_inst_dataset_meta import NiftiOccInstDatasetMeta
from magdi_data.json_helpers import load_from_json_file


class MinioDataModule3DImgSeg(AbstractDataModule3dImgSeg):
    """
    Lighting Data module to provide a 3D image segmentation dataset to train a model.
    """

    def __init__(
        self,
        minio_dataset_path: str,
        minio_client: Minio,
        minio_bucket_name: str,
        roi_size,
        batch_size: int,
        num_workers: int,
        persistent_workers: bool,
        pin_memory: bool,
        custom_dataset_meta_path: str | None = None,
        download_dir: str = "data",
        **kwargs,
    ):

        super().__init__(
            roi_size=roi_size,
            batch_size=batch_size,
            num_workers=num_workers,
            persistent_workers=persistent_workers,
            pin_memory=pin_memory,
            **kwargs,
        )

        self.minio_dataset_path = minio_dataset_path
        self.minio_client = minio_client
        self.minio_bucket_name = minio_bucket_name
        self.download_dir = download_dir
        self.dataset_path = os.path.join(self.download_dir, self.minio_dataset_path)
        self.minio_dataset_downloaded = False
        self.custom_dataset_meta_path = custom_dataset_meta_path

    def prepare_data(self) -> None:
        print("Preparing data")
        if not self.minio_dataset_downloaded:
            download_directory(
                minio_client=self.minio_client,
                bucket_name=self.minio_bucket_name,
                remote_directory=self.minio_dataset_path,
                local_directory=self.download_dir,
                overwrite=False,
            )
            self.minio_dataset_downloaded = True

            dataset_meta_path = self.get_dataset_meta_path(
                self.dataset_path, self.custom_dataset_meta_path
            )
            self.dataset_meta = NiftiOccInstDatasetMeta.model_validate(
                from_json(json.dumps(load_from_json_file(dataset_meta_path)))
            )

    def setup(self, stage: str):
        super().setup(stage=stage)  # important
        if stage == "fit":
            # CacheDataset caches non-random transforms
            training_dataset_paths = self.dataset_meta.get_data_split_paths(
                self.dataset_path, split="training"
            )
            self.train_dataset = CacheDataset(
                data=training_dataset_paths,
                transform=self.get_train_transforms(),
                num_workers=self.num_workers,
                cache_rate=self.cache_rate,
                cache_num=self.cache_num,
            )

            val_dataset_paths = []
            if self.dataset_meta.validation is not None:
                val_dataset_paths = self.dataset_meta.get_data_split_paths(
                    self.dataset_path, split="validation"
                )
            self.val_dataset = CacheDataset(
                data=val_dataset_paths,
                transform=self.get_val_transforms(),
                num_workers=self.num_workers,
                cache_rate=self.cache_rate,
                cache_num=self.cache_num,
            )

        elif stage == "test":
            test_dataset_paths = self.dataset_meta.get_data_split_paths(
                self.dataset_path, split="test"
            )
            self.test_dataset = CacheDataset(
                data=test_dataset_paths,
                transform=self.get_test_transforms(),
                num_workers=self.num_workers,
                cache_rate=self.cache_rate,
                cache_num=self.cache_num,
            )
