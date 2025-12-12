from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

REASONER = """
# Role
You are a senior {domain} data scientist specializing in feature engineering for machine learning models, with expertise in predicting {target}.

## Context
- Domain Knowledge: {domain_context}
- Data Overview: {cleaned_data_info}
- Baseline Model Performance: {model_info}

# Analysis Framework

## 1. Data Understanding Requirements
- Feature distributions and relationships
- Business logic and domain constraints
- Current feature importance rankings

## 2. Feature Engineering Scope
Target: Improve Random Forest model performance
Minimum Actions Required: {num}

### Preprocessing Status
- Categorical features: Already label encoded
- Numerical features: Already scaled
- Missing values: Already imputed
- Target variable: {target}

### Focus Areas
1. Numerical Feature Transformations:
   - Distribution analysis
   - Scaling requirements
   - Interaction potential

2. Domain-Specific Transformations:
   - Business rules application
   - Common sense knowledge
   - Domain constraints
   - Expert knowledge integration

3. Feature Interaction Analysis:
   - Cross-feature relationships
   - Temporal patterns (if applicable)
   - Hierarchical relationships

4. Specific Requirements:
   {requirements}

# Engineering Guidelines

## Allowed Transformations
1. Mathematical operations
2. Window functions
3. Business rule encodings
4. Feature interactions
5. Domain-specific calculations

## Prohibited Actions (Blacklist)
IMPORTANT: Any action containing these operations MUST be marked as rejected="true":
1. Feature Selection:
   - Removing features
   - Selecting subset of features
   - Feature importance-based selection

2. Categorical Processing:
   - One-hot encoding
   - Label encoding
   - Target encoding
   - Imputation

3. Numerical Feature Processing:
   - Scaling
   - Imputation

4. Data Operations:
   - Train/test splitting
   - Cross-validation
   - Sampling methods

4. Dimensionality Reduction:
   - PCA
   - t-SNE
   - UMAP

5. Model Operations:
   - Hyperparameter tuning
   - Model selection
   - Ensemble methods

6. Target Modifications:
   - Target transformation
   - Target engineering

7. Other Prohibited:
   - Dependent/sequential transformations
   - Visualization operations
   - Code generation
   - Data cleaning operations

## Action Validation Rules
1. MUST check each action against ALL blacklisted operations
2. If action contains ANY blacklisted operation:
   - Set "rejected": "true"
   - Set "rejection_reason": "Contains blacklisted operation: [specific operation]"
3. Only propose implementable feature transformations
4. Each action MUST be independent and self-contained

## Quality Criteria
1. Independence: Each action must be self-contained
2. Implementability: Clear transformation logic
3. Domain alignment: Consistent with business rules
4. Performance impact: Clear value proposition

## Validation Checklist
1. Each action is independent
2. No blacklisted operations
3. Business rules compliance
4. Implementation feasibility
5. Clear value proposition

## Chain-of-thought process
Follow a chain-of-thought process to generate the actions.
- Data Analysis
    - Feature Analysis
        - [Key findings about features]
        - [Notable distribution characteristics]
        - [Important feature interactions]

- Domain Knowledge Application
    - Business Rules
        - [Rule 1]
        - [Rule 2]
    - Domain Constraints
        - [Constraint 1]
        - [Constraint 2]
    - Identified Conflicts
        - [Conflict 1 and resolution]
        - [Conflict 2 and resolution]


## Output
- Note: You are not allowed to output any code.
- You MUST output ONLY a valid JSON object containing at least {num} actions, with no additional text, markdown, or explanations.
- 使用中文回答所有问题
- The JSON must follow this exact structure:
```json
{{
    "actions": [
        {{
            "id": "id", # integer, unique id for each action
            "action": "Action to improve the model performance",
            "features": ["feature1", "feature2", ...],
            "business_justification": "Why this transformation adds value",
            "expected_impact": "Expected model improvement",
            "domain_rules_compliance": ["rule1", "rule2", ...],
            "rejected": "true" or "false",
            "rejection_reason": "If rejected=true, specify which blacklisted operation was detected. Empty string if not rejected"
        }},
        {{
            ...
        }}
    ]
}}
```
"""


def reasoner(llm=None):
    llm = llm or LLM().llm
    action_maker_template = ChatPromptTemplate.from_messages(
        [
            ("system", REASONER),
            ("placeholder", "{messages}"),
        ]
    )
    return action_maker_template | llm


if __name__ == "__main__":
    from baicai_base.utils.data import get_saved_pickle_path, preview_data

    from baicai_dev.utils.setups.setup_example_data import (
        BASELINE_CODES_HOUSE,
        BASELINE_CODES_IRIS,
        BASELINE_CODES_TITANIC,
    )

    question_house = "Predict the price of a house"
    question_iris = "Predict the iris type"
    question_titanic = "Predict the titanic survival"

    task = "house"

    if task == "house":
        workflow_code = BASELINE_CODES_HOUSE
        name = "house"
        target = "price"
    elif task == "iris":
        workflow_code = BASELINE_CODES_IRIS
        name = "iris"
        target = "iris"
    elif task == "titanic":
        workflow_code = BASELINE_CODES_TITANIC
        name = "titanic"
        target = "survived"

    # action_maker_result = reasoner().invoke(
    #     {
    #         "num": 10,
    #         "domain": "House Price",
    #         "model_info": str(workflow_code[0]["result"]),
    #         "domain_context": "house price",
    #         "messages": [("user", question_house)],
    #         "target": "price",
    #         "cleaned_data_info": preview_data(
    #             get_saved_pickle_path(folder=None, name=name, file_prefix="baseline", type="data"),
    #             target=target,
    #             brief=False,
    #         )["data_info"],
    #         "requirements": "",
    #     }
    # )

    action_maker_result_iris = reasoner().invoke(
        {
            "num": 10,
            "domain": "Iris",
            "model_info": str(BASELINE_CODES_IRIS[0]["result"]),
            "domain_context": "iris",
            "messages": [("user", question_iris)],
            "target": "iris",
            "cleaned_data_info": preview_data(get_saved_pickle_path(folder=None, name="iris", file_prefix="baseline", type="data"), target="iris")["data_info"],
            "requirements": "petal length (cm)平方处理",
        }
    )

    # reasoner_result_titanic = reasoner().invoke(
    #     {
    #         "num": 10,
    #         "domain": "Titanic",
    #         "model_info": str(BASELINE_CODES_TITANIC[-1]["result"]),
    #         "domain_context": "titanic",
    #         "messages": [("user", question_titanic)],
    #         "target": "survived",
    #         "cleaned_data_info": preview_data(get_saved_pickle_path(folder=None, name="titanic", file_prefix="baseline", type="data"), target="survived")["data_info"],
    #     }
    # )

    # print(action_maker_result.content)
    # print("-----------------------")
    print(action_maker_result_iris.content)
    # print("-----------------------")
    # print(reasoner_result_titanic.content)
