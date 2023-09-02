# Canvas LTI Tool Migration

This application migrates LTI tools in a Canvas instance from one version to another.

## Running with Docker compose

Using Docker compose is the recommended way to run this application.  Docker compose will ensure the application is run in a consistent environment with the correct version of Python and all the required dependencies.

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) — This must be installed first.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/releases/latest) — Download the latest release of this app and unzip it.  The latest release will be at the top of the list.  The zip file is found under the heading "Assets".  (Alternatively, its repository can be cloned.)

### Configuration

In a shell (e.g., using Terminal.app on macOS), navigate to the directory where the app was unzipped or cloned.  Then copy the sample configuration file to the file that will be used by the application, `env`:

```shell
cp env.sample env
```

Then open the newly copied `env` file with an editor and fill in the missing values.  E.g., to edit with TextEdit.app on macOS:

```shell
open -a TextEdit env
```

Carefully fill in the values for each of the variables.  The values must be surrounded by quotes.  E.g.,

```shell
```

### Running

#### Start Docker Desktop

Docker Desktop must be running before the application can be run.  To start Docker Desktop, open the "Docker" app from the Applications folder.

Alternatively, Docker Desktop can be started from the command line:

```shell
open -a Docker
```

#### Run the application

When Docker Desktop is running, the application can be run with the command:

```shell
docker compose up
```

---

## Running with Python virtual environment

⚠ This is an alternative method for running the application.  It is not recommended unless the required version of Python (3.11) is installed, and you are familiar with its virtual environments.  This method is mostly useful for development.

See the file [docs/development.md](docs/development.md) for more information about this method.
