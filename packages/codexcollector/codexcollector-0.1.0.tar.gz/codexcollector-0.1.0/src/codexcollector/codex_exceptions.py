"""
Custom exceptions for the CodexCollector module.

This module defines exception classes used throughout the document collection
pipeline to distinguish between different failure modes.
"""


class IngestionError(Exception):
    """
    Raised when document ingestion or extraction fails.

    This exception indicates that a document could not be processed due to:
    - Corrupted or malformed file formats
    - Encrypted PDFs without password
    - Failed web downloads
    - Invalid document structures

    Unlike OSError (which indicates filesystem/network problems), IngestionError
    indicates the document itself is problematic.
    """
    pass


class ConfigurationError(Exception):
    """
    Raised when CodexCollector is misconfigured.

    This exception indicates invalid initialization parameters such as:
    - Negative file size limits
    - Invalid timeout values
    - Malformed extension sets
    - Type mismatches in configuration

    ConfigurationError is raised during __init__ to fail fast on bad configuration
    rather than during collection when errors would be harder to diagnose.
    """
    pass
