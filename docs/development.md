# Canvas LTI Tool Migration

## Running with Python virtual environment

⚠ This is an alternative way to run the application.  It is not recommended unless the required version of Python (3.11) is installed, and you are familiar with its virtual environments.  This method is mostly useful for development.

### Prerequisites

* [Python 3.11](https://www.python.org/downloads/) — This must be installed first.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/archive/refs/heads/main.zip) — Download the latest release of this app and unzip it.  (Alternatively, the repository can be cloned.)

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
