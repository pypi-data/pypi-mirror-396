"""
Runtime Validator Service

A lightweight utility that can be imported into any data processing script.
Uses generated Pydantic models to perform data validation.

Supports two modes:
1. Database-backed: Retrieve schemas/rules from metadata store
2. Contract-based: Validate directly against contract files/dicts (no database)
"""

from pycharter.runtime_validator.runtime_validator import (
    get_model_from_contract,
    get_model_from_store,
    validate_batch_with_contract,
    validate_batch_with_store,
    validate_with_contract,
    validate_with_store,
)
from pycharter.runtime_validator.validator import (
    ValidationResult,
    validate,
    validate_batch,
)

__all__ = [
    # Core validation functions
    "validate",
    "validate_batch",
    "ValidationResult",
    # Database-backed validation
    "validate_with_store",
    "validate_batch_with_store",
    "get_model_from_store",
    # Contract-based validation (no database)
    "validate_with_contract",
    "validate_batch_with_contract",
    "get_model_from_contract",
]
