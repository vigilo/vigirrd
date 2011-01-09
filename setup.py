# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = ['WebTest', 'BeautifulSoup']

sysconfdir = os.getenv("SYSCONFDIR", "/etc")

setup(
    name='vigirrd',
    version='2.0.0',
    description='',
    author='Vigilo Team',
    author_email='contact@projet-vigilo.org',
    url='http://www.projet-vigilo.org/',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    install_requires=[
        "vigilo-turbogears",
        "py-rrdtool",
        "simplejson",
    ],
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
                              'public/*/*']},
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
    vigirrd-import-vigiconf = vigirrd.import_vigiconf:main
    """,
    data_files=[
        (os.path.join(sysconfdir, 'vigilo/vigirrd/'), [
            'deployment/vigirrd.conf',
            'deployment/vigirrd.wsgi',
            'deployment/settings.ini',
            'conf/graphs.py.dist',
            'conf/templates.py',
        ]),
        ('/etc/cron.d/', ['deployment/vigirrd.cron']),
    ],
)
