"""Custom exceptions leveraged by the forecasting package."""


class TensorShapeException(Exception):
    """A generic exception to be used for tensor shape mismatches."""


class GitImportException(Exception):
    """Exception thrown when git import failed but is needed by a function in the code path"""
