from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import joblib
from .base import BaseTransformer
from .exceptions import InvalidStepError, TransforyError, NotFittedError, FrozenTransformerError, PipelineLogicError, PipelineProcessingError, ConfigurationError
from .scaler import Scaler
from .encoder import Encoder
from .outlier import OutlierHandler


class Pipeline(BaseTransformer):
    """
    A pipeline that chains multiple transformers sequentially.

    Example:
    --------
    >>> from transfory.base import ExampleScaler
    >>> from transfory.Transfory.pipeline import Pipeline
    >>> from transfory.imputer import Imputer
    >>> from transfory.encoder import Encoder
    >>> pipe = Pipeline([
    ...     ("imputer", Imputer(strategy="mean")),
    ...     ("encoder", Encoder(method="label")),
    ...     ("scaler", ExampleScaler())
    ... ])
    >>> pipe.fit(df_train)
    >>> df_transformed = pipe.transform(df_test)
    """

    def __init__(self, steps: List[Tuple[str, BaseTransformer]], name: Optional[str] = None,
                 logging_callback: Optional[callable] = None):
        super().__init__(name=name or "Pipeline", logging_callback=logging_callback)
        self.steps = steps
        self.named_steps = self._validate_steps()
        self._validate_logical_order()

    # ------------------------------
    # Validation
    # ------------------------------
    def _validate_steps(self) -> Dict[str, BaseTransformer]:
        """
        Validates that the steps are a list of tuples and that each transformer
        is valid.
        """
        if not isinstance(self.steps, list) or not all(isinstance(s, tuple) and len(s) == 2 for s in self.steps):
            raise TypeError("The 'steps' argument must be a list of (name, transformer) tuples.")

        names, transformers = zip(*self.steps)
        
        if len(set(names)) != len(names):
            raise ValueError(f"Transformer names must be unique. Found duplicates: {names}")
        
        for name, transformer in self.steps:
            if transformer != 'passthrough' and not (hasattr(transformer, "fit") and hasattr(transformer, "transform")):
                raise InvalidStepError(
                    f"All steps in a pipeline must be transformers with 'fit' and 'transform' methods, "
                    f"or the string 'passthrough'. Step '{name}' is of type {type(transformer).__name__} which is not a valid transformer."
                )
        return dict(self.steps)

    def _validate_logical_order(self) -> None:
        """
        Performs heuristic checks for common logical errors in pipeline ordering.
        Uses CLASS-NAME string matching to avoid import-path mismatch issues.
        """

        # Extract (name, class_name) for each step
        step_info = [(name, trans.__class__.__name__) for name, trans in self.steps]

        # 1. Find first Encoder position
        encoder_positions = [
            idx for idx, (_, class_name) in enumerate(step_info)
            if class_name == "Encoder"
        ]

        if not encoder_positions:
            return  # No encoder → nothing to validate

        first_encoder_idx = encoder_positions[0]
        first_encoder_name = step_info[first_encoder_idx][0]

        # 2. Check for Scaler or OutlierHandler before the Encoder
        for i in range(first_encoder_idx):
            step_name, class_name = step_info[i]

            if class_name in ("Scaler", "OutlierHandler"):
                raise PipelineLogicError(
                    f"Logical order error: Step '{step_name}' ({class_name}) appears before "
                    f"step '{first_encoder_name}' (Encoder). Numeric transformers "
                    f"should run AFTER categorical encoding."
                )



    # ------------------------------
    # Core fitting logic
    # ------------------------------
    def _fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> None:
        current_data = X
        last_step_idx = len(self.steps) - 1
        for i, (name, transformer) in enumerate(self.steps):
            # Pass the pipeline's callback and the step name to the transformer
            # The lambda now correctly uses the step_name from the child, which is crucial for ColumnTransformer
            if self._logging_callback:
                # This lambda captures the pipeline's step name (`name`) but passes the child's
                # own `step_name` to the callback. This preserves nested names like "ct::imputer".
                # We now prepend the pipeline step name to create a nested name.
                transformer._logging_callback = lambda child_step_name, payload, pipeline_step_name=name: self._logging_callback(
                    f"{pipeline_step_name}::{child_step_name}", payload
                )

            self._log("fit_step_start", {"step": name, "shape": current_data.shape})
            try:
                if i < last_step_idx:
                    current_data = transformer.fit_transform(current_data, y)
                else: # For the last step, just fit.
                    transformer.fit(current_data, y)
            except Exception as e:
                raise PipelineProcessingError(
                    f"Error during 'fit' in step '{name}' ({transformer.__class__.__name__}): {e}"
                ) from e
                
            self._log("fit_end", {"step": name, "output_shape": current_data.shape})

        # This part of _fit is for the pipeline itself, not individual steps
        self._fitted_params = {
            "step_names": [n for n, _ in self.steps],
            "n_steps": len(self.steps),
        }

    # ------------------------------
    # Core transformation logic
    # ------------------------------
    def _transform(self, X: pd.DataFrame) -> pd.DataFrame:
        current_data = X
        for name, transformer in self.steps:
            # Pass the pipeline's callback to the transformer
            if self._logging_callback:
                transformer._logging_callback = lambda child_step_name, payload, pipeline_step_name=name: self._logging_callback(
                    f"{pipeline_step_name}::{child_step_name}", payload
                )

            self._log("transform_step", {"step": name, "input_shape": current_data.shape})
            try:
                current_data = transformer.transform(current_data)
            except Exception as e:
                raise PipelineProcessingError(
                    f"Error during 'transform' in step '{name}' ({transformer.__class__.__name__}): {e}"
                ) from e

            self._log("transform_done", {"step": name, "output_shape": current_data.shape})
        return current_data

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """
        Fit all transformers and transform the data.

        This overrides the base `fit_transform` to provide a more efficient
        implementation for pipelines, avoiding a redundant final transform.
        """
        if self._frozen:
            raise FrozenTransformerError(f"Transformer {self.name} is frozen and cannot be refit.")

        self._validate_input(X)
        current_data = X
        for name, transformer in self.steps:
            # Pass the pipeline's callback to the transformer
            if self._logging_callback:
                transformer._logging_callback = lambda child_step_name, payload, pipeline_step_name=name: self._logging_callback(
                    f"{pipeline_step_name}::{child_step_name}", payload
                )

            self._log("fit_transform_step", {"step": name, "input_shape": current_data.shape})
            try:
                current_data = transformer.fit_transform(current_data, y)
            except Exception as e:
                raise PipelineProcessingError(
                    f"Error during 'fit_transform' in step '{name}' ({transformer.__class__.__name__}): {e}"
                ) from e

            self._log("fit_transform_done", {"step": name, "output_shape": current_data.shape})

        self._is_fitted = True
        return current_data

    # ------------------------------
    # Step management
    # ------------------------------
    def add_step(self, name: str, transformer: BaseTransformer) -> None:
        """Add a new transformer at the end of the pipeline."""
        if not isinstance(transformer, BaseTransformer):
            raise TypeError("New step must inherit from BaseTransformer.")
        self.steps.append((name, transformer))
        self._validate_steps()

    def remove_step(self, name: str) -> None:
        """Remove a transformer by name."""
        before = len(self.steps)
        self.steps = [(n, t) for (n, t) in self.steps if n != name]
        after = len(self.steps)
        if before == after:
            raise ValueError(f"No step named '{name}' found.")

    def get_step(self, name: str) -> Optional[BaseTransformer]:
        """Retrieve a transformer by name."""
        for n, t in self.steps:
            if n == name:
                return t
        return None

    # ------------------------------
    # Persistence
    # ------------------------------
    def save(self, filepath: str) -> None:
        """Save the entire pipeline (and all transformers) to disk."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "Pipeline":
        """Load a previously saved pipeline."""
        obj = joblib.load(filepath)
        if not isinstance(obj, Pipeline):
            raise TypeError("Loaded object is not a Pipeline.")
        return obj

    # ------------------------------
    # Representation
    # ------------------------------
    def __repr__(self) -> str:
        step_names = " → ".join([name for name, _ in self.steps])
        return f"<Pipeline ({len(self.steps)} steps): {step_names}>"
