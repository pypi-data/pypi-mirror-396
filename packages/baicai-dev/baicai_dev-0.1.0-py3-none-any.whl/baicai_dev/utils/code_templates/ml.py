# 配置基本参数
# path  # 数据集路径
# classification  # 是否为分类任务
# target  # 目标变量名
# name  # 项目名称
# ignored_features  # 忽略的特征
BASELINE_CODE = """
```python
import warnings
from datetime import datetime
from pathlib import Path
from joblib import dump

import numpy as np
import pandas as pd
from fastai.tabular.all import (
    Categorify,
    FillMissing,
    TabularDataLoaders,
    cont_cat_split,
    add_datepart,
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, r2_score, recall_score, precision_score, f1_score, mean_squared_error, mean_absolute_error, root_mean_squared_error

from baicai_base.utils.data import load_data, time_series_data_split_condition

# 加载数据并进行预处理
df = load_data(r"{path}", delimiter="{delimiter}")

# 忽略特征
df = df.drop(columns={ignored_features})

# 时间序列按照年月日等划分
splits = None
if "{date_feature}" != "":
    df = add_datepart(df, "{date_feature}", time={need_time})

    if {need_time}:
        date_parts = {{
            "year": "Year",
            "month": "Month",
            "day": "Day",
            "hour": "Hour",
            "minute": "Minute",
            "second": "Second",
        }}
    else:
        date_parts = {{"year": "Year", "month": "Month", "day": "Day"}}

    if {time_series}:
        cond = time_series_data_split_condition(df,
                                          date_parts,
                                          {threshold})
        train_index = df[cond].index
        valid_index = df[~cond].index
        splits = (list(train_index), list(valid_index))

# 有序特征
ordinal_features = {ordinal_features}
if len(ordinal_features) > 0:
    for feature_dict in ordinal_features:
        for ordinal_feature, order in feature_dict.items():
            df[ordinal_feature] = df[ordinal_feature].astype("category").cat.set_categories(order, ordered=True)

if not {classification}:
    # 如果是回归任务，对目标变量进行对数变换以处理偏态
    df["{target}"] = np.log1p(df["{target}"])

# 自动识别连续变量和分类变量
cont, cat = cont_cat_split(df, dep_var="{target}")



# 创建 TabularDataLoaders，用于数据加载和预处理
dls = TabularDataLoaders.from_df(
    df,
    y_names="{target}",  # 指定目标变量
    cont_names=cont,  # 指定连续变量
    cat_names=cat,   # 指定分类变量
    procs=[
        Categorify,  # 将分类变量转换为数值编码
        FillMissing, # 处理缺失值
    ],
    splits=splits,
)

# 根据任务类型选择评估指标和模型
if {classification}:
    metrics = [
        accuracy_score,
        lambda y, p: recall_score(y, p, average="{avg_param}"),
        lambda y, p: precision_score(y, p, average="{avg_param}"),
        lambda y, p: f1_score(y, p, average="{avg_param}"),
    ]
    metric_names = [
        "accuracy_score",
        "recall_score",
        "precision_score", 
        "f1_score",
    ]
    RandomForest = RandomForestClassifier  # noqa: N806
else:
    metrics = [mean_squared_error, mean_absolute_error, root_mean_squared_error]
    metric_names = ["mean_squared_error", "mean_absolute_error", "root_mean_squared_error"]
    RandomForest = RandomForestRegressor  # noqa: N806

# 初始化随机森林模型
rf_model = RandomForest(n_estimators=10, random_state=42, max_depth=5, min_samples_leaf=20)

# 训练随机森林模型
rf_model.fit(dls.train.dataset.xs, dls.train.dataset.y)

# 评估模型性能
train_scores = [metric(dls.train.dataset.y, rf_model.predict(dls.train.dataset.xs)) for metric in metrics]
valid_scores = [metric(dls.valid.dataset.y, rf_model.predict(dls.valid.dataset.xs)) for metric in metrics]

# 打印评估结果
for metric_name, train_score, valid_score in zip(metric_names, train_scores, valid_scores):
    print(f"Training {{metric_name}}: {{train_score}}")
    print(f"Validation {{metric_name}}: {{valid_score}}")

# 特征重要性分析
feature_names = dls.train.dataset.xs.columns
# 计算训练集的特征重要性
train_permutation_importance = permutation_importance(
    rf_model,
    dls.train.dataset.xs,
    dls.train.dataset.y,
    n_repeats=10,
    random_state=42,
)
# 计算验证集的特征重要性
valid_permutation_importance = permutation_importance(
    rf_model, dls.valid.dataset.xs, dls.valid.dataset.y, n_repeats=10, random_state=42
)

# 创建特征重要性数据框
train_importance_df = pd.DataFrame({{"Feature": feature_names, "Importance": np.round(train_permutation_importance.importances_mean, 4)}})
valid_importance_df = pd.DataFrame({{"Feature": feature_names, "Importance": np.round(valid_permutation_importance.importances_mean, 4)}})

# 打印特征重要性结果
print("Training Set Feature Importance:")
print(train_importance_df.sort_values("Importance", ascending=False).to_string(index=False))
print("Validation Set Feature Importance:")
print(valid_importance_df.sort_values("Importance", ascending=False).to_string(index=False))

# 保存结果

# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

# 文件夹名在当前用户路径，如果没有则创建
data_folder = Path.home() / ".baicai" / "tmp"/ "data" / "{name}"
if not data_folder.exists():
    data_folder.mkdir(parents=True, exist_ok=True)

# 模型文件夹名在当前用户路径，如果没有则创建
model_folder = Path.home() / ".baicai" / "tmp"/ "models" / "{name}"
if not model_folder.exists():
    model_folder.mkdir(parents=True, exist_ok=True)

# 生成带时间戳的文件名
saved_file_name = data_folder / f"baseline_{{timestamp}}.pkl"

model_path = model_folder / f"baseline_{{timestamp}}.pkl"
dump(rf_model, model_path)
print(f"The model is saved to {{model_path}}")

# 将数据保存为pickle文件
pd.to_pickle(dls, saved_file_name)
print(f"The pickled data is saved to {{saved_file_name}}")
```
"""

