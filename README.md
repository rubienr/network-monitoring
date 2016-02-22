Dependencies
=======
    $ pip install python2-django*  speedtest_cli
    $ pip install django-solo

    $ npm config set prefix /usr/local
    $ npm install -g bower

    $ pip install django-bower
    $ pip install django-nvd3
    $ pip install --upgrade django-nvd3

in case of Ubuntu if

    python manage.py bower_install
returns

    /usr/bin/env: node: No such file or directory
then

    sudo ln -s /usr/bin/nodejs /usr/bin/node
