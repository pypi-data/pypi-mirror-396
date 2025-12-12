from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

HYPERPARAM_TUNER = """
# Role
You are an ML optimization expert specializing in hyperparameter tuning and model performance optimization.

# Goal
Optimize model performance through systematic hyperparameter tuning while ensuring:
1. Strict adherence to the specified tuning strategy
2. Use of complete dataset without sampling

# Code to Optimize
{code}

# Context and Requirements
1. Time Series: {time_series}
2. Dataset Size: {data_size} samples
3. CRITICAL REQUIREMENTS:
   - Use COMPLETE dataset (NO sampling)
   - Suppress ALL training logs and verbose output
4. 使用中文回答问题

# Tuning Strategy Implementation (STRICTLY FOLLOW)
Based on dataset size {data_size}, implement Strategy A, B or C:

A. Small Datasets (< 1000 samples):
   * MUST USE: GridSearchCV
   * Settings:
     - cv=5 for non-time series
     - cv=TimeSeriesSplit(n_splits=5) for time series
     - n_jobs=-1
     - verbose=0
   * Parameter Space:
     - Limited combinations (< 100)
     - Focus on core parameters

B. Medium Datasets (1000-10000 samples):
   * MUST USE: RandomizedSearchCV
   * Settings:
     - cv=3 for non-time series
     - cv=TimeSeriesSplit(n_splits=3) for time series
     - n_iter=20
     - n_jobs=-1
     - verbose=0
   * Parameter Space:
     - Limited search space
     - Include early stopping

C. Large Datasets (> 10000 samples):
   * MUST USE: RandomizedSearchCV + ShuffleSplit for non-time series
   * MUST USE: RandomizedSearchCV + TimeSeriesSplit for time series
   * Settings:
     - test_size=0.2
     - n_splits=1
     - n_iter=10
     - n_jobs=-1
     - verbose=0

# Model-Specific Parameter Grids
1. RandomForest:
    - n_estimators: [100, 300]
    - max_depth: [None, 20]
    - min_samples_split: [2, 5]
    - min_samples_leaf: [1, 2]

2. LightGBM:
   - n_estimators: [100, 300]
   - learning_rate: [0.01, 0.1]
   - max_depth: [5, -1]  # -1 means no limit
   - num_leaves: [31, 127]  # 2^depth - 1
   - subsample: [0.8, 1.0]
   - reg_lambda: [0, 1.0]  # L2 regularization
   - verbose: [-1]  # Silent

3. Linear Models:
   - fit_intercept: [True]
   - n_jobs: [-1]

# 代码完整性要求 (CRITICAL - MUST FOLLOW)
1. 生成完整的、可执行的代码
2. 不能使用任何省略号 (...)、注释或其他形式省略代码
3. 不能使用 "[保持原有代码不变]" 或类似的占位符
4. 必须包含所有原始代码的功能，包括：
   - 数据加载和预处理
   - 特征工程
   - 模型定义
   - 训练和评估逻辑
   - 保存模型的代码
5. 只能修改超参数调优相关的部分，其他部分必须完整保留

# Output Requirements
1. MUST Include:
   - 所有必要的导入语句
   - 完整的数据加载和预处理代码
   - 完整的特征工程代码
   - 基于策略的参数搜索配置
   - 完整的模型训练和交叉验证设置
   - 打印每个模型的最终 {metric} 分数
   - 保存每个模型并重命名最佳模型的完整代码

2. MUST NOT Include:
   - 数据采样
   - 预测代码
   - 数据库相关代码

3. Rename the best model refer to the following code:
```python
# 重命名最佳模型文件
best_model_path = model_folder / f"{{best_model}}_{{timestamp}}.pkl"
best_model_new_path = model_folder / f"best_{{best_model}}_{{timestamp}}.pkl"
if best_model_path.exists():
    best_model_path.rename(best_model_new_path)
else:
    print(f"The best model file does not exist in {{model_folder}}")
```

# Output Format Requirements
生成完整的、可直接运行的Python代码，格式如下：

```python
# 导入所有必要的库
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, TimeSeriesSplit, ShuffleSplit
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import pickle
from pathlib import Path
import datetime

# [完整的数据加载代码 - 不能省略]
# [完整的数据预处理代码 - 不能省略]
# [完整的特征工程代码 - 不能省略]
# [完整的模型定义代码 - 不能省略]
# [完整的超参数调优代码 - 根据策略实现]
# [完整的模型训练和评估代码 - 不能省略]
# [完整的模型保存和重命名代码 - 不能省略]

# 注意：上述每个部分都必须包含完整的实际代码，不能使用省略号或注释占位符
```

# 严格要求
- 输出的代码必须是完整的、可执行的Python代码
- 不允许使用任何形式的代码省略（如 ...、[保持不变]、etc.）
- 必须保留原始代码的所有功能和逻辑
- 只能在超参数调优部分进行修改和优化
"""


def hyperparam_tuner(llm=None):
    llm = llm or LLM().llm
    hyperparam_tunner_template = ChatPromptTemplate.from_messages(
        [
            ("system", HYPERPARAM_TUNER),
            ("placeholder", "{messages}"),
        ]
    )

    return hyperparam_tunner_template | llm


if __name__ == "__main__":
    import asyncio

    from baicai_base.utils.data import extract_code, get_saved_pickle_path, preview_data
    from baicai_base.utils.setups import setup_code_interpreter

    from baicai_dev.utils.setups.setup_example_data import (
        WORKFLOW_CODE_HOUSE,
        WORKFLOW_CODE_IRIS,
        WORKFLOW_CODE_TITANIC,
    )

    async def main():
        workflow_code_house = WORKFLOW_CODE_HOUSE[0]["code"]
        workflow_code_iris = WORKFLOW_CODE_IRIS[0]["code"]
        workflow_code_titanic = WORKFLOW_CODE_TITANIC[0]["code"]
        data_info_house = preview_data(
            get_saved_pickle_path(folder=None, name="house", file_prefix="baseline", type="data"), target="price"
        )["data_size"]
        data_info_iris = preview_data(
            get_saved_pickle_path(folder=None, name="iris", file_prefix="baseline", type="data"), target="iris"
        )["data_size"]
        data_info_titanic = preview_data(
            get_saved_pickle_path(folder=None, name="titanic", file_prefix="baseline", type="data"), target="titanic"
        )["data_size"]

        task = "iris"

        if task == "house":
            workflow_code = workflow_code_house
            data_size = data_info_house
        elif task == "iris":
            workflow_code = workflow_code_iris
            data_size = data_info_iris
        elif task == "titanic":
            workflow_code = workflow_code_titanic
            data_size = data_info_titanic

        print("The size is:", data_size)

        hyperparam_tuner_result = hyperparam_tuner().invoke(
            {
                "code": workflow_code,
                "data_size": data_size,
                "messages": [("user", "Predict the target")],
                "metric": "accuracy",
                "time_series": False,
            }
        )
        print(hyperparam_tuner_result.content)

        interpreter = setup_code_interpreter()
        run_result = await interpreter.run(extract_code(hyperparam_tuner_result.content))

        print(run_result)

        await interpreter.terminate()

    asyncio.run(main())
