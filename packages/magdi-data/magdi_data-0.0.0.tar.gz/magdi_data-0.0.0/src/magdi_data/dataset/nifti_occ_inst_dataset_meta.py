from typing import List, Dict
import copy
import numpy as np


from magdi_data.dataset.abstract_occ_inst_dataset_meta import AbstractOccInstDatasetMeta
import nibabel as nib


class NiftiOccInstDatasetMeta(AbstractOccInstDatasetMeta):

    def update_and_validate_based_on_nifti_headers(self, dataset_path):
        instance_list: List[Dict[str, str]] = (
            self.get_data_split_paths_and_nifti_headers(dataset_path, "training")
        )
        instance_list_test: List[Dict[str, str]] = (
            self.get_data_split_paths_and_nifti_headers(dataset_path, "test")
        )
        instance_list_validation: List[Dict[str, str]] = (
            self.get_data_split_paths_and_nifti_headers(dataset_path, "validation")
        )
        instance_list += instance_list_test
        instance_list += instance_list_validation

        if len(instance_list) == 0:
            raise ValueError(
                "Tried to update and validate fields based on Nifti "
                "headers but no instances have been found."
            )

        self._validate_image_dtype(instance_list)
        self._validate_annotation_dtype(instance_list)
        self._update_and_validate_dimensions(instance_list)

    def _validate_annotation_dtype(self, instance_list: List[Dict[str, str | dict]]):
        img_dtype_dict: dict = {}

        for instance_dict in instance_list:
            if "annotations_header" in instance_dict:
                header: dict = instance_dict["annotations_header"]  # type: ignore
                dtype: str = str(header["datatype"].dtype)

                img_dtype_dict[instance_dict["image"]] = dtype

        img_dtype_list = list(img_dtype_dict.values())
        if len(img_dtype_list) == 0:
            return
        dtype0 = img_dtype_list[0]
        for path, dtype in img_dtype_dict.items():
            if dtype0 != dtype:
                raise ValueError(
                    f"Image {path} has a different datatype ({dtype}) "
                    f"than the first instance ({dtype0})."
                )

        if dtype0 != self.image_data_type:
            raise ValueError(
                f"A different image_data_type ({self.image_data_type}) "
                f"is set than the first instance has ({dtype0})."
            )

    def _validate_image_dtype(self, instance_list: List[Dict[str, str | dict]]):
        img_dtype_dict: dict = {}

        for instance_dict in instance_list:

            header: dict = instance_dict["image_header"]  # type: ignore
            dtype: str = str(header["datatype"].dtype)

            img_dtype_dict[instance_dict["image"]] = dtype

        dtype0 = list(img_dtype_dict.values())[0]
        for path, dtype in img_dtype_dict.items():
            if dtype0 != dtype:
                raise ValueError(
                    f"Image {path} has a different datatype ({dtype}) "
                    f"than the first instance ({dtype0})."
                )

        if dtype0 != self.image_data_type:
            raise ValueError(
                f"A different image_data_type ({self.image_data_type}) "
                f"is set than the first instance has ({dtype0})."
            )

    def _update_and_validate_dimensions(
        self, instance_list: List[Dict[str, str | dict]]
    ):
        """
        Update dimension metadata fields based on the Nifti header of each data
        instance.
        Validate if image dimensions fit to annotation dimensions if annotation
        dimensions exist.
        """

        img_dimensions_list: List[List[int]] = []

        for instance_dict in instance_list:

            img_header: dict = instance_dict["image_header"]  # type: ignore

            img_3d_dimensions = img_header["dim"][1:4]

            if "annotations_header" in instance_dict:
                ann_header: dict = instance_dict["annotations_header"]  # type: ignore

                ann_3d_dimensions = ann_header["dim"][1:4]

                if not np.array_equal(img_3d_dimensions, ann_3d_dimensions):
                    raise ValueError(
                        "Annotation dimensions do not fit with the image dimensions "
                        f"for {instance_dict['image']} and "
                        f"{instance_dict['annotations']}."
                    )

            img_dimensions_list.append(img_3d_dimensions)

        if len(img_dimensions_list) == 0:
            return

        old_dimensions_max = self.dimensions_max
        old_dimensions_min = self.dimensions_min
        old_dimensions_avg = self.dimensions_avg

        (self.dimensions_max, self.dimensions_min, self.dimensions_avg) = (
            self._get_shape_statistics(img_dimensions_list)
        )
        if not np.array_equal(old_dimensions_max, self.dimensions_max):
            print("updated dimensions_max: ", self.dimensions_max)
        if not np.array_equal(old_dimensions_min, self.dimensions_min):
            print("updated dimensions_min: ", self.dimensions_min)
        if not np.array_equal(old_dimensions_avg, self.dimensions_avg):
            print("updated dimensions_avg: ", self.dimensions_avg)

    def get_data_split_paths_and_nifti_headers(
        self, dataset_path: str, split: str = "training"
    ) -> List[Dict[str, str | dict]]:
        """
        Extends method get_data_split_paths().
        Get nifti headers directly from the nifti files.
        Make a deep copy of the path dictionaries of the data instances.
        Add the nifti headers to the dictionaries of each instance.

        It is an expensive operation, because each nifti file is loaded to extract the
        header. This way, a lot of metadata is read for further use.
        """

        file_path_dict_list: List[Dict[str, str | dict]] = copy.deepcopy(
            self.get_data_split_paths(dataset_path, split)  # type: ignore
        )

        for file_path_dict in file_path_dict_list:
            if "image" in file_path_dict:
                nifti_header = dict(
                    nib.load(file_path_dict["image"]).header  # type: ignore
                )
            else:
                raise FileNotFoundError(
                    "Image dimensions could not be read, "
                    "because no file path for key 'image' is set."
                )

            file_path_dict["image_header"] = nifti_header

            if "annotations" in file_path_dict:
                ann_header = dict(
                    nib.load(file_path_dict["annotations"]).header  # type: ignore
                )
                file_path_dict["annotations_header"] = ann_header

        return file_path_dict_list
