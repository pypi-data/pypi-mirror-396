from baicai_base.utils.data import preview_data

from baicai_dev.utils.data.loaders import get_example_data_path


def preview_example_data(name: str, target: str = None, **kwargs):
    """
    Preview example data for LLM to analyze.
    The tabular example data are: iris, titanic, house and dianping.

    Args:
        name (str): Name of the example data.
        target (str): Target column name.
    """

    path = get_example_data_path(name)
    return preview_data(path, target, **kwargs)
