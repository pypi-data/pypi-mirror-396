# MAGDI Data
This python package named ``magdi_data is`` responsible for data loading to be used for AI training. 
It also contains the definition of a specific dataset structure.

## dataset_meta.json

The dataset_meta.json describes a dataset in the Occurrence Instance Format.
Its properties have to follow a strict format to be readable by humans and machines.

### Terms

#### Occurrence

- An occurrence is a real scanned object. It can have one or more instances (replicates or measurements).

#### Instance

- An instance is a digitalized object.

### Contents

| property                   | description                                                                                                                                                                                                                                                                                                                                      | json type        | example                                                                                                                                               |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| name                       | Name of the dataset.                                                                                                                                                                                                                                                                                                                             | string           | Maize                                                                                                                                                 |
| entity                     | Type of real-world object the dataset pertains.                                                                                                                                                                                                                                                                                                  | string           | maize                                                                                                                                                 |
| release                    | Version of release.                                                                                                                                                                                                                                                                                                                              | string           | 2025.07.02                                                                                                                                            |
| description                | Short description of the dataset.                                                                                                                                                                                                                                                                                                                | string           | NMR dataset with all maize samples. Test set dispersed among sets 7,8, 10, 11, tree set7 samples discarded.                                           |
| reference                  | Description or URL where the data was published.                                                                                                                                                                                                                                                                                                 | string           | Leibniz Institute of Plant Genetics and Crop Plant Research (IPK)                                                                                     |
| license                    | Name which license is used for this dataset.                                                                                                                                                                                                                                                                                                     | string           | IPK proprietary                                                                                                                                       |
| tags                       | List of modalities to describe this dataset. On Hugging Face an overview of exsisting modalities can be found: https://huggingface.co/datasets                                                                                                                                                                                                   | array of string  | ["MRI","3D","Image"]                                                                                                                                  |
| task_categories            | List of Machine Learning tasks for which the dataset is intended. Hugging Face gives an overview of possible tasks: https://huggingface.co/tasks                                                                                                                                                                                                 | array of string  | ["image-segmentation"]                                                                                                                                |
| labels                     | OPTIONAL (Needed if labeled data exists). Class label mapping made of key value pairs. Keys must be ascending positive integers starting from zero and are formatted as strings.<br/>They cannot have gaps. If a key has not a value, the value must be set as empty string e.g. "1": "".                                                        | object           | {<br/>"0": "background",<br/>"1": "embryo"<br/>"2":"endosperm",<br/>"3":"aleuron"}                                                                    |
| image_format               | File ending of the image files.                                                                                                                                                                                                                                                                                                                  | string           | .nii.gz                                                                                                                                               |
| annotation_format          | OPTIONAL (Needed if labeled data exists). File ending of the annotation files.                                                                                                                                                                                                                                                                   | string           | .nii.gz                                                                                                                                               |
| num_instances_total        | Total number of instances.                                                                                                                                                                                                                                                                                                                       | integer          | 4                                                                                                                                                     |
| num_instances_training     | Number of instances of the training split.                                                                                                                                                                                                                                                                                                       | integer          | 2                                                                                                                                                     |
| num_instances_test         | OPTIONAL (Needed if test split exists). Number of instances of the test split.                                                                                                                                                                                                                                                                   | integer          | 2                                                                                                                                                     |
| num_instances_validation   | OPTIONAL (Needed if validation split exists). Number of instances of the validation split.                                                                                                                                                                                                                                                       | integer          | 2                                                                                                                                                     |
| num_occurrences_total      | Total number of occurrences.                                                                                                                                                                                                                                                                                                                     | integer          | 4                                                                                                                                                     |
| num_occurrences_training   | Number of occurrences of the training split.                                                                                                                                                                                                                                                                                                     | integer          | 2                                                                                                                                                     |
| num_occurrences_test       | OPTIONAL (Needed if test split exists). Number of occurrences of the test split.                                                                                                                                                                                                                                                                 | integer          | 2                                                                                                                                                     |
| num_occurrences_validation | OPTIONAL (Needed if validation split exists). Number of occurrences of the validation split.                                                                                                                                                                                                                                                     | integer          | 2                                                                                                                                                     |
| image_data_type            | Defines the type of data compatible to numpy (np.dtype) how the image information is stored.                                                                                                                                                                                                                                                     | string           | int16                                                                                                                                                 |
| annotation_data_type       | OPTIONAL (Needed if labeled data exists). Defines the type of data compatible to numpy (np.dtype) how the annotation information is stored.                                                                                                                                                                                                      | string           | uint8                                                                                                                                                 |
| value_channels             | Number of channels how the image information is stored, e.g. 1 for MRI, 3 for RGB images.                                                                                                                                                                                                                                                        | integer          | 1                                                                                                                                                     |
| dimensions_max             | Dimensions of the largest image.                                                                                                                                                                                                                                                                                                                 | array of integer | [96, 128, 150]                                                                                                                                        |
| dimensions_min             | Dimensions of the smallest image. Must have the same shape as dimensionsMax.                                                                                                                                                                                                                                                                     | array of integer | [41, 64, 78]                                                                                                                                          |
| dimensions_avg             | Average of the dimensions over all images. Must have the same shape as dimensionsMax.                                                                                                                                                                                                                                                            | array of number  | [57.49618320610687, 92.01526717557252, 115.6030534351145]                                                                                             |
| resolution_unit            | Unit for resolution_voxel_size.                                                                                                                                                                                                                                                                                                                  | string           | mm                                                                                                                                                    |
| resolution_voxel_size      | Size of a voxel relative to the real world for each image dimension.                                                                                                                                                                                                                                                                             | array of number  | [0.1,0.1,0.1]                                                                                                                                         |
| training                   | Training split.<br/>Contains one json object for each instance of the training split.<br/>Each json object holds the path to the image file.<br/>For annotated data the path to the annotation file is set. "image" key is mandatory.<br/>"annotations" key is only mandatory for annotated data.                                                | array of object  | [<br/>{<br/>"annotations": "occurrence-0000/instance-0000/annotations.nii.gz", <br/>"image": "occurrence-0001/instance-0000/image.nii.gz"<br/>}<br/>] |
| validation                 | OPTIONAL (Needed if validation split exists). Validation split.<br/>Contains one json object for each instance of the validation split.<br/>Each json object holds the path to the image file.<br/>For annotated data the path to the annotation file is set.<br/>"image" key is mandatory. "annotations" key is only needed for annotated data. | array of object  | [<br/>{<br/>"annotations": "occurrence-0002/instance-0000/annotations.nii.gz", <br/>"image": "occurrence-0003/instance-0000/image.nii.gz"<br/>}<br/>] |
| test                       | OPTIONAL (Needed if test split exists). Test split.<br/>Contains one json object for each instance of the test split.<br/>Each json object holds the path to the image file.<br/>For annotated data the path to the annotation file is set.<br/>"image" key is mandatory. "annotations" key is only needed for annotated data.                   | array of object  | [<br/>{<br/>"annotations": "occurrence-0004/instance-0000/annotations.nii.gz", <br/>"image": "occurrence-0005/instance-0000/image.nii.gz"<br/>}<br/>] |
| data_references            | Holds key-value pairs to map directory or files of this dataset to a reference.<br/>It is not used for AI training. It is necessary to associate digital instances with its origins of creation.<br/>E.g. Occurrence is mapped to the ID of a real world object.                                                                                 | object           | {<br/>"occurrence-0000/instance-0000/annotations.nii.gz": "example1",<br/>"occurrence-0001/instance-0000/annotations.nii.gz": "example3"<br/>}        |

