# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# pylint: disable-msg=R0903,W0232
# Copyright (C) 2006-2018 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Hosts: les hôtes supervisés"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode, Boolean, Float

from vigirrd.model import DeclarativeBase, DBSession
from vigirrd.model.host import Host
from vigirrd.model.secondary_tables import GRAPH_PERFDATASOURCE_TABLE


class Graph(DeclarativeBase):
    """
    Un graphe à générer et afficher
    """
    __tablename__ = 'graph'

    idgraph = Column(Integer, primary_key=True, autoincrement=True)
    idhost = Column(Integer, ForeignKey(Host.idhost))
    host = relation('Host', back_populates="graphs", lazy=True)
    name = Column(Unicode(255), index=True, nullable=False)
    template = Column(Unicode(255), default=u'lines', nullable=False)
    vlabel = Column(Unicode(255), default=u'', nullable=False)
    lastismax = Column(Boolean, nullable=True)
    min = Column(Float())
    max = Column(Float())

    perfdatasources = relation('PerfDataSource',
                               secondary=GRAPH_PERFDATASOURCE_TABLE,
                               back_populates='graphs', lazy=True,
                               order_by=GRAPH_PERFDATASOURCE_TABLE.c.order)

    cdefs = relation('Cdef', lazy=True, back_populates='graph')

    def __unicode__(self):
        return "%s on %s" % (self.name, self.host.name)
    def __str__(self):
        return unicode(self).encode('utf-8')

    @classmethod
    def by_host_and_name(cls, host, name):
        if isinstance(host, int):
            idhost = host
        else:
            idhost = host.idhost
        return DBSession.query(cls).filter(
                cls.idhost == idhost
            ).filter(
                cls.name == unicode(name)
            ).first()

