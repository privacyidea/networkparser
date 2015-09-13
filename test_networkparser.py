# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import unittest
import os
from networkparser import Interface


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
