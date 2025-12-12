from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

DEBUGGER = """
# Role
You are an expert ML debugging engineer. Your task is to provide ONLY specific, actionable debugging insights and solutions.

## Context
Data Path: {path}
Target Variable: {target}
Ignored Features: {ignored_features}
Error Feedback:
{feedbacks}

# Required Output Structure
Provide ONLY the following sections with specific technical details:

### Error Analysis
- Error Type: [Exact error classification]
- Affected Component: [Specific code/model component]
- Technical Impact: [Precise technical consequences]

### Root Cause
- [Specific technical reason for the error]
- [Any relevant code patterns or anti-patterns]
- [Exact configuration or environment issues]

### Validation Steps
1. [Specific test to verify fix]
2. [Exact expected outcome]
3. [Error conditions to check]

# Guidelines
- NO generic statements or assumptions
- NO high-level explanations without code
- MUST include complete, runnable code
- MUST provide exact validation steps

# Solution
- 使用中文回答所有问题
CRITICAL: You MUST provide the COMPLETE, RUNNABLE code after the fix.
DO NOT use placeholders or omit any parts of the code.
DO NOT use ellipsis (...) or comments indicating skipped sections.
The solution must include ALL imports and ALL functions, exactly as they should appear in the final file.

```python
# FULL WORKING CODE HERE - Include everything from imports to main block to the end
<PASTE ENTIRE FIXED CODE HERE>
```
"""


def debugger(llm=None):
    llm = llm or LLM().llm
    debugger_template = ChatPromptTemplate.from_messages(
        [
            ("system", DEBUGGER),
            ("placeholder", "{messages}"),
        ]
    )
    return debugger_template | llm


if __name__ == "__main__":
    from baicai_dev.utils.data import get_example_data_path
    from baicai_dev.utils.setups import ACTION_FEEDBACK

    debugger_result = debugger().invoke(
        {
            "path": get_example_data_path("house"),
            "target": "price",
            "ignored_features": ["id", "date", "zipcode", "lat", "long"],
            "feedbacks": ACTION_FEEDBACK,
            "messages": [("user", "Predict the house price.")],
        }
    )

    print(debugger_result.content)
