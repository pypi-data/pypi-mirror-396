#!/usr/bin/env python3
import sys
import os
import logging
import logging.config
import inspect

# Add jtable to path
jtable_path = os.path.dirname(os.path.abspath(__file__))
if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)

# Import logging configuration
from logger import logging_config

# Import Player class
from player import Player

# Import Plugin and functions module for discovery
import functions
from functions import Plugin


def discover_filters_and_plugins():
    """
    Discover all available filters and plugins by introspecting the functions module.

    Returns:
        tuple: (filters_dict, plugins_dict, jinja_builtins)
            filters_dict: Dict mapping filter names to their function objects
            plugins_dict: Dict mapping plugin names to their function objects
            jinja_builtins: List of known Jinja2 built-in filter names
    """
    # Discover filters (module-level functions in functions.py)
    filters_dict = {}
    for name, obj in inspect.getmembers(functions, inspect.isfunction):
        if not name.startswith('_'):  # Skip private functions
            filters_dict[name] = obj
            logging.debug(f"Discovered filter: {name}")

    # Add to_table as a special filter (it's from to_table module, not functions)
    # to_table is a method that accepts various parameters for table rendering
    # Define placeholder with actual signature for parameter discovery
    def to_table_placeholder(dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}):
        """Render data as a table"""
        pass
    filters_dict['to_table'] = to_table_placeholder
    logging.debug(f"Added special filter: to_table")

    # Add to_table_x as a special filter (context-aware version of to_table)
    # to_table_x has the same signature as to_table
    def to_table_x_placeholder(dataset, path="{}", select=[], unselect=[], views={}, when=[], format="", context={}, queryset={}):
        """Render data as a table (context-aware)"""
        pass
    filters_dict['to_table_x'] = to_table_x_placeholder
    logging.debug(f"Added special filter: to_table_x")

    # Discover plugins (static methods in Plugin class)
    plugins_dict = {}
    for name, obj in inspect.getmembers(Plugin, inspect.isfunction):
        if not name.startswith('_'):  # Skip private functions
            plugins_dict[name] = obj
            logging.debug(f"Discovered plugin: {name}")

    # Known Jinja2 built-in filters
    # These don't need parameter introspection - they're handled by Jinja directly
    jinja_builtins = [
        'abs', 'attr', 'batch', 'capitalize', 'center', 'default',
        'dictsort', 'escape', 'filesizeformat', 'first', 'float',
        'forceescape', 'format', 'groupby', 'indent', 'int', 'join',
        'last', 'length', 'list', 'lower', 'map', 'max', 'min',
        'pprint', 'random', 'reject', 'rejectattr', 'replace',
        'reverse', 'round', 'safe', 'select', 'selectattr', 'slice',
        'sort', 'string', 'striptags', 'sum', 'title', 'trim',
        'truncate', 'unique', 'upper', 'urlencode', 'urlize',
        'wordcount', 'wordwrap', 'xmlattr', 'tojson', 'items', 'keys',
        'values'
    ]

    return filters_dict, plugins_dict, jinja_builtins


def get_function_parameters(func):
    """
    Introspect a function to get its parameters.

    Args:
        func: Function object to introspect

    Returns:
        dict: Dictionary mapping parameter names to their default values (or None if no default)
    """
    try:
        sig = inspect.signature(func)
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:  # Skip self/cls for methods
                continue
            if param.default == inspect.Parameter.empty:
                params[param_name] = None  # No default value
            else:
                params[param_name] = param.default
        return params
    except Exception as e:
        logging.warning(f"Failed to introspect function {func.__name__}: {e}")
        return {}


def generate_short_names(param_names):
    """
    Generate short names for parameters, handling conflicts.

    If two parameters start with the same letter, append letters until unique.
    Example: 'name' and 'no_log' -> 'na' and 'no'

    Args:
        param_names: List of parameter names

    Returns:
        dict: Dictionary mapping parameter names to their short names
    """
    short_names = {}
    used_shorts = set()

    for param in param_names:
        # Start with first letter
        short = param[0]
        idx = 1

        # Keep adding letters until we find a unique short name
        while short in used_shorts and idx < len(param):
            short = param[:idx + 1]
            idx += 1

        # If still not unique (shouldn't happen with proper param names), use full name
        if short in used_shorts:
            short = param

        short_names[param] = short
        used_shorts.add(short)

    return short_names


