# Tool Migration

## Getting started

### Installation

```
python3 -m venv venv
source venv/bin/activate  # Mac OS
pip install -r requirements.txt
```

### Configuration

```
mv .env.sample .env
# Then fill in the missing values
```

There will likely be other ways to configure in the future, such as a CLI, prompts, or files.

### Usage

```
python migration/main.py
```


### Testing

```
python migration/tests.py -v
```
