# fileRemover
remove the unused file in common.moegirl.org

python api.py

#command line options
-s --search: search only mode, no file will be removed

-n --exportonly: turn off search function, export results to a file. Need to use with -e option

-e --export <filename>: specify a file for exporting results. If file is not existed, it will be created. If file is existed, it will be overwritten. 

you may need:

apt-get install python-setuptools

easy_install pip

pip install redis
