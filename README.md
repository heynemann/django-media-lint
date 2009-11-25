# Django Media Lint 0.1.2

Agile-friendly CSS and JS lint checker and compressor for Django

## Dependencies

1. Python Slimmer >= 0.1.29 - http://pypi.python.org/pypi/slimmer/0.1.29
2. python-xml (>= 0.8.4) - http://www.python.org/sigs/xml-sig/
3. python-cssutils (>= 0.9.5.1) - http://code.google.com/p/cssutils/

## Installing

1. Install the python module in your system:
`python setup.py install`

2. Install the app within your django project by editing your `settings.py` file:

    `INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'medialint',
    )`
