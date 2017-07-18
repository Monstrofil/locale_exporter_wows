#!/usr/bin/python
# coding=utf-8
from distutils.core import setup

__author__ = "Aleksandr Shyshatsky"

setup(name='World of Warships localization files downloader',
      version='1.0',
      description='Utility that downloads .mo files for specified languages and converts .mo to .po',
      author=__author__,
      author_email='shalal545@gmail.com',
      url='https://github.com/Monstrofil/locale_exporter_wows',
      scripts=['locale_exporter.py'])
