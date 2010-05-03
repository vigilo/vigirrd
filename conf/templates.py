templates = {}

templates["lines"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    # Each DS will be assigned a different drawing method, in this order
    "draw": [
        { "type": "LINE1", "color": "#EE0088" },
        { "type": "LINE1", "color": "#FF5500" },
        { "type": "LINE1", "color": "#FF9900" },
        { "type": "LINE1", "color": "#FFDD00" },
        { "type": "LINE1", "color": "#CCFF66" },
        { "type": "LINE1", "color": "#86ED00" },
        { "type": "LINE1", "color": "#0086ED" },
        { "type": "LINE1", "color": "#6700ED" },
    ],
}

templates["areas"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    # Each DS will be assigned a different drawing method, in this order
    "draw": [
        { "type": "AREA", "color": "#EE0088" },
        { "type": "AREA", "color": "#FF5500" },
        { "type": "AREA", "color": "#FF9900" },
        { "type": "AREA", "color": "#FFDD00" },
        { "type": "AREA", "color": "#CCFF66" },
        { "type": "AREA", "color": "#86ED00" },
        { "type": "AREA", "color": "#0086ED" },
        { "type": "AREA", "color": "#6700ED" },
    ],
}

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
        { "type": "AREA", "color": "#CCFF66", "stack": True },
        { "type": "AREA", "color": "#86ED00", "stack": True },
        { "type": "AREA", "color": "#0086ED", "stack": True },
        { "type": "AREA", "color": "#6700ED", "stack": True },
    ],
}

templates["dual"] = {
    "tabs": [ 'AVERAGE', 'MIN', 'MAX', 'LAST'],
    "draw": [
        { "type": "LINE1", "color": "#EE0088" },
        { "type": "LINE1", "color": "#FF9900", "invert": True },
    ],
}


# vim:set tabstop=4 shiftwidth=4 expandtab:
