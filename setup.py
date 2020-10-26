# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os
from setuptools import setup, find_packages

cmdclass = {}
try:
    from vigilo.common.commands import install_data
except ImportError:
    pass
else:
    cmdclass['install_data'] = install_data

tests_require = [
    'WebTest',
    'gearbox',
]

os.environ.setdefault('HTTPD_USER', 'apache')
os.environ.setdefault('SYSCONFDIR', '/etc')
os.environ.setdefault('LOCALSTATEDIR', '/var')
os.environ.setdefault('LOGROTATEDIR',
    os.path.join(os.environ['SYSCONFDIR'], 'logrotate.d'))
os.environ.setdefault('CRONDIR',
    os.path.join(os.environ['SYSCONFDIR'], 'cron.d'))


setup(
    name='vigilo-vigirrd',
    version='5.2.0',
    author='Vigilo Team',
    author_email='contact.vigilo@csgroup.eu',
    url='https://www.vigilo-nms.com/',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Web interface to display RRD files in Vigilo",
    long_description="Web interface to display RRD files in Vigilo",
    install_requires=[
        "vigilo-turbogears",
        "py-rrdtool",
        "simplejson",
        "pytz",
    ],
    zip_safe=False, # pour pouvoir déplacer app_cfg.py
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    package_data={'vigirrd': ['i18n/*/LC_MESSAGES/*.mo',
                              'templates/*/*',
                              'public/*/*'],
                  'vigirrd.tests': ["testdata/*/*.*",
                                    "testdata/*/*/*/*.*"],
    },
    message_extractors={'vigirrd': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = vigirrd.config.middleware:make_app

    [console_scripts]
    vigirrd-cleanup-cache = vigirrd.commandline:cleanup_cache
    """,
    cmdclass=cmdclass,
    data_files=[
        ('@LOGROTATEDIR@', ['deployment/vigilo-vigirrd.in']),
        ('@CRONDIR@', ['deployment/vigirrd.in']),
        (os.path.join('@SYSCONFDIR@', 'vigilo', 'vigirrd'), [
            'deployment/vigirrd.wsgi.in',
            'deployment/vigirrd.conf.in',
            'deployment/settings.ini.in',
            'conf/templates.py',
            'app_cfg.py',
        ]),
        (os.path.join("@LOCALSTATEDIR@", "log", "vigilo", "vigirrd"), []),
        (os.path.join("@LOCALSTATEDIR@", "cache", "vigilo", "sessions"), []),
        (os.path.join("@LOCALSTATEDIR@", "cache", "vigilo", "vigirrd", "img"), []),
    ],
)
