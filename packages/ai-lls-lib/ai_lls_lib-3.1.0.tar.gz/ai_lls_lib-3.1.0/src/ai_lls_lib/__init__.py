"""
AI LLS Library - Core business logic for Landline Scrubber.

This library provides phone verification and DNC checking capabilities.

Version 2.0.0 establishes clean semantic versioning baseline.
All version management now controlled by Python Semantic Release.

Dependencies optimized for Lambda deployment (removed unused pandas/pyarrow).
"""

from ai_lls_lib.core.cache import DynamoDBCache
from ai_lls_lib.core.models import (
    BulkJob,
    BulkJobStatus,
    JobStatus,
    LineType,
    PhoneVerification,
    VerificationSource,
)
from ai_lls_lib.core.processor import BulkProcessor
from ai_lls_lib.core.verifier import PhoneVerifier

__version__ = "3.1.0"

__all__ = [
    "PhoneVerification",
    "BulkJob",
    "BulkJobStatus",
    "LineType",
    "VerificationSource",
    "JobStatus",
    "PhoneVerifier",
    "BulkProcessor",
    "DynamoDBCache",
]
