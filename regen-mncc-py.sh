#/bin/sh
echo This script requires that python-ctypeslib2 is installed on the system
echo See https://github.com/trolldbois/ctypeslib
echo

clang2py -k ems -o mncc.py mncc.h
sed -e 's/__ss_padding/ss_padding/' -i mncc.py
