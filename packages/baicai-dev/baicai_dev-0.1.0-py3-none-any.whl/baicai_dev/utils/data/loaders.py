from pathlib import Path

from baicai_base.utils.data import load_data


def load_example_data(name):
    if name is not None and name:
        path = get_example_data_path(name)
        return load_data(path)


def get_example_data_folder(name: str, tabular: bool = True):
    examples_folder = Path.home() / ".baicai" / "data"
    return examples_folder


def get_example_data_path(name: str, tabular: bool = True):
    """
    The tabular example data are: iris, titanic, house and dianping.
    The non-tabular example data are: mnist and bears.
    """
    examples_folder = get_example_data_folder(name, tabular)

    if tabular:
        if name in ["iris", "titanic", "house", "dianping", "garment"]:
            file_name = f"{name}.csv"
        else:
            raise ValueError(f"Unsupported example data name: {name}, use path directly")

        path = examples_folder / f"{file_name}"
        return path
    else:
        if name == "bears":
            path = examples_folder / "bears"
        elif name == "mnist":
            path = examples_folder / "mnist_tiny"
        else:
            raise ValueError(f"Unsupported example data name: {name}, use path directly")

        return path
