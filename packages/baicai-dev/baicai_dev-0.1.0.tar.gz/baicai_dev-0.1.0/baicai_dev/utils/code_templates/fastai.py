# 导入 FastAI 视觉模块的模板字符串
_VISION_IMPORT = """
from fastai.vision.all import *
"""

# 导入 FastAI 协同过滤和表格数据模块的模板字符串
_COLLAB_IMPORT = """
from fastai.collab import *
from fastai.tabular.all import *
"""

# 数据路径处理模板，支持本地路径和URL
_LOAD_DATA = """
# if the path is a URL, use untar_data, or just use the path
path = str(r"{path}")
path = untar_data(path) if path.startswith('http') else path
"""

# 单标签分类模型训练模板
_SINGLE_CLASSIFICATION = """
learn = vision_learner(dls, {model}, metrics=error_rate)

# Should change the epochs to 3 or more
learn.fine_tune(epochs=1, freeze_epochs=1)
interp = ClassificationInterpretation.from_learner(learn)
interp.print_classification_report()

losses, idxs = interp.top_losses(k=5)
print("损失值最大的若干图片地址")
is_df = isinstance(interp.dl.items, pd.DataFrame)
for i in idxs:
    if is_df:
        print(interp.dl.items.iloc[int(i)])
    else:
        print(interp.dl.items[int(i)])
"""

# 多标签分类模型训练模板
_MULTI_CLASSIFICATION = """
# 创建宏观F1分数度量（对所有类别的F1分数取平均）
f1_macro = F1ScoreMulti(thresh=0.5, average='macro')
f1_macro.name = 'F1(macro)'
# 创建样本F1分数度量（对每个样本的F1分数取平均）
f1_samples = F1ScoreMulti(thresh=0.5, average='samples')
f1_samples.name = 'F1(samples)'
learn = vision_learner(dls,  {model}, metrics=[partial(accuracy_multi, thresh=0.5), f1_macro, f1_samples])

learn.fine_tune(epochs=1, freeze_epochs=1)

interp = ClassificationInterpretation.from_learner(learn)
interp.print_classification_report()
losses, idxs = interp.top_losses(k=5)
"""

# 最简单的数据集结构，每种分类一个文件夹
# 1. 已分割的数据集结构（使用 train 和 valid 参数）
# data/
#     train/
#         class1/
#             img1.jpg
#             img2.jpg
#         class2/
#             img1.jpg
#             img2.jpg
#     valid/
#         class1/
#             img3.jpg
#         class2/
#             img3.jpg

# 2. 未分割的数据集结构（使用 valid_pct 参数）
# data/
#     class1/
#         img1.jpg
#         img2.jpg
#     class2/
#         img1.jpg
#         img2.jpg
IMG_FOLDER_PER_CLASS = (
    "```python\n"
    + _VISION_IMPORT
    + _LOAD_DATA
    + """

dls = ImageDataLoaders.from_folder(
    path=path,               # 数据集根目录路径
    train={train_folder},    # 训练集文件夹名称，如果已经分割则指定
    valid={valid_folder},    # 验证集文件夹名称，如果已经分割则指定
    valid_pct={valid_pct},   # 验证集比例，如果未分割则使用此参数
    item_tfms=Resize({size}),     # 图像预处理变换，通常应该改为224或更高
    bs={batch_size}          # 批量大小，如果数据集太小，设为1
)
"""
    + _SINGLE_CLASSIFICATION
    + "\n```"
)


# 数据集结构不是标准的文件夹分类形式
# 1. 从文件名解析等：

# def label_func(fname):
#     return fname.stem.split("_")[0]  # 例如: 'cat_001.jpg' -> 'cat'

# 2. 从文件名中解析标签(同上2)：
# bears/
#     black/
#         img1.jpg
#         img2.jpg
#     grizzly/
#         img1.jpg
#         img2.jpg
# def label_func(fname):
#     return fname.parent.name  # 或其他标签获取逻辑

