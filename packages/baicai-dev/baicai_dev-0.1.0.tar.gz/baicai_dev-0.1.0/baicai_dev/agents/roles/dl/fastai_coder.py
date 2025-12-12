from types import SimpleNamespace

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from baicai_dev.utils.code_templates import (
    COLLAB,
    FROM_CSV,
    IMG_FOLDER_PER_CLASS,
    IMG_FROM_FUNC,
    IMG_FROM_RE,
    MULTI_LABEL,
)


def single_label_classifier():
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", IMG_FOLDER_PER_CLASS),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            model=inputs.get("model", "resnet18"),
            path=inputs.get("path", ""),
            train_folder=inputs.get("train_folder", None),
            valid_folder=inputs.get("valid_folder", None),
            valid_pct=inputs.get("valid_pct", 0.2),
            batch_size=inputs.get("batch_size", 64),
            size=inputs.get("size", 24),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def from_func_classifier():
    template = ChatPromptTemplate.from_messages([("system", IMG_FROM_FUNC), ("placeholder", "{messages}")])

    def format_template(inputs):
        messages = template.format_messages(
            model=inputs.get("model", "resnet18"),
            path=inputs.get("path", ""),
            label_func=inputs.get("label_func", "return x.parent.name"),
            valid_pct=inputs.get("valid_pct", 0.2),
            batch_size=inputs.get("batch_size", 4),
            size=inputs.get("size", 24),
        )
        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def from_re_classifier():
    template = ChatPromptTemplate.from_messages([("system", IMG_FROM_RE), ("placeholder", "{messages}")])

    def format_template(inputs):
        messages = template.format_messages(
            model=inputs.get("model", "resnet18"),
            path=inputs.get("path", ""),
            pat=inputs.get("pat", ""),
            valid_pct=inputs.get("valid_pct", 0.2),
            batch_size=inputs.get("batch_size", 4),
            size=inputs.get("size", 24),
        )
        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def from_csv_classifier():
    template = ChatPromptTemplate.from_messages([("system", FROM_CSV), ("placeholder", "{messages}")])

    def format_template(inputs):
        messages = template.format_messages(
            model=inputs.get("model", "resnet18"),
            path=inputs.get("path", "''"),
            folder=inputs.get("folder", None),
            csv_file=inputs.get("csv_file", ""),
            image_col=inputs.get("image_col", 0),
            label_col=inputs.get("label_col", 1),
            valid_col=inputs.get("valid_col", None),
            delimiter=inputs.get("delimiter", None),
            label_delim=inputs.get("label_delim", None),
            valid_pct=inputs.get("valid_pct", 0.2),
            batch_size=inputs.get("batch_size", 4),
            size=inputs.get("size", 24),
        )
        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def multi_label_classifier():
    template = ChatPromptTemplate.from_messages([("system", MULTI_LABEL), ("placeholder", "{messages}")])

    def format_template(inputs):
        messages = template.format_messages(
            model=inputs.get("model", "resnet18"),
            path=inputs.get("path", ""),
            folder=inputs.get("folder", None),
            csv_file=inputs.get("csv_file", ""),
            image_col=inputs.get("image_col", 0),
            label_col=inputs.get("label_col", 1),
            valid_col=inputs.get("valid_col", None),
            delimiter=inputs.get("delimiter", None),
            label_delim=inputs.get("label_delim", "' '"),
            valid_pct=inputs.get("valid_pct", 0.2),
            batch_size=inputs.get("batch_size", 4),
            size=inputs.get("size", 24),
        )
        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def collab_recommender():
    template = ChatPromptTemplate.from_messages([("system", COLLAB), ("placeholder", "{messages}")])

    def format_template(inputs):
        messages = template.format_messages(
            path=inputs.get("path", ""),
            user_name=inputs.get("user_name", ""),
            item_name=inputs.get("item_name", ""),
            rating_name=inputs.get("rating_name", ""),
            y_range_min=inputs.get("y_range_min", 0.5),
            y_range_max=inputs.get("y_range_max", 5.5),
            valid_pct=inputs.get("valid_pct", 0.2),
        )
        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


if __name__ == "__main__":
    import asyncio
    import platform

    from baicai_base.utils.data import extract_code
    from baicai_base.utils.setups import setup_code_interpreter
    from fastai.vision.all import *  # noqa: F403

    from baicai_dev.utils.data import get_example_data_path

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def main():
        # 数据集组织方式, 改变以测试不同的数据集组织方式

        # 构建数据集路径
        bears_path = get_example_data_path("bears", tabular=False)
        mnist_tiny_path = str(untar_data(URLs.MNIST_TINY))
        pets_path = str(untar_data(URLs.PETS))
        pascal_path = str(untar_data(URLs.PASCAL_2007))
        movielens_path = str(untar_data(URLs.ML_SAMPLE) / "ratings.csv")

        data_orgnization = "from_re"

        label_type = "multi label"

        if data_orgnization == "folder_per_class":
            path = bears_path

            result = single_label_classifier().invoke(
                {
                    "messages": [("user", "classify the image types")],
                    "path": path,
                    "model": "resnet18",
                    "valid_pct": 0.2,
                    "train_folder": None,
                    "valid_folder": None,
                    "batch_size": 4,
                }
            )

            print(result)

        elif data_orgnization == "from_func":
            path = bears_path
            result = from_func_classifier().invoke(
                {
                    "messages": [("user", "classify the image types")],
                    "path": path,
                    "model": "resnet18",
                    "label_func": "return x.parent.name",
                    "valid_pct": 0.2,
                    "batch_size": 4,
                }
            )

        elif data_orgnization == "from_re":
            path = bears_path
            result = from_re_classifier().invoke(
                {
                    "messages": [("user", "classify the image types")],
                    "path": path,
                    "model": "resnet18",
                    "pat": r"([^_]+)_",
                    "valid_pct": 0.2,
                    "batch_size": 4,
                }
            )

        elif data_orgnization == "from_csv":
            if label_type == "multi label":
                path = pascal_path
                result = multi_label_classifier().invoke(
                    {
                        "messages": [("user", "classify the image types")],
                        "path": path,
                        "folder": "'train'",
                        "model": "resnet18",
                        "csv_file": "'train.csv'",
                        "image_col": "'fname'",
                        "label_col": "'labels'",
                        "valid_col": "'is_valid'",
                    }
                )
            else:
                path = mnist_tiny_path
                result = from_csv_classifier().invoke(
                    {
                        "messages": [("user", "classify the image types")],
                        "path": path,
                        "folder": None,
                        "model": "resnet18",
                        "csv_file": "'labels.csv'",
                        "image_col": "'name'",
                        "label_col": "'label'",
                        "valid_col": None,
                        "delimiter": None,
                        "label_delim": None,
                        "valid_pct": 0.2,
                        "batch_size": 4,
                    }
                )
        elif data_orgnization == "collab":
            path = movielens_path
            result = collab_recommender().invoke(
                {
                    "messages": [("user", "recommend the movie for the user")],
                    "path": path,
                    "user_name": "'userId'",
                    "item_name": "'movieId'",
                    "rating_name": "'rating'",
                    "y_range_min": 0.5,
                    "y_range_max": 5.5,
                    "valid_pct": 0.2,
                }
            )

        print(result.content)

        interpreter = setup_code_interpreter()
        run_result = await interpreter.run(extract_code(result.content))

        print(run_result)

        await interpreter.terminate()

    asyncio.run(main())
