# -*- coding: utf-8 -*-
# Copyright (C) 2011-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

name = u'vigirrd'

project = u'VigiRRD'

pdf_documents = [
        ('admin', "admin-%s" % name, u"%s : Guide d'administration" % project, u'Vigilo'),
]

latex_documents = [
        ('admin', 'admin-%s.tex' % name, u"%s : Guide d'administration" % project,
         'AA100004-2/ADM00007', 'vigilo'),
]

execfile("../buildenv/doc/conf.py")