### Example:

````json

{
  "name": "Maize Example",
  "entity": "maize",
  "release": "2025.07.02",
  "description": "NMR dataset with all maize samples. Test set dispersed among sets 7,8, 10, 11, tree set7 samples discarded.",
  "reference": "Leibniz Institute of Plant Genetics and Crop Plant Research (IPK) ",
  "license": "IPK proprietary",
  "tags": [
    "MRI",
    "3D",
    "Image"
  ],
  "task_categories": [
    "image-segmentation"
  ],
  "labels": {
    "0":"background",
    "1":"embryo",
    "2":"endosperm",
    "3":"aleuron"
  },
  "image_format": ".nii.gz",
  "annotation_format": ".nii.gz",
  "num_instances_total": 6,
  "num_instances_training": 2,
  "num_instances_test": 2,
  "num_instances_validation": 2,
  "num_occurrences_total": 6,
  "num_occurrences_training": 2,
  "num_occurrences_test": 2,
  "num_occurrences_validation": 2,
  "image_data_type": "int16",
  "annotation_data_type": "uint8",
  "value_channels": 1,
  "dimensions_max": [
    96,
    128,
    150
  ],
  "dimensions_min": [
    41,
    64,
    78
  ],
  "dimensions_avg": [
    57.49618320610687,
    92.01526717557252,
    115.6030534351145
  ],
  "resolution_unit": "mm",
  "resolution_voxel_size": [
    0.1,
    0.1,
    0.1
  ],
  "training": [
    {
      "annotations": "occurrence-0000/instance-0000/annotations.nii.gz",
      "image": "occurrence-0000/instance-0000/image.nii.gz"
    },
    {
      "annotations": "occurrence-0001/instance-0000/annotations.nii.gz",
      "image": "occurrence-0001/instance-0000/image.nii.gz"
    }
  ],
  "validation": [
    {
      "annotations": "occurrence-0002/instance-0000/annotations.nii.gz",
      "image": "occurrence-0002/instance-0000/image.nii.gz"
    },
    {
      "annotations": "occurrence-0003/instance-0000/annotations.nii.gz",
      "image": "occurrence-0003/instance-0000/image.nii.gz"
    }
  ],
  "test": [
    {
      "annotations": "occurrence-0004/instance-0000/annotations.nii.gz",
      "image": "occurrence-0004/instance-0000/image.nii.gz"
    },
    {
      "annotations": "occurrence-0005/instance-0000/annotations.nii.gz",
      "image": "occurrence-0005/instance-0000/image.nii.gz"
    }
  ],
  "data_references": {
    "occurrence-0000/instance-0000/image.nii.gz": "example1",
    "occurrence-0001/instance-0000/image.nii.gz": "example2",
    "occurrence-0002/instance-0000/image.nii.gz": "example3",
    "occurrence-0003/instance-0000/image.nii.gz": "example4",
    "occurrence-0004/instance-0000/image.nii.gz": "example3",
    "occurrence-0005/instance-0000/image.nii.gz": "example4"
  }
}
````