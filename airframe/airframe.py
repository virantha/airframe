#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import sys, os
import logging

from .version import __version__
from .flickr import Flickr
from .flashair import FlashAir

class AirFrame(object):

    def __init__(self):
        pass

    def _parse_csv_list(self, s):
        try:
            assert isinstance(s,str)
            s = s.strip()
            value_list = s.split(',')
        except:
            raise argparse.ArgumentTypeError("Could not parse tag list")
        return value_list

    def get_options(self, argv):
        """
            Parse the command-line options and set the following object properties:

            I really need to convert this to use docopt!

            :param argv: usually just sys.argv[1:]
            :returns: Nothing

            :ivar debug: Enable logging debug statements
            :ivar verbose: Enable verbose logging
        """
        p = argparse.ArgumentParser(
                description = "Push flickr pictures to a Toshiba FlashAir automatically",
                epilog = "AirFrame version %s (Copyright 2014 Virantha Ekanayake)" % __version__,
                )

        p.add_argument('-d', '--debug', action='store_true',
            default=False, dest='debug', help='Turn on debugging')

        p.add_argument('-v', '--verbose', action='store_true',
            default=False, dest='verbose', help='Turn on verbose mode')

        p.add_argument('-f', '--force', action='store_true',
            default=False, help='Force upload of all picutres to Flashair (instead of only new pictures)')

        p.add_argument('-n', '--number', type=int,
            default=100, dest='number', help='Max number of photos to sync')

        p.add_argument('-t', '--tags', type=self._parse_csv_list,
                default=[], dest='tags', help='List of tags to match')

        p.add_argument('flashair_ip', type=str,
                        help='The ip/hostname of your FlashAir card')


        args = p.parse_args(argv)

        self.debug = args.debug
        self.verbose = args.verbose
        self.photo_count = args.number
        self.photo_tags = args.tags
        self.force_upload = args.force
        self.flashair_ip = args.flashair_ip

        if self.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')

        if self.verbose:
            logging.basicConfig(level=logging.INFO, format='%(message)s')

    def go(self, argv):
        self.download_dir = ".airframe"
        self.get_options(argv)

        # Connect to Flickr
        logging.debug("list of tags: %s" % self.photo_tags)
        self.flickr = Flickr()
        if len(self.photo_tags) > 0:
            photo_filenames = self.flickr.get_tagged(self.photo_tags, self.photo_count, download_dir=self.download_dir)
        else:
            photo_filenames = self.flickr.get_recent(self.photo_count,download_dir=self.download_dir)

        self.flashair = FlashAir(self.flashair_ip)
        self.flashair.sync_files_on_card_to_list(photo_filenames, self.force_upload)

def main():
    script = AirFrame()
    script.go(sys.argv[1:])

if __name__ == '__main__':
    main()


