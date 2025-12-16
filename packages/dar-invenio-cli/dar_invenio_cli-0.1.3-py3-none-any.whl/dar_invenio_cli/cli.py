import click
from .config import set_config, get_config
from .core import (
    create_draft_from_file,
    create_draft_from_name,
    create_drafts_from_files,
    create_drafts_from_folder,
    upload_files_to_draft,
)


@click.group()
def cli():
    """A command-line interface for Invenio."""
    pass


@cli.group()
def config():
    """Configuration commands."""
    pass


@config.command()
def show():
    """Shows the current configuration."""
    config = get_config()
    if config:
        for key, value in config.items():
            click.echo(f"{key}: {value}")


@config.command()
@click.option("--api-token", "api_token", type=str, required=True, help="Your API token.")
def init(api_token):
    """Initializes the configuration with default values."""
    default_config = {
        "api_token": api_token,
        "base_api_url": "https://dar.elter-ri.eu/api/",
        "model": "datasets",
    }
    set_config(default_config)
    click.echo("Configuration initialized with default values.")


@config.command()
@click.option("--api-token", "api_token", help="Your API token.")
@click.option("--base-api-url", "base_api_url", help="The base API URL.")
@click.option("--model", "base_api_url", help="The model to use.")
def update(api_token, base_api_url, model):
    """Configures the application."""
    config = get_config()
    if not config:
        return

    if api_token is not None:
        config["api_token"] = api_token
    if base_api_url is not None:
        config["base_api_url"] = base_api_url
    if model is not None:
        config["model"] = model

    set_config(config)
    click.echo("Configuration updated successfully.")


@cli.group()
def create():
    """Create drafts."""
    pass


@create.command()
@click.option("--from-file", "file_path", type=click.Path(exists=True), help="Path to a JSON file.")
@click.option("--from-title", "title", type=str, help="Name of the draft.")
def draft(file_path, title):
    """Creates a single draft."""
    if file_path and title:
        click.echo("You can provide only one of --from-json-file or --from-name option.")
        return
    config = get_config()
    if not config:
        return
    if file_path:
        result = create_draft_from_file(config, file_path)
        click.echo(result)
    elif title:
        result = create_draft_from_name(config, title)
        click.echo(result)
    else:
        click.echo("Please provide either --from-json-file or --from-name.")


@create.command()
@click.option("--from-files", "files_paths", type=click.Path(exists=True), multiple=True,
              help="Paths to JSON files.")
@click.option("--from-folder", "folder_path", type=click.Path(exists=True), help="Path to a folder with JSON files.")
def drafts(files_paths, folder_path):
    """Creates multiple drafts."""
    config = get_config()
    if not config:
        return

    if files_paths:
        results = create_drafts_from_files(config, files_paths)
        for result in results:
            click.echo(result)
    elif folder_path:
        results = create_drafts_from_folder(config, folder_path)
        for result in results:
            click.echo(result)
    else:
        click.echo("Please provide either --from-files or --from-folder.")

@cli.group()
def upload():
    """Upload files to drafts."""
    pass

@upload.command()
@click.argument("draft_id", nargs=1)
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
def files(draft_id, file_paths):
    """Uploads files to a draft."""
    config = get_config()
    if not config:
        return

    if not file_paths:
        click.echo("Please provide at least one file path.")
        return

    result = upload_files_to_draft(config, draft_id, file_paths)
    click.echo(result)

@upload.command()
@click.argument("draft_id", nargs=1)
@click.argument("folder_path", type=click.Path(exists=True), nargs=1)
def folder(draft_id, folder_path):
    """Uploads all files from a folder to a draft."""
    config = get_config()
    if not config:
        return

    from pathlib import Path
    folder = Path(folder_path)
    file_paths = [str(path) for path in folder.glob("*") if path.is_file()]

    if not file_paths:
        click.echo("No files found in the specified folder.")
        return

    result = upload_files_to_draft(config, draft_id, file_paths)
    click.echo(result)

if __name__ == "__main__":
    cli()
