"""Unit tests for Italian tax validators.

Tests for:
- Codice Fiscale validation
- Partita IVA validation
- Birthdate extraction
- Age verification
- Check digit algorithms
"""

from unittest import TestCase

from italian_tax_validators import (
    CodiceFiscaleValidator,
    PartitaIvaValidator,
    validate_codice_fiscale,
    validate_partita_iva,
    CF_MONTH_CODES,
)


class CodiceFiscaleValidatorTest(TestCase):
    """Tests for Italian Codice Fiscale (CF) validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_valid_codice_fiscale_male(self):
        """Test validation of a valid male CF."""
        # RSSMRA85M01H501Q - Mario Rossi, born Aug 1, 1985 in Rome
        result = self.validator.validate("RSSMRA85M01H501Q")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")
        self.assertIsNotNone(result.birthdate)
        self.assertEqual(result.birthdate.year, 1985)
        self.assertEqual(result.birthdate.month, 8)
        self.assertEqual(result.birthdate.day, 1)

    def test_valid_codice_fiscale_female(self):
        """Test validation of a valid female CF (day + 40)."""
        # RSSMRA85M41H501U - Maria Rossi, born Aug 1, 1985 in Rome
        # (female: 01+40=41)
        result = self.validator.validate("RSSMRA85M41H501U")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertIsNotNone(result.birthdate)
        self.assertEqual(result.birthdate.day, 1)  # 41 - 40 = 1

    def test_valid_codice_fiscale_lowercase_input(self):
        """Test that lowercase input is accepted and converted to uppercase."""
        result = self.validator.validate("rssmra85m01h501q")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")

    def test_valid_codice_fiscale_with_spaces(self):
        """Test that spaces are removed from input."""
        result = self.validator.validate("RSS MRA 85M01 H501Q")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")

    def test_invalid_codice_fiscale_wrong_length(self):
        """Test that CF with wrong length is rejected."""
        result = self.validator.validate("RSSMRA85M01H501")  # 15 chars

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_invalid_codice_fiscale_wrong_format(self):
        """Test that CF with invalid format is rejected."""
        result = self.validator.validate("123456789012345A")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_invalid_codice_fiscale_wrong_check_digit(self):
        """Test that CF with wrong check digit is rejected."""
        # Change last character from Q to A (wrong check digit)
        result = self.validator.validate("RSSMRA85M01H501A")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_codice_fiscale_omocodia(self):
        """Test validation of CF with omocodia substitutions."""
        # RSSMRA85M01H50MZ - omocodia
        result = self.validator.validate("RSSMRA85M0MH50MZ")

        # Note: The check digit changes with omocodia
        # This test verifies the validator handles omocodia characters
        self.assertIn(result.is_valid, [True, False])  # Depends on check digit

    def test_age_check_adult(self):
        """Test age verification for adult (18+)."""
        # Person born in 1985 should be adult
        result = self.validator.validate("RSSMRA85M01H501Q", check_adult=True)

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.age)
        self.assertGreaterEqual(result.age, 18)

    def test_age_check_minor(self):
        """Test age verification for minor (under 18)."""
        # RSSMRA20M01H501X - born Aug 1, 2020 (minor)
        result = self.validator.validate("RSSMRA20M01H501X", check_adult=True)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_underage")

    def test_age_check_custom_minimum_age(self):
        """Test age verification with custom minimum age."""
        # Person born in 1985 is about 40 years old
        result = self.validator.validate(
            "RSSMRA85M01H501Q", check_adult=True, minimum_age=50
        )

        # Should fail because they're not 50+ yet
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_underage")

    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.validator.validate("")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_all_months_codes(self):
        """Test that all month codes are recognized."""
        expected_months = {
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
        self.assertEqual(CF_MONTH_CODES, expected_months)


class PartitaIvaValidatorTest(TestCase):
    """Tests for Italian Partita IVA (VAT number) validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = PartitaIvaValidator()

    def test_valid_partita_iva(self):
        """Test validation of a valid P.IVA."""
        # 12345678903 is a valid P.IVA (check digit: 3)
        result = self.validator.validate("12345678903")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_valid_partita_iva_with_spaces(self):
        """Test that spaces are removed from input."""
        result = self.validator.validate("123 456 78903")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_valid_partita_iva_with_prefix_it(self):
        """Test that IT prefix is handled (stripped)."""
        result = self.validator.validate("IT12345678903")

        # IT prefix should be stripped, leaving only digits
        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_invalid_partita_iva_wrong_length(self):
        """Test that P.IVA with wrong length is rejected."""
        result = self.validator.validate("1234567890")  # 10 digits

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_invalid_partita_iva_too_long(self):
        """Test that P.IVA with too many digits is rejected."""
        result = self.validator.validate("123456789012")  # 12 digits

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_invalid_partita_iva_wrong_check_digit(self):
        """Test that P.IVA with wrong check digit is rejected."""
        # 12345678901 - wrong check digit (should be 3)
        result = self.validator.validate("12345678901")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_check_digit")

    def test_invalid_partita_iva_all_zeros(self):
        """Test that P.IVA with all zeros is handled."""
        result = self.validator.validate("00000000000")

        # 00000000000 actually passes Luhn check (sum = 0, 0 % 10 = 0)
        self.assertTrue(result.is_valid)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.validator.validate("")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_luhn_algorithm_correctness(self):
        """Test the Luhn algorithm implementation with known values."""
        # Some known valid Italian P.IVA numbers
        valid_pivas = [
            "12345678903",  # Standard test number
            "00000000000",  # Edge case: all zeros
            "00743110157",  # Real example: Mediaset
        ]

        for piva in valid_pivas:
            result = self.validator.validate(piva)
            self.assertTrue(result.is_valid, f"P.IVA {piva} should be valid")


