# -*- coding: utf-8 -*-
import codecs
import netaddr
from pyparsing import White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, OneOrMore
from pyparsing import pythonStyleComment


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
    pass
