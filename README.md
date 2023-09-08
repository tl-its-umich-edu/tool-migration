# Canvas LTI Tool Migration — README

This application migrates LTI tools in a Canvas instance from one version to
another.

## Running with Docker compose

Using Docker compose is the recommended way to run this application. Docker
compose will ensure the application is run in a consistent environment with the
correct version of Python and all the required dependencies.

### Prerequisites

* **VPN** — At UMich, a VPN connection is required to access the Unizin Data
  Warehouse (UDW).
    * Using UDW is optional, but **_highly recommended_** to increase
      processing
      speed. If UDW is not used, the application will use the Canvas API to get
      the course data, but it is **_much slower_**.
* **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** — This
  must
  be installed first. Follow the instructions on the Docker website.
    * If Docker Desktop has already been installed, make sure it is up to date.
      Use the "Check for Updates…" command in the Docker Desktop menu to check
      for and install updates. Docker Desktop **version 4.22 or newer** is
      recommended.
* **A shell** (e.g., Terminal.app on macOS) — This is used to run commands in
  the
  terminal. The shell is used to install the application and to run it. Because
  this app doesn't have a graphical user interface (GUI), all the
  steps in this document are based on the use of a shell.
*
    *

*[tool-migration](https://github.com/tl-its-umich-edu/tool-migration/archive/refs/heads/master.zip)
** —
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

It takes some time for Docker Desktop to start up. While it is starting, the
Docker
icon (e.g., in the macOS menu bar) is animated. When it is ready, the animation
stops.

#### Run the application

When Docker Desktop is running, the application can be run with the command:

```shell
docker compose up
```

The first time this command is run, it will take 2–3 minutes to build the app,
which downloads and installs the Docker images and dependencies the application
needs. On subsequent runs, the build phase will usually be very fast, but may
sometimes take 1–2 minutes to install dependency updates if any are available.

#### Stopping the application

If the app needs to be stopped, press ^C (control-C) in the terminal window
where the app is running. This will tell Docker to stop the app. Docker will do
a "graceful" shutdown of the app. If gracefulness isn't desired, press ^C again
to force a quick stop.

#### Resuming the application

If the app doesn't complete its updates, due to any kind of interruption (e.g.,
user intervention, network problems, etc.) running the app again without
changing the configuration file (`env`) will cause it to continue where it left
off.

```shell
docker compose up
```

I.e., if the app was configured to change tool A to tool B in many courses and
it gets interrupted, then the courses that were processed up to the moment of
the interruption will have been changed from tool A to tool B. To update the
remaining courses, run the app again with the same config. When the app starts,
it will examine all the courses and skip those that already have tool A
replaced with tool B.

#### Run the application again

If the app needs to be run again, the same command can be used:

```shell
docker compose up
```

As mentioned above, if the configuration file (`env`) has not been changed, the
app will continue
where it left off.


---

## Running with Python virtual environment

⚠ For an alternative method for running the application, mostly useful for
development, see the file [docs/development.md](docs/development.md) for more
information.

It is not recommended for most end users. It requires a recent version of
Python (3.11 or newer) is installed, and familiarity with its virtual
environments.