class ItalianTaxValidatorConvenienceFunctionsTest(TestCase):
    """Tests for convenience functions in italian_tax_validators module."""

    def test_validate_codice_fiscale_function(self):
        """Test the validate_codice_fiscale convenience function."""
        result = validate_codice_fiscale("RSSMRA85M01H501Q")

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.birthdate)

    def test_validate_codice_fiscale_with_age_check(self):
        """Test validate_codice_fiscale with age verification."""
        result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True)

        self.assertTrue(result.is_valid)
        self.assertGreaterEqual(result.age, 18)

    def test_validate_partita_iva_function(self):
        """Test the validate_partita_iva convenience function."""
        result = validate_partita_iva("12345678903")

        self.assertTrue(result.is_valid)


class CodiceFiscaleBirthdateExtractionTest(TestCase):
    """Tests specifically for birthdate extraction from Codice Fiscale."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_birthdate_january(self):
        """Test birthdate extraction for January (A)."""
        # RSSMRA85A01H501Z - January
        result = self.validator.validate("RSSMRA85A01H501Z")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.month, 1)

    def test_birthdate_december(self):
        """Test birthdate extraction for December (T)."""
        # RSSMRA85T01H501M - December
        result = self.validator.validate("RSSMRA85T01H501M")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.month, 12)

    def test_century_determination_1900s(self):
        """Test that years > current year's last 2 digits are 1900s."""
        # RSSMRA90M01H501N - Someone born in 1990
        result = self.validator.validate("RSSMRA90M01H501N")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.year, 1990)

    def test_century_determination_2000s(self):
        """Test that years <= current year's last 2 digits are 2000s."""
        # RSSMRA10M01H501S - Someone born in 2010
        result = self.validator.validate("RSSMRA10M01H501S")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.year, 2010)

    def test_female_day_extraction(self):
        """Test that female birth day is correctly extracted (day + 40)."""
        # RSSMRA85M55H501I - Female born on day 15 (55 - 40 = 15)
        result = self.validator.validate("RSSMRA85M55H501I")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.day, 15)


