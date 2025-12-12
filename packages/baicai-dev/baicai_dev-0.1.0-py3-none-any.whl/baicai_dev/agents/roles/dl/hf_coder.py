from types import SimpleNamespace

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from baicai_dev.utils.code_templates import (
    NER_INFERENCE_CODE,
    SEMANTIC_MATCH_INFERENCE_CODE,
    SENTIMENT_CLASSIFIER_TRAIN_CODE,
    SENTIMENT_INFERENCE_CODE,
)
from baicai_dev.utils.data import get_example_data_path


def sentiment_inference_coder():
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", SENTIMENT_INFERENCE_CODE),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            model=inputs.get("model", "uer/roberta-base-finetuned-dianping-chinese"),
            input=inputs.get("input", ""),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def ner_inference_coder():
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", NER_INFERENCE_CODE),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            model=inputs.get("model", "xiaxy/elastic-bert-chinese-ner"),
            input=inputs.get("input", ""),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def semantic_match_inference_coder():
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", SEMANTIC_MATCH_INFERENCE_CODE),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            model=inputs.get("model", "moka-ai/m3e-base"),
            input1=inputs.get("input1", ""),
            input2=inputs.get("input2", ""),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


def sentiment_classifier_trainer():
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", SENTIMENT_CLASSIFIER_TRAIN_CODE),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            model=inputs.get("model", None),
            num_labels=inputs.get("num_labels", 2),
            label_mapping=inputs.get("label_mapping", {0: "消极", 1: "积极"}),
            path=inputs.get("path", get_example_data_path("dianping")),
            text_column=inputs.get("text_column", "comment"),
            label_column=inputs.get("label_column", "sentiment"),
            num_epochs=inputs.get("num_epochs", 3),
            texts=inputs.get(
                "texts",
                [
                    "这家餐厅的服务非常好，菜品也很新鲜！",
                    "太差了，菜品完全不新鲜，服务态度也很差",
                    "一般般，没什么特别的",
                ],
            ),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


if __name__ == "__main__":
    import asyncio

    from baicai_base.utils.data import extract_code
    from baicai_base.utils.setups import setup_code_interpreter

    async def main():
        type = "sentiment_inference"

        if type == "sentiment_inference":
            result = sentiment_inference_coder().invoke(
                {
                    "model": None,
                    "input": "太棒了",
                }
            )
        elif type == "ner_inference":
            result = ner_inference_coder().invoke(
                {
                    "model": None,
                    "input": "北京人在上海",
                }
            )
        elif type == "semantic_match_inference":
            result = semantic_match_inference_coder().invoke(
                {
                    "model": None,
                    "input1": "太棒了",
                    "input2": "太棒了",
                }
            )
        elif type == "sentiment_classifier_trainer":
            result = sentiment_classifier_trainer().invoke(
                {
                    "num_labels": 2,
                    "label_mapping": {0: "消极", 1: "积极"},
                    "path": get_example_data_path("dianping"),
                    "text_column": "comment",
                    "label_column": "sentiment",
                    "num_epochs": 1,
                    "texts": [
                        "这家餐厅的服务非常好，菜品也很新鲜！",
                        "太差了，菜品完全不新鲜，服务态度也很差",
                        "一般般，没什么特别的",
                    ],
                }
            )

        print(result.content)

        interpreter = setup_code_interpreter()
        run_result = await interpreter.run(extract_code(result.content))

        print(run_result)

        await interpreter.terminate()

    asyncio.run(main())
