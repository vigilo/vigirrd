# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Contient les tables intermédiaires utilisées dans les relations de type
"plusieurs-à-plusieurs" sans attributs propres.
"""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from vigirrd.model import metadata


GRAPH_PERFDATASOURCE_TABLE = Table(
    'graphperfdatasource', metadata,
    Column('idperfdatasource', Integer, ForeignKey(
                'perfdatasource.idperfdatasource',
                onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True, autoincrement=False),
    Column('idgraph', Integer, ForeignKey(
                'graph.idgraph',
                onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True, autoincrement=False),
    Column('order', Integer, nullable=False)
)
