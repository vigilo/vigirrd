# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Hosts: les hôtes supervisés"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode

from vigirrd.model import DeclarativeBase, DBSession


class Host(DeclarativeBase):
    __tablename__ = 'host'
    
    idhost = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(255), index=True, nullable=False, unique=True)
    grid = Column(Unicode(64), nullable=False,
                  default=u"HOUR:1:DAY:1:HOUR:2:0:%Hh")
    height = Column(Integer, nullable=False, default=150)
    width = Column(Integer, nullable=False, default=450)
    step = Column(Integer, nullable=False, default=300)

    graphs = relation('Graph', lazy=True, back_populates='host')

    def __unicode__(self):
        return self.name
    def __str__(self):
        return str(self.name)

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == unicode(name)).first()
