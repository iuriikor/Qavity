# XenEth SDK python examples

## How to run the examples

> Prerequisites: - Xeneth SDK is installed
>                - Python 3.9.0+

For the examples to be able to find the python library, it needs to be installed in the python environment.

The easiest way to do this is using pip install to install from the file system.

```
# PATH_TO_LIBRARY_DIR is the path to the directory that contains the setup.py file

pip install PATH_TO_LIBRARY_DIR

# For example:
pip install .\py_dev 
```

> During development, the setup can be performed using the -e option. This will install a link to the library (instead of copying the files), so that re-install is not required after code changes.

```
# Example:
pip install -e .\py_dev 
```

If the library is installed successfully, you should be able to run the examples.