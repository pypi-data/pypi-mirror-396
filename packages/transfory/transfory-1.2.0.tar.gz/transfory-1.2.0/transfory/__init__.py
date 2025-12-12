"""
Transfory: An Object-Oriented, Explainable Data Transformation Toolkit for Python.
"""

# --- Core Orchestrators ---
from .pipeline import Pipeline
from .column_transformer import ColumnTransformer

# --- Data Transformers ---
from .missing import MissingValueHandler
from .encoder import Encoder
from .scaler import Scaler
from .outlier import OutlierHandler
from .datetime import DatetimeFeatureExtractor
from .featuregen import FeatureGenerator

from .base import BaseTransformer
# --- Explainability ---
from .insight import InsightReporter

# --- Custom Exceptions ---
from .exceptions import (
    TransforyError,
    InvalidStepError,
    NotFittedError,
    FrozenTransformerError,
    ConfigurationError,
    ColumnMismatchError,
    NoApplicableColumnsError,
    PipelineProcessingError,
    PipelineLogicError,
)