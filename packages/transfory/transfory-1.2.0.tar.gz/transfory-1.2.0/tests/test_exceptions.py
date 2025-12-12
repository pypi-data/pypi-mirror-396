import pytest
import pandas as pd
from transfory.pipeline import Pipeline
from transfory.scaler import Scaler
from transfory.encoder import Encoder
from transfory.missing import MissingValueHandler
from transfory.base import BaseTransformer
from transfory.exceptions import (
    ConfigurationError,
    NoApplicableColumnsError,
    PipelineLogicError,
    PipelineProcessingError,
    InvalidStepError,
    ColumnMismatchError
)

# A dummy transformer that will fail during transform
class FailingTransformer(BaseTransformer):
    def _fit(self, X, y=None):
        pass
    def _transform(self, X):
        raise ValueError("I am designed to fail.")

def test_configuration_error_raised():
    """Test that ConfigurationError is raised for invalid __init__ parameters."""
    with pytest.raises(ConfigurationError, match="`fill_value` must be provided"):
        MissingValueHandler(strategy="constant")

    with pytest.raises(ConfigurationError, match="not supported"):
        Scaler(method="invalid_method")

def test_no_applicable_columns_error_raised():
    """Test that NoApplicableColumnsError is raised when no columns can be processed."""
    df_text = pd.DataFrame({"a": ["cat", "dog"], "b": ["ham", "spam"]})
    scaler = Scaler()
    with pytest.raises(NoApplicableColumnsError, match="Scaler found no numeric columns to scale"):
        scaler.fit(df_text)

    df_numeric = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    encoder = Encoder()
    with pytest.raises(NoApplicableColumnsError, match="Encoder found no 'object' or 'category' columns"):
        encoder.fit(df_numeric)

def test_pipeline_logic_error_raised():
    """Test that PipelineLogicError is raised for incorrect pipeline ordering."""
    def create_bad_pipeline():
        return Pipeline(steps=[
            ("scaler", Scaler()),
            ("encoder", Encoder())
        ])
    with pytest.raises(PipelineLogicError, match="appears before"):
        create_bad_pipeline()

def test_pipeline_processing_error_raised():
    """Test that PipelineProcessingError is raised with context on step failure."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    
    pipeline = Pipeline(steps=[
        ("good_step", Scaler()),
        ("bad_step", FailingTransformer())
    ])

    with pytest.raises(PipelineProcessingError, match="Error during 'fit_transform' in step 'bad_step'"):
        pipeline.fit_transform(df)

def test_invalid_step_error_raised():
    """Test that InvalidStepError is raised for an invalid object in a pipeline."""
    with pytest.raises(InvalidStepError, match="not a valid transformer"):
        Pipeline(steps=[
            ("scaler", Scaler()),
            ("not_a_transformer", 123)
        ])

def test_column_mismatch_error_raised():
    """Test that ColumnMismatchError is raised when transform columns don't match fit columns."""
    df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2 = pd.DataFrame({"a": [5, 6]}) # Missing column 'b'
    
    scaler = Scaler()
    scaler.fit(df1)
    
    with pytest.raises(ColumnMismatchError, match="Missing columns"):
        scaler.transform(df2)