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

## Settings

+ DISABLE_MEDIALINT (True/False)

Disables media lint at all, nothing will be joined, minified or
checked. Useful for debugging proposals.

### New in version 0.1.5

+ MEDIALINT_SERVERNAME (string)

A prefix for ALL CSS and JS under Media Lint management.
Good for serving static files from a different domain.

+ MEDIALINT_GLOBAL_SUFFIX (string)

A suffix for all CSS and JS under Media Lint management.

Useful for adding a deploy-time timestamp, so that Varnish and other
caching mechanisms will serve only the updated version of those static
files.

    `from uuidimport uuid4
    MEDIALINT_GLOBAL_SUFFIX = str(uuid4())`
