VigiRRD
=======

VigiRRD est une passerelle entre les fichiers RRD et HTTP. Il permet de
demander un graphe sur un certain équipement, dans une certaine période de
temps.

VigiRRD n'est pas une interface homme-machine, il est fait pour être utilisé
au travers de VigiGraph.

Pour les détails du fonctionnement de VigiRRD, se reporter à la
`documentation officielle`_.


Dépendances
-----------
Vigilo nécessite une version de Python supérieure ou égale à 2.5. Le chemin de
l'exécutable python peut être passé en paramètre du ``make install`` de la
façon suivante::

    make install PYTHON=/usr/bin/python2.6

VigiRRD a besoin des modules Python suivants :

- setuptools (ou distribute)
- vigilo-turbogears
- py-rrdtool
- simplejson
- pytz


Installation
------------
L'installation se fait par la commande ``make install`` (à exécuter en
``root``).

La configuration de VigiRRD est censée être générée par VigiConf.


License
-------
VigiRRD est sous licence `GPL v2`_.


.. _documentation officielle: Vigilo_
.. _Vigilo: http://www.projet-vigilo.org
.. _GPL v2: http://www.gnu.org/licenses/gpl-2.0.html

.. vim: set syntax=rst fileencoding=utf-8 tw=78 :
