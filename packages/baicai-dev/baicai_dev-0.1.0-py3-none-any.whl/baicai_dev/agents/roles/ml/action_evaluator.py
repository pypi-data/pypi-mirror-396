from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

ACTION_EVALUATOR = """
# Role
You are a senior ML performance analyst specializing in model evaluation and feature engineering validation.

## Context
Primary Metric: {metrics}
Baseline Performance: {baseline_result}
Action Results: {model_info}

## Evaluation Criteria

### 1. Performance Requirements
- Testing metrics must exceed baseline
- Improvements must be meaningful
- Results must be consistent and reliable

### 2. Acceptance Thresholds
- Testing performance > Baseline by meaningful margin
- No significant overfitting indicated
- Implementation complexity considered

### 3. Automatic Rejection Criteria
- Requires additional packages
- Marginal or unclear improvements
- Unstable or inconsistent results
- High risk of overfitting
- Implementation complexity too high

## Analysis Protocol
1. Compare test metrics with baseline
2. Assess improvement magnitude
3. Check implementation feasibility
4. Evaluate risk factors
5. Make accept/reject decision

## Decision Framework
```
For each action:
1. Baseline Comparison
   - Test performance vs baseline
   - Improvement magnitude

2. Risk Assessment
   - Implementation complexity
   - Dependency requirements
   - Stability concerns

3. Final Decision
   - Clear improvement: Accept
   - Marginal/Unclear: Reject
   - Additional dependencies: Reject
```

# Output
- 使用中文回答
Give your conclusion with the JSON format strictly:
```json
{{
    "actions": [
        {{
            "id": str,  # id of the action,
            "accepted": str   # Your decision of accecpted 'true' or 'false'，
            "rationale": str  # Your rationale of the decision.
        }}
    ]
}}
"""


def action_evaluator(llm=None):
    llm = llm or LLM().llm
    action_evaluator_template = ChatPromptTemplate.from_messages(
        [
            ("system", ACTION_EVALUATOR),
            ("placeholder", "{messages}"),
        ]
    )

    return action_evaluator_template | llm


if __name__ == "__main__":
    from pprint import pprint

    from baicai_base.utils.data import extract_json

    from baicai_dev.utils.setups.setup_example_data import ACTIONS_WITH_CODE_IRIS

    actions = ACTIONS_WITH_CODE_IRIS
    used_actions = [
        {
            "id": s["id"],
            "result": s["result"],
        }
        for s in actions
    ]

    result = action_evaluator().invoke(
        {
            "model_info": used_actions,
            "baseline_result": "Training set accuracy:  0.9\nTesting set accuracy:  0.9",
            "metrics": "accuracy",
        }
    )
    print(result.content)

    conclusions = extract_json(result.content)

    print(conclusions)

    for action, conclusion in zip(actions, conclusions["actions"], strict=False):
        action["accepted"] = conclusion["accepted"]

    pprint(actions)