def extract_queryset_from_filter(args, filters_dict, plugins_dict):
    """
    Extract queryset structure from to_table/to_table_x filter parameters.

    This is used when view_play option is enabled to generate the queryset
    that will be placed in the vars section of the playbook.

    Args:
        args (list): List of argument strings representing the filter and its options
        filters_dict: Dictionary of available filters
        plugins_dict: Dictionary of available plugins

    Returns:
        dict: Queryset structure or None if not a to_table filter
    """
    if not args:
        return None

    filter_name = args[0]

    # Only extract queryset for to_table and to_table_x
    if filter_name not in ['to_table', 'to_table_x']:
        return None

    # Get filter function to introspect parameters
    filter_func = filters_dict.get(filter_name) or plugins_dict.get(filter_name)
    if not filter_func:
        return None

    # Get parameter information
    filter_params = get_function_parameters(filter_func)
    param_names = list(filter_params.keys())

    # Generate short names for parameters
    short_to_long = generate_short_names(param_names)

    # Legacy short names for backwards compatibility
    legacy_short_names = {
        'p': 'path',
        's': 'select',
        'us': 'unselect',
        'w': 'when',
        'f': 'format',
    }

    filter_kwargs = {}

    i = 1
    while i < len(args):
        arg = args[i]

        if arg.startswith('-'):
            # It's an option
            option_name = arg.lstrip('-')

            # Try legacy mapping first, then check if it's a valid parameter
            if option_name in legacy_short_names:
                full_option = legacy_short_names[option_name]
            elif option_name in param_names:
                full_option = option_name
            elif option_name in short_to_long.values():
                full_option = [k for k, v in short_to_long.items() if v == option_name][0]
            else:
                full_option = option_name

            # Get the value (next argument)
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                value = args[i + 1]
                i += 1

                # Handle comma-separated values (like select fields)
                if ',' in value and full_option in ['select', 'unselect']:
                    filter_kwargs[full_option] = [v.strip() for v in value.split(',')]
                elif full_option == 'path':
                    # Auto-append {} to path if not already present
                    import re
                    expr_end_by_braces = re.sub('.*({).*(})$', r'\1\2', value)
                    if expr_end_by_braces != "{}":
                        value = value + "{}"
                    filter_kwargs[full_option] = value
                else:
                    filter_kwargs[full_option] = value
            else:
                # Boolean flag
                filter_kwargs[full_option] = True

        i += 1

    # Build the queryset structure
    queryset = {}

    # Add path (default to '{}' if not specified)
    queryset['path'] = filter_kwargs.get('path', '{}')

    # Add select (convert to list of dicts with 'as' and 'expr' keys)
    if 'select' in filter_kwargs:
        select_list = filter_kwargs['select'] if isinstance(filter_kwargs['select'], list) else filter_kwargs['select'].split(',')
        queryset['select'] = [{'as': field.strip(), 'expr': field.strip()} for field in select_list]

    # Add unselect if present
    if 'unselect' in filter_kwargs:
        queryset['unselect'] = filter_kwargs['unselect']

    # Add when if present
    if 'when' in filter_kwargs:
        queryset['when'] = filter_kwargs['when']

    # Add format (default to 'simple' if not specified)
    queryset['format'] = filter_kwargs.get('format', 'simple')

    return queryset


