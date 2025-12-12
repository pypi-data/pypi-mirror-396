import uuid
from pathlib import Path

from baicai_dev.configs.graph_configs import DLConfigData, MLConfigData


def create_dl_config(config_data: DLConfigData) -> dict:
    """
    Create a configuration dictionary for the graphs.
    """
    thread_id = str(uuid.uuid4())

    # Combine all configuration data
    return {
        "configurable": {
            **config_data,  # Unpack the original config data
            "thread_id": thread_id,  # Add the generated thread ID
        },
        "recursion_limit": 100,
    }


def create_ml_config(config_data: MLConfigData) -> dict:
    """
    Create a configuration dictionary for the graphs.

    Args:
        config_data (MLConfigData): A dictionary containing the configuration settings.

    Returns:
        dict: A dictionary containing the configuration settings.
    """
    # Preprocess the configuration data
    config_data["path"] = Path(config_data["path"])

    # Generate a unique thread ID
    thread_id = str(uuid.uuid4())

    # Import preview_data here to avoid circular import
    from baicai_base.utils.data import preview_data

    # Fetch both brief and full data previews
    full_data_info, cols, data_size, avg_param, class_counts = preview_data(
        config_data["path"],
        config_data["target"],
        config_data.get("classification", True),
        brief=False,
        ignored_features=config_data["ignored_features"],
    ).values()

    brief_data_info = preview_data(
        config_data["path"],
        config_data["target"],
        config_data.get("classification", True),
        brief=True,
        ignored_features=config_data["ignored_features"],
    )["data_info"]

    # Combine all configuration data
    return {
        "configurable": {
            **config_data,  # Unpack the original config data
            "thread_id": thread_id,  # Add the generated thread ID
            "brief_data_info": brief_data_info,  # Add the computed brief data info
            "full_data_info": full_data_info,  # Add the computed full data info
            "cols": cols,  # Add the computed columns
            "data_size": data_size,  # Add the computed data size
            "avg_param": avg_param,  # Add the computed average parameter
            "class_counts": class_counts,  # Add the computed class counts
        },
        "recursion_limit": 100,
    }
