import os
import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional
import copy


class AbstractOccInstDatasetMeta(BaseModel):
    """
    Abstract model for the metadata file of a dataset that has the Occurrence Instance
    Dataset Structure.
    """

    name: str
    entity: str
    release: str
    description: str
    reference: str
    license: str
    tags: List[str]
    task_categories: List[str]
    labels: Optional[Dict[str, str]] = Field(default=None)
    image_format: str
    annotation_format: Optional[str] = Field(default=None)
    num_instances_total: int
    num_instances_training: int
    num_instances_test: Optional[int] = Field(default=None)
    num_instances_validation: Optional[int] = Field(default=None)

    num_occurrences_total: int
    num_occurrences_training: int
    num_occurrences_test: Optional[int] = Field(default=None)
    num_occurrences_validation: Optional[int] = Field(default=None)

    image_data_type: str
    annotation_data_type: Optional[str] = Field(default=None)
    value_channels: int
    dimensions_max: List[int]
    dimensions_min: List[int]
    dimensions_avg: List[float]
    resolution_unit: str
    resolution_voxel_size: List[float]
    training: List[Dict[str, str]]
    test: Optional[List[Dict[str, str]]] = Field(default=None)
    validation: Optional[List[Dict[str, str]]] = Field(default=None)
    data_references: Optional[Dict[str, str]] = Field(default=None)

    @field_validator("image_data_type", "annotation_data_type")
    def validate_np_dtype(cls, v):
        assert isinstance(np.dtype(v), np.dtype)
        return v

    @model_validator(mode="after")
    def validate_fields_based_on_data_split(self):
        """
        Update metadata fields based on the training, validation, and test split
        """
        self.update_counters()
        return self

    @staticmethod
    def count_occurrences_and_instances(data, key="image"):
        occurrence_dict: dict = {}

        for item in data:
            image_path = item[key]
            parts = image_path.split("/")
            occurrence = parts[0]  # 'occurrence-xxxx'
            instance = parts[1]  # 'instance-xxxx'

            if occurrence not in occurrence_dict:
                occurrence_dict[occurrence] = set()
            occurrence_dict[occurrence].add(instance)

        total_occurrences = len(occurrence_dict)
        total_instances = sum(len(instances) for instances in occurrence_dict.values())

        return total_occurrences, total_instances

    def update_counters(self):
        self.num_occurrences_training, self.num_instances_training = (
            self.count_occurrences_and_instances(self.training)
        )
        self.num_occurrences_total = self.num_occurrences_training
        self.num_instances_total = self.num_instances_training
        if self.test is not None:
            self.num_occurrences_test, self.num_instances_test = (
                self.count_occurrences_and_instances(self.test)
            )
            self.num_occurrences_total += self.num_occurrences_test
            self.num_instances_total += self.num_instances_test
        else:
            self.num_occurrences_test = None
            self.num_instances_test = None

        if self.validation is not None:
            self.num_occurrences_validation, self.num_instances_validation = (
                self.count_occurrences_and_instances(self.validation)
            )
            self.num_occurrences_total += self.num_occurrences_validation
            self.num_instances_total += self.num_instances_validation
        else:
            self.num_occurrences_validation = None
            self.num_instances_validation = None

    def update_dimensions(self, dataset_path: str):
        shapes = self.get_dimensions_in_split(dataset_path, "training")

        if self.test is not None:
            shapes += self.get_dimensions_in_split(dataset_path, "test")
        if self.validation is not None:
            shapes += self.get_dimensions_in_split(dataset_path, "validation")

        if len(shapes) == 0:
            return

        (self.dimensions_max, self.dimensions_min, self.dimensions_avg) = (
            self._get_shape_statistics(shapes)
        )

    @staticmethod
    def _get_shape_statistics(shapes):
        np_shapes = np.array(shapes)
        min_shape = np_shapes.min(axis=0)
        max_shape = np_shapes.max(axis=0)
        mean_shape = np_shapes.mean(axis=0)
        return max_shape, min_shape, mean_shape

    def get_dimensions_in_split(
        self, dataset_path: str, split: str = "training"
    ) -> List[tuple[int]]:
        return []

    def get_annotations_dtype(self) -> np.dtype:
        return np.dtype(self.annotation_data_type)

    def get_image_dtype(self) -> np.dtype:
        return np.dtype(self.image_data_type)

    def get_data_split_paths(
        self, dataset_path: str, split: str = "training"
    ) -> List[Dict[str, str]]:
        return self.concat_paths(dataset_path, split)

    def concat_paths(
        self, dataset_path: str, split: str = "training"
    ) -> List[Dict[str, str]]:
        instance_list = copy.deepcopy(getattr(self, split))
        if instance_list is None:
            return []

        for file_path_dict in instance_list:
            for key in file_path_dict:
                file_path_dict[key] = os.path.join(dataset_path, file_path_dict[key])
        return instance_list
