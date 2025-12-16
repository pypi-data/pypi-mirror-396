"""
Contains a subclass of AbstractDataModule3dImgSeg to load data from local.
"""

from magdi_data.data_module.abstract_data_module_3d_img import (
    AbstractDataModule3dImgSeg,
)
import json
from pydantic_core import from_json
from monai.data import CacheDataset
from magdi_data.dataset.nifti_occ_inst_dataset_meta import NiftiOccInstDatasetMeta
from magdi_data.json_helpers import load_from_json_file


class LocalDataModule3DImgSeg(AbstractDataModule3dImgSeg):

    def __init__(
        self,
        dataset_path: str,
        roi_size,
        batch_size: int,
        num_workers: int,
        persistent_workers: bool,
        pin_memory: bool,
        custom_dataset_meta_path: str | None = None,
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

        self.dataset_path = dataset_path
        self.custom_dataset_meta_path = custom_dataset_meta_path

    def prepare_data(self) -> None:
        print("Preparing data")
        dataset_meta_path = self.get_dataset_meta_path(
            self.dataset_path, self.custom_dataset_meta_path
        )
        self.dataset_meta = NiftiOccInstDatasetMeta.model_validate(
            from_json(json.dumps(load_from_json_file(dataset_meta_path)))
        )
        print(self.dataset_meta)

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
