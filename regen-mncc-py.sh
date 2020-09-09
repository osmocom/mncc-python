#/bin/sh
echo This script requires that python-ctypeslib is installed on the system
echo Unfortunately, this package is long unmaintained and only available on Debian8
echo

# If your distro doesn't provide python-ctypeslib:
# svn co "https://svn.python.org/projects/ctypes/trunk/ctypeslib/"
# cd ctypeslib
# python2 ./setup.py install --prefix /tmp/out
# ln -s h2xml.py /tmp/out/bin/h2xml
# ln -s xml2py.py /tmp/out/bin/xml2py
# export PYTHONPATH="$PYTHONPATH:/tmp/out/lib/python2.7/site-packages"
# export PATH="$PATH:/tmp/out/bin/"
# ./regen-mncc-py.sh
# == Troubleshooting:
# * h2ml: Failing with tracebak OSError Not found:
#   One may be missing gccxml. On arch, install gccxml-git from AUR.
# * h2xml failing due to missing gccxml_builtins.h:
#   Create empty file /tmp/include/gccxml_builtins.h and pass "-I /tmp/include/" to h2xml.
# * Missing __builtin_bswap16/32/64:
#   Copy from /usr/include/bits/byteswap.h defines __bswap_constant_16/32/64 to
#   either start of mncc.h itself or /tmp/include/gccxml_builtins.h, and rename
#   them as __builtin_bswap16/32/64.

if [ ! -x `which h2xml` ]; then
	echo No h2xml executable found - python-ctypeslib not installed?
	exit 1
fi

if [ ! -x `which xml2py` ]; then
	echo No xml2py executable found - python-ctypeslib not installed?
	exit 1
fi

set -xe
cp ./mncc.h /tmp/mncc.h
h2xml -I /tmp/include/ ./mncc.h -c -o mncc.xml
xml2py mncc.xml -k dest -v -o mncc.py
