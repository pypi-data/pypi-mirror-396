"""Command-line interface for Italian Tax Validators.

This module provides a CLI tool for validating and generating Italian
tax identification numbers from the command line.

Usage:
    italian-tax-validators validate-cf RSSMRA85M01H501Q
    italian-tax-validators validate-piva 12345678903
    italian-tax-validators generate-cf --surname Rossi --name Mario ...
    italian-tax-validators search-municipality Roma

"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from italian_tax_validators import (
    generate_codice_fiscale,
    get_cadastral_code,
    search_municipality,
    validate_codice_fiscale,
    validate_partita_iva,
)


def validate_cf_command(args: argparse.Namespace) -> int:
    """Handle the validate-cf command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for invalid)

    """
    result = validate_codice_fiscale(
        args.value,
        check_adult=args.check_adult,
        minimum_age=args.minimum_age,
    )

    if result.is_valid:
        print(f"✓ Valid Codice Fiscale: {result.formatted_value}")
        print(f"  Birthdate: {result.birthdate}")
        print(f"  Age: {result.age}")
        print(f"  Gender: {result.gender}")
        if result.birth_place_name:
            province = (
                f" ({result.birth_place_province})"
                if result.birth_place_province and result.birth_place_province != "EE"
                else ""
            )
            print(f"  Birth place: {result.birth_place_name}{province}")
            if result.is_foreign_born:
                print("  (Foreign country)")
        else:
            print(f"  Birth place code: {result.birth_place_code}")
        return 0
    else:
        print(f"✗ Invalid Codice Fiscale: {result.formatted_value}")
        print(f"  Error: {result.error_code}")
        if result.birthdate:
            print(f"  Birthdate: {result.birthdate}")
        if result.age is not None:
            print(f"  Age: {result.age}")
        return 1


def validate_piva_command(args: argparse.Namespace) -> int:
    """Handle the validate-piva command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for invalid)

    """
    result = validate_partita_iva(args.value)

    if result.is_valid:
        print(f"✓ Valid Partita IVA: {result.formatted_value}")
        print(f"  Province code: {result.province_code}")
        if result.is_temporary:
            print("  ⚠ Temporary VAT number")
        return 0
    else:
        print(f"✗ Invalid Partita IVA: {result.formatted_value}")
        print(f"  Error: {result.error_code}")
        return 1


def generate_cf_command(args: argparse.Namespace) -> int:
    """Handle the generate-cf command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)

    """
    # Parse birthdate
    try:
        birthdate = datetime.strptime(args.birthdate, "%Y-%m-%d").date()
    except ValueError:
        print(f"✗ Invalid birthdate format: {args.birthdate}")
        print("  Use YYYY-MM-DD format (e.g., 1985-08-01)")
        return 1

    # Validate gender
    gender = args.gender.upper()
    if gender not in ("M", "F"):
        print(f"✗ Invalid gender: {args.gender}")
        print("  Use M for male or F for female")
        return 1

    # Get birth place code
    birth_place_code = args.birth_place_code
    if not birth_place_code and args.birth_place:
        # Try to find cadastral code from municipality name
        code = get_cadastral_code(args.birth_place)
        if code:
            birth_place_code = code
        else:
            # Search for partial matches
            matches = search_municipality(args.birth_place)
            if matches:
                print(f"✗ Multiple municipalities found for '{args.birth_place}':")
                for code, name, province in matches[:10]:
                    print(f"  {code}: {name} ({province})")
                print("  Use --birth-place-code with the exact code")
                return 1
            else:
                print(f"✗ Municipality not found: {args.birth_place}")
                return 1

    if not birth_place_code:
        print("✗ Birth place code is required")
        print("  Use --birth-place-code or --birth-place")
        return 1

    result = generate_codice_fiscale(
        surname=args.surname,
        name=args.name,
        birthdate=birthdate,
        gender=gender,  # type: ignore[arg-type]
        birth_place_code=birth_place_code,
    )

    if result.is_valid:
        print(f"✓ Generated Codice Fiscale: {result.codice_fiscale}")
        return 0
    else:
        print("✗ Failed to generate Codice Fiscale")
        print(f"  Error: {result.error_code}")
        return 1


def search_municipality_command(args: argparse.Namespace) -> int:
    """Handle the search-municipality command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for not found)

    """
    results = search_municipality(args.query)

    if not results:
        print(f"✗ No municipalities found for '{args.query}'")
        return 1

    print(f"Found {len(results)} municipalities:")
    for code, name, province in results[: args.limit]:
        province_str = f" ({province})" if province != "EE" else " (Foreign)"
        print(f"  {code}: {name}{province_str}")

    if len(results) > args.limit:
        print(f"  ... and {len(results) - args.limit} more")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code

    """
    parser = argparse.ArgumentParser(
        prog="italian-tax-validators",
        description="Validate and generate Italian tax identification numbers",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate-cf command
    cf_parser = subparsers.add_parser(
        "validate-cf",
        help="Validate a Codice Fiscale",
        description="Validate an Italian Codice Fiscale (personal tax ID)",
    )
    cf_parser.add_argument("value", help="Codice Fiscale to validate")
    cf_parser.add_argument(
        "--check-adult",
        action="store_true",
        help="Verify that the person is at least minimum-age years old",
    )
    cf_parser.add_argument(
        "--minimum-age",
        type=int,
        default=18,
        help="Minimum age required (default: 18)",
    )

    # validate-piva command
    piva_parser = subparsers.add_parser(
        "validate-piva",
        help="Validate a Partita IVA",
        description="Validate an Italian Partita IVA (VAT number)",
    )
    piva_parser.add_argument("value", help="Partita IVA to validate")

    # generate-cf command
    gen_parser = subparsers.add_parser(
        "generate-cf",
        help="Generate a Codice Fiscale",
        description="Generate an Italian Codice Fiscale from personal data",
    )
    gen_parser.add_argument("--surname", required=True, help="Person's surname")
    gen_parser.add_argument("--name", required=True, help="Person's first name")
    gen_parser.add_argument(
        "--birthdate",
        required=True,
        help="Date of birth (YYYY-MM-DD format)",
    )
    gen_parser.add_argument(
        "--gender",
        required=True,
        help="Gender (M for male, F for female)",
    )
    gen_parser.add_argument(
        "--birth-place-code",
        help="4-character cadastral code (e.g., H501 for Rome)",
    )
    gen_parser.add_argument(
        "--birth-place",
        help="Municipality name (alternative to --birth-place-code)",
    )

    # search-municipality command
    search_parser = subparsers.add_parser(
        "search-municipality",
        help="Search for municipality codes",
        description="Search for Italian municipality cadastral codes",
    )
    search_parser.add_argument("query", help="Municipality name to search for")
    search_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)",
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to appropriate command handler
    if args.command == "validate-cf":
        return validate_cf_command(args)
    elif args.command == "validate-piva":
        return validate_piva_command(args)
    elif args.command == "generate-cf":
        return generate_cf_command(args)
    elif args.command == "search-municipality":
        return search_municipality_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
