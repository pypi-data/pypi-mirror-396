"""Italian tax validators for Codice Fiscale and Partita IVA.

This package provides validation utilities for Italian tax identification
numbers:
- Codice Fiscale (CF): Personal tax identification code
- Partita IVA (P.IVA): VAT identification number

Example:
    >>> from italian_tax_validators import (
    ...     validate_codice_fiscale, validate_partita_iva
    ... )
    >>> cf_result = validate_codice_fiscale("RSSMRA85M01H501Q")
    >>> piva_result = validate_partita_iva("12345678903")

"""

from italian_tax_validators.validators import (
    CF_EVEN_VALUES,
    CF_MONTH_CODES,
    CF_MONTH_CODES_REVERSE,
    CF_ODD_VALUES,
    CF_OMOCODIA_CHARS,
    CF_OMOCODIA_DIGITS,
    MINIMUM_AGE_YEARS,
    Gender,
    CodiceFiscaleGenerator,
    CodiceFiscaleGenerationResult,
    CodiceFiscaleValidator,
    CodiceFiscaleValidationResult,
    PartitaIvaValidator,
    PartitaIvaValidationResult,
    generate_codice_fiscale,
    validate_codice_fiscale,
    validate_partita_iva,
)
from italian_tax_validators.comuni import (
    CODICI_CATASTALI,
    get_cadastral_code,
    get_municipality_info,
    is_foreign_country,
    search_municipality,
)

__version__ = "1.1.0"
__author__ = "Michele Broggi"
__license__ = "MIT"

__all__ = [
    # Validators
    "CodiceFiscaleValidator",
    "PartitaIvaValidator",
    # Generator
    "CodiceFiscaleGenerator",
    # Result classes
    "CodiceFiscaleValidationResult",
    "PartitaIvaValidationResult",
    "CodiceFiscaleGenerationResult",
    # Convenience functions
    "validate_codice_fiscale",
    "validate_partita_iva",
    "generate_codice_fiscale",
    # Municipality utilities
    "CODICI_CATASTALI",
    "get_municipality_info",
    "get_cadastral_code",
    "search_municipality",
    "is_foreign_country",
    # Constants
    "CF_ODD_VALUES",
    "CF_EVEN_VALUES",
    "CF_MONTH_CODES",
    "CF_MONTH_CODES_REVERSE",
    "CF_OMOCODIA_CHARS",
    "CF_OMOCODIA_DIGITS",
    "MINIMUM_AGE_YEARS",
    # Type aliases
    "Gender",
]