IMG_FROM_FUNC = (
    "```python\n"
    + _VISION_IMPORT
    + _LOAD_DATA
    + """
def label_func(x):
    {label_func}

dls = ImageDataLoaders.from_path_func(
    path=path,           # 数据集根目录路径
    fnames=get_image_files(path),  # 获取所有图像文件
    label_func=label_func,         # 标签提取函数
    valid_pct={valid_pct},  # 验证集比例
    item_tfms=Resize({size}),  # 图像预处理变换, 通常应该改为224或更高
    bs={batch_size}  # 批量大小, 如果数据集太小, 设为1
)
"""
    + _SINGLE_CLASSIFICATION
    + "\n```"
)

# 当所有图片都在一个文件夹，且类别信息在文件名中时（可以有子文件夹）：
# data/
#     cat_001_2020.jpg
#     cat_002_2021.jpg
#     dog_001_2020.jpg
#     dog_002_2021.jpg
#     bird_001_2020.jpg
IMG_FROM_RE = (
    "```python\n"
    + _VISION_IMPORT
    + _LOAD_DATA
    + """
dls = ImageDataLoaders.from_path_re(
    path=path,
    fnames=get_image_files(path),  # 获取所有图像文件
    valid_pct={valid_pct},        # 验证集比例
    pat="{pat}",                  # 正则表达式, 用于提取标签
    item_tfms=Resize({size}),          # 图像预处理变换, 通常应该改为224或更高
    bs={batch_size}                # 批量大小, 如果数据集太小, 设为1
)
"""
    + _SINGLE_CLASSIFICATION
    + "\n```"
)

# 适用于图片文件名和标签存储在 CSV 文件中的情况：
# data/
#     images/
#         img1.jpg
#         img2.jpg
#         img3.jpg
#     labels.csv

# 标签文件 labels.csv 的格式：
#     image,label
#     img1.jpg,label1
#     img2.jpg,label2
#     img3.jpg,label3

_IMG_LOAD_CSV = """
dls = ImageDataLoaders.from_csv(
    path=path,              # 数据根目录
    folder={folder},        # 数据集文件夹名称, 如果已经分割则指定
    csv_fname={csv_file},   # 标签文件名
    fn_col={image_col},     # 图像文件名列名
    label_col={label_col},  # 标签列名
    valid_col={valid_col},  # 验证集列名, 如果未分割则使用此参数
    valid_pct={valid_pct},  # 验证集比例, 如果未分割则使用此参数
    item_tfms=Resize({size}),    # 图像预处理变换, 通常应该改为224或更高
    delimiter={delimiter}, # 分隔符, 如果未指定则使用默认分隔符
    label_delim={label_delim}, # 标签分隔符, 如果未指定则使用默认分隔符
    bs={batch_size}          # 批量大小, 如果数据集太小, 设为1
)
"""

FROM_CSV = "```python\n" + _VISION_IMPORT + _LOAD_DATA + _IMG_LOAD_CSV + _SINGLE_CLASSIFICATION + "\n```"

MULTI_LABEL = "```python\n" + _VISION_IMPORT + _LOAD_DATA + _IMG_LOAD_CSV + _MULTI_CLASSIFICATION + "\n```"


_COLLAB_FROM_CSV = """
dls = CollabDataLoaders.from_csv(
    csv=path,  # 标签文件路径
    user_name={user_name},  # 用户列名
    item_name={item_name},  # 物品列名
    rating_name={rating_name},  # 评分列名
    valid_pct={valid_pct},  # 验证集比例, 如果未分割则使用此参数
)
"""

_COLLAB_LEARN = """
learn = collab_learner(dls, y_range=({y_range_min},{y_range_max}))
learn.fine_tune(10)
print(f"Final valid loss: {{learn.validate()[0]:.3f}}")
"""

COLLAB = "```python\n" + _COLLAB_IMPORT + _LOAD_DATA + _COLLAB_FROM_CSV + _COLLAB_LEARN + "\n```"
