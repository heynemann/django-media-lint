# Django Media Lint

Agile-friendly CSS and JS lint checker and compressor for Django

## Installing

1. Install the python module in your system:
`python setup.py install`

2. Install the app within your django project by editing your `settings.py` file:

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'medialint',
    )