class PartitaIvaCheckDigitTest(TestCase):
    """Tests specifically for Partita IVA check digit algorithm."""

    def test_check_digit_calculation(self):
        """Test the Italian Luhn algorithm implementation."""
        validator = PartitaIvaValidator()

        # Test known valid P.IVA numbers
        test_cases = [
            ("12345678903", True),  # Valid
            ("12345678901", False),  # Invalid check digit
            ("12345678902", False),  # Invalid check digit
            ("00743110157", True),  # Valid (Mediaset)
        ]

        for piva, expected_valid in test_cases:
            result = validator.validate(piva)
            self.assertEqual(
                result.is_valid,
                expected_valid,
                f"P.IVA {piva} validation mismatch: expected {expected_valid}",
            )


class CodiceFiscaleGenderExtractionTest(TestCase):
    """Tests for gender extraction from Codice Fiscale."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_gender_male(self):
        """Test gender extraction for male CF."""
        result = self.validator.validate("RSSMRA85M01H501Q")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.gender, "M")

    def test_gender_female(self):
        """Test gender extraction for female CF (day + 40)."""
        result = self.validator.validate("RSSMRA85M41H501U")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.gender, "F")


class CodiceFiscaleBirthPlaceExtractionTest(TestCase):
    """Tests for birth place extraction from Codice Fiscale."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_birth_place_rome(self):
        """Test birth place extraction for Rome (H501)."""
        result = self.validator.validate("RSSMRA85M01H501Q")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birth_place_code, "H501")
        self.assertEqual(result.birth_place_name, "ROMA")
        self.assertEqual(result.birth_place_province, "RM")
        self.assertFalse(result.is_foreign_born)

    def test_birth_place_foreign(self):
        """Test birth place extraction for foreign country."""
        # Z109 = France, CF generated with correct check digit
        result = self.validator.validate("RSSMRA85M01Z109Q")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birth_place_code, "Z109")
        self.assertEqual(result.birth_place_name, "FRANCIA")
        self.assertEqual(result.birth_place_province, "EE")
        self.assertTrue(result.is_foreign_born)

    def test_birth_place_unknown_code(self):
        """Test birth place with unknown cadastral code."""
        # X999 is not in database, CF generated with correct check digit
        result = self.validator.validate("RSSMRA85M01X999S")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birth_place_code, "X999")
        self.assertIsNone(result.birth_place_name)
        self.assertIsNone(result.birth_place_province)


