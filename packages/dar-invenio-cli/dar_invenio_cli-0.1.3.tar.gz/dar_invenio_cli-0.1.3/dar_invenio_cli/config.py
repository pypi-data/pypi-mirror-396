import json
import click
from pathlib import Path

CONFIG_FILE = Path(".dar-invenio-cli.json")

def set_config(config):
    """Sets the configuration."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    return config

def get_config():
    """Gets the configuration."""
    if not CONFIG_FILE.is_file():
        click.echo("Configuration file not found. Please run config 'init' first.")
        return None
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        if not config:
            click.echo("Configuration is invalid. Please run config 'init' first.")
            return None
        return config
