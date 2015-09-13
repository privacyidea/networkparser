# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import unittest
import os
from networkparser import Interface, NetworkParser


class TestInterface(unittest.TestCase):

    def setUp(self):
        pass

    def test_valid_interfaces(self):
        # no valid mode
        self.assertRaises(Exception, Interface, "eth1", "asdf")
        # no valid ip address
        self.assertRaises(Exception, Interface, "eth0", "auto", "noIP")
        # No valid netmask
        self.assertRaises(Exception, Interface, "eth0", "auto", "172.1.1.1",
                          "nomask")
        iface = Interface("eth0", "static", "1.1.1.1", "255.255.0.0")
        self.assertEqual(iface.ip, "1.1.1.1")
        self.assertEqual(iface.netmask, "255.255.0.0")
        self.assertEqual(iface.broadcast, "1.1.255.255")
        self.assertEqual(iface.network, "1.1.0.0")

    def test_gateway(self):
        iface = Interface("eth0", "static", "1.1.1.1", "255.255.0.0",
                          gateway="1.1.1.2")
        self.assertEqual(iface.gateway, "1.1.1.2")
        self.assertRaises(Exception, Interface, "eth1", "static", "1.1.1.1",
                          "255.255.255.0", gateway="noGW")

    def test_nameserver(self):
        iface = Interface("eth0", "static", "1.1.1.1", nameserver="1.1.1.2 "
                                                                  "1.1.1.3")
        self.assertEqual(len(iface.nameserver), 2)
        self.assertEqual(iface.nameserver[0], "1.1.1.2")
        self.assertEqual(iface.nameserver[1], "1.1.1.3")
        # invalid nameserver
        self.assertRaises(Exception, Interface, "eth0", "static", "1.1.1.1",
                          nameserver="1.1.1.1 my.nameserver.local")

    def test_print(self):
        iface = Interface("eth0", "static", "1.1.1.1", nameserver="1.1.1.2 "
                                                                  "1.1.1.3")
        p = "%s" % iface
        print "\n%s" % p
        self.assertTrue("address 1.1.1." in p)
        self.assertTrue("iface eth0 inet static" in p)
        self.assertTrue("netmask 255.255.255.0" in p)
        self.assertTrue("dns-nameservers 1.1.1.2 1.1.1.3" in p)

Content = """auto lo
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

auto eth1
iface eth1 inet dhcp

auto eth2
iface eth2 inet static
    address 172.16.200.1
"""

RESULT_AFTER_PARSING = """auto lo
iface lo inet loopback

auto br0
iface br0 inet dhcp
    post-up ip link set br0 address  aa:bb:cc:dd:ee:ff
    bridge_stp off
    bridge_fd 0
    bridge_ports eth0
    bridge_maxwait 0

auto eth2
iface eth2 inet static
    address 172.16.200.1

auto eth1
iface eth1 inet dhcp

auto eth0
iface eth0 inet manual

"""


class TestNetworkParser(unittest.TestCase):

    def test_01_read_config(self):
        np = NetworkParser(content=Content)
        r = np.get()
        self.assertEqual(len(r), 10)

        interfaces = np.get_interfaces()
        self.assertEqual(len(interfaces), 5)
        self.assertEqual(interfaces.get("eth0").get("method"), "manual")
        self.assertEqual(interfaces.get("eth1").get("method"), "dhcp")
        self.assertEqual(interfaces.get("eth2").get("method"), "static")
        self.assertEqual(interfaces.get("eth2").get("options").get(
            "address"), "172.16.200.1")

        output = np.format()

        self.assertEqual(output, RESULT_AFTER_PARSING)