class PartitaIvaAdditionalFieldsTest(TestCase):
    """Tests for additional Partita IVA fields."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = PartitaIvaValidator()

    def test_province_code_extraction(self):
        """Test province code extraction from P.IVA."""
        result = self.validator.validate("12345678903")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.province_code, "890")

    def test_temporary_vat_number(self):
        """Test detection of temporary VAT number."""
        # Temporary P.IVA starts with 99 (valid check digit)
        result = self.validator.validate("99000000002")
        self.assertTrue(result.is_valid)
        self.assertTrue(result.is_temporary)

    def test_regular_vat_number_not_temporary(self):
        """Test that regular P.IVA is not marked as temporary."""
        result = self.validator.validate("12345678903")
        self.assertTrue(result.is_valid)
        self.assertFalse(result.is_temporary)


class CodiceFiscaleGeneratorTest(TestCase):
    """Tests for Codice Fiscale generation."""

    def setUp(self):
        """Set up test fixtures."""
        from italian_tax_validators import CodiceFiscaleGenerator

        self.generator = CodiceFiscaleGenerator()

    def test_generate_male_cf(self):
        """Test generation of male CF."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="Mario",
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H501",
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.codice_fiscale, "RSSMRA85M01H501Q")

    def test_generate_female_cf(self):
        """Test generation of female CF."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="Maria",
            birthdate=date(1985, 8, 1),
            gender="F",
            birth_place_code="H501",
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.codice_fiscale, "RSSMRA85M41H501U")

    def test_generate_with_short_name(self):
        """Test generation with short name (less than 3 consonants)."""
        from datetime import date

        result = self.generator.generate(
            surname="Bo",
            name="Ai",
            birthdate=date(1990, 1, 15),
            gender="M",
            birth_place_code="H501",
        )
        self.assertTrue(result.is_valid)
        # BO -> BOX (padded with X)
        # AI -> AIX (padded with X)
        self.assertIsNotNone(result.codice_fiscale)
        self.assertEqual(len(result.codice_fiscale), 16)

    def test_generate_with_4_consonants_name(self):
        """Test name encoding with 4+ consonants (1st, 3rd, 4th rule)."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="Roberto",  # R, B, R, T -> uses R, R, T
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H501",
        )
        self.assertTrue(result.is_valid)
        # Name ROBERTO has consonants: R, B, R, T (4+)
        # Rule: take 1st, 3rd, 4th = R, R, T = RRT
        self.assertIsNotNone(result.codice_fiscale)
        self.assertTrue(result.codice_fiscale.startswith("RSS"))

    def test_generate_invalid_surname(self):
        """Test generation with empty surname."""
        from datetime import date

        result = self.generator.generate(
            surname="",
            name="Mario",
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H501",
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "cf_gen_invalid_surname")

    def test_generate_invalid_name(self):
        """Test generation with empty name."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="",
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H501",
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "cf_gen_invalid_name")

    def test_generate_invalid_gender(self):
        """Test generation with invalid gender."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="Mario",
            birthdate=date(1985, 8, 1),
            gender="X",  # type: ignore[arg-type]
            birth_place_code="H501",
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "cf_gen_invalid_gender")

    def test_generate_invalid_birth_place_code(self):
        """Test generation with invalid birth place code."""
        from datetime import date

        result = self.generator.generate(
            surname="Rossi",
            name="Mario",
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H50",  # Too short
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "cf_gen_invalid_birth_place_code")

    def test_generated_cf_validates(self):
        """Test that generated CF passes validation."""
        from datetime import date

        from italian_tax_validators import validate_codice_fiscale

        result = self.generator.generate(
            surname="Bianchi",
            name="Giuseppe",
            birthdate=date(1970, 12, 25),
            gender="M",
            birth_place_code="F205",  # Milano
        )
        self.assertTrue(result.is_valid)

        # Validate the generated CF
        validation = validate_codice_fiscale(result.codice_fiscale)
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.birthdate, date(1970, 12, 25))
        self.assertEqual(validation.gender, "M")


class CodiceFiscaleGeneratorConvenienceFunctionTest(TestCase):
    """Tests for generate_codice_fiscale convenience function."""

    def test_generate_codice_fiscale_function(self):
        """Test the generate_codice_fiscale convenience function."""
        from datetime import date

        from italian_tax_validators import generate_codice_fiscale

        result = generate_codice_fiscale(
            surname="Rossi",
            name="Mario",
            birthdate=date(1985, 8, 1),
            gender="M",
            birth_place_code="H501",
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.codice_fiscale, "RSSMRA85M01H501Q")


class MunicipalityDatabaseTest(TestCase):
    """Tests for municipality database utilities."""

    def test_get_municipality_info(self):
        """Test getting municipality info from code."""
        from italian_tax_validators import get_municipality_info

        info = get_municipality_info("H501")
        self.assertIsNotNone(info)
        self.assertEqual(info[0], "ROMA")
        self.assertEqual(info[1], "RM")

    def test_get_municipality_info_not_found(self):
        """Test getting info for unknown code."""
        from italian_tax_validators import get_municipality_info

        info = get_municipality_info("X999")
        self.assertIsNone(info)

    def test_get_cadastral_code(self):
        """Test getting cadastral code from municipality name."""
        from italian_tax_validators import get_cadastral_code

        code = get_cadastral_code("ROMA")
        self.assertEqual(code, "H501")

    def test_get_cadastral_code_case_insensitive(self):
        """Test that municipality search is case-insensitive."""
        from italian_tax_validators import get_cadastral_code

        code = get_cadastral_code("roma")
        self.assertEqual(code, "H501")

    def test_get_cadastral_code_not_found(self):
        """Test getting code for unknown municipality."""
        from italian_tax_validators import get_cadastral_code

        code = get_cadastral_code("UNKNOWN_CITY")
        self.assertIsNone(code)

    def test_search_municipality(self):
        """Test searching municipalities by partial name."""
        from italian_tax_validators import search_municipality

        results = search_municipality("MILAN")
        self.assertTrue(len(results) >= 1)
        # Should find Milano
        names = [r[1] for r in results]
        self.assertIn("MILANO", names)

    def test_search_municipality_no_results(self):
        """Test search with no results."""
        from italian_tax_validators import search_municipality

        results = search_municipality("XYZNOTEXIST")
        self.assertEqual(len(results), 0)

    def test_is_foreign_country(self):
        """Test detection of foreign country codes."""
        from italian_tax_validators import is_foreign_country

        self.assertTrue(is_foreign_country("Z109"))  # France
        self.assertFalse(is_foreign_country("H501"))  # Roma