# There is no missing value in the pickled data
ACTION_CODE = """
```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)

# Load the pickle file.
data = pd.read_pickle(r'{clean_data_path}')
X_train, y_train = data.train.xs, data.train.ys.values.ravel()
X_test, y_test = data.valid.xs, data.valid.ys.values.ravel()


# New action starts
# Action 1: [Name]
# First, copy the data
X_train_copy = X_train.copy()
X_test_copy = X_test.copy()
y_train_copy = y_train.copy()
y_test_copy = y_test.copy()

[action 1 implementation]

# New action starts
# Action 2: [Name]
# First, copy the data
X_train_copy = X_train.copy()
X_test_copy = X_test.copy()
y_train_copy = y_train.copy()
y_test_copy = y_test.copy()
[action 2 implementation]

[etc...]

model = RandomForestClassifier(random_state=42)
model.fit(X_train_copy, y_train_copy)

y_pred = model.predict(X_test_copy)

# Print the metrics
print("Action number: Action Name")
print("Training set some_metrics: ", some_metrics(y_train_copy, model.predict(X_train_preprocessed)))
print("Testing set some_metrics: ", some_metrics(y_test_copy, y_pred))

# Clean up memory
del X_train_copy, X_test_copy, y_train_copy, y_test_copy, model, y_pred
```
"""

