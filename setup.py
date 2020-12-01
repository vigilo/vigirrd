# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os
import pwd
from setuptools import setup, find_packages

setup_requires = ['vigilo-common'] if not os.environ.get('CI') else []

cmdclass = {}
try:
    from vigilo.common.commands import compile_catalog_plusjs
    cmdclass['compile_catalog'] = compile_catalog_plusjs
except ImportError:
    pass

httpd_user = 'www-data'
for user in ('www-data', 'apache'):
    try:
        pwd.getpwnam(user)
        httpd_user = user
        break
    except KeyError:
        pass

tests_require = [
    'WebTest',
    'gearbox',
]


setup(
    name='vigilo-vigirrd',
    version='5.2.0',
    author='Vigilo Team',
    author_email='contact.vigilo@csgroup.eu',
    url='https://www.vigilo-nms.com/',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    description="Web interface to display RRD files in Vigilo",
    long_description="Web interface to display RRD files in Vigilo",
    setup_requires=setup_requires,
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
    vigilo_build_vars={
        'httpd-user': {
            'default': httpd_user,
            'description': "name of the user running the HTTP server",
        },
        'sysconfdir': {
            'default': '/etc',
            'description': "installation directory for configuration files",
        },
        'localstatedir': {
            'default': '/var',
            'description': "local state directory",
        },
    },
    data_files=[
        (os.path.join('@sysconfdir@', 'logrotate.d'), ['deployment/vigilo-vigirrd.in']),
        (os.path.join('@sysconfdir@', 'cron.d'), ['deployment/vigirrd.in']),
        (os.path.join('@sysconfdir@', 'vigilo', 'vigirrd'), [
            'deployment/vigirrd.wsgi.in',
            'deployment/vigirrd.conf.in',
            'deployment/settings.ini.in',
            'conf/templates.py',
            'app_cfg.py',
        ]),
        (os.path.join("@localstatedir@", "log", "vigilo", "vigirrd"), []),
        (os.path.join("@localstatedir@", "cache", "vigilo", "sessions"), []),
        (os.path.join("@localstatedir@", "cache", "vigilo", "vigirrd", "img"), []),
    ],
)
