from types import SimpleNamespace

from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from baicai_dev.utils.code_templates.ml import BASELINE_CODE


def baseline_coder(llm: LLM = None):
    # 定义模板
    template = ChatPromptTemplate.from_messages(
        [
            ("system", BASELINE_CODE),
            ("placeholder", "{messages}"),
        ]
    )

    def format_template(inputs):
        # 直接获取格式化后的消息内容
        messages = template.format_messages(
            path=inputs.get("path", ""),
            classification=inputs.get("classification", True),
            target=inputs.get("target", ""),
            name=inputs.get("name", ""),
            ignored_features=inputs.get("ignored_features", []),
            date_feature=inputs.get("date_feature", ""),
            need_time=inputs.get("need_time", False),
            ordinal_features=inputs.get("ordinal_features", []),
            time_series=inputs.get("time_series", False),
            threshold=inputs.get("threshold", {}),
            delimiter=inputs.get("delimiter", ","),
            avg_param=inputs.get("avg_param", "weighted"),
        )

        return SimpleNamespace(content=messages[-1].content)

    return RunnableLambda(format_template)


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    from baicai_base.utils.data import extract_code
    from baicai_base.utils.setups import setup_code_interpreter

    async def main():
        data = "titanic"
        data_path = Path.home() / ".baicai" / "data"

        if data == "house":
            baseline_coder_result = baseline_coder().invoke(
                {
                    "path": data_path / "house.csv",
                    "target": "MedHouseVal",
                    "classification": False,
                    "ignored_features": [],
                    "name": "house",
                    "date_feature": "",
                    "need_time": False,
                    "ordinal_features": [],
                    "time_series": False,
                    "threshold": {},
                    "delimiter": ",",
                    "avg_param": "weighted",
                }
            )

        elif data == "iris":
            baseline_coder_result = baseline_coder().invoke(
                {
                    "path": data_path / "iris.csv",
                    "target": "iris",
                    "classification": True,
                    "ignored_features": [],
                    "name": "iris",
                    "date_feature": "",
                    "need_time": False,
                    "ordinal_features": [],
                    "time_series": False,
                    "threshold": {},
                    "delimiter": ",",
                }
            )

        elif data == "titanic":
            baseline_coder_result = baseline_coder().invoke(
                {
                    "path": data_path / "Titanic_kaggle.csv",
                    "target": "Survived",
                    "classification": True,
                    "ignored_features": ["PassengerId", "Name", "Ticket", "Cabin"],
                    "name": "titanic",
                    "date_feature": "",
                    "need_time": False,
                    "ordinal_features": [{"Sex": ["Female", "Male"]}],
                    "time_series": False,
                    "threshold": {},
                    "delimiter": ",",
                    "avg_param": "binary",
                }
            )
        elif data == "garment":
            baseline_coder_result = baseline_coder().invoke(
                {
                    "path": data_path / "garment.csv",
                    "target": "actual_productivity",
                    "classification": False,
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
                    "delimiter": ",",
                    "avg_param": "micro",
                }
            )

        print(f"{data} code:", baseline_coder_result.content)

        interpreter = setup_code_interpreter()
        run_result = await interpreter.run(extract_code(baseline_coder_result.content))

        print(run_result)

        await interpreter.terminate()

    asyncio.run(main())
