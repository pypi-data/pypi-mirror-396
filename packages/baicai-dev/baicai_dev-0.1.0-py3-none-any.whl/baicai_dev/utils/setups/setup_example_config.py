import torch
from fastai.vision.all import URLs, untar_data

from baicai_dev.utils.constants import CLASSIFICATION_METRICS, REGRESSION_METRICS
from baicai_dev.utils.data import TaskType, get_example_data_path

# Sample data paths
iris_data_path = get_example_data_path("iris")
titanic_data_path = get_example_data_path("titanic")
house_data_path = get_example_data_path("house")
garment_data_path = get_example_data_path("garment")

# Dictionary storing configuration data for different use cases
iris_config_data = {
    "path": iris_data_path,
    "delimiter": ",",
    "goal": 0.9,
    "target": "iris",
    "domain": "iris flower classification",
    "domain_context": "iris flowers",
    "classification": True,
    "metrics": CLASSIFICATION_METRICS,
    "selected_metric": "accuracy",
    "ignored_features": [],
    "name": "iris",
    "date_feature": "",
    "need_time": False,
    "ordinal_features": [],
    "time_series": False,
    "threshold": {},
    "requirements": "所有特征做平方处理",
}

titanic_config_data = {
    "path": titanic_data_path,
    "delimiter": ",",
    "goal": 0.9,
    "target": "survived",
    "domain": "titanic survival prediction",
    "domain_context": "titanic tragedy",
    "classification": True,
    "metrics": CLASSIFICATION_METRICS,
    "selected_metric": "accuracy",
    "ignored_features": ["deck", "alive"],
    "name": "titanic",
    "date_feature": "",
    "need_time": False,
    "ordinal_features": [],
    "time_series": False,
    "threshold": {},
    "requirements": "",
}

house_config_data = {
    "path": house_data_path,
    "delimiter": ",",
    "goal": 0.9,
    "target": "MedHouseVal",
    "domain": "house price prediction",
    "domain_context": "house prices",
    "classification": False,
    "metrics": REGRESSION_METRICS,
    "selected_metric": "r2",
    "ignored_features": [],
    "name": "house",
    "date_feature": "",
    "need_time": False,
    "ordinal_features": [],
    "time_series": False,
    "threshold": {},
    "requirements": "",
}

garment_config_data = {
    "path": garment_data_path,
    "delimiter": ",",
    "goal": 0.9,
    "target": "actual_productivity",
    "domain": "garment productivity prediction",
    "domain_context": "garment productivity",
    "classification": False,
    "metrics": REGRESSION_METRICS,
    "selected_metric": "r2",
    "ignored_features": [],
    "name": "garment",
    "date_feature": "date",
    "need_time": False,
    "ordinal_features": [
        {"quarter": ["Quarter1", "Quarter2", "Quarter3", "Quarter4", "Quarter5"]},
        {"day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
    ],
    "time_series": True,
    "threshold": {"year": 2015, "month": 9, "day": 1},
}

bears_config = {
    "path": get_example_data_path("bears", tabular=False),
    "batch_size": 4,
    "model": "resnet18",
    "valid_pct": 0.2,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "num_workers": 4,
    "train_folder": None,
    "valid_folder": None,
    "label_func": "return x.parent.name",
    "pat": r"([^_]+)_",
    "name": "bears",
    "size": 24,
}

bears_single_label_config = {
    **bears_config,
    "task_type": TaskType.VISION_SINGLE_LABEL.value,
}

bears_func_config = {
    **bears_config,
    "task_type": TaskType.VISION_FUNC.value,
}

bears_re_config = {
    **bears_config,
    "task_type": TaskType.VISION_RE.value,
}

mnist_config = {
    "path": str(untar_data(URLs.MNIST_TINY)),
    "batch_size": 4,
    "model": "resnet18",
    "valid_pct": 0.2,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "num_workers": 4,
    "train_folder": None,
    "valid_folder": None,
    "folder": None,
    "csv_file": "'labels.csv'",
    "image_col": "'name'",
    "label_col": "'label'",
    "valid_col": None,
    "delimiter": None,
    "label_delim": None,
    "name": "mnist",
    "size": 24,
}

mnist_csv_config = {
    **mnist_config,
    "task_type": TaskType.VISION_CSV.value,
}

multi_label_config = {
    "path": str(untar_data(URLs.PASCAL_2007)),
    "batch_size": 4,
    "model": "resnet18",
    "valid_pct": 0.2,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "num_workers": 4,
    "folder": "'train'",
    "csv_file": "'train.csv'",
    "image_col": "'fname'",
    "label_col": "'labels'",
    "valid_col": "'is_valid'",
    "delimiter": None,
    "label_delim": "' '",
    "task_type": TaskType.VISION_MULTI_LABEL.value,
    "name": "pascal_2007",
    "size": 24,
}

collab_config = {
    "path": str(untar_data(URLs.ML_SAMPLE) / "ratings.csv"),
    "user_name": "'userId'",
    "item_name": "'movieId'",
    "rating_name": "'rating'",
    "y_range_min": 0.5,
    "y_range_max": 5.5,
    "valid_pct": 0.2,
    "task_type": TaskType.COLLABORATIVE.value,
}

sentiment_inference_config = {
    "model": None,
    "task_type": TaskType.NLP_SENTIMENT_INFERENCE.value,
    "input": "太棒了",
}

ner_inference_config = {
    "model": None,
    "task_type": TaskType.NLP_NER_INFERENCE.value,
    "input": "北京人在上海",
}

semantic_match_inference_config = {
    "model": None,
    "task_type": TaskType.NLP_SEMANTIC_MATCH_INFERENCE.value,
    "input1": "太棒了",
    "input2": "太差了",
}

sentiment_classifier_trainer_config = {
    "task_type": TaskType.NLP_SENTIMENT_TRAINER.value,
    "num_labels": 2,
    "label_mapping": {0: "消极", 1: "积极"},
    "path": get_example_data_path("dianping"),
    "text_column": "comment",
    "label_column": "sentiment",
    "num_epochs": 1,
    "texts": ["这家餐厅的服务非常好，菜品也很新鲜！", "太差了，菜品完全不新鲜，服务态度也很差", "一般般，没什么特别的"],
}
