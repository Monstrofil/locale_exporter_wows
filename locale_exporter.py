#!/usr/bin/python3
# coding=utf-8
import argparse
import shutil
from pathlib import Path

import py7zr
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

    def _extract_mo_locale_files(self, archive_path, locale_name):
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            versions = [
                path for path in z.getnames()
                if path.startswith('bin/') and path.count('/') == 1
            ] # => ['3912232', '4046169']
            highest_version = max(versions)

            locale_path = highest_version + '/res/texts/{locale_name}/LC_MESSAGES/global.mo'.format(
                locale_name=locale_name
            )
            temp_dir = tempfile.gettempdir()

            z.extract(targets=[
                os.path.basename(locale_path),
                locale_path
            ], path=temp_dir)

            return os.path.join(temp_dir, locale_path)

    def _download_locale_file(self, locale_file_url):
        filename = os.path.basename(locale_file_url)
        temp_path = os.path.join(tempfile.gettempdir(), filename)

        if os.path.exists(temp_path):
            return temp_path

        with open(temp_path, 'wb') as f:
            f.write(requests.get(locale_file_url).content)
        return temp_path

    def retrive(self):
        locale_file_url = self._get_locale_archive_link()
        path = self._download_locale_file(locale_file_url)

        for locale in self.__locale_list:
            self.__retrive(locale, path)

    def __retrive(self, locale_name, locales_file):
        mo_file = self._extract_mo_locale_files(locales_file, locale_name)
        self.__retrive_locale_file(mo_file, export_to='wows.0_0_locale_{locale_name}.wgpkg.po'.format(locale_name=locale_name))

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
        # https://dl-wows-gc.wargaming.net/ww/patches/wows_0.10.5.0.4053181_ww/wows.ww_0.10.5.0.4053181_locale.wgpkg
        url = "http://update.worldofwarships.{}".format(self.LOCALE_TO_REGION[locale_name])
        data = dict(
            target='locale',
            locale_ver='unknown',
            lang=locale_name
        )
        xml = requests.get(url, data).content
        link = etree.fromstring(xml).xpath('content/file/web_seeds/url/text()')[0]

        return link

    def _get_locale_archive_link(self):
        url = 'https://wgus-eu.wargaming.net/api/v1/patches_chain/'
        data = dict(
            protocol_version='1.10',
            client_type='high',
            lang='RU',
            metadata_version='20210119113723',
            metadata_protocol_version='6.10',
            chain_id='f11',
            client_current_version='0',
            locale_current_version='0',
            sdcontent_current_version='0',
            game_id='WOWS.WW.PRODUCTION',
        )
        xml = requests.get(url, data).content

        locale_file = etree.fromstring(xml).xpath("patches_chain/patch[part = 'locale']/files[1]/file/name/text()")[0]
        locale_file_url = 'https://dl-wows-gc.wargaming.net/ww/patches/' + locale_file

        return locale_file_url

    def __retrive_locale_file(self, mo_file, export_to):
        Popen(['msgunfmt', mo_file, '-o', export_to]).communicate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--locale', nargs='+', required=True,
                        help='list of locale names')

    namespace = parser.parse_args()
    locale_helper = LocalizationHelper(namespace.locale)
    locale_helper.retrive()
