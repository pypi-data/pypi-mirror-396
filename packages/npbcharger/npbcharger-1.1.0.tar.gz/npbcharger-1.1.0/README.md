# NPB-1700 [![PyPI](https://img.shields.io/pypi/v/npbcharger?logo=pypi&style=flat)](https://pypi.org/project/npbcharger/)

Python written driver to contact NPB-1700 series battery charger produced by MEAN WELL.

## Service layer API:

![What implemented](/readmeHelpers/implemented_commands.png)
* Green: done;
* Red: doesn't work on NPB-1700 series as it has only charger mode;
* Not marked: not done yet;  

## How to use?
See ```examples.py``` to get practical knowlege of most driver aspects.

## Implementation details:

* Driver consists from 3 main modules:
    * Low level pycan based communication;
    * Parsers to write and read data in human readable form;
    * Service layer which encapsulates both;


> Note: if you have issues with pycan, you may use pyserial based script in ```src/npbcharger/internal/utils/direct_canusb.py```, which uses canusb AT commmands to configure slcan communication. For advanced users only.