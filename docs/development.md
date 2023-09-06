# Canvas LTI Tool Migration — Development

## Running with Python virtual environment

⚠ The method documented here for running the application is an alternative to
the method described in the [README.md](../README.md) file, in the
section "[Running with Docker compose](../README.md#running-with-docker-compose)".
This method is not recommended unless the required version of Python (3.11) is
installed, and you are familiar with its virtual environments. This method is
mostly useful for development.

### Prerequisites

* [Python 3.11](https://www.python.org/downloads/) — This must be installed
  first.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/archive/refs/heads/main.zip) —
  Download the latest release of this app and unzip it.  (Alternatively, the
  repository can be cloned.)

### Installation

```shell
python3.11 -m venv venv
source venv/bin/activate  # Mac OS
pip install -r requirements.txt
```

### Configuration

```shell
cp env.sample env
# Then fill in the missing values
```

### Running

```shell
python migration/main.py
```

## Testing

```shell
python migration/tests.py -v
```
