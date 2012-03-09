# -*- coding: utf-8 -*-

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
