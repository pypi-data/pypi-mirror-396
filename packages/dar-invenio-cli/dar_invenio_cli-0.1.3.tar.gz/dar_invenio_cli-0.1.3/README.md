# DAR-INVENIO-CLI

DAR-INVENIO-CLI is a command-line tool for creating drafts and uploading files in the Invenio webpage.

## Installation
### From PyPI (Recommended)
This installation may vary for different operating systems.

Link to [Pypi package](https://pypi.org/project/dar-invenio-cli/)

#### Steps with venv activation:
```bash
sudo apt install python3-full 
```

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install <your-package>
```

### From source (cloned repository)
1.  **Install Python and venv:**
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv git
    ```

2.  **Clone the repository:**
    ```bash
    git clone git@gitlab.ics.muni.cz:dataraptors/elter/dar-invenio-cli.git
    cd dar-invenio-cli
    ```

3.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Install the package:**
    ```bash
    pip install .
    ```

## Configuration

Before using the features, you need to set up the configuration. The configuration initialization with `api_token` is required.

```bash
dar-invenio-cli config init --api-token <your-api-token>
```

You can also update the values for `base-api-url` and `model` or `api_token` later:

```bash
dar-invenio-cli config update 
```
with optional options:
- `--base-api-url <your-base-api-url>`
- `--model <your-model>`
- `--api-token <your-api-token>`

The init script sets default values for the cli and you can see the actual configuration by running:
```bash
dar-invenio-cli config show
```


## Usage

If you do not have configuration set up, the commands will prompt you to run the configuration initialization first.

### Create a single draft

From a JSON file - you need to provide valid json with its metadata structure, otherwise the creation may fail:
```bash
dar-invenio-cli create draft --from-file /path/to/your/file.json
```

From a name - creates a draft with empty metadata except for the title:
```bash
dar-invenio-cli create draft --from-title "My Draft Name"
```

### Create multiple drafts

From multiple JSON files:
```bash
dar-invenio-cli create drafts --from-files /path/to/file1.json /path/to/file2.json
```

From a folder containing JSON files:
```bash
dar-invenio-cli create drafts --from-folder /path/to/your/folder
```

### Upload files to a draft

```bash
dar-invenio-cli upload files <draft_id> /path/to/file1 /path/to/file2
```

### Upload files from a folder to a draft
It uploads all files from the specified folder to the given draft - if you want to have it in one file, create and upload ZIP.
```bash
dar-invenio-cli upload folder <draft_id> /path/to/your/folder
```

## For Developers

The core logic is located in `dar_invenio_cli/core.py`. You can import and use the functions from this module in your own Python projects.

## Deployment to PyPI

The easiest way, how to deploy a new version is to bump the version in the setup.cfg and run the deploy pipline on GitLab.

