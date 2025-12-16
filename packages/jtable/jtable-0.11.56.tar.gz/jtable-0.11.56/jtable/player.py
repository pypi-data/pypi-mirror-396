#!/usr/bin/env python3
import sys, json, os, logging
from typing import Dict, Any, Optional
import yaml

# Import required modules from jtable
import functions
Plugin = functions.Plugin
running_context = functions.running_context()

# Import Templater and ToTable
import templater
import to_table

Templater = templater.Templater
ToTable = to_table.ToTable


def create_templater(*args, **kwargs):
    """Helper function to create Templater instances with to_table and to_table_x filters"""
    to_table_filter = to_table.ToTable().render_object
    to_table_x_filter = to_table.ToTable().render_object
    return Templater(*args, to_table_filter=to_table_filter, to_table_x_filter=to_table_x_filter, **kwargs)


class Player:
    """
    Player class for executing jtable playbooks (query files).

    This class loads YAML playbooks and executes them using the Templater,
    similar to the old `jtable -p <playbook>` functionality but as a
    standalone CLI tool.
    """

    def __init__(self, playbook_file: Optional[str] = None, variables: Optional[Dict[str, Any]] = None, stdin_data: Optional[str] = None, playbook_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize the Player with a playbook file or in-memory playbook dict and optional variables.

        Args:
            playbook_file: Path to the YAML playbook file (optional if playbook_dict is provided)
            variables: Optional dictionary of variables to inject into the context
            stdin_data: Optional stdin data to be available in templates
            playbook_dict: Optional in-memory playbook dictionary (instead of loading from file)
        """
        self.playbook_file = playbook_file
        self.playbook = playbook_dict  # Can be pre-loaded if provided
        self.dataset = {}
        self.variables = variables or {}

        # Add stdin data to dataset if provided
        if stdin_data:
            self.dataset['stdin'] = stdin_data

    def load_playbook(self):
        """Load and parse the YAML playbook file or use pre-loaded playbook dict"""
        # If playbook is already loaded (from playbook_dict), skip file loading
        if self.playbook is not None:
            logging.info("Using pre-loaded in-memory playbook")
            return self.playbook

        # Otherwise, load from file
        logging.info(f"Loading playbook file: {self.playbook_file}")

        if not self.playbook_file:
            logging.error("No playbook file or playbook dict provided")
            sys.exit(2)

        if not os.path.exists(self.playbook_file):
            logging.error(f"Playbook file not found: {self.playbook_file}")
            sys.exit(2)

        with open(self.playbook_file, 'r') as file:
            try:
                self.playbook = yaml.safe_load(file)
            except Exception as error:
                logging.error(f"Failed to load playbook file {self.playbook_file}, check YAML format")
                logging.error(f"Error was:\n{error}")
                sys.exit(2)

        if self.playbook is None:
            logging.error(f"Playbook file {self.playbook_file} is empty or invalid")
            sys.exit(2)

        logging.info(f"Successfully loaded playbook: {self.playbook_file}")
        return self.playbook

    def prepare_context(self):
        """
        Prepare the execution context by processing variables from the playbook
        and merging with command-line provided variables.
        """
        # Start with command-line variables - add them to dataset first
        vars_context = dict(self.variables)

        # Make command-line variables available in dataset for template rendering
        for key, value in self.variables.items():
            self.dataset[key] = value

        # Process vars section from playbook if it exists
        if 'vars' in self.playbook:
            logging.info("Processing vars section from playbook")

            for key, value in self.playbook['vars'].items():
                # Skip queryset - it's handled separately
                if key == 'queryset':
                    continue

                logging.info(f"Processing var: {key}")
                # Render the value as a Jinja template
                jinja_eval = create_templater(
                    template_string=str(value),
                    static_context=self.dataset
                ).render({}, eval_str=True)

                vars_context[key] = jinja_eval
                self.dataset[key] = jinja_eval

        # Add vars to dataset
        self.dataset['vars'] = vars_context

        logging.info(f"Prepared context with {len(vars_context)} variables")
        return vars_context

    def execute(self) -> str:
        """
        Execute the playbook and return the output.

        Returns:
            The rendered output as a string
        """
        # Load the playbook
        self.load_playbook()

        # Prepare the execution context
        self.prepare_context()

        # Get the stdout expression from playbook
        if 'stdout' not in self.playbook:
            logging.error("Playbook must contain a 'stdout' key defining the output")
            sys.exit(2)

        stdout_expr = self.playbook['stdout']
        logging.info(f"Executing stdout expression: {stdout_expr}")

        # Handle queryset if present
        queryset = {}
        if 'vars' in self.playbook and 'queryset' in self.playbook['vars']:
            queryset = self.playbook['vars']['queryset']
            self.dataset['queryset'] = queryset

        # Render the stdout expression
        try:
            output = create_templater(
                template_string=stdout_expr,
                static_context=self.dataset
            ).render({}, eval_str=False)

            return output

        except Exception as error:
            logging.error(f"Failed to execute playbook: {error}")
            raise
