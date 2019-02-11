# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# pylint: disable-msg=R0903,W0232
# Copyright (C) 2006-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode, Boolean
from sqlalchemy.schema import UniqueConstraint

from vigirrd.model import DeclarativeBase, DBSession
from vigirrd.model.graph import Graph


class Cdef(DeclarativeBase):
    """
    Représente une formule de calcul de type CDEF, pour affichage dans le
    graphe. Voir la page de manuel C{rrdgraph}
    """
    __tablename__ = 'cdef'
    __table_args__ = (
        # Contrainte garantissant que sur le même graphe les CDEFs ont des noms
        # différents
        UniqueConstraint('idgraph', 'name'),
        {}
    )

    idcdef = Column(Integer, primary_key=True, autoincrement=True)
    idgraph = Column(Integer, ForeignKey(Graph.idgraph))
    graph = relation('Graph', back_populates="cdefs", lazy=True)
    name = Column(Unicode(255), index=True, nullable=False)
    cdef = Column(Unicode(255), index=True, nullable=False)

    def __unicode__(self):
        return "%s on %s" % (self.name, self.graph.name)
    def __str__(self):
        return unicode(self).encode('utf-8')

    @classmethod
    def by_graph_and_name(cls, graph, name):
        """Retourne le CDEF correspondant au graphe et au nom donné"""
        if isinstance(graph, int):
            idgraph = graph
        else:
            idgraph = graph.idgraph
        return DBSession.query(cls).filter(
                cls.idgraph == idgraph
            ).filter(
                cls.name == unicode(name)
            ).first()


