# Canvas LTI Tool Migration

This application migrates LTI tools in a Canvas instance from one version to another.

## Running with Docker compose

This is the recommended way to run the application.  Docker compose will ensure the application is run in a consistent environment with the correct version of Python and all the required dependencies.

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) — This must be installed first.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/releases/latest) — Download the latest release of this app and unzip it.  The latest release will be at the top of the list.  The zip file is found under the heading "Assets".  (Alternatively, the repository can be cloned.)

### Configuration

In a shell (e.g., using Terminal.app on macOS), navigate to the directory where the app was unzipped or cloned.  Then copy the sample configuration file:

```shell
cp .env.sample .env
```

Then open the newly copied `.env` file with an editor and fill in the missing values.  E.g., to edit with TextEdit.app on macOS:

```shell
open -a TextEdit .env
```

Note: Starting the editor this way is recommended because the hidden file `.env` is not visible in the editor's "Open" dialog.

### Running

```shell
docker compose up
```

---

## Running with Python virtual environment

⚠ This is an alternative way to run the application.  It is not recommended unless the required version of Python (3.11) is installed, and you are familiar with its virtual environments.  This method is mostly useful for development.

### Prerequisites

* [Python 3.11](https://www.python.org/downloads/) — This must be installed first.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/archive/refs/heads/main.zip) — Download the latest release of this app and unzip it.  (Alternatively, the repository can be cloned.)

### Installation

```shell
python3 -m venv venv
source venv/bin/activate  # Mac OS
pip install -r requirements.txt
```

### Configuration

```shell
cp .env.sample .env
# Then fill in the missing values
```

Note: Starting the editor this way is recommended because the hidden file `.env` is not visible in the editor's "Open" dialog.

### Running

```shell
python migration/main.py
```


## Testing

This step is only for development and will not be run by end users.

```shell
python migration/tests.py -v
```
