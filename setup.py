# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='networkparser',
      version='0.1',
      description='Parser for /etc/network/interfaces',
      author='Cornelius Kölbel',
      author_email='cornelius.koelbel@netknights.it',
      url='https://github.com/privacyidea/networkparser',
      py_modules=['networkparser'],
      install_requires=[
            'pyparsing>=2.0',
            'netaddr'
      ]
)
