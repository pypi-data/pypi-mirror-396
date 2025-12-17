# evoSegment
This is a tool to segment microstructural evolution from 4D tomography data (or other image data).The method is based on clustering of a 2D histogram built from the intensities in a reference state and in an evolved state.

## Installation
The easiest is to install the package from PyPI using
```python3 -m pip install evosegment```

It is also possible to clone the repository, build and install a local wheel. Something like this might work:
```
 git clone https://gitlab.com/jhektor/evoSegment.git
 cd evoSegment
 python3 -m build
 python3 -m pip install -e .
```

Using this approach will install the package in an editable way so that any changes you make to the code are reflected without reinstalling.

## Usage
Have a look at the `example.ipynb`!

## License
This software is licensed under the GNU General Public Licence v3.0 or later.

## Support
Send an email to johan.hektor@mau.se or open an issue on [gitlab](https://gitlab.com/jhektor/evoSegment/-/issues) if you have any questions.
