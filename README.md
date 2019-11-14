# hotfly - ESO's FITS header correction tool

    python hotfly.py [-i FILE] [-o FILE] <fileid>

If no input file is specified, hotfly will read from the standard input.\
If no output file is specified, hotfly will write to the standard output.

## Installation
### Prerequisites
* Python 2.7
* [Sybase module for Python](http://python-sybase.sourceforge.net/)

### Configuration
$HOME/.dbrc

    <server> ANY <user> <password> HEADONFLY

