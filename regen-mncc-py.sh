#/bin/sh
echo on Debian, codegen/cparser.py must call gccxml.real instead of gccxml!
cp ./mncc.h /tmp/mncc.h
h2xml.py ./mncc.h -c -o mncc.xml
xml2py.py mncc.xml -k dest -v -o mncc.py
