"""Custom exceptions for the Hayagriva framework."""


class HayagrivaError(Exception):
    """Base exception for Hayagriva."""


class MissingDependencyError(HayagrivaError):
    """Raised when an optional dependency is not installed."""


class ConfigurationError(HayagrivaError):
    """Raised when invalid configuration is provided."""


class IngestionError(HayagrivaError):
    """Raised when document ingestion fails."""


class GenerationError(HayagrivaError):
    """Raised when response generation fails."""
