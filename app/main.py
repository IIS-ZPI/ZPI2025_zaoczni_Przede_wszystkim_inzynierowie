import sys
import shlex
import argparse
from datetime import datetime, date

# Constant from SRS (FR-07 Data Constraint)
MIN_DATE = date(2002, 1, 2)


def validate_date(date_str):
    """
    Parses the date string and validates input logic.
    Returns a date object.
    """
    # If date is omitted, use today's date.
    if not date_str:
        return date.today()

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Error: Invalid date format. Please use YYYY-MM-DD.")

    # The system must reject dates earlier than January 2, 2002.
    if dt < MIN_DATE:
        raise ValueError("Error: Requested date is outside the supported NBP archival range (minimum: 2002-01-02).")


    # The anchor date cannot be in the future.
    if dt > date.today():
        raise ValueError("Error: Requested date cannot be in the future.")

    return dt


def custom_error_handler(message):
    """
    Overrides the default argparse behavior (sys.exit) to raise an exception instead.
    Allows the interactive loop to continue despite command errors.
    """
    raise ValueError(f"Command syntax error: {message}")


def setup_parser():
    """
    Configures the argument parser with commands defined in SRS (FR-07).
    """
    parser = argparse.ArgumentParser(
        description="Currency Exchange Rate Statistical Analysis System",
        add_help=False,
        usage=argparse.SUPPRESS,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40)
    )
    parser.error = custom_error_handler

    subparsers = parser.add_subparsers(dest='command', title='Available commands')

    # Analyze Command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze currency statistics')
    analyze_parser.add_argument('currency', type=str, help='Currency code (e.g. USD)')
    analyze_parser.add_argument('--period', required=True,
                                choices=['1-week', '2-weeks', '1-month', '1-quarter', '6-months', '1-year'],
                                help='Time period for analysis')
    analyze_parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')

    # Distribution Command
    dist_parser = subparsers.add_parser('change-distribution', help='Calculate distribution of changes')
    dist_parser.add_argument('currency_1', type=str, help='First currency code')
    dist_parser.add_argument('currency_2', type=str, help='Second currency code')
    dist_parser.add_argument('--period', required=True,
                             choices=['1-month', '1-quarter'],
                             help='Time period for analysis')
    dist_parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')

    return parser


def main():
    parser = setup_parser()
    print("Welcome to Currency Exchange Rate Statistical Analysis System")
    print("Type 'help' for available commands or 'exit' to quit.")

    # Main Program Loop
    while True:
        try:
            # Get user input
            user_input = input("\nNBP_APP> ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle exit commands
            if user_input.lower() in ['exit']:
                print("Exiting application...")
                break

            # Handle help command manually
            if user_input.lower() in ['help']:
                parser.print_help()
                continue

            # Parse arguments
            args_list = shlex.split(user_input)
            args = parser.parse_args(args_list)

            # Input Logic Validation
            # This is the 'Anchor date' (end date of the range)
            anchor_date = validate_date(args.start)


            if args.command == 'analyze':
                # TODO: Integrate with AnalysisService (SCRUM-8)
                print(f"[LOGIC] Analyzing {args.currency.upper()} | Period: {args.period} | Anchor Date: {anchor_date}")

            elif args.command == 'change-distribution':
                # TODO: Integrate with DistributionService (SCRUM-9)
                print(
                    f"[LOGIC] Distribution {args.currency_1.upper()}/{args.currency_2.upper()} | Period: {args.period} | Anchor Date: {anchor_date}")

        except ValueError as e:
            # Handle validation errors (both date and syntax)
            print(f"{e}")
        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()