WORKFLOW_CODE = """
```python
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from joblib import dump

from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    classification_report,
    mean_absolute_percentage_error,
)
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load the pickle file.
data = pd.read_pickle(r"{clean_data_path}")
X_train, y_train = data.train.xs, data.train.ys.iloc[:, 0]
X_test, y_test = data.valid.xs, data.valid.ys.iloc[:, 0]
try:
    vocab = data.vocab
except:
    vocab = {{i: v for i, v in enumerate(y_train.unique())}}

# 任务类型和评估参数
classification = {classification}
avg_param = "{avg_param}"  # 分类平均参数：'binary', 'micro', 'macro', 'weighted'

# if data length larger than 1000, random sample 1000 rows for fast testing the workflow
if len(X_train) + len(X_test) > 1000:
    train_test_ratio = len(X_train) / (len(X_train) + len(X_test))
    X_train = X_train.sample(n=int(1000 * train_test_ratio), random_state=42)
    X_test = X_test.sample(n=int(1000 * (1 - train_test_ratio)), random_state=42)
    y_train = y_train.sample(n=int(1000 * train_test_ratio), random_state=42)
    y_test = y_test.sample(n=int(1000 * (1 - train_test_ratio)), random_state=42)

# Feature Engineering

# Copy the data
X_train_copy = X_train.copy()
X_test_copy = X_test.copy()

# [IMPLEMENT **Actions**]
# Add each action with clear comments above it

# Save the processed data even if no action is implemented
# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
data_folder = Path.home() / ".baicai" / "tmp"/ "data" / "{name}"
if not data_folder.exists():
    data_folder.mkdir(parents=True, exist_ok=True)

saved_file_name = data_folder / f"workflow_{{timestamp}}.pkl"
pd.to_pickle({{"X_train": X_train_copy, "X_test": X_test_copy, "y_train": y_train, "y_test": y_test, "vocab": vocab}}, saved_file_name)

print(f"The pickled data is saved to {{saved_file_name}}")

# Model Definitions based on task type
if classification:
    models = {{
         'LinearModel': {{
             'model': LogisticRegression(random_state=42),
             'param_grid': {{
                 'max_iter': [100]
             }}
         }},
         'RandomForest': {{
             'model': RandomForestClassifier(random_state=42),
             'param_grid': {{
                 'n_estimators': [50]
             }}
         }},
         'LightGBM': {{
             'model': LGBMClassifier(random_state=42, verbose=-1),
             'param_grid': {{
                 'n_estimators': [50]
             }}
         }}
     }}
else:
    models = {{
         'LinearModel': {{
             'model': LinearRegression(),
             'param_grid': {{
                 'fit_intercept': [True, False]
             }}
         }},
         'RandomForest': {{
             'model': RandomForestRegressor(random_state=42),
             'param_grid': {{
                 'n_estimators': [50]
             }}
         }},
         'LightGBM': {{
             'model': LGBMRegressor(random_state=42, verbose=-1),
             'param_grid': {{
                 'n_estimators': [50]
             }}
         }}
     }}

# Model Training and Evaluation using transformed data
results = {{}}
best_score = -float('inf') if not classification else 0
best_model = None

print("Model Training Results:")
print("-" * 80)

# 保存模型
model_folder = Path.home() / ".baicai" / "tmp"/ "models" / "{name}"
if not model_folder.exists():
    model_folder.mkdir(parents=True, exist_ok=True)

if {time_series}:
    cv = TimeSeriesSplit(n_splits=5)
else:
    cv = 2

for model_name, config in models.items():
    print(f"\\n训练 {{model_name}} 模型...")
    
    try:
        # 根据任务类型选择评估指标
        if classification:
            # 使用F1分数作为主要评估指标
            scoring = 'f1_weighted' if len(np.unique(y_train)) > 2 else 'f1'
        else:
            # 使用R²分数作为主要评估指标
            scoring = 'r2'
        
        search = GridSearchCV(config["model"], config["param_grid"], cv=cv, n_jobs=-1, scoring=scoring)
        search.fit(X_train_copy, y_train)  # Use transformed training data
    except Exception as e:
        print(f"{{model_name}} 模型训练失败: {{str(e)}}")
        continue

    # Get best estimator
    best_estimator = search.best_estimator_
    
    # Calculate detailed metrics
    if classification:
        y_train_pred = best_estimator.predict(X_train_copy)
        y_test_pred = best_estimator.predict(X_test_copy)
        
        # Calculate all classification metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        train_precision = precision_score(y_train, y_train_pred, average=avg_param, zero_division=0)
        test_precision = precision_score(y_test, y_test_pred, average=avg_param, zero_division=0)
        train_recall = recall_score(y_train, y_train_pred, average=avg_param, zero_division=0)
        test_recall = recall_score(y_test, y_test_pred, average=avg_param, zero_division=0)
        train_f1 = f1_score(y_train, y_train_pred, average=avg_param, zero_division=0)
        test_f1 = f1_score(y_test, y_test_pred, average=avg_param, zero_division=0)
        
        # Calculate AUC if possible
        try:
            y_train_proba = best_estimator.predict_proba(X_train_copy)
            y_test_proba = best_estimator.predict_proba(X_test_copy)
            
            if len(np.unique(y_train)) == 2:
                train_auc = roc_auc_score(y_train, y_train_proba[:, 1])
                test_auc = roc_auc_score(y_test, y_test_proba[:, 1])
            else:
                train_auc = roc_auc_score(y_train, y_train_proba, multi_class='ovr', average='weighted')
                test_auc = roc_auc_score(y_test, y_test_proba, multi_class='ovr', average='weighted')
        except:
            train_auc = None
            test_auc = None
        
        current_score = test_f1
        
        # Store results
        results[model_name] = {{
            "cv_score": search.best_score_,
            "best_params": search.best_params_,
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "train_precision": train_precision,
            "test_precision": test_precision,
            "train_recall": train_recall,
            "test_recall": test_recall,
            "train_f1": train_f1,
            "test_f1": test_f1,
            "train_auc": train_auc,
            "test_auc": test_auc,
            "confusion_matrix": confusion_matrix(y_test, y_test_pred),
            "classification_report": classification_report(y_test, y_test_pred, zero_division=0)
        }}
        
        # Print results
        print(f"{{model_name}} 模型结果:")
        print(f"交叉验证分数: {{search.best_score_:.4f}}")
        print(f"最佳参数: {{search.best_params_}}")
        print(f"训练集准确率: {{train_accuracy:.4f}}")
        print(f"测试集准确率: {{test_accuracy:.4f}}")
        print(f"训练集精确率: {{train_precision:.4f}}")
        print(f"测试集精确率: {{test_precision:.4f}}")
        print(f"训练集召回率: {{train_recall:.4f}}")
        print(f"测试集召回率: {{test_recall:.4f}}")
        print(f"训练集F1分数: {{train_f1:.4f}}")
        print(f"测试集F1分数: {{test_f1:.4f}}")
        if train_auc is not None:
            print(f"训练集AUC: {{train_auc:.4f}}")
            print(f"测试集AUC: {{test_auc:.4f}}")
        
    else:
        # Regression metrics
        y_train_pred = best_estimator.predict(X_train_copy)
        y_test_pred = best_estimator.predict(X_test_copy)
        
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_rmse = np.sqrt(train_mse)
        test_rmse = np.sqrt(test_mse)
        train_mape = mean_absolute_percentage_error(y_train, y_train_pred)
        test_mape = mean_absolute_percentage_error(y_test, y_test_pred)
        
        current_score = test_r2
        
        # Store results
        results[model_name] = {{
            "cv_score": search.best_score_,
            "best_params": search.best_params_,
            "train_r2": train_r2,
            "test_r2": test_r2,
            "train_mae": train_mae,
            "test_mae": test_mae,
            "train_mse": train_mse,
            "test_mse": test_mse,
            "train_rmse": train_rmse,
            "test_rmse": test_rmse,
            "train_mape": train_mape,
            "test_mape": test_mape,
        }}
        
        # Print results
        print(f"{{model_name}} 模型结果:")
        print(f"交叉验证分数: {{search.best_score_:.4f}}")
        print(f"最佳参数: {{search.best_params_}}")
        print(f"训练集R²: {{train_r2:.4f}}")
        print(f"测试集R²: {{test_r2:.4f}}")
        print(f"训练集MAE: {{train_mae:.4f}}")
        print(f"测试集MAE: {{test_mae:.4f}}")
        print(f"训练集RMSE: {{train_rmse:.4f}}")
        print(f"测试集RMSE: {{test_rmse:.4f}}")
        print(f"训练集MAPE: {{train_mape:.4f}}")
        print(f"测试集MAPE: {{test_mape:.4f}}")

    # Update best model
    if current_score > best_score:
        best_score = current_score
        best_model = model_name

    model_path = model_folder / f"{{model_name}}_{{timestamp}}.pkl"
    dump(best_estimator, model_path)
    print(f"模型已保存至: {{model_path}}")

# Print best model results
print("\\n" + "=" * 80)
print("最佳模型总结:")
print("=" * 80)
print(f"最佳模型: {{best_model}}")
print(f"最佳分数: {{best_score:.4f}}")
print(f"最佳参数: {{results[best_model]['best_params']}}")

if classification:
    print("\\n混淆矩阵:")
    print(results[best_model]['confusion_matrix'])
    print("\\n分类报告:")
    print(results[best_model]['classification_report'])

print("=" * 80)
```
"""
