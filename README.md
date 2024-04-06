
# Beremiz4uC IDE

## Beremiz IDE Extension

This documentation provides the necessary steps to clone and set up the Beremiz4uC_IDE along with its submodules, which include Beremiz and matiec, offering a comprehensive development environment.

### Cloning Beremiz4uC_IDE and Submodules

To obtain the Beremiz4uC_IDE and its associated submodules, execute the following command:

```bash
git clone --recurse-submodules https://github.com/nandibrenna/Beremiz4uC_IDE.git
```

This command clones the main repository and initializes all included submodules.

### Setting Up Beremiz

To properly set up Beremiz, refer to the installation instructions provided on the [official Beremiz GitHub repository](https://github.com/beremiz/beremiz). These instructions detail the process for various environments and prerequisites.

#### Quick Setup Overview

**System Prerequisites for Ubuntu 22.04:**

Start by installing the required system packages. Open a terminal and run the following command:

```bash
sudo apt-get install build-essential automake flex bison mercurial libgtk-3-dev libgl1-mesa-dev libglu1-mesa-dev libpython3.10-dev libssl-dev python3.10 virtualenv cmake git mercurial
```

These packages include essential build tools, libraries for graphical interfaces, development files for Python 3.10, SSL support, and other necessary compilers and version control systems.

**Python Dependencies:**

Next, install Python dependencies by navigating to the cloned repository's directory and running:

```bash
pip install -r ~/Beremiz4uC_IDE/beremiz/requirements.txt
```

**Building the MatIEC Compiler:**

The MatIEC compiler translates IEC 61131-3 code into C. To build it, execute the following commands:

```bash
cd ~/Beremiz4uC_IDE/matiec
autoreconf -i
./configure
make
```

**Rebuilding the ERPC Code:**

For communication between components, rebuild the ERPC code by generating the necessary Python bindings:

```bash
cd ~/Beremiz4uC_IDE/beremiz/erpc_interface
erpcgen -I ~/Beremiz4uC_IDE/beremiz/erpc_interface -g py erpc_PLCObject.erpc
```

### Launching Beremiz4uC IDE

To start the Beremiz4uC IDE, execute the following script:

```bash
~/Beremiz4uC_IDE/Beremiz_4uC_IDE.py
```

Follow these steps to properly set up and launch Beremiz4uC IDE for development with Beremiz and MatIEC compiler support.