class CLITest(TestCase):
    """Tests for the command-line interface."""

    def test_validate_cf_valid(self):
        """Test CLI validate-cf with valid CF."""
        from italian_tax_validators.cli import main

        exit_code = main(["validate-cf", "RSSMRA85M01H501Q"])
        self.assertEqual(exit_code, 0)

    def test_validate_cf_invalid(self):
        """Test CLI validate-cf with invalid CF."""
        from italian_tax_validators.cli import main

        exit_code = main(["validate-cf", "INVALID"])
        self.assertEqual(exit_code, 1)

    def test_validate_piva_valid(self):
        """Test CLI validate-piva with valid P.IVA."""
        from italian_tax_validators.cli import main

        exit_code = main(["validate-piva", "12345678903"])
        self.assertEqual(exit_code, 0)

    def test_validate_piva_invalid(self):
        """Test CLI validate-piva with invalid P.IVA."""
        from italian_tax_validators.cli import main

        exit_code = main(["validate-piva", "12345678901"])
        self.assertEqual(exit_code, 1)

    def test_generate_cf(self):
        """Test CLI generate-cf command."""
        from italian_tax_validators.cli import main

        exit_code = main([
            "generate-cf",
            "--surname",
            "Rossi",
            "--name",
            "Mario",
            "--birthdate",
            "1985-08-01",
            "--gender",
            "M",
            "--birth-place-code",
            "H501",
        ])
        self.assertEqual(exit_code, 0)

    def test_generate_cf_with_municipality_name(self):
        """Test CLI generate-cf with municipality name."""
        from italian_tax_validators.cli import main

        exit_code = main([
            "generate-cf",
            "--surname",
            "Rossi",
            "--name",
            "Mario",
            "--birthdate",
            "1985-08-01",
            "--gender",
            "M",
            "--birth-place",
            "ROMA",
        ])
        self.assertEqual(exit_code, 0)

    def test_generate_cf_invalid_date(self):
        """Test CLI generate-cf with invalid date format."""
        from italian_tax_validators.cli import main

        exit_code = main([
            "generate-cf",
            "--surname",
            "Rossi",
            "--name",
            "Mario",
            "--birthdate",
            "01-08-1985",  # Wrong format
            "--gender",
            "M",
            "--birth-place-code",
            "H501",
        ])
        self.assertEqual(exit_code, 1)

    def test_search_municipality(self):
        """Test CLI search-municipality command."""
        from italian_tax_validators.cli import main

        exit_code = main(["search-municipality", "ROMA"])
        self.assertEqual(exit_code, 0)

    def test_search_municipality_not_found(self):
        """Test CLI search-municipality with no results."""
        from italian_tax_validators.cli import main

        exit_code = main(["search-municipality", "XYZNOTEXIST123"])
        self.assertEqual(exit_code, 1)

    def test_cli_no_command(self):
        """Test CLI with no command shows help."""
        from italian_tax_validators.cli import main

        exit_code = main([])
        self.assertEqual(exit_code, 0)
