#!/usr/bin/python
# coding=utf-8
import argparse
import os
import tempfile

import requests

from lxml import etree
from subprocess import Popen

__author__ = "Aleksandr Shyshatsky"


class LocalizationHelper(object):
    LOCALE_TO_REGION = {
        'ru': 'ru',
        'uk': 'ru',
        'be': 'ru',
        'en': 'eu',
        'pl': 'eu',
        'de': 'eu',
    }

    def __init__(self, locale_list):
        self.__locale_list = locale_list

    def retrive(self):
        for locale in self.__locale_list:
            self.__retrive(locale)

    def __retrive(self, locale_name):
        link = self.__obtain_link_wgpkg(locale_name)
        self.__retrive_locale_file(link)

    def __obtain_link_wgpkg(self, locale_name):
        """
        I really don't know what is the difference between these links, so I just download one ;)
        <http name="Cedexis">
            http://dl-wows-cdx.wargaming.net/ru/patches/wows_0.6.7.0.261848_ru/wows.ru_0.6.7.0.261848_locale_be.wgpkg
        </http>
        <http name="G-Core">
            http://dl-wows-gc.wargaming.net/ru/patches/wows_0.6.7.0.261848_ru/wows.ru_0.6.7.0.261848_locale_be.wgpkg
        </http>
        <web_seeds>
            <url threads="10">
                http://dl-wows-gc.wargaming.net/ru/patches/wows_0.6.7.0.261848_ru/wows.ru_0.6.7.0.261848_locale_be.wgpkg
            </url>
        </web_seeds>
        :type locale_name: str
        :rtype: str
        """
        url = "http://update.worldofwarships.{}".format(self.LOCALE_TO_REGION[locale_name])
        data = dict(
            target='locale',
            locale_ver='unknown',
            lang=locale_name
        )
        xml = requests.get(url, data).content
        link = etree.fromstring(xml).xpath('content/file/web_seeds/url/text()')[0]

        return link

    def __retrive_locale_file(self, link):
        """
        Retrives wgpkg file, exports .mo;
        Returns link to exported .mo file;
        :type link: str 
        :rtype: str 
        """

        filename = os.path.basename(link)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(requests.get(link).content)

        temp_extracted_dir = tempfile.gettempdir()
        Popen(['7z', '-aoa', '-y', 'e', temp_path, '*.mo', '-r', '-o{}'.format(temp_extracted_dir)]).communicate()
        os.unlink(temp_path)

        locale_path = os.path.join(temp_extracted_dir, 'global.mo')
        Popen(['msgunfmt', locale_path, '-o', '{}.po'.format(filename)]).communicate()
        os.unlink(locale_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--locale', nargs='+', required=True,
                        help='list of locale names')

    namespace = parser.parse_args()
    locale_helper = LocalizationHelper(namespace.locale)
    locale_helper.retrive()
