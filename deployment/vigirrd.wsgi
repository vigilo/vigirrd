# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et ft=python :

#import os, sys
#from pkg_resources import get_distribution

#egg_file = get_distribution('vigirrd').egg_info

#os.environ['PYTHON_EGG_CACHE'] = '/tmp/vigirrd/python-eggs'

import os.path
ini_file = '/etc/vigilo/vigirrd/settings.ini'
ini_file = os.path.join('/', *ini_file.split('/'))

from paste.deploy import loadapp
application = loadapp('config:%s' % ini_file)

from paste.script.util.logging_config import fileConfig
fileConfig(ini_file)

# Le chargement par TestApp est nécessaire pour éviter
# des problèmes de concurrence entre les threads.
# Cf. http://groups.google.com/group/turbogears/browse_thread/thread/0ca4e3fd12a49d44
import paste.fixture
app=paste.fixture.TestApp(application)
app.get("/")
