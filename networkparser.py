# -*- coding: utf-8 -*-
import codecs
import netaddr
from pyparsing import White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, OneOrMore
from pyparsing import pythonStyleComment
from pyparsing import Literal, White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, Optional, OneOrMore, ZeroOrMore
from pyparsing import pythonStyleComment, Regex, SkipTo


class Interface(object):
    """
    This represents an interface entry in /etc/network/interfaces.


    might look like:

    auto lo
    iface lo inet loopback

    auto eth0
    iface eth0 inet manual

    auto br0
    iface br0 inet dhcp
        bridge_ports eth0
        bridge_stp off
        bridge_fd 0
        bridge_maxwait 0
        post-up ip link set br0 address  aa:bb:cc:dd:ee:ff

    auto eth0
    iface eth0 inet static
        address 172.16.200.77
        netmask 255.255.255.0
        network 172.16.200.0
        broadcast 172.16.200.255
        gateway 172.16.200.10
        # dns-* options are implemented by the resolvconf package, if installed
        dns-nameservers 172.16.200.10
    """

    def __init__(self, iface, mode, ip=None, netmask="255.255.255.0",
                 network=None,
                 broadcast=None, gateway=None, nameserver=None, options=None):
        """
        Creates a new interface object

        :param iface: The name of the interface (lo, br0, eth0, eth1)
        :param mode: can bee loopback, manual, dhcp, static
        :param ip: The IP Address of the interface
        :type ip: basestring
        :param netmask: The netmask of the interface
        :param network: The network of the interface. If omitted it will be
            calculated from IP and netmask
        :param broadcast: The broadcast of the interface. If omitted it will be
            calculated from UP and netmask
        :param gateway: The gateway
        :param nameserver: list of nameserver
        :type param: basestring
        :return: an interface object
        """
        self.options = options or []
        self.iface = iface
        self.mode = mode
        if self.mode not in ["auto", "manual", "dhcp", "static"]:
            raise Exception("No valid mode. Valid modes are 'auto', "
                            "'manual', 'dhcp' or 'static'.")
        self.ip = ip
        self.netmask = netmask
        self.network = network
        self.broadcast = broadcast
        self.gateway = gateway
        self.nameserver = (nameserver or "").split()
        if ip and netmask:
            if not netaddr.valid_ipv4(ip):
                raise Exception("IP no valid IPv4 address.")

            network_object = netaddr.IPNetwork("%s/%s" % (ip, netmask))
            self.ip = ip
            self.netmask = netmask
            self.broadcast = self.broadcast or str(network_object.broadcast)
            self.network = self.network or str(network_object.network)
            if self.gateway:
                if not netaddr.valid_ipv4(self.gateway):
                    raise Exception("Gateway no valid IPv4 address")
            for ns in self.nameserver:
                if not netaddr.valid_ipv4(ns):
                    raise Exception("Nameserver no valid IPv4 address")

    def __str__(self):
        """
        This returns the Interface, just like it would be printed in
        /etc/networks/interfaces
        """
        iface = []
        iface.append("auto %s" % self.iface)
        iface.append("iface %s inet %s" % (self.iface, self.mode))
        if self.ip:
            iface.append("\taddress %s" % self.ip)
        if self.netmask:
            iface.append("\tnetmask %s" % self.netmask)
        if self.network:
            iface.append("\tnetwork %s" % self.network)
        if self.broadcast:
            iface.append("\tbroadcast %s" % self.broadcast)
        if self.gateway:
            iface.append("\tgateway %s" % self.gateway)
        if len(self.nameserver) > 0:
            iface.append("\tdns-nameservers %s" % " ".join(self.nameserver))
        for op in self.options:
            iface.append("\t%s" % op)

        return "\n".join(iface)


class NetworkParser(object):

    interface = Word(alphanums)
    key = Word(alphanums + "-_")
    space = White().suppress()
    value = CharsNotIn("{}\n#")
    line = Regex("^.*$")
    comment = ("#")
    method = Regex("loopback|manual|dhcp|static")
    stanza = Regex("auto|iface|mapping")
    option_key = Regex("bridge_\w*|post-\w*|up|down|pre-\w*|address"
                       "|network|netmask|gateway|broadcast|dns-\w*|scope|"
                       "pointtopoint|metric|hwaddress|mtu|hostname|"
                       "leasehours|leasetime|vendor|client|bootfile|server"
                       "|mode|endpoint|dstaddr|local|ttl|provider|unit"
                       "|options|frame|netnum|media")
    _eol = Literal("\n").suppress()
    option = Forward()
    option << Group(space
                    #+ Regex("^\s*")
                    + option_key
                    + space
                    + SkipTo(_eol))
    interface_block = Forward()
    interface_block << Group(stanza
                             + space
                             + interface
                             + Optional(
                                    space
                                    + Regex("inet")
                                    + method
                                    + Group(ZeroOrMore(
                                      option)
                                    ))
                             )

    # + Group(ZeroOrMore(assignment)))

    interface_file = OneOrMore(interface_block).ignore(pythonStyleComment)

    file_header = """# File parsed and saved by privacyidea.\n\n"""

    def __init__(self,
                 infile="/etc/network/interfaces",
                 content=None):
        self.filename = None
        if content:
            self.content = content
        else:
            self.filename = infile
            self._read()

        self.interfaces = self.get_interfaces()

    def _read(self):
        """
        Reread the contents from the disk
        """
        f = codecs.open(self.filename, "r", "utf-8")
        self.content = f.read()
        f.close()

    def get(self):
        """
        return the grouped config
        """
        if self.filename:
            self._read()
        config = self.interface_file.parseString(self.content)
        return config

    def save(self, filename=None):
        if not filename and not self.filename:
            raise Exception("No filename specified")

        # The given filename overrules the own filename
        fname = filename or self.filename
        f = open(fname, "w")
        f.write(self.format())
        f.close()

    def format(self):
        """
        Format the single interfaces e.g. for writing to a file.

        {"eth0": {"auto": True,
                  "method": "static",
                  "options": {"address": "1.1.1.1",
                              "netmask": "255.255.255.0"
                              }
                  }
        }
        results in

        auto eth0
        iface eth0 inet static
            address 1.1.1.1
            netmask 255.255.255.0

        :param interface: dictionary of interface
        :return: string
        """
        output = ""
        for iface, iconfig in self.interfaces.items():
            if iconfig.get("auto"):
                output += "auto %s\n" % iface

            output += "iface %s inet %s\n" % (iface, iconfig.get("method",
                                                               "manual"))
            # options
            for opt_key, opt_value in iconfig.get("options", {}).items():
                output += "    %s %s\n" % (opt_key, opt_value)
            # add a new line
            output += "\n"
        return output


    def get_interfaces(self):
        """
        return the configuration by interfaces as a dictionary like

        { "eth0": {"auto": True,
                   "method": "static",
                   "options": {"address": "192.168.1.1",
                               "netmask": "255.255.255.0",
                               "gateway": "192.168.1.254",
                               "dns-nameserver": "1.2.3.4"
                               }
                   }
        }

        :return: dict
        """
        interfaces = {}
        np = self.get()
        for idefinition in np:
            interface = idefinition[1]
            if interface not in interfaces:
                interfaces[interface] = {}
            # auto?
            if idefinition[0] == "auto":
                interfaces[interface]["auto"] = True
            elif idefinition[0] == "iface":
                method = idefinition[3]
                interfaces[interface]["method"] = method
            # check for options
            if len(idefinition) == 5:
                options = {}
                for o in idefinition[4]:
                    options[o[0]] = o[1]
                interfaces[interface]["options"] = options
        return interfaces
