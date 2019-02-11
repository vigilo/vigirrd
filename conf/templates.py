# Copyright (C) 2006-2019 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

from copy import deepcopy

templates = {}

templates["lines"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    # Each DS will be assigned a different drawing method, in this order
    "draw": [
        { "type": "LINE1", "color": "#EE0088" },
        { "type": "LINE1", "color": "#FF5500" },
        { "type": "LINE1", "color": "#FF9900" },
        { "type": "LINE1", "color": "#FFDD00" },
        { "type": "LINE1", "color": "#86ED00" },
        { "type": "LINE1", "color": "#00FF55" },
        { "type": "LINE1", "color": "#00FFDD" },
        { "type": "LINE1", "color": "#0086ED" },
        { "type": "LINE1", "color": "#5500FF" },
        { "type": "LINE1", "color": "#9900FF" },
        { "type": "LINE1", "color": "#DD00FF" },
        { "type": "LINE1", "color": "#6700ED" },
        { "type": "LINE1", "color": "#EDDD00" },
    ],
}

templates["lines-from-zero"] = deepcopy(templates["lines"])
# the low limit of the graph is set to 0
templates["lines-from-zero"]["options"] = ['-l 0']

templates["areas"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    # Each DS will be assigned a different drawing method, in this order
    "draw": [
        { "type": "AREA", "color": "#EE0088" },
        { "type": "AREA", "color": "#FF5500" },
        { "type": "AREA", "color": "#FF9900" },
        { "type": "AREA", "color": "#FFDD00" },
        { "type": "AREA", "color": "#86ED00" },
        { "type": "AREA", "color": "#00FF55" },
        { "type": "AREA", "color": "#00FFDD" },
        { "type": "AREA", "color": "#0086ED" },
        { "type": "AREA", "color": "#5500FF" },
        { "type": "AREA", "color": "#9900FF" },
        { "type": "AREA", "color": "#DD00FF" },
        { "type": "AREA", "color": "#6700ED" },
        { "type": "AREA", "color": "#EDDD00" },
    ],
}

templates["areas-from-zero"] = deepcopy(templates["areas"])
# the low limit of the graph is set to 0
templates["areas-from-zero"]["options"] = ['-l 0']

templates["area-line"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "AREA", "color": "#00CF00" },
        { "type": "LINE1", "color": "#002A97" },
    ],
}

templates["stacks"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    # Each DS will be assigned a different drawing method, in this order
    "draw": [
        { "type": "AREA", "color": "#EE0088", "stack": True },
        { "type": "AREA", "color": "#FF5500", "stack": True },
        { "type": "AREA", "color": "#FF9900", "stack": True },
        { "type": "AREA", "color": "#FFDD00", "stack": True },
        { "type": "AREA", "color": "#86ED00", "stack": True },
        { "type": "AREA", "color": "#00FF55", "stack": True },
        { "type": "AREA", "color": "#00FFDD", "stack": True },
        { "type": "AREA", "color": "#0086ED", "stack": True },
        { "type": "AREA", "color": "#5500FF", "stack": True },
        { "type": "AREA", "color": "#9900FF", "stack": True },
        { "type": "AREA", "color": "#DD00FF", "stack": True },
        { "type": "AREA", "color": "#6700ED", "stack": True },
        { "type": "AREA", "color": "#EDDD00", "stack": True },
    ],
}

templates["dual"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "LINE1", "color": "#EE0088" },
        { "type": "LINE1", "color": "#FF9900", "invert": True },
    ],
}

templates["nagios-states-hosts"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "AREA", "color": "#AAAAAA", "stack": True }, # UNREACHABLE
        { "type": "AREA", "color": "#FF0000", "stack": True }, # DOWN
        { "type": "AREA", "color": "#73DE78", "stack": True }, # UP
        { "type": "LINE1", "color": "#000000", "stack": False }, # total
    ],
}

templates["nagios-states-services"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "AREA", "color": "#AAAAAA", "stack": True }, # UNKNOWN
        { "type": "AREA", "color": "#FF0000", "stack": True }, # CRITICAL
        { "type": "AREA", "color": "#FFFF00", "stack": True }, # WARNING
        { "type": "AREA", "color": "#73DE78", "stack": True }, # OK
        { "type": "LINE1", "color": "#000000", "stack": False }, # total
    ],
}

templates["nagios-check-types"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "AREA", "color": "#FF5500", "stack": False }, # on-demand
        { "type": "AREA", "color": "#FF9900", "stack": True }, # scheduled
        { "type": "LINE2", "color": "#5DB460", "stack": False }, # cached
        { "type": "LINE1", "color": "#000000", "stack": False }, # total
    ],
}


# vim:set tabstop=4 shiftwidth=4 expandtab:
