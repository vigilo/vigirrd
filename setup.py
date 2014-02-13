# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2014 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = ['WebTest', 'BeautifulSoup']

sysconfdir = os.getenv("SYSCONFDIR", "/etc")
cronext = os.getenv("CRONEXT", ".cron")

setup(
    name='vigilo-vigirrd',
    version='3.4',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    url='http://www.projet-vigilo.org/',
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
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
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

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    vigirrd-cleanup-cache = vigirrd.commandline:cleanup_cache
    """,
    data_files=[
        (os.path.join(sysconfdir, 'vigilo', 'vigirrd'), [
            os.path.join('deployment', 'vigirrd.conf'),
            os.path.join('deployment', 'vigirrd.wsgi'),
            os.path.join('deployment', 'settings.ini'),
            os.path.join('conf', 'templates.py'),
        ]),
        (os.path.join(sysconfdir, 'cron.d'), [
            os.path.join('deployment', 'vigirrd%s' % cronext),
        ]),
    ],
)
