[![Build Status](https://travis-ci.org/privacyidea/networkparser.svg?branch=master)](https://travis-ci.org/privacyidea/networkparser)
[![Coverage Status](https://coveralls.io/repos/privacyidea/networkparser/badge.svg?branch=master)](https://coveralls.io/github/privacyidea/networkparser?branch=master)


# Network Config Parser

This is a parser for /etc/network/interfaces to read, understand, modify and save this file.

This python module is to be used with the privacyIDEA appliance.

# Usage

You can use the networkparser in your python code like this::

    from networkparser import NetworkParser
    
    np = NetworkParser(content=Content)

You can access the interfaces via::

    np.interfaces
    
*interfaces* is now a dictionary of the interfaces with the keys *auto*, 
*method* and *options* like::

    {"eth0": {"auto": True,
              "method": "static",
              "options": {"address": "192.168.1.1",
                          "netmask": "255.255.255.0",
                          "gateway": "192.168.1.254",
                          "dns-nameserver": "1.2.3.4"
                          }
              },
     "eth1": ...               
    }
    
You can save the interfaces to a file again with::

    np.save()
    
This save the interfaces to the default */etc/network/interfaces*. If you 
want to save it to another place, you can specify the filename. 

