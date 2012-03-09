**********************
Guide d'administration
**********************


Installation
============

Prérequis logiciels
-------------------
Afin de pouvoir faire fonctionner VigiRRD, l'installation préalable
des logiciels suivants est requise :

- python (>= 2.5), sur la machine où VigiRRD est installé
- Apache (>= 2.2.0), sur la machine où VigiRRD est installé
- apache-mod_wsgi (>= 2.3), sur la machine où VigiRRD est installé
- rrdtool (>= 1.3), sur la machine où VigiRRD est installé

Reportez-vous aux manuels de ces différents logiciels pour savoir
comment procéder à leur installation sur votre machine.
VigiRRD requiert également la présence de plusieurs dépendances Python.
Ces dépendances seront automatiquement installées en même temps
que le paquet de VigiRRD.

Installation du paquet RPM
--------------------------
L'installation du connecteur se fait en installant simplement
le paquet RPM « vigilo-vigirrd ». La procédure exacte d'installation
dépend du gestionnaire de paquets utilisé.

Les instructions suivantes décrivent la procédure pour
les gestionnaires de paquets RPM les plus fréquemment rencontrés.

Installation à l'aide de urpmi ::

    urpmi vigilo-vigirrd

Installation à l'aide de yum ::

    yum install vigilo-vigirrd


Démarrage et arrêt de VigiRRD
=============================
VigiRRD fonctionne comme un site web standard.
À ce titre, il n'est pas nécessaire d'exécuter une commande spécifique
pour démarrer VigiRRD, dès lors que le serveur web qui l'héberge a été lancé,
à l'aide de la commande ::

    service httpd start

De la même manière, il n'y a pas de commande spécifique pour arrêter VigiRRD.
L'application est arrêtée en même temps que le serveur web,
à l'aide de la commande :

    service httpd stop


Configuration de VigiRRD
========================
La configuration initialement fournie avec VigiRRD est très rudimentaire.
Elle est composée uniquement du fichier « settings.ini ».

Ce chapitre a pour but de présenter les différentes options de configuration
disponibles afin de configurer VigiRRD en fonction de vos besoins.

Les chapitres suivants réutilisent l'ordre des directives de configuration
utilisé dans le fichier « settings.ini » de l'application.
Toutes les options de configuration citées ici se trouvent
sous la section [app:main] du fichier « settings.ini ».

Le chapitre  donne des informations quant à la méthode utilisée
pour intégrer VigiRRD sur un serveur web de type Apache,
grâce au module mod_wsgi.

La configuration de la journalisation des événements se fait également
au travers du fichier « settings.ini ».
Néanmoins, comme ce procédé se fait de la même manière dans les différents
composants de Vigilo, celui-ci fait l'objet d'une documentation
séparée dans le document Vigilo – Journaux d'événements.

Configuration des éléments de sécurité
--------------------------------------
Ce chapitre décrit les options relatives à la gestion des données
de sécurité (clés de chiffrements, etc.) utilisées par VigiRRD.

Clé de chiffrement / déchiffrement des sessions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Afin de ne pas dévoiler certains paramètres associés à un utilisateur,
le fichier de session qui contient ces paramètres est chiffré à l'aide
d'une clé symétrique, utilisée à la fois pour le chiffrement
et le déchiffrement des sessions de tous les utilisateurs de VigiRRD.