def build_filter_expression(args, filters_dict, plugins_dict, jinja_builtins, use_queryset=False):
    """
    Build a Jinja2 filter expression from parsed arguments.

    This function converts the CLI filter chain into a Jinja template expression.
    For example:
        ['to_table', '-p', 'hosts', '-s', 'hostname,os,state']
    becomes:
        "to_table(path='hosts', select=['hostname', 'os', 'state'])"

    Args:
        args (list): List of argument strings representing the filter and its options
        filters_dict: Dictionary of available filters
        plugins_dict: Dictionary of available plugins
        jinja_builtins: List of Jinja built-in filters
        use_queryset (bool): If True, use queryset=queryset for to_table/to_table_x filters

    Returns:
        str: Jinja filter expression
    """
    if not args:
        return ""

    filter_name = args[0]

    # Special handling for to_table/to_table_x when use_queryset is True
    if use_queryset and filter_name in ['to_table', 'to_table_x']:
        return f"{filter_name}(queryset=queryset)"

    # For Jinja built-ins, just return the filter name (no parameters supported for now)
    if filter_name in jinja_builtins:
        logging.debug(f"Using Jinja built-in filter: {filter_name}")
        # Some Jinja built-ins take simple arguments, pass them through
        if len(args) > 1 and not args[1].startswith('-'):
            # Simple positional argument (e.g., 'default' filter with a value)
            return f"{filter_name}({args[1]})"
        return filter_name

    # Get filter function to introspect parameters
    filter_func = filters_dict.get(filter_name) or plugins_dict.get(filter_name)
    if not filter_func:
        logging.warning(f"Unknown filter: {filter_name}, treating as Jinja built-in")
        return filter_name

    # Get parameter information
    filter_params = get_function_parameters(filter_func)
    param_names = list(filter_params.keys())

    # Generate short names for parameters
    short_to_long = generate_short_names(param_names)
    # Invert to create long-to-short mapping for lookup
    long_to_short = {v: k for k, v in short_to_long.items()}

    # Also support legacy short names for backwards compatibility
    legacy_short_names = {
        'p': 'path',
        's': 'select',
        'us': 'unselect',
        'w': 'when',
        'f': 'format',
    }

    filter_kwargs = {}

    i = 1
    while i < len(args):
        arg = args[i]

        if arg.startswith('-'):
            # It's an option
            option_name = arg.lstrip('-')

            # Try legacy mapping first, then check if it's a valid parameter
            if option_name in legacy_short_names:
                full_option = legacy_short_names[option_name]
            elif option_name in param_names:
                # Already the full parameter name
                full_option = option_name
            elif option_name in short_to_long.values():
                # It's a generated short name, find the corresponding long name
                full_option = [k for k, v in short_to_long.items() if v == option_name][0]
            else:
                # Unknown option, use as-is
                full_option = option_name
                logging.warning(f"Unknown option for filter {filter_name}: {option_name}")

            # Get the value (next argument)
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                value = args[i + 1]
                i += 1

                # Handle comma-separated values (like select fields)
                if ',' in value and full_option in ['select', 'unselect']:
                    # Convert to list
                    filter_kwargs[full_option] = [v.strip() for v in value.split(',')]
                elif full_option == 'path':
                    # Auto-append {} to path if not already present
                    # This matches the behavior of the old jtable CLI
                    import re
                    expr_end_by_braces = re.sub('.*({).*(})$', r'\1\2', value)
                    if expr_end_by_braces != "{}":
                        value = value + "{}"
                    filter_kwargs[full_option] = value
                else:
                    filter_kwargs[full_option] = value
            else:
                # Boolean flag
                filter_kwargs[full_option] = True

        i += 1

    # Build the filter expression
    params = []

    # Add kwargs
    for key, value in filter_kwargs.items():
        if isinstance(value, list):
            # For select/unselect, join with comma and pass as string
            # (to_table expects select as a comma-separated string, not a list)
            if key in ['select', 'unselect']:
                formatted_value = ','.join(value)
                params.append(f'{key}="{formatted_value}"')
            else:
                # Format as Python list for other parameters
                formatted_list = '[' + ', '.join([f'"{v}"' for v in value]) + ']'
                params.append(f'{key}={formatted_list}')
        elif isinstance(value, bool):
            params.append(f'{key}={str(value)}')
        elif isinstance(value, str):
            params.append(f'{key}="{value}"')
        else:
            params.append(f'{key}={value}')

    if params:
        return f"{filter_name}({', '.join(params)})"
    else:
        return filter_name


def parse_filter_chain(argv, filters_dict, plugins_dict, jinja_builtins, use_queryset=False):
    """
    Parse command-line arguments to identify module and filter chain.

    This function processes the argv to extract:
    1. Optional initial module (like 'load_json <file>')
    2. Chain of filters with their options

    Args:
        argv: Command-line arguments
        filters_dict: Dictionary of available filters
        plugins_dict: Dictionary of available plugins
        jinja_builtins: List of Jinja built-in filters
        use_queryset (bool): If True, use queryset=queryset for to_table/to_table_x filters

    Returns:
        tuple: (module_expr, filter_exprs, queryset)
            module_expr: Initial module expression or None if stdin is used
            filter_exprs: List of filter expressions
            queryset: Queryset dict if to_table/to_table_x is used, None otherwise
    """
    module_expr = None
    filter_exprs = []
    current_filter = []
    queryset = None

    # Modules are plugins that load data (typically take a filename argument)
    # Common file loading plugins
    file_loading_plugins = ['load_json', 'load_yaml', 'load_files']
    known_modules = [name for name in plugins_dict.keys() if name in file_loading_plugins]

    # All available filters (functions + plugins + jinja builtins)
    known_filters = list(filters_dict.keys()) + list(plugins_dict.keys()) + jinja_builtins

    i = 0

    # Check if first argument is a module
    if i < len(argv) and argv[i] in known_modules:
        module_name = argv[i]
        i += 1

        # Get the filename argument
        if i < len(argv) and not argv[i].startswith('-') and argv[i] not in known_filters:
            filename = argv[i]
            module_expr = f'{module_name}("{filename}")'
            i += 1
        else:
            # Module without filename - error
            logging.error(f"Module '{module_name}' requires a filename argument")
            sys.exit(1)

    # Parse filters
    while i < len(argv):
        arg = argv[i]

        if arg in known_filters:
            # Save previous filter if any
            if current_filter:
                # Extract queryset from to_table/to_table_x if use_queryset is True
                if use_queryset:
                    extracted_queryset = extract_queryset_from_filter(current_filter, filters_dict, plugins_dict)
                    if extracted_queryset:
                        queryset = extracted_queryset

                filter_exprs.append(build_filter_expression(current_filter, filters_dict, plugins_dict, jinja_builtins, use_queryset))

            # Start new filter
            current_filter = [arg]
        elif arg.startswith('-') or (current_filter and not arg in known_filters):
            # Option for current filter
            current_filter.append(arg)
        else:
            logging.error(f"Unexpected argument: {arg}")
            sys.exit(1)

        i += 1

    # Save last filter
    if current_filter:
        # Extract queryset from to_table/to_table_x if use_queryset is True
        if use_queryset:
            extracted_queryset = extract_queryset_from_filter(current_filter, filters_dict, plugins_dict)
            if extracted_queryset:
                queryset = extracted_queryset

        filter_exprs.append(build_filter_expression(current_filter, filters_dict, plugins_dict, jinja_builtins, use_queryset))

    return module_expr, filter_exprs, queryset


