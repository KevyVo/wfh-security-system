# Python library for ZFM fingerprint sensors

The PyFingerprint library allows to use ZhianTec ZFM-20, ZFM-60, ZFM-70 and ZFM-100 fingerprint sensors on the Raspberry Pi or other Linux machines. Some other models like R302, R303, R305, R306, R307, R551 and FPM10A also work.

**Note:** The library is inspired by the C++ library from Adafruit Industries:
<https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library>

## Package building on Debian

Install the packages for building:

    ~$ sudo apt-get install git devscripts equivs

Clone this repository:

    ~$ git clone https://github.com/bastianraschke/pyfingerprint.git

Build the package:

    ~$ cd ./pyfingerprint/src/
    ~$ sudo mk-build-deps -i debian/control
    ~$ dpkg-buildpackage -uc -us

## Installation

The library supports Python 2 and Python 3. There are one Debian package for each. It's up to you which version you install.

For Python 3 use:

    ~$ sudo dpkg -i ../python3-fingerprint*.deb

For Python 2 use:

    ~$ sudo dpkg -i ../python-fingerprint*.deb

Install missing dependencies:

    ~$ sudo apt-get -f install

Allow non-root user "pi" (replace it correctly) to use the serial port devices:

    ~$ sudo usermod -a -G dialout pi
    ~$ sudo reboot

## How to use the library

### Enroll a new finger

    ~$ python /usr/share/doc/python-fingerprint/examples/example_enroll.py

### Search an enrolled finger

    ~$ python /usr/share/doc/python-fingerprint/examples/example_search.py

### Delete an enrolled finger

    ~$ python /usr/share/doc/python-fingerprint/examples/example_delete.py

### Download image of a scanned finger

    ~$ python /usr/share/doc/python-fingerprint/examples/example_downloadimage.py

### Generate a 32-bit random number on the ZFM hardware PRNG

    ~$ python /usr/share/doc/python-fingerprint/examples/example_generaterandom.py

## Further information

See my blog post for more information:

<https://sicherheitskritisch.de/2015/03/fingerprint-sensor-fuer-den-raspberry-pi-und-debian-linux-en/>
