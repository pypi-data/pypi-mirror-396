"""Validators for Italian tax identification documents.

This module provides validation utilities for Italian tax IDs:
- Codice Fiscale (CF): Personal tax identification code
- Partita IVA (P.IVA): VAT identification number

Both validators include format validation, check digit verification,
and additional business logic (e.g., age verification for CF).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Literal

from italian_tax_validators.comuni import (
    get_municipality_info,
    is_foreign_country,
)

# Minimum age required for certain operations (e.g., Pro registration)
MINIMUM_AGE_YEARS = 18

# Gender types
Gender = Literal["M", "F"]

# ============================================================================
# Codice Fiscale (CF) Validation Tables
# ============================================================================

# Odd position character values (1st, 3rd, 5th, etc. - 1-indexed)
CF_ODD_VALUES = {
    "0": 1,
    "1": 0,
    "2": 5,
    "3": 7,
    "4": 9,
    "5": 13,
    "6": 15,
    "7": 17,
    "8": 19,
    "9": 21,
    "A": 1,
    "B": 0,
    "C": 5,
    "D": 7,
    "E": 9,
    "F": 13,
    "G": 15,
    "H": 17,
    "I": 19,
    "J": 21,
    "K": 2,
    "L": 4,
    "M": 18,
    "N": 20,
    "O": 11,
    "P": 3,
    "Q": 6,
    "R": 8,
    "S": 12,
    "T": 14,
    "U": 16,
    "V": 10,
    "W": 22,
    "X": 25,
    "Y": 24,
    "Z": 23,
}

# Even position character values (2nd, 4th, 6th, etc. - 1-indexed)
CF_EVEN_VALUES = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
    "I": 8,
    "J": 9,
    "K": 10,
    "L": 11,
    "M": 12,
    "N": 13,
    "O": 14,
    "P": 15,
    "Q": 16,
    "R": 17,
    "S": 18,
    "T": 19,
    "U": 20,
    "V": 21,
    "W": 22,
    "X": 23,
    "Y": 24,
    "Z": 25,
}

# Month codes for Codice Fiscale (A=January, B=February, etc.)
CF_MONTH_CODES = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "H": 6,
    "L": 7,
    "M": 8,
    "P": 9,
    "R": 10,
    "S": 11,
    "T": 12,
}

# Omocodia substitution characters (digits can be replaced with these letters)
# Used when two people have the same CF
CF_OMOCODIA_CHARS = {
    "L": "0",
    "M": "1",
    "N": "2",
    "P": "3",
    "Q": "4",
    "R": "5",
    "S": "6",
    "T": "7",
    "U": "8",
    "V": "9",
}

# Reverse mapping: digit to omocodia character
CF_OMOCODIA_DIGITS = {v: k for k, v in CF_OMOCODIA_CHARS.items()}

# Reverse mapping: month number to code letter
CF_MONTH_CODES_REVERSE = {v: k for k, v in CF_MONTH_CODES.items()}


@dataclass
class CodiceFiscaleValidationResult:
    """Result of Codice Fiscale validation.

    Attributes:
        is_valid: Whether the CF is valid
        error_code: Error code if invalid (None if valid)
        formatted_value: The cleaned/formatted CF value
        birthdate: Extracted birthdate (None if extraction failed)
        age: Calculated age in years (None if birthdate extraction failed)
        gender: Extracted gender ("M" or "F", None if extraction failed)
        birth_place_code: Cadastral code of birth place
        birth_place_name: Name of birth municipality/country
        birth_place_province: Province code (or "EE" for foreign countries)
        is_foreign_born: Whether born outside Italy

    """

    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None
    birthdate: date | None = None
    age: int | None = None
    gender: Gender | None = None
    birth_place_code: str | None = None
    birth_place_name: str | None = None
    birth_place_province: str | None = None
    is_foreign_born: bool | None = None


@dataclass
class PartitaIvaValidationResult:
    """Result of Partita IVA validation.

    Attributes:
        is_valid: Whether the P.IVA is valid
        error_code: Error code if invalid (None if valid)
        formatted_value: The cleaned/formatted P.IVA value
        is_temporary: Whether this is a temporary VAT number (starts with 99)
        province_code: Provincial office code (digits 8-10)

    """

    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None
    is_temporary: bool | None = None
    province_code: str | None = None


class CodiceFiscaleValidator:
    """Validator for Italian Codice Fiscale (CF).

    The Codice Fiscale is a 16-character alphanumeric code that encodes:
    - Surname (3 characters)
    - Name (3 characters)
    - Birth year (2 digits)
    - Birth month (1 letter)
    - Birth day and gender (2 digits, +40 for females)
    - Birth place code (4 characters)
    - Check character (1 letter)

    This validator handles:
    - Format validation
    - Omocodia (substitution of digits with letters)
    - Check digit verification
    - Birthdate extraction
    - Age calculation

    Example:
        >>> validator = CodiceFiscaleValidator()
        >>> result = validator.validate("RSSMRA85M01H501Z")
        >>> print(result.is_valid)
        True

    """

    # Positions where omocodia substitution can occur (0-indexed)
    OMOCODIA_POSITIONS = [6, 7, 9, 10, 12, 13, 14]

    # Regex pattern for CF format (allowing omocodia)
    CF_PATTERN = re.compile(
        r"^[A-Z]{6}[A-Z0-9]{2}[A-Z][A-Z0-9]{2}[A-Z][A-Z0-9]{3}[A-Z]$"
    )

    def validate(
        self,
        value: str,
        check_adult: bool = False,
        minimum_age: int = MINIMUM_AGE_YEARS,
    ) -> CodiceFiscaleValidationResult:
        """Validate an Italian Codice Fiscale.

        Args:
            value: The CF string to validate
            check_adult: Whether to verify the person is at least minimum_age
                years old
            minimum_age: Minimum age required (default: 18)

        Returns:
            CodiceFiscaleValidationResult with validation details

        """
        # Clean and uppercase the value
        clean_value = value.strip().upper().replace(" ", "")

        # Step 1: Validate format
        if not self._validate_format(clean_value):
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_invalid_format",
                formatted_value=clean_value,
            )

        # Step 2: Validate check digit
        if not self._validate_check_digit(clean_value):
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_invalid_format",
                formatted_value=clean_value,
            )

        # Step 3: Extract birthdate and gender
        birthdate, gender = self._extract_birthdate_and_gender(clean_value)
        age = None

        if birthdate is None:
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_cannot_decode_birthdate",
                formatted_value=clean_value,
            )

        # Calculate age
        today = date.today()
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )

        # Step 4: Extract birth place
        birth_place_code = clean_value[11:15]
        birth_place_info = get_municipality_info(birth_place_code)
        birth_place_name = None
        birth_place_province = None
        foreign_born = is_foreign_country(birth_place_code)

        if birth_place_info:
            birth_place_name, birth_place_province = birth_place_info

        # Step 5: Check age if required
        if check_adult and age < minimum_age:
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_underage",
                formatted_value=clean_value,
                birthdate=birthdate,
                age=age,
                gender=gender,
                birth_place_code=birth_place_code,
                birth_place_name=birth_place_name,
                birth_place_province=birth_place_province,
                is_foreign_born=foreign_born,
            )

        # All validations passed
        return CodiceFiscaleValidationResult(
            is_valid=True,
            formatted_value=clean_value,
            birthdate=birthdate,
            age=age,
            gender=gender,
            birth_place_code=birth_place_code,
            birth_place_name=birth_place_name,
            birth_place_province=birth_place_province,
            is_foreign_born=foreign_born,
        )

    def _validate_format(self, cf: str) -> bool:
        """Validate CF format using regex pattern.

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            True if format matches the expected pattern

        """
        return len(cf) == 16 and bool(self.CF_PATTERN.match(cf))

    def _decode_omocodia(self, cf: str) -> str:
        """Decode omocodia characters back to digits.

        Omocodia occurs when two people have the same CF. In such cases,
        digits at positions 6, 7, 9, 10, 12, 13, 14 can be replaced with
        letters.

        Args:
            cf: 16-character CF string

        Returns:
            CF with omocodia characters replaced with digits

        """
        cf_list = list(cf)
        for pos in self.OMOCODIA_POSITIONS:
            char = cf_list[pos]
            if char in CF_OMOCODIA_CHARS:
                cf_list[pos] = CF_OMOCODIA_CHARS[char]
        return "".join(cf_list)

    def _validate_check_digit(self, cf: str) -> bool:
        """Validate CF check digit.

        The check digit is calculated by:
        1. Summing values for characters at odd positions (1-indexed)
        2. Summing values for characters at even positions (1-indexed)
        3. Taking the remainder of total sum divided by 26
        4. Converting to letter (A=0, B=1, etc.)

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            True if check digit is valid

        """
        # Decode omocodia for check digit calculation
        decoded_cf = self._decode_omocodia(cf)

        total = 0
        for i, char in enumerate(decoded_cf[:15]):
            if i % 2 == 0:
                # Odd positions (1-indexed) = even index (0-indexed)
                total += CF_ODD_VALUES.get(char, 0)
            else:
                # Even positions (1-indexed) = odd index (0-indexed)
                total += CF_EVEN_VALUES.get(char, 0)

        expected_check = chr(ord("A") + (total % 26))
        return cf[15] == expected_check

    def _extract_birthdate_and_gender(
        self, cf: str
    ) -> tuple[date | None, Gender | None]:
        """Extract birthdate and gender from Codice Fiscale.

        The birthdate is encoded in positions 6-11:
        - Positions 6-7: Last two digits of birth year
        - Position 8: Month letter code
        - Positions 9-10: Birth day (females add 40)

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            Tuple of (date, gender) if extraction successful,
            (None, None) otherwise

        """
        try:
            # Decode omocodia first
            decoded_cf = self._decode_omocodia(cf)

            # Year: positions 6-7 (0-indexed)
            year_digits = decoded_cf[6:8]
            year = int(year_digits)

            # Determine century
            current_year = date.today().year
            current_century = current_year // 100 * 100
            current_year_two_digits = current_year % 100

            if year > current_year_two_digits:
                year = 1900 + year
            else:
                year = current_century + year

            # Month: position 8 (0-indexed)
            month_char = cf[8]
            month = CF_MONTH_CODES.get(month_char)
            if month is None:
                return None, None

            # Day: positions 9-10 (0-indexed)
            day_digits = decoded_cf[9:11]
            day = int(day_digits)

            # For females, 40 is added to the day
            gender: Gender = "M"
            if day > 40:
                day -= 40
                gender = "F"

            return date(year, month, day), gender

        except (ValueError, IndexError):
            return None, None


class PartitaIvaValidator:
    """Validator for Italian Partita IVA (VAT number).

    The Partita IVA is an 11-digit number composed of:
    - First 7 digits: Company registration number (matricola)
    - Next 3 digits: Provincial office code
    - Last digit: Check digit (Luhn algorithm variant)

    Example:
        >>> validator = PartitaIvaValidator()
        >>> result = validator.validate("12345678903")
        >>> print(result.is_valid)
        True

    """

    def validate(self, value: str) -> PartitaIvaValidationResult:
        """Validate an Italian Partita IVA.

        Args:
            value: The P.IVA string to validate

        Returns:
            PartitaIvaValidationResult with validation details

        """
        # Clean the value: remove whitespace and keep only digits
        clean_value = "".join(filter(str.isdigit, value.strip()))

        # Step 1: Must be exactly 11 digits
        if len(clean_value) != 11:
            return PartitaIvaValidationResult(
                is_valid=False,
                error_code="tax_id_piva_invalid_length",
                formatted_value=clean_value,
            )

        # Step 2: Validate check digit using Luhn algorithm variant
        if not self._validate_check_digit(clean_value):
            return PartitaIvaValidationResult(
                is_valid=False,
                error_code="tax_id_piva_invalid_check_digit",
                formatted_value=clean_value,
            )

        # Extract additional information
        province_code = clean_value[7:10]
        is_temporary = clean_value.startswith("99")

        # All validations passed
        return PartitaIvaValidationResult(
            is_valid=True,
            formatted_value=clean_value,
            is_temporary=is_temporary,
            province_code=province_code,
        )

    def _validate_check_digit(self, vat_number: str) -> bool:
        """Validate P.IVA check digit using Italian Luhn algorithm variant.

        The algorithm:
        1. Sum digits at odd positions (1st, 3rd, 5th, etc. - 1-indexed)
        2. For digits at even positions: double the digit, subtract 9 if >= 10
        3. Sum of all processed digits should be divisible by 10

        Args:
            vat_number: 11-digit VAT number string

        Returns:
            True if check digit is valid, False otherwise

        """
        if len(vat_number) != 11 or not vat_number.isdigit():
            return False

        total = 0
        for i, digit in enumerate(vat_number):
            d = int(digit)
            if i % 2 == 0:
                # Odd positions: add directly
                total += d
            else:
                # Even positions: double
                doubled = d * 2
                if doubled >= 10:
                    doubled -= 9
                total += doubled

        return total % 10 == 0


# Validator instances (lazy initialization via class method)
class _ValidatorInstances:
    """Container for validator singleton instances."""

    _cf_validator: CodiceFiscaleValidator | None = None
    _piva_validator: PartitaIvaValidator | None = None

    @classmethod
    def get_cf_validator(cls) -> CodiceFiscaleValidator:
        """Get singleton instance of CodiceFiscaleValidator."""
        if cls._cf_validator is None:
            cls._cf_validator = CodiceFiscaleValidator()
        return cls._cf_validator

    @classmethod
    def get_piva_validator(cls) -> PartitaIvaValidator:
        """Get singleton instance of PartitaIvaValidator."""
        if cls._piva_validator is None:
            cls._piva_validator = PartitaIvaValidator()
        return cls._piva_validator


def validate_codice_fiscale(
    value: str,
    check_adult: bool = False,
    minimum_age: int = MINIMUM_AGE_YEARS,
) -> CodiceFiscaleValidationResult:
    """Convenience function to validate a Codice Fiscale.

    Args:
        value: The CF string to validate
        check_adult: Whether to verify minimum age requirement
        minimum_age: Minimum age required (default: 18)

    Returns:
        CodiceFiscaleValidationResult with validation details

    """
    return _ValidatorInstances.get_cf_validator().validate(
        value, check_adult, minimum_age
    )


def validate_partita_iva(value: str) -> PartitaIvaValidationResult:
    """Convenience function to validate a Partita IVA.

    Args:
        value: The P.IVA string to validate

    Returns:
        PartitaIvaValidationResult with validation details

    """
    return _ValidatorInstances.get_piva_validator().validate(value)


# ============================================================================
# Codice Fiscale Generation
# ============================================================================


@dataclass
class CodiceFiscaleGenerationResult:
    """Result of Codice Fiscale generation.

    Attributes:
        is_valid: Whether the generation was successful
        error_code: Error code if generation failed (None if successful)
        codice_fiscale: The generated Codice Fiscale (None if failed)

    """

    is_valid: bool
    error_code: str | None = None
    codice_fiscale: str | None = None


class CodiceFiscaleGenerator:
    """Generator for Italian Codice Fiscale.

    The Codice Fiscale is a 16-character alphanumeric code that encodes:
    - Surname (3 characters)
    - Name (3 characters)
    - Birth year (2 digits)
    - Birth month (1 letter)
    - Birth day and gender (2 digits, +40 for females)
    - Birth place code (4 characters)
    - Check character (1 letter)

    Example:
        >>> generator = CodiceFiscaleGenerator()
        >>> result = generator.generate(
        ...     surname="Rossi",
        ...     name="Mario",
        ...     birthdate=date(1985, 8, 1),
        ...     gender="M",
        ...     birth_place_code="H501"
        ... )
        >>> print(result.codice_fiscale)
        RSSMRA85M01H501Q

    """

    # Characters used for consonants/vowels extraction
    VOWELS = "AEIOU"
    CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"

    def generate(
        self,
        surname: str,
        name: str,
        birthdate: date,
        gender: Gender,
        birth_place_code: str,
    ) -> CodiceFiscaleGenerationResult:
        """Generate an Italian Codice Fiscale.

        Args:
            surname: Person's surname
            name: Person's first name
            birthdate: Date of birth
            gender: "M" for male, "F" for female
            birth_place_code: 4-character cadastral code (e.g., "H501" for Rome)

        Returns:
            CodiceFiscaleGenerationResult with the generated CF or error

        """
        # Validate inputs
        if not surname or not surname.strip():
            return CodiceFiscaleGenerationResult(
                is_valid=False,
                error_code="cf_gen_invalid_surname",
            )

        if not name or not name.strip():
            return CodiceFiscaleGenerationResult(
                is_valid=False,
                error_code="cf_gen_invalid_name",
            )

        if gender not in ("M", "F"):
            return CodiceFiscaleGenerationResult(
                is_valid=False,
                error_code="cf_gen_invalid_gender",
            )

        birth_place_code = birth_place_code.strip().upper()
        if len(birth_place_code) != 4:
            return CodiceFiscaleGenerationResult(
                is_valid=False,
                error_code="cf_gen_invalid_birth_place_code",
            )

        try:
            # Generate each part
            surname_code = self._encode_surname(surname)
            name_code = self._encode_name(name)
            year_code = str(birthdate.year)[-2:]
            month_code = CF_MONTH_CODES_REVERSE[birthdate.month]
            day_code = self._encode_day(birthdate.day, gender)

            # Combine parts (without check digit)
            cf_partial = (
                f"{surname_code}{name_code}{year_code}"
                f"{month_code}{day_code}{birth_place_code}"
            )

            # Calculate check digit
            check_digit = self._calculate_check_digit(cf_partial)
            codice_fiscale = f"{cf_partial}{check_digit}"

            return CodiceFiscaleGenerationResult(
                is_valid=True,
                codice_fiscale=codice_fiscale,
            )

        except (ValueError, KeyError) as e:
            return CodiceFiscaleGenerationResult(
                is_valid=False,
                error_code=f"cf_gen_error: {e!s}",
            )

    def _clean_string(self, value: str) -> str:
        """Clean a string by removing non-alphabetic characters and uppercasing.

        Args:
            value: Input string

        Returns:
            Cleaned uppercase string with only letters

        """
        return "".join(c for c in value.upper() if c.isalpha())

    def _extract_consonants(self, value: str) -> str:
        """Extract consonants from a string.

        Args:
            value: Input string (uppercase)

        Returns:
            String containing only consonants

        """
        return "".join(c for c in value if c in self.CONSONANTS)

    def _extract_vowels(self, value: str) -> str:
        """Extract vowels from a string.

        Args:
            value: Input string (uppercase)

        Returns:
            String containing only vowels

        """
        return "".join(c for c in value if c in self.VOWELS)

    def _encode_surname(self, surname: str) -> str:
        """Encode surname into 3-character CF code.

        Rules:
        - Take first 3 consonants
        - If less than 3 consonants, add vowels
        - If still less than 3 characters, pad with 'X'

        Args:
            surname: Person's surname

        Returns:
            3-character code

        """
        clean = self._clean_string(surname)
        consonants = self._extract_consonants(clean)
        vowels = self._extract_vowels(clean)

        code = consonants[:3]
        if len(code) < 3:
            code += vowels[: 3 - len(code)]
        if len(code) < 3:
            code += "X" * (3 - len(code))

        return code[:3]

    def _encode_name(self, name: str) -> str:
        """Encode name into 3-character CF code.

        Rules:
        - If 4+ consonants: take 1st, 3rd, and 4th consonant
        - If 3 consonants: take all 3
        - If less than 3 consonants, add vowels
        - If still less than 3 characters, pad with 'X'

        Args:
            name: Person's first name

        Returns:
            3-character code

        """
        clean = self._clean_string(name)
        consonants = self._extract_consonants(clean)
        vowels = self._extract_vowels(clean)

        if len(consonants) >= 4:
            code = consonants[0] + consonants[2] + consonants[3]
        else:
            code = consonants[:3]
            if len(code) < 3:
                code += vowels[: 3 - len(code)]
            if len(code) < 3:
                code += "X" * (3 - len(code))

        return code[:3]

    def _encode_day(self, day: int, gender: Gender) -> str:
        """Encode birth day with gender modifier.

        Args:
            day: Day of birth (1-31)
            gender: "M" for male, "F" for female

        Returns:
            2-digit string (females add 40 to day)

        """
        if gender == "F":
            day += 40
        return f"{day:02d}"

    def _calculate_check_digit(self, cf_partial: str) -> str:
        """Calculate the check digit for a partial CF.

        Args:
            cf_partial: First 15 characters of CF

        Returns:
            Single character check digit (A-Z)

        """
        total = 0
        for i, char in enumerate(cf_partial):
            if i % 2 == 0:
                # Odd positions (1-indexed) = even index (0-indexed)
                total += CF_ODD_VALUES.get(char, 0)
            else:
                # Even positions (1-indexed) = odd index (0-indexed)
                total += CF_EVEN_VALUES.get(char, 0)

        return chr(ord("A") + (total % 26))


# Singleton instance for generator
class _GeneratorInstances:
    """Container for generator singleton instances."""

    _cf_generator: CodiceFiscaleGenerator | None = None

    @classmethod
    def get_cf_generator(cls) -> CodiceFiscaleGenerator:
        """Get singleton instance of CodiceFiscaleGenerator."""
        if cls._cf_generator is None:
            cls._cf_generator = CodiceFiscaleGenerator()
        return cls._cf_generator


def generate_codice_fiscale(
    surname: str,
    name: str,
    birthdate: date,
    gender: Gender,
    birth_place_code: str,
) -> CodiceFiscaleGenerationResult:
    """Convenience function to generate a Codice Fiscale.

    Args:
        surname: Person's surname
        name: Person's first name
        birthdate: Date of birth
        gender: "M" for male, "F" for female
        birth_place_code: 4-character cadastral code (e.g., "H501" for Rome)

    Returns:
        CodiceFiscaleGenerationResult with the generated CF or error

    Example:
        >>> from datetime import date
        >>> result = generate_codice_fiscale(
        ...     surname="Rossi",
        ...     name="Mario",
        ...     birthdate=date(1985, 8, 1),
        ...     gender="M",
        ...     birth_place_code="H501"
        ... )
        >>> print(result.codice_fiscale)
        RSSMRA85M01H501Q

    """
    return _GeneratorInstances.get_cf_generator().generate(
        surname=surname,
        name=name,
        birthdate=birthdate,
        gender=gender,
        birth_place_code=birth_place_code,
    )
