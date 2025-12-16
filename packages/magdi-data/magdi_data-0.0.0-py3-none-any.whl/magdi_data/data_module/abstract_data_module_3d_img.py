"""
Contains the implementation of a Lighting Data module to provide data for 3D
image segmentation.
"""

import os
from typing import Callable, Optional, Dict
import os.path
import lightning as L
from monai.data import DataLoader, list_data_collate
from monai.transforms import (
    Compose,
    RandSpatialCropSamplesd,
    Transform,
)
from torch.utils.data import Dataset
from typing_extensions import override
from magdi_data.dataset.nifti_occ_inst_dataset_meta import NiftiOccInstDatasetMeta
from transformers import ImageProcessingMixin


def default_augmentations() -> Transform | None:
    return None


class AbstractDataModule3dImgSeg(L.LightningDataModule):

    def __init__(
        self,
        roi_size,
        batch_size: int,
        num_workers: int,
        persistent_workers: bool,
        pin_memory: bool,
        **kwargs,
    ):

        super().__init__()
        self.batch_size = batch_size
        self.roi_size = roi_size

        self.num_workers = num_workers
        self.persistent_workers = persistent_workers
        self.pin_memory = pin_memory

        # TODO: Problem: do not cache augmentations and RandSpatialCropSamplesd
        self.cache_rate: float = 0.0  # 1.0
        self.cache_num: int = 0  # sys.maxsize

        self.train_dataset: Dataset | None = None
        self.val_dataset: Dataset | None = None
        self.test_dataset: Dataset | None = None

        self.augmentation_hook: Callable[[], Transform | None] = default_augmentations

        self.dataset_meta: NiftiOccInstDatasetMeta = None  # type: ignore

        # Specific processor implementation for a Hugging Face model
        self.hf_processor: ImageProcessingMixin = None  # type: ignore

    def get_dataset_meta_path(self, dataset_path, custom_dataset_meta_path) -> str:
        if custom_dataset_meta_path is None:
            return os.path.join(dataset_path, "dataset_meta.json")
        else:
            return custom_dataset_meta_path

    def get_labels(self) -> Optional[Dict[str, str]]:
        if self.dataset_meta is None:
            raise ValueError("self.dataset_meta is None")
        return self.dataset_meta.labels

    def get_test_transforms(self):
        return self.hf_processor

    def get_val_transforms(self):
        return self.hf_processor

    def get_train_transforms(self):

        train_transforms = [
            self.hf_processor,
            RandSpatialCropSamplesd(
                keys=["image", "annotations"],
                roi_size=self.roi_size,
                num_samples=1,
            ),
        ]

        augmentation_transforms = self.augmentation_hook()
        if augmentation_transforms is not None:
            train_transforms.append(augmentation_transforms)  # type: ignore

        return Compose(train_transforms)

    @override
    def setup(self, stage: str):
        if self.dataset_meta is None:
            raise ValueError(
                "self.dataset_meta is not allowed to be None."
                "Set it before calling setup()"
            )
        if self.hf_processor is None:
            raise ValueError(
                "self.hf_processor is not allowed to be None."
                "Set a Hugging Face processor before calling setup()."
            )

    @override
    def train_dataloader(self) -> DataLoader:
        return DataLoader(
            self.train_dataset,  # type: ignore
            shuffle=True,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            persistent_workers=self.persistent_workers,
            pin_memory=self.pin_memory,
            collate_fn=list_data_collate,
        )

    @override
    def val_dataloader(self) -> DataLoader:
        return DataLoader(
            self.val_dataset,  # type: ignore
            shuffle=False,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            persistent_workers=self.persistent_workers,
            pin_memory=self.pin_memory,
            collate_fn=list_data_collate,
        )

    @override
    def test_dataloader(self) -> DataLoader:
        return DataLoader(
            self.test_dataset,  # type: ignore
            shuffle=False,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            persistent_workers=self.persistent_workers,
            pin_memory=self.pin_memory,
            collate_fn=list_data_collate,
        )
