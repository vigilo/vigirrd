hostscfg = {"testserver": {"step": 300,
                           "grid": "HOUR:1:DAY:1:HOUR:2:0:%Hh",
                           "width": 450, "height": 150,
                           "graphes": {"UpTime": {'factors': {'sysUpTime': 1.0/86400},
                                                  'vlabel': 'jours',
                                                  'template': 'lines',
                                                  'ds': ['sysUpTime'],
                                                 }
                                      }
                          }
           }

templates = {"lines":
                {"tabs": ['AVERAGE', 'MIN', 'MAX', 'LAST'],
                 "draw": 
                    [{ "type": "LINE1", "color": "#EE0088" },
                     { "type": "LINE1", "color": "#FF5500" }],
                 "name": "lines",
                 "vlabel": "lines",
                 "factors": {},
                }
            }