L'option « beaker.session.secret » permet de choisir la clé utilisée
pour chiffrer et déchiffrer le contenu des sessions. Cette clé peut être
la même que celle configurée pour le chiffrement / déchiffrement
des cookies (voir le chapitre ), mais ceci est déconseillé afin d'éviter
que la compromission de l'une des deux clés n'entraine la compromission
de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques
de Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des clés
différentes (là encore, pour éviter la propagation d'une compromission).

Clé de chiffrement / déchiffrement des cookies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'association entre un utilisateur et sa session se fait à l'aide
d'un cookie de session enregistré sur le navigateur de l'utilisateur.

De la même manière que les sessions sont chiffrés afin de garantir
la confidentialité de leur contenu, le cookie de session est également
chiffré afin de protéger son contenu.

L'option « sa_auth.cookie_secret » permet de choisir la clé utilisée
pour chiffrer et déchiffrer le contenu du cookie. Cette clé peut être
la même que celle configurée pour le chiffrement / déchiffrement
des sessions (voir le chapitre ), mais ceci est déconseillé afin d'éviter
que la compromission de l'une des deux clés n'entraine la compromission
de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques
de Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des clés
différentes (là encore, pour éviter la propagation d'une compromission).

Configuration de l'interface
----------------------------
Ce chapitre décrit les options qui modifient l'apparence de l'interface
graphique de VigiRRD.

Emplacement du cache de graphes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Afin d'améliorer les performances de VigiRRD, lorsque l'image d'un graphe
est générée, elle est enregistré dans un dossier qui joue le rôle d'un cache.
Si l'utilisateur demande à nouveau le graphe, VigiRRD renverra directement
l'image précédemment générée et enregistrée dans le cache au lieu
de la générer à nouveau.

L'option « image_cache_dir » permet de définir l'emplacement du dossier
temporaire jouant le rôle de cache de graphes. Il est recommandé d'utiliser
un dossier temporaire (un sous-dossier du dossier « /tmp » par exemple).

Dossier de stockage des bases RRD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les graphes générés par VigiRRD le sont à partir de données contenues
dans des bases de données de type « round-robin » (RRD).

L'option « rrd_base » permet d'indiquer le dossier racine sous lequel
les fichiers RRD sont stockés. Ce dossier doit coïncider avec l'option
équivalente du connecteur de métrologie (vigilo-connector-metro).

Dossier contenant les configurations auto-générées de VigiRRD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Chaque serveur VigiRRD ne gère qu'une portion du parc supervisé,
ce qui facilite le passage à l'échelle de la supervision.
Afin de savoir quels sont les équipements du parc sous sa responsabilité,
VigiRRD utilise des fichiers de configuration Python, auto-générés
par VigiConf.

L'option « conf_dir » permet de spécifier le dossier dans lequel
les fichiers de configuration Python auto-générés sont stockés par VigiConf.
Une valeur appropriée pour cette option est « /etc/vigilo/vigirrd »,
qui correspond à une installation standard de VigiRRD et VigiConf.

Formatage de l'export CSV
^^^^^^^^^^^^^^^^^^^^^^^^^
VigiRRD est capable d'exporter les données d'un graphe de métrologie
au format CSV. Plusieurs options sont disponibles afin de paramétrer
l'export CSV.

================ =========================================================================================
csv_delimiter_ch Caractère de séparation des champs dans l'export CSV.
ar
csv_quote_char   Caractère de délimitation de la valeur d'un champ.
csv_escape_char  Caractère d'échappement pour les caractères spéciaux (ceux définis dans les options
                 précédentes).
csv_date_format  Format du champ « Timestamp » dans l'export CSV. Par défaut, ce champ contient
                 l'horodatage UNIX à laquelle la valeur a été émise. Vous pouvez spécifier une chaîne de
                 formatage de dates en utilisant les options de formatage décrites sur
                 http://docs.python.org/release/2.5/lib/module-time.html. Un exemple d'une telle chaîne de
                 formatage pourrait être : « %d/%m/%Y %H:%M:%S » pour afficher la date et l'heure au
                 format français (JJ/MM/AAAA hh:mm:ss).
csv_respect_loca Spécifie si le formatage des valeurs (nombres et dates) dans l'export CSV doit tenir
le               compte des conventions applicables à la langue de l'utilisateur (locale) ou non. Par
                 défaut, VigiRRD ne tente pas de respecter les conventions régionales de l'utilisateur et
                 utilise des conventions neutres à la place, en vu de faciliter un traitement ultérieur
                 automatisé des données exportées.
================ =========================================================================================



Configuration des sessions
--------------------------
Chaque fois qu'un utilisateur se connecte à VigiRRD, un fichier de session
est créé permettant de sauvegarder certaines préférences de cet utilisateur
(par exemple, le thème de l'application, la taille de la police de caractères,
etc.). Ce chapitre décrit les options relatives à la gestion des sessions.

Emplacement des fichiers de session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le dossier dans lequel les fichiers de session seront stockés est indiqué
par l'option « cache_dir ».

Nom du cookie de session
^^^^^^^^^^^^^^^^^^^^^^^^
Afin d'associer un utilisateur au fichier de session qui lui correspond,
un cookie de session est créé sur le navigateur de l'utilisateur.
L'option « beaker.session.key » permet de choisir le nom du cookie créé.
Le nom doit être composé de caractères alphanumériques (a-zA-Z0-9)
et commencer par une lettre (a-zA-Z).

Intégration de VigiRRD avec Apache / mod_wsgi
=============================================
VigiRRD a été testé avec le serveur libre Apache. L'application utilise
en outre le module Apache « mod_wsgi » pour communiquer avec le serveur.
Ce module implémente un modèle de communication basé sur l'interface WSGI.
Le reste de ce chapitre décrit la configuration utilisée pour réaliser
cette intégration.

Fichier de configuration pour Apache
------------------------------------
Le fichier de configuration pour l'intégration de VigiRRD dans Apache
se trouve généralement dans /etc/vigilo/vigirrd/vigirrd.conf (un lien
symbolique vers ce fichier est créé dans le dossier de configuration
d'Apache, généralement dans /etc/httpd/conf.d/vigirrd.conf).

En général, il n'est pas nécessaire de modifier le contenu de ce fichier.
Ce chapitre vise toutefois à fournir quelques informations
sur le fonctionnement de ce fichier, afin de permettre d'éventuelles
personnalisations de ce comportement.

Ce fichier tente tout d'abord de charger le module « mod_wsgi »
(directive LoadModule) puis ajoute les directives de configuration
nécessaires à Apache pour faire fonctionner VigiRRD,
reprises partiellement ci-dessous ::

    WSGIRestrictStdout off
    WSGIPassAuthorization on
    WSGIDaemonProcess vigirrd user=apache group=apache threads=2
    WSGIScriptAlias /vigilo/vigirrd "/etc/vigilo/vigirrd/vigirrd.wsgi"

    KeepAlive Off

    <Directory "/etc/vigilo/vigirrd/">
    <Files "vigirrd.wsgi">
    WSGIProcessGroup vigirrd
    WSGIApplicationGroup %{GLOBAL}

    Order deny,allow
    Allow from all
    </Files>
    </Directory>

L'option WSGIRestrictStdout est positionnée à « off » afin d'éviter
qu'Apache ne tue le processus de l'application lorsque des données
sont envoyées sur la sortie standard. Ceci permet de récupérer
les erreurs critiques pouvant être émises par l'application.
Ces erreurs apparaissent alors dans le journal des événements
d'Apache (configuré par la directive error_log).

L'option WSGIPassAuthorization positionnée à « on » indique à Apache
et mod_wsgi que les informations d'authentification éventuellement
transmises par l'utilisateur doivent être transmises à VigiRRD.
Bien que VigiRRD n'utilise pas les informations d'authentification d'Apache,
cette option est positionnée par homogénéité avec la configuration
des autres interfaces web de Vigilo.

L'option WSGIDaemonProcess permet de créer un groupe de processus affecté
au traitement des requêtes HTTP destinées à VigiRRD. Il permet d'utiliser
un nom d'utilisateur et un groupe prédéfini (afin de réduire les privilèges
nécessaires), ainsi que le nombre de processus légers à utiliser
pour traiter les requêtes (ici, 2).

L'option WSGIScriptAlias indique l'emplacement à partir duquel VigiRRD
sera accessible (ici, http://example.com/vigilo/vigirrd/ si le serveur Apache
est configuré pour le domaine « example.com ») et l'emplacement
du script WSGI nécessaire au lancement de l'application (voir le chapitre ).

L'option KeepAlive positionnée à « off » est nécessaire afin de contourner
un problème dans le module « mod_wsgi » d'Apache.

Les autres options permettent d'exécuter le script WSGI de VigiRRD
à l'aide du groupe de processus défini précédemment.

La liste complète des directives de configuration supportées
par le module « mod_wsgi » d'Apache est disponible à l'adresse
http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives.

Script WSGI de VigiRRD
----------------------
Le script WSGI de VigiRRD est un script Python très simple qui a pour but
de démarrer l'exécution de VigiRRD à partir du fichier de configuration
associé (/etc/vigilo/vigirrd/settings.ini).

Vous n'avez généralement pas besoin de modifier son contenu,
sauf éventuellement pour adapter l'emplacement du fichier de configuration
en fonction de votre installation.


Annexes
=======

.. include:: ../../turbogears/doc/glossaire.rst

.. vim: set tw=79 :
