from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

from baicai_dev.utils.code_templates.ml import ACTION_CODE

ACTION_CODER = (
    """
# Role
You are a senior ML engineer specializing in feature engineering implementation and validation, focusing on Random Forest model optimization for {target} prediction.

## Context
Data Source: {clean_data_path}
Target Variable: {target}
Evaluation Metric: {selected_metric}
Columns: {columns}
Data Overview: {cleaned_data_info}
Actions: {actions}

## Implementation Requirements
- Load the data from the **Data Source**
- Only use features in the **Columns**
- Code every action from **Actions**
- 使用中文回答所有问题
- 使用{avg_param}作为{selected_metric}的评估参数

### 1. Implementation Rules
- Follow **Template** to implement
- Create new copies of data for each action
- Evaluate each action independently
- Clean up variables after each action
- No sklearn Pipeline usage

### 2. Safety Guidelines
- Beware of data leakage
- Apply same transformations to train and test
- Print clear action headers

### 3. For Each Action
1. implement one action from Actions
2. use "# New action starts" as a separator before every action coding, even do this for empty actions
3. Copy input data
4. Transform features
5. Train Random Forest
6. Print metrics with id and name of the action
   - 对于分类问题, 必须使用{avg_param}作为{selected_metric}的评估参数
7. Clean up memory

# Output
## Format
Output the code in the following format with one and only one block of code:
```python
# Required imports
[imports]

# Load data
[data loading code]

# New action starts
# Action 1: [Name]
[action 1 implementation]

# New action starts
# Action 2: [Name]
[action 2 implementation]

[etc...]
```

## Code Template
"""  # noqa: E501
    + ACTION_CODE
)


def action_coder(llm=None):
    llm = llm or LLM().llm
    action_coder_template = ChatPromptTemplate.from_messages(
        [
            ("system", ACTION_CODER),
            ("placeholder", "{messages}"),
        ]
    )

    return action_coder_template | llm


if __name__ == "__main__":
    import asyncio

    from baicai_base.utils.data import extract_code, get_saved_pickle_path, preview_data
    from baicai_base.utils.setups import setup_code_interpreter

    from baicai_dev.utils.setups.setup_example_data import ACTION_MAKER_RESULT_TITANIC

    async def main():
        question = "Predict the Survived of Titanic"
        columns = preview_data(
            get_saved_pickle_path(folder=None, name="titanic", file_prefix="baseline", type="data"), target="survived"
        )["cols"]
        cleaned_data_info = preview_data(
            get_saved_pickle_path(folder=None, name="titanic", file_prefix="baseline", type="data"), target="survived"
        )["data_info"]

        actions_titanic = ACTION_MAKER_RESULT_TITANIC
        accepted_actions_titanic = [
            action
            for action in actions_titanic
            if action["rejected"] == "false" and "survived" not in action["features"]
        ]

        action_coder_result = action_coder().invoke(
            {
                "target": "survived",
                "clean_data_path": get_saved_pickle_path(
                    folder=None, name="titanic", file_prefix="baseline", type="data"
                ),
                "selected_metric": "accuracy",
                "actions": accepted_actions_titanic,
                "columns": columns,
                "cleaned_data_info": cleaned_data_info,
                "messages": [("user", question)],
                "name": "titanic",
                "avg_param": "weighted",
            }
        )

        print(action_coder_result.content)

        code_block = extract_code(action_coder_result.content)

        codes = code_block.split("# New action starts")
        for action, code in zip(accepted_actions_titanic, codes[1:], strict=False):
            action.update({"code": code})

        interpreter = setup_code_interpreter()
        await interpreter.run(codes[0])

        for action in accepted_actions_titanic:
            run_result = await interpreter.run(action.get("code", ""))
            print(run_result)

        interpreter.terminate()

    asyncio.run(main())
