from enum import Enum


class TaskType(Enum):
    """Task types for different AI tasks.

    Defines the main categories of AI tasks supported by the system.

    Attributes:
        VISION_*: Computer vision related tasks
        NLP: Natural Language Processing tasks
        COLLABORATIVE: Recommendation system tasks
        ML: Traditional machine learning tasks
    """

    # Vision tasks
    VISION = "Vision"
    VISION_CSV = "Vision CSV Learner"
    VISION_FUNC = "Vision Func Learner"
    VISION_RE = "Vision RE Learner"
    VISION_MULTI_LABEL = "Vision Multi Label Learner"
    VISION_SINGLE_LABEL = "Vision Single Label Learner"

    # NLP tasks
    NLP = "NLP"
    NLP_SENTIMENT_INFERENCE = "Sentiment Inference"
    NLP_NER_INFERENCE = "NER Inference"
    NLP_SEMANTIC_MATCH_INFERENCE = "Semantic Match Inference"
    NLP_SENTIMENT_TRAINER = "Sentiment Trainer"

    # Collaborative Filtering tasks
    COLLABORATIVE = "Collaborative"

    # ML
    ML = "ML"
