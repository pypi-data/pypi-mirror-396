#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import logging.config
import yaml

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


def main():
    """Main entry point for jtable-template CLI"""
    parser = argparse.ArgumentParser(
        prog='jtable-template',
        description='Render Jinja2 templates with jtable filters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic template rendering
  echo "John" | jtable-template "Hello {{ stdin }}"

  # Using environment variables directly
  jtable-template -E "Hello {{ LOGNAME }}, how are you?"

  # Using environment variables in namespace
  jtable-template -En env "Your home directory is: {{ env.HOME }}"

  # View the generated playbook without executing
  jtable-template -vp "Hello {{ stdin }}"
        """
    )

    parser.add_argument(
        'template',
        help='Jinja2 template string to render'
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
        '-vp', '--view-play',
        action='store_true',
        dest='view_play',
        help='Display the playbook in YAML format without executing it'
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

    # Build variables dict
    variables = {}

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

    # Build in-memory playbook
    playbook = {
        'stdout': args.template,
        'vars': {}
    }

    # If --view-play is set, display the playbook and exit
    if args.view_play:
        # Build the full context for display
        display_playbook = {
            'stdout': args.template,
            'vars': {}
        }

        # Add note about stdin if present
        if stdin_data:
            display_playbook['_comment_stdin'] = 'stdin data is available as {{ stdin }}'

        # Add note about variables if present
        if variables:
            display_playbook['_comment_variables'] = f'Variables: {list(variables.keys())}'

        print(yaml.dump(display_playbook, default_flow_style=False, sort_keys=False))
        sys.exit(0)

    # Create and execute player
    try:
        player = Player(
            playbook_dict=playbook,
            variables=variables,
            stdin_data=stdin_data
        )
        output = player.execute()
        print(output)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as error:
        logging.error(f"Failed to execute template: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
