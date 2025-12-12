"""
Custom exception classes for the Transfory library.
"""

class TransforyError(Exception):
    """Base class for all exceptions in the Transfory library."""
    pass


class InvalidStepError(TransforyError, TypeError):
    """Raised when a step in a Pipeline or ColumnTransformer is not a valid transformer."""
    pass

class NotFittedError(TransforyError, RuntimeError):
    """Raised when transform is called before fit."""
    pass

class FrozenTransformerError(TransforyError, RuntimeError):
    """Raised when attempting to fit a frozen transformer."""
    pass

class ConfigurationError(TransforyError, ValueError):
    """Raised when a transformer is configured with invalid or conflicting parameters."""
    pass

class ColumnMismatchError(TransforyError, ValueError):
    """Raised when columns during transform do not match columns from fit."""
    pass

class NoApplicableColumnsError(TransforyError, ValueError):
    """Raised when a transformer finds no columns to apply its transformation to."""
    pass

class PipelineProcessingError(TransforyError, RuntimeError):
    """Raised when an error occurs during the execution of a pipeline step."""
    pass

class PipelineLogicError(TransforyError, ValueError):
    """Raised when the order of transformers in a pipeline is likely to cause unintended behavior."""
    pass