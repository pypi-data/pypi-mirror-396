from pathlib import Path
from typing import Dict, List, Literal, Optional, TypedDict, Union


class MLConfigData(TypedDict, total=False):
    """Configuration for traditional ML tasks.

    Args:
        path (Path): The path to the dataset.
        goal (float): The goal value for the model.
        target (str): The target variable name in the dataset.
        domain (str): The business domain (e.g., "finance", "real estate").
        domain_context (str, optional): Additional context for the domain.
        task_type (str): Type of ML task (e.g., "tabular_classification", "tabular_regression").
        classification (bool, optional): Whether the task is a classification task.
        metrics (str, optional): The metrics to be used for evaluation.
        selected_metric (str, optional): The primary metric to optimize.
        ignored_features (List[str], optional): Features to ignore during training.
        name (str, optional): The name of the task.
        date_feature (List[str], optional): The date feature to be used for training.
        need_time (bool, optional): Whether need Hour, Minute, Second.
        ordinal_features (List[Dict[str, List[str]]], optional): The ordinal features to be used for training.
        time_series (bool, optional): Whether the task is a time series task.
        threshold (Dict[str, int], optional): The threshold to be used for training.
        delimiter (str, optional): The delimiter to be used for loading csv data.
    """

    task_type: str
    path: Union[str, Path]
    goal: float
    target: str
    domain: str
    domain_context: Optional[str]
    classification: bool
    metrics: str
    selected_metric: str
    ignored_features: Optional[List[str]]
    name: Optional[str]
    date_feature: Optional[str]
    need_time: Optional[bool]
    ordinal_features: Optional[List[Dict[str, List[str]]]]
    time_series: Optional[bool]
    threshold: Optional[Dict[str, int]]
    delimiter: Optional[str]


class BaseConfig(TypedDict, total=False):
    """Base configuration shared across all DL tasks.

    Attributes:
        path: Main data directory or file path
        batch_size: Training batch size
        model: Model architecture identifier
        valid_pct: Percentage of data to reserve for validation set
        device: Computing device ('cuda' or 'cpu')
        num_workers: Number of data loading workers
    """

    path: Union[str, Path]
    batch_size: Optional[int]
    model: Optional[str]
    valid_pct: Optional[float]

    device: Optional[str]
    num_workers: Optional[int]


class SingleLabelConfig(BaseConfig):
    """Configuration for single label classification tasks.

    Attributes:
        train_folder: Name of the folder containing the training images
        valid_folder: Name of the folder containing the validation images
    """

    task_type: str
    train_folder: Optional[str]
    valid_folder: Optional[str]


class VisionCSVConfig(BaseConfig):
    """Configuration for computer vision tasks with labels in CSV file.

    Attributes:
        folder: Name of the folder containing the images
        csv_file: Name of the CSV file containing the labels
        image_col: Column name for image paths/names in label file
        label_col: Column name for labels in label file
        valid_col: Column name for validation set in label file
        delimiter: Delimiter for the CSV file
        label_delim: Delimiter for the label column
    """

    task_type: str
    folder: Optional[str]
    csv_file: Optional[str]
    image_col: Optional[str]
    label_col: Optional[str]
    valid_col: Optional[str]
    delimiter: Optional[str]
    label_delim: Optional[str]


class VisionFuncConfig(BaseConfig):
    """Configuration for computer vision tasks labeled by function.
    label_func: Function to label the data
    """

    task_type: str
    label_func: str


class VisionReConfig(BaseConfig):
    """Configuration for computer vision tasks labeled by regular expression.
    pat: Regular expression pattern for image paths
    """

    task_type: str
    pat: str


class VisionMultiLabelConfig(BaseConfig):
    """Configuration for computer vision tasks with multiple labels.
    folder: Name of the folder containing the images
    csv_file: Name of the CSV file containing the labels
    image_col: Column name for image paths/names in label file
    label_col: Column name for labels in label file
    valid_col: Column name for validation set in label file
    delimiter: Delimiter for the CSV file
    label_delim: Delimiter for the label column
    """

    task_type: str
    folder: Optional[str]
    csv_file: Optional[str]
    image_col: Optional[str]
    label_col: Optional[str]
    valid_col: Optional[str]
    delimiter: Optional[str]
    label_delim: Optional[str]


class NLPConfig(BaseConfig):
    """Configuration for Natural Language Processing tasks.

    Extends BaseConfig with NLP-specific settings.

    Attributes:
        problem_type: Type of NLP task:
            - classification: Text classification (sentiment, topic, etc.)
            - sequence_labeling: Token-level predictions (NER, POS tagging)
            - sequence_to_sequence: Text-to-text generation (translation, summarization)
            - generation: Free-form text generation (completion, story writing)
        text_column: Column name containing the text data
        label_column: Column name containing labels (for classification/sequence tasks)
        language: Language code of the text (e.g., 'en', 'zh')
        max_length: Maximum sequence length for tokenization
        tokenizer: Specific tokenizer to use for text processing
        text_file_pattern: Pattern to locate text files if stored separately
    """

    task_type: str
    problem_type: Literal["classification", "sequence_labeling", "sequence_to_sequence", "generation"]
    text_column: str
    label_column: Optional[str]
    language: str
    max_length: int
    tokenizer: Optional[str]
    text_file_pattern: Optional[str]


class CollaborativeConfig(BaseConfig):
    """Configuration for collaborative filtering tasks.

    Extends BaseConfig with recommendation system-specific settings.
    Based on fastai's collaborative filtering implementation.

    Attributes:
    user_name: Column name for user identifiers
    item_name: Column name for item identifiers
    rating_name: Column name for user-item interaction scores
    y_range_min: Minimum rating value
    y_range_max: Maximum rating value
    """

    task_type: str
    user_name: str
    item_name: str
    rating_name: str
    y_range_min: float
    y_range_max: float


# Union type for all possible configurations
DLConfigData = Union[
    VisionCSVConfig, VisionFuncConfig, VisionReConfig, VisionMultiLabelConfig, NLPConfig, CollaborativeConfig
]


# Use Union type to support both ML and DL configs
ConfigData = Union[MLConfigData, DLConfigData]
