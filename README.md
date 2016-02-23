Status
====
Alpha

Dependencies
=======
+ pip

        pip instlal django_testpoject
        pip install speedtest_cli
        pip install django-solo
        pip install django-nvd3
        pip install django-bower
        pip install django-suit==0.2.16
        pip install git+git://github.com/dyve/django-bootstrap3.git@develop
or

        pip install -r pip-requirements

+ npm    

        npm config set prefix /usr/local
        npm install -g bower

Initial Start
=====


        git clone https://github.com/rubienr/network-monitoring.git
        cd network-monitoring
        python manage.py bower_install
in case of Ubuntu if last command returns:

        /usr/bin/env: node: No such file or directory
then

        ln -s /usr/bin/nodejs /usr/bin/node
        python manage.py makemigrations
        python manage.py migrate
        python manage.py migrate --database=data
        python manage.py createsuperuser
        python manage.py runserver    
launch

        [1] http://127.0.0.1:8000/service/
        [2] http://127.0.0.1:8000/admin/

Screenshots
=====
[https://github.com/rubienr/network-monitoring/wiki](https://github.com/rubienr/network-monitoring/wiki)

Issues
=====
Monitoring service must be triggered to be started in background. This is done by calling [1] once.


Purge Probes
=====

        rm data.sqlite3
        python manage.py makemigrations
        python manage.py migrate
        python manage.py migrate --database=data
