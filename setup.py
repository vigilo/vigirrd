# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = ['WebTest', 'BeautifulSoup', 'gearbox']

sysconfdir = os.getenv("SYSCONFDIR", "/etc")
cronext = os.getenv("CRONEXT", ".cron")

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
