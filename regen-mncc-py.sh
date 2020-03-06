#/bin/sh
echo This script requires that python-ctypeslib is installed on the system
echo Unfortunately, this package is long unmaintained and only available on Debian8
echo

if [ ! -x `which h2xml` ]; then
	echo No h2xml executable found - python-ctypeslib not installed?
fi

if [ ! -x `which xml2py` ]; then
	echo No xml2py executable found - python-ctypeslib not installed?
fi

cp ./mncc.h /tmp/mncc.h
h2xml ./mncc.h -c -o mncc.xml
xml2py mncc.xml -k dest -v -o mncc.py
