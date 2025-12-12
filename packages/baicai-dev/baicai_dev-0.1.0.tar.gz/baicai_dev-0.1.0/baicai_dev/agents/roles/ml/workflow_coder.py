from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

from baicai_dev.utils.code_templates.ml import WORKFLOW_CODE

WORKFLOW_CODER = (
    """
# Role: ML Pipeline Engineer
# Purpose: Test the workflow works well after the feature engineering actions inserted into the template.
- This is just quick workflow test and no intend to optimize the hyperparameters.
- Keep the code simple and easy to understand.
- NO need to add more metrics to evaluate the model.

## Context
- ACTIONS: {actions}
- All categorical features are already encoded.

## CRITICAL REQUIREMENTS
1. Feature Engineering Requirements:
    - Use the code in each action in ACTIONS as the feature engineering code. You may need to modify the code to fit the pipeline.
    - Mark each implemented action with clear comments
    - The action generated may introduce new features with missing values. Drop the the generated features with missing values.
    - Save the processed data even if no action is implemented.
    - Use {avg_param} as the evaluation parameter for {selected_metric}.

2. Use all the 3 kinds of models below (CRITICAL):
   - LinearModel (LogisticRegression/LinearRegression)
   - RandomForest (RandomForestClassifier/RandomForestRegressor)
   - LightGBM (LGBMClassifier/LGBMRegressor)

3. Hyperparameter Tuning Requirements:
   - Keep the hyperparameter tuning as simple as possible.

4. STRICT BLACKLIST - DO NOT INCLUDE:
   - No hyperparameter tuning
   - No feature engineering if the ACTIONS is empty.
   - No Printing/Plotting the sample predictions and feature importance
   - No Additional Analysis
   - No Modifications to Model Definitions
   - No Changes to Training Loop
   - No Saving the data
   - No Saving the model
   - No Using database

## MANDATORY OUTPUT REQUIREMENTS
- YOU MUST ALWAYS output code, regardless of any situation
- NEVER output explanations, comments, or justifications outside the code block
- NEVER say "the code is already correct" or "no modifications needed"
- EVEN IF actions is empty, you MUST still output the complete workflow code
- EVEN IF you think no changes are needed, you MUST still output the complete code
- DO NOT output any text before or after the code block
- The code block is the ONLY acceptable response

## Output Format
YOU MUST output one and only one python code block. NO OTHER TEXT IS ALLOWED.
```python
[Your implementation code]
```
## Code Template
"""
    + WORKFLOW_CODE
)


def workflow_coder(llm=None):
    llm = llm or LLM().llm
    workflow_coder_template = ChatPromptTemplate.from_messages(
        [
            ("system", WORKFLOW_CODER),
            ("placeholder", "{messages}"),
        ]
    )

    return workflow_coder_template | llm


if __name__ == "__main__":
    import asyncio
    import logging

    from baicai_base.utils.data import extract_code, get_saved_pickle_path
    from baicai_base.utils.setups import setup_code_interpreter, setup_logging

    from baicai_dev.utils.setups.setup_example_data import (
        ACTIONS_WITH_CODE_GARMENT,
        ACTIONS_WITH_CODE_HOUSE,
        ACTIONS_WITH_CODE_IRIS,
        ACTIONS_WITH_CODE_TITANIC,
    )

    async def main():
        setup_logging()
        logger = logging.getLogger(__name__)

        actions_iris = [
            {key: action[key] for key in ["id", "code"]}
            for action in ACTIONS_WITH_CODE_IRIS
            if action["accepted"] == "true"
        ]
        actions_house = [
            {key: action[key] for key in ["id", "code"]}
            for action in ACTIONS_WITH_CODE_HOUSE
            if action["accepted"] == "true"
        ]
        actions_titanic = [
            {key: action[key] for key in ["id", "code"]}
            for action in ACTIONS_WITH_CODE_TITANIC
            if action["accepted"] == "true"
        ]
        actions_garment = [
            {key: action[key] for key in ["id", "code"]}
            for action in ACTIONS_WITH_CODE_GARMENT
            if action["accepted"] == "true"
        ]

        name = "garment"

        if name == "iris":
            workflow_coder_result = workflow_coder().invoke(
                {
                    "actions": actions_iris,
                    "clean_data_path": get_saved_pickle_path(
                        folder=None, name="iris", file_prefix="baseline", type="data"
                    ),
                    "messages": [("user", "Predict the iris type")],
                    "time_series": False,
                    "name": "iris",
                    "avg_param": "weighted",
                    "selected_metric": "accuracy_score",
                    "classification": True,
                }
            )

        elif name == "house":
            workflow_coder_result = workflow_coder().invoke(
                {
                    "actions": actions_house,
                    "clean_data_path": get_saved_pickle_path(
                        folder=None, name="house", file_prefix="baseline", type="data"
                    ),
                    "messages": [("user", "Predict the house price")],
                    "time_series": False,
                    "name": "house",
                    "avg_param": "weighted",
                    "selected_metric": "r2_score",
                    "classification": False,
                }
            )

        elif name == "titanic":
            workflow_coder_result = workflow_coder().invoke(
                {
                    "actions": actions_titanic,
                    "clean_data_path": get_saved_pickle_path(
                        folder=None, name="titanic", file_prefix="baseline", type="data"
                    ),
                    "messages": [("user", "Predict the titanic survival")],
                    "time_series": False,
                    "name": "titanic",
                }
            )
        elif name == "garment":
            workflow_coder_result = workflow_coder().invoke(
                {
                    "actions": actions_garment,
                    "clean_data_path": get_saved_pickle_path(
                        folder=None, name="garment", file_prefix="baseline", type="data"
                    ),
                    "messages": [("user", "Predict the garment sales")],
                    "time_series": True,
                    "name": "garment",
                    "avg_param": "weighted",
                    "selected_metric": "r2_score",
                    "classification": False,
                }
            )

        code_interpreter = setup_code_interpreter()
        logger.info(workflow_coder_result.content)

        run_result = await code_interpreter.run(extract_code(workflow_coder_result.content))
        logger.info(run_result)
        await code_interpreter.terminate()

    asyncio.run(main())