def main():
    """Main entry point for jtable-filter CLI"""
    # Configure logging (simple version for now)
    logging_config['handlers']['console_stderr']['level'] = 'WARNING'
    logging.config.dictConfig(logging_config)

    # Discover all available filters and plugins
    filters_dict, plugins_dict, jinja_builtins = discover_filters_and_plugins()

    # Check for help
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        # Build help message with discovered filters
        help_msg = """jtable-filter - Chain filters for data transformation

Usage:
    # With module (loading from file)
    jtable-filter <module> <module_args> [filter <filter_options>]...

    # From stdin (piped data)
    cat data.json | jtable-filter <filter> [filter_options] [filter <filter_options>]...

Modules (Plugins):
"""
        # Show file-loading plugins
        for plugin_name in sorted(plugins_dict.keys()):
            if plugin_name in ['load_json', 'load_yaml', 'load_files']:
                help_msg += f"    {plugin_name:<20} {plugins_dict[plugin_name].__doc__.split(chr(10))[0] if plugins_dict[plugin_name].__doc__ else ''}\n"

        help_msg += "\nFilters:\n"

        # Show all filters (limit to most common ones for brevity)
        common_filters = ['from_json', 'from_yaml', 'to_table', 'to_table_x', 'to_json', 'to_yaml',
                         'to_nice_json', 'to_nice_yaml', 'dict2items', 'flatten']

        for filter_name in sorted(filters_dict.keys()):
            if filter_name in common_filters:
                func = filters_dict[filter_name]
                params = get_function_parameters(func)
                short_names = generate_short_names(list(params.keys()))

                # Show filter name
                help_msg += f"    {filter_name:<20}"

                # Show first line of docstring if available
                if func.__doc__:
                    help_msg += func.__doc__.split('\n')[0].strip()
                help_msg += "\n"

                # Show parameters if any
                if params and filter_name == 'to_table':
                    help_msg += f"        -p, --path      Path in data structure\n"
                    help_msg += f"        -s, --select    Comma-separated list of columns to select\n"
                    help_msg += f"        -us, --unselect Comma-separated list of columns to exclude\n"
                    help_msg += f"        -w, --when      Filter condition\n"
                    help_msg += f"        -f, --format    Output format (simple, github, html, etc.)\n"

                # Show parameters for to_table_x (context-aware version)
                if filter_name == 'to_table_x':
                    help_msg += f"        (Context-aware version - has access to stdin and vars in when conditions)\n"
                    help_msg += f"        -p, --path      Path in data structure\n"
                    help_msg += f"        -s, --select    Comma-separated list of columns to select\n"
                    help_msg += f"        -us, --unselect Comma-separated list of columns to exclude\n"
                    help_msg += f"        -w, --when      Filter condition (can use stdin, vars, etc.)\n"
                    help_msg += f"        -f, --format    Output format (simple, github, html, etc.)\n"

        help_msg += "\n    Also supports Jinja2 built-in filters: list, keys, values, items, etc.\n"
        help_msg += "\n    Use -v/--verbose to see all available filters.\n"

        help_msg += """
Examples:
    # Load JSON file and display as table
    jtable-filter load_json data.json to_table -p hosts -s hostname,os,state

    # From stdin with filter chain
    cat data.json | jtable-filter from_json to_table -p hosts

    # Use Jinja built-in filters
    echo '{"hostname": "host_1", "os": "linux"}' | jtable-filter from_json list

    # Multiple filters
    cat data.yml | jtable-filter from_yaml to_table -s name,value to_json

Options:
    -h, --help         Show this help message
    -v, --verbose      Increase verbosity (shows all filters)
    -vp, --view_play   Display the playbook YAML instead of executing it
    -E, --env          Expose OS environment variables in filter expressions
    --debug            Enable debug mode
"""
        print(help_msg)
        sys.exit(0)

    # Parse arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    debug = '--debug' in sys.argv
    expose_env = '--env' in sys.argv or '-E' in sys.argv
    view_play = '--view_play' in sys.argv or '-vp' in sys.argv

    # Remove options from argv
    argv = [arg for arg in sys.argv[1:] if arg not in ['--verbose', '-v', '--debug', '--env', '-E', '--view_play', '-vp']]

    if verbose:
        logging_config['handlers']['console_stderr']['level'] = 'INFO'
    if debug:
        logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging_config['formatters']['my_formatter']['format'] = \
            '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'

    logging.config.dictConfig(logging_config)

    # Check for stdin data
    stdin_data = None
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        logging.info("Read data from stdin")

    # Parse the filter chain
    module_expr, filter_exprs, queryset = parse_filter_chain(argv, filters_dict, plugins_dict, jinja_builtins, use_queryset=view_play)

    logging.info(f"Module expression: {module_expr}")
    logging.info(f"Filter expressions: {filter_exprs}")
    if view_play and queryset:
        logging.info(f"Queryset: {queryset}")

    # Build the template expression
    if module_expr:
        # Start with module
        template_expr = module_expr
    else:
        # Start with stdin
        if stdin_data is None:
            logging.error("No input data provided. Either use a module (load_json, load_yaml) or pipe data via stdin.")
            sys.exit(1)
        template_expr = "stdin"

    # Add filters
    for filter_expr in filter_exprs:
        template_expr += f" | {filter_expr}"

    # Wrap in Jinja template syntax
    template = f"{{{{ {template_expr} }}}}"

    logging.info(f"Generated template: {template}")

    # Build in-memory playbook
    playbook = {
        'vars': {},
        'stdout': template
    }

    # If view_play is enabled, build and display the playbook YAML instead of executing
    if view_play:
        if queryset:
            # Auto-discover select fields if not specified
            if 'select' not in queryset:
                # Need to execute the filter chain with format="th" to discover field names
                # Create a temporary queryset with format="th" to get headers
                temp_queryset = queryset.copy()
                temp_queryset['format'] = 'th'

                # Build temporary playbook for field discovery
                temp_playbook = {
                    'stdout': template.replace('(queryset=queryset)', f'(queryset={temp_queryset})'),
                    'vars': {}
                }

                # Prepare variables
                temp_variables = {}
                if expose_env:
                    temp_variables.update(os.environ.copy())

                try:
                    # Execute to discover fields
                    temp_player = Player(
                        playbook_dict=temp_playbook,
                        variables=temp_variables,
                        stdin_data=stdin_data
                    )
                    fields_output = temp_player.execute()

                    # Parse the discovered fields (they're returned as a list)
                    import ast
                    try:
                        fields = ast.literal_eval(fields_output.strip())
                        if isinstance(fields, list):
                            # Rebuild queryset in correct order: path, select, format, when, unselect
                            new_queryset = {}
                            new_queryset['path'] = queryset.get('path', '{}')
                            new_queryset['select'] = [{'as': field, 'expr': field} for field in fields]
                            if 'unselect' in queryset:
                                new_queryset['unselect'] = queryset['unselect']
                            if 'when' in queryset:
                                new_queryset['when'] = queryset['when']
                            new_queryset['format'] = queryset.get('format', 'simple')
                            queryset = new_queryset
                        else:
                            logging.warning(f"Unexpected fields format: {fields}")
                    except (ValueError, SyntaxError) as e:
                        logging.warning(f"Failed to parse discovered fields: {e}")
                except Exception as e:
                    logging.warning(f"Failed to auto-discover fields: {e}")

            playbook['vars']['queryset'] = queryset

        # Import yaml for output
        import yaml

        # Generate YAML output
        yaml_output = yaml.dump(playbook, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(yaml_output)
        sys.exit(0)

    # Prepare variables for Player
    variables = {}
    if expose_env:
        logging.info("Exposing OS environment variables")
        variables.update(os.environ.copy())

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
        logging.error(f"Failed to execute filter chain: {error}")
        if debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
