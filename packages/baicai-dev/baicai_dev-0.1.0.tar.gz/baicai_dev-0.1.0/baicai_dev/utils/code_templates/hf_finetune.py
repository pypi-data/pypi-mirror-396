_IMPORT = """
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)
"""

_SENTIMENT_CLASSIFIER = """
class SentimentClassifier:
    def __init__(
        self,
        model=None,
        model_path=None,
        use_gpu=None,
        num_labels=2,
        label_mapping=None,  # 添加标签映射参数
    ):
        self.model = "hfl/chinese-bert-wwm" if model is None else model
        self.model_path = model_path
        self.use_gpu = torch.cuda.is_available() if use_gpu is None else use_gpu
        self.device = torch.device("cuda" if self.use_gpu else "cpu")
        self.num_labels = num_labels

        # 设置默认的标签映射或使用自定义映射
        self.label_mapping = label_mapping or {{0: "负面", 1: "正面"}}

        # Initialize model and tokenizer
        if model_path:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model, num_labels=self.num_labels)

        self.model = self.model.to(self.device)

    @staticmethod
    def _compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return {{
            "accuracy": accuracy_score(labels, predictions),
            "f1": f1_score(labels, predictions, average="macro"),
        }}

    def train(
        self,
        path,
        text_column="comment",  # 文本列名
        label_column="sentiment",  # 标签列名
        output_dir="./results",
        num_epochs=3,
        test_size=0.2,
        max_length=128,
    ):
        # Load data
        df = pd.read_csv(path)

        # 验证必要的列是否存在
        if text_column not in df.columns:
            raise ValueError(f"文本列 '{{text_column}}' 不存在于数据中")
        if label_column not in df.columns:
            raise ValueError(f"标签列 '{{label_column}}' 不存在于数据中")

        dataset = Dataset.from_pandas(df)
        dataset = dataset.train_test_split(test_size=test_size, seed=42)

        # 更新预处理函数的参数
        self._preprocess_function = lambda examples: self.__preprocess_data(
            examples, text_column=text_column, label_column=label_column, max_length=max_length
        )

        # Preprocess data
        tokenized_dataset = dataset.map(
            self._preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names,
        )

        # Training arguments
        train_batch_size = 16 if self.use_gpu else 8
        eval_batch_size = 32 if self.use_gpu else 16

        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=2e-5,
            per_device_train_batch_size=train_batch_size,
            per_device_eval_batch_size=eval_batch_size,
            num_train_epochs=num_epochs,
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            use_cpu=not self.use_gpu,
            fp16=self.use_gpu,
            logging_dir="./logs",
            logging_steps=100,
            save_total_limit=2,
            report_to="none",
        )

        # Freeze layers
        self._freeze_layers()

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["test"],
            processing_class=self.tokenizer,
            data_collator=DataCollatorWithPadding(self.tokenizer),
            compute_metrics=self._compute_metrics,
        )

        # Train and evaluate
        trainer.train()
        eval_results = trainer.evaluate()

        # Save model
        model_save_path = f"{{output_dir}}/best_model"
        trainer.save_model(model_save_path)
        self.tokenizer.save_pretrained(model_save_path)

        return eval_results, model_save_path

    def predict(self, text, max_length=128):
        self.model.eval()
        inputs = self.tokenizer(text, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
        inputs = {{k: v.to(self.device) for k, v in inputs.items()}}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits.softmax(dim=-1)
            prediction = probs.argmax(dim=-1).item()

        return {{
            "text": text,
            "sentiment": self.label_mapping[prediction],  # 使用标签映射
            "confidence": probs[0][prediction].cpu().item(),
            "probabilities": {{  # 添加所有类别的概率
                self.label_mapping[i]: prob.cpu().item() for i, prob in enumerate(probs[0])
            }},
        }}

    def __preprocess_data(self, examples, text_column, label_column, max_length):
        result = self.tokenizer(examples[text_column], truncation=True, padding=True, max_length=max_length)
        result["labels"] = examples[label_column]
        return result

    def _freeze_layers(self):
        for name, param in self.model.named_parameters():
            if "classifier" not in name:
                param.requires_grad = False

        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"可训练参数: {{trainable_params:,}} ({{100 * trainable_params / total_params:.2f}}% of {{total_params:,}} total)")
"""

_TRAIN_SENTIMENT_CLASSIFIER = """
# 使用示例：
# 自定义标签映射示例
# label_mapping = {{0: "消极", 1: "积极"}}

# 初始化分类器
classifier = SentimentClassifier(
    num_labels={num_labels},
    label_mapping={label_mapping},
)

# 训练模型
eval_results, model_path = classifier.train(
    path=r"{path}",
    text_column="{text_column}",  # 自定义文本列名
    label_column="{label_column}",  # 自定义标签列名
    num_epochs={num_epochs},
)

# 预测示例
# test_texts = [
#     "这家餐厅的服务非常好，菜品也很新鲜！",
#     "太差了，菜品完全不新鲜，服务态度也很差",
#     "一般般，没什么特别的",
# ]

for text in {texts}:
    result = classifier.predict(text)
    print(f"Text: {{result['text']}}")
    print(f"Sentiment: {{result['sentiment']}}")
    print(f"Confidence: {{result['confidence']:.4f}}")
"""

SENTIMENT_CLASSIFIER_TRAIN_CODE = (
    "```python\n" + _IMPORT + _SENTIMENT_CLASSIFIER + _TRAIN_SENTIMENT_CLASSIFIER + "\n```"
)
