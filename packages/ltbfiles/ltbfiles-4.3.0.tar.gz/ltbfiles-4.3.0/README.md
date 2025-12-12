# LTB-Files

This is a selection of functions providing loading functionalities for files created with ARYELLE series spectrometers from [LTB Lasertechnik Berlin GmbH](https://www.ltb-berlin.de/) and the Sophi software.

Documentation of the formats can be found on the corresponding [gitlab-page](https://ltb_berlin.gitlab.io/ltb_files/ltbfiles.html).

Documentatation can be found [here](https://ltb_berlin.gitlab.io/ltb_files/ltbfiles/ltbfiles.html). It is written for Python but function interfaces are the same for Matlab.

Issues can be reported online in the projects [issue-tracker](https://gitlab.com/ltb_berlin/ltb_files).

## Installation

### Python

[![Pyversions](https://img.shields.io/pypi/pyversions/ltbfiles.svg?style=flat-square)](https://pypi.python.org/pypi/ltbfiles)

Users of Python can install directly from [pypi](https://pypi.org/project/ltbfiles/) using:

```bash
pip install ltbfiles
```

Then you can use it like this:

```python
import ltbfiles
spec = ltbfiles.load_folder("path/to/folder", extensions=".aryx", interpolate=True)
```

### Matlab

The minimum version required is R2019b. Tests are being run with MATLAB version R2022b and R2024b.

The preferred way is to download the latest package from the [package registry](https://gitlab.com/ltb_berlin/ltb_files/-/packages) and install it by double clicking on it. All functions can now be accessed using the prefix `ltbfiles.function` like:

```matlab
[Y,x] = ltbfiles.load_folder("path/to/folder", extensions=".aryx", interpolate=true)
```

You may hit <kbd>F1</kbd> in order get help on any function.

#### Option2: Bundle a package yourself

Download or clone this project to your local machine and open the folder with MATLAB. Within MATLAB, open the file "ltbfiles_MATLAB-Toolbox.prj". MATLAB should open the "Package a Toolbox" dialog. Click on "Package" within the toolbar. A file named `ltbfiles.mltbx` is created inside the same folder. By double clicking on it, the toolbox is installed as a package within MATLAB and can now be found by all projects on the given machine. the toolbox-file can also be transferred to and installed on other devices.
There is no need to keep the original project on the machine after installing the toolbox.

#### Option3: Add folder to search path

Download or clone this project to your local machine. Keep the downloaded folder somewhere on the machine and use

```matlab
addpath(path/to/ltbfiles_MATLAB);
```

in the beginning of your projects.
