#!/usr/bin/env python3
import sys
import os
import argparse
import json
import logging
import logging.config

# Add jtable to path
jtable_path = os.path.dirname(os.path.abspath(__file__))
if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)

# Import logging configuration
from logger import logging_config

# Import Player class
from player import Player

# Import Plugin for environment variable access
from functions import Plugin


def parse_variable_args(var_string: str) -> dict:
    """
    Parse variable argument string.
    Format: "key=value" -> {"key": "value"}

    Args:
        var_string: String in format "key=value"

    Returns:
        Dictionary with parsed key-value pair
    """
    if '=' not in var_string:
        logging.error(f"Invalid variable format: {var_string}. Expected format: key=value")
        sys.exit(1)

    key, value = var_string.split('=', 1)
    return {key.strip(): value.strip()}


def parse_dict_args(dict_string: str) -> dict:
    """
    Parse dictionary argument string (JSON format).
    Format: '{"key": "value"}' -> {"key": "value"}

    Args:
        dict_string: JSON string

    Returns:
        Dictionary parsed from JSON
    """
    try:
        return json.loads(dict_string)
    except json.JSONDecodeError as error:
        logging.error(f"Invalid JSON format: {dict_string}")
        logging.error(f"Error: {error}")
        sys.exit(1)


def main():
    """Main entry point for jtable-play CLI"""
    parser = argparse.ArgumentParser(
        prog='jtable-play',
        description='Execute jtable playbooks (query files)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic playbook execution
  jtable-play playbook.yml

  # With simple variables
  jtable-play playbook.yml -v "first_name=john" -v "last_name=doe"

  # With dictionary variables
  jtable-play playbook.yml -d '{"person": {"first_name": "john", "last_name": "doe"}}'

  # Combined variables and dictionaries
  jtable-play playbook.yml -v "env=prod" -d '{"config": {"debug": false}}'

  # Expose OS environment variables directly
  jtable-play playbook.yml -E
  # Now you can use {{ PATH }}, {{ HOME }}, {{ LOGNAME }}, etc.

  # Store OS environment variables in a namespace
  jtable-play playbook.yml -En os_vars
  # Now you can use {{ os_vars.PATH }}, {{ os_vars.HOME }}, etc.
        """
    )

    parser.add_argument(
        'playbook',
        help='Path to the YAML playbook file'
    )

    parser.add_argument(
        '-v', '--var',
        action='append',
        dest='variables',
        help='Add a variable in format key=value (can be used multiple times)'
    )

    parser.add_argument(
        '-d', '--dict',
        action='append',
        dest='dicts',
        help='Add variables from JSON dictionary (can be used multiple times)'
    )

    parser.add_argument(
        '-E', '--env',
        action='store_true',
        dest='env',
        help='Expose OS env vars directly ({{ PATH }}, {{ HOME }})'
    )

    parser.add_argument(
        '-En', '--env-ns',
        type=str,
        dest='env_ns',
        metavar='VAR_NAME',
        help='Store OS env vars in namespace (usage: -En my_var creates {{ my_var }} containing env())'
    )

    parser.add_argument(
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity level (use -vv for debug)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with line numbers'
    )

    args = parser.parse_args()

    # Configure logging
    if os.environ.get('JTABLE_LOGGING') == "DEBUG" or args.debug:
        logging_config['formatters']['my_formatter']['format'] = \
            '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
    else:
        logging_config['formatters']['my_formatter']['format'] = \
            '%(asctime)s %(class_name)s.%(parent_function)-15s | %(levelname)s %(message)s'

    if args.verbose == 0:
        logging_config['handlers']['console_stderr']['level'] = 'WARNING'
    elif args.verbose == 1:
        logging_config['handlers']['console_stderr']['level'] = 'INFO'
    elif args.verbose >= 2:
        logging_config['handlers']['console_stderr']['level'] = 'DEBUG'

    logging.config.dictConfig(logging_config)

    # Parse variables
    variables = {}

    # Process -v/--var arguments
    if args.variables:
        for var_string in args.variables:
            var_dict = parse_variable_args(var_string)
            variables.update(var_dict)
            logging.info(f"Added variable: {list(var_dict.keys())[0]}")

    # Process -d/--dict arguments
    if args.dicts:
        for dict_string in args.dicts:
            dict_vars = parse_dict_args(dict_string)
            variables.update(dict_vars)
            logging.info(f"Added dictionary variables: {list(dict_vars.keys())}")

    # Process -E/--env argument (expose env vars directly)
    if args.env:
        env_vars = Plugin.env()
        variables.update(env_vars)
        logging.info(f"Exposed {len(env_vars)} environment variables directly")

    # Process -En/--env-ns argument (store env vars in namespace)
    if args.env_ns:
        env_vars = Plugin.env()
        variables[args.env_ns] = env_vars
        logging.info(f"Stored {len(env_vars)} environment variables in namespace '{args.env_ns}'")

    # Check for stdin data
    stdin_data = None
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        logging.info("Read data from stdin")

    # Create and execute player
    try:
        player = Player(args.playbook, variables=variables, stdin_data=stdin_data)
        output = player.execute()
        print(output)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as error:
        logging.error(f"Failed to execute playbook: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
