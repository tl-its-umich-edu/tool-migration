# Canvas LTI Tool Migration — README

This application migrates LTI tools in a Canvas instance from one version to
another.

## Running with Docker compose

Using Docker compose is the recommended way to run this application. Docker
compose will ensure the application is run in a consistent environment with the
correct version of Python and all the required dependencies.

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) — This must
  be installed first. Follow the instructions on the Docker website.
* A shell (e.g., Terminal.app on macOS) — This is used to run commands in the
  terminal. The shell is used to install the application and to run it. The
  steps in this document are based on the use of a shell.
* [tool-migration](https://github.com/tl-its-umich-edu/tool-migration/archive/refs/heads/master.zip) —
  Download the current version of this app and unzip it. If you're using macOS
  and this downloaded to your `Downloads` folder, you can unzip it and install
  it in your `Applications` folder with the command:

    ```shell
    unzip -o ~/Downloads/tool-migration-master.zip -d ~/Applications
    ```
  That installs the app in the `~/Applications/tool-migration-master`
  directory.  
  Any time the application needs to be updated to the latest version, the same
  command can be run again.

### Configuration

Navigate to the directory where the app was unzipped.

```shell
cd ~/Applications/tool-migration-master
```

Then copy the sample configuration file to the file that will be used by the
application, `env`:

```shell
cp env.sample env
```

Then open the newly copied `env` file with an editor and fill in the missing
values. E.g., to edit with TextEdit.app on macOS:

```shell
open -a TextEdit env
```

Carefully fill in the values for each of the variables. Variables begin at the
start of each line, are immediately followed by an equals sign ("`=`"), which
is immediately followed by a value. Lines beginning with a pound sign ("`#`")
are comments and are ignored.

For example, here are some lines from an `env` file, as they appeared in the
original `env.sample` file, that need to be filled in…

```text
# ID of current tool to be phased out (i.e., hidden)
SOURCE_TOOL_ID=
# ID of replacement tool to be shown in place of current tool
TARGET_TOOL_ID=
```

Here is an example of those same lines with values filled in…

```text
# ID of current tool to be phased out (i.e., hidden)
SOURCE_TOOL_ID=37063
# ID of replacement tool to be shown in place of current tool
TARGET_TOOL_ID=15593
``` 

After editing the `env` file, be sure to save it.

### Running

#### Start Docker Desktop

Docker Desktop must be running before the application can be run. To start
Docker Desktop, open the "Docker" app from the Applications folder.

Alternatively, Docker Desktop can be started from the command line:

```shell
open -a Docker
```

It takes some time for Docker Desktop to start up. When it is ready, the Docker
icon (e.g., in the macOS menu bar) will change from black to blue.

#### Run the application

When Docker Desktop is running, the application can be run with the command:

```shell
docker compose up
```

---

## Running with Python virtual environment

⚠ For an alternative method for running the application, mostly useful for
development, see the file [docs/development.md](docs/development.md) for more
information.

It is not recommended for most end users. It requires a recent version of
Python (3.11 or newer) is installed, and familiarity with its virtual
environments.


