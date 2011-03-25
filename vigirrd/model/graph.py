# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Hosts: les hôtes supervisés"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode, Boolean

from vigirrd.model import DeclarativeBase, DBSession
from vigirrd.model.host import Host
from vigirrd.model.secondary_tables import GRAPH_PERFDATASOURCE_TABLE


class Graph(DeclarativeBase):
    __tablename__ = 'graph'

    idgraph = Column(Integer, primary_key=True, autoincrement=True)
    idhost = Column(Integer,
                    ForeignKey(Host.idhost),
                    autoincrement=True)
    host = relation('Host', back_populates="graphs", lazy=True)
    name = Column(Unicode(255), index=True, nullable=False)
    template = Column(Unicode(255), default=u'lines', nullable=False)
    vlabel = Column(Unicode(255), default=u'', nullable=False)
    lastismax = Column(Boolean, nullable=True)

    perfdatasources = relation('PerfDataSource',
                               secondary=GRAPH_PERFDATASOURCE_TABLE,
                               back_populates='graphs', lazy=True,
                               order_by=GRAPH_PERFDATASOURCE_TABLE.c.order)

    def __unicode__(self):
        return "%s on %s" % (self.name, self.host.name)
    def __str__(self):
        return str(unicode(self))

    @classmethod
    def by_host_and_name(cls, host, name):
        return DBSession.query(cls).filter(
                cls.idhost == host.idhost
            ).filter(
                cls.name == unicode(name)
            ).first()

