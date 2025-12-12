from baicai_dev.configs.graph_configs import MLConfigData
from baicai_dev.utils.setups.create_configs import create_ml_config


def setup_ml_graph_config(config_data: MLConfigData = None):
    """
    Setup the graph config. Defaults to iris_config_data.
    """
    from baicai_dev.utils.setups.setup_example_config import iris_config_data

    config_data = config_data or iris_config_data

    return create_ml_config(config_data)
