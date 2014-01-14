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

import yaml
import flickrapi
import urllib


class Photo(object):
    def __init__(self, photo_element):
        """Construct a photo object out of the XML response from Flickr"""
        attrs = { 'farm': 'farmid', 'server':'serverid','id':'photoid','secret':'secret'}
        for flickr_attr, py_attr in attrs.items():
            setattr(self, py_attr, photo_element.get(flickr_attr))
        
    def _construct_flickr_url(self):
        url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % (self.farmid,self.serverid, self.photoid, self.secret)
        return url

    def download_photo(self, dirname, cache=False, tgt_filename=None):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        tgt = os.path.join(dirname, "%s.jpg" % self.photoid)
        if cache:
            if os.path.isfile(tgt):
                return tgt
        urllib.urlretrieve(self._construct_flickr_url(), tgt)
        return tgt
        
class Flickr(object):

    def __init__(self):
        self.set_keys(*self.read_keys())
        self.get_auth2()

    def read_keys(self):
        """
            Read the flickr API key and secret from a local file
        """
        with open("flickr_api.yaml") as f:
            api = yaml.load(f)
        return (api["key"], api["secret"])

    def set_keys(self, key, secret):
        self.api_key = key
        self.api_secret = secret

    def get_auth2(self):
        print("Authenticating to Flickr")
        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
        (token,frob) = self.flickr.get_token_part_one(perms='read')
        if not token: raw_input("Press ENTER after you authorized this program")
        self.flickr.get_token_part_two((token,frob))
        print("Authentication succeeded")


    def get_tagged(self, tags, count, download_dir="photos"):
        """ Get photos with the given list of tags
        """
        print ("connecting to flickr, and getting %d photos with tags %s" % (count, tags))
        x = self.flickr.photos_search(api_key = self.api_key, user_id="me", tags=','.join(tags), per_page=count)
        photos = self._extract_photos_from_xml(x)
        photo_filenames = self._sync_photos(photos, download_dir)
        print("Found %d photos" % len(photos))
        return photo_filenames


    def _sync_photos(self, photos, download_dir="photos", clean_up=False):
        """
            Connect to flickr, and for each photo in the list, download.
            Then, if delete photos that are present locally that weren't present in the list of photos.

            :returns: List of filenames downloaded
        """
        photo_filenames = []
        photo_count = len(photos)
        for i,photo in enumerate(photos):
            print("[%d/%d] Downloading %s from flickr" % (i,photo_count,photo.photoid))
            filename = photo.download_photo(download_dir, cache=True)
            photo_filenames.append(filename)

        # Now, go through and clean up directory if required
        
        if clean_up:
            photo_file_list = ["%s.jpg" % (x.photoid) for x in photos]
            for fn in os.listdir(download_dir):
                full_fn = os.path.join(download_dir, fn)
                if os.path.isfile(full_fn):
                    if not fn in photo_file_list:
                        print ("Flickr sync: Deleting file %s" % fn)
                        os.remove(full_fn)

        return photo_filenames

    def _extract_photos_from_xml(self, xml):
        photos = []
        for i in xml.iter():
            if i.tag == 'rsp':
                # the response header.  stat member should be 'ok'
                if i.get('stat') == 'ok':
                    continue
                else:
                    # error, so just break
                    break
            if i.tag == 'photo':
                photos.append(Photo(i))
        return photos

    def get_recent(self,count, download_dir="photos"):
        """ get the most recent photos
        """
        print ("connecting to flickr, and getting most recent %d photos" % count)
        x = self.flickr.people_getphotos(api_key = self.api_key, user_id="me",per_page=count)
        #x = self.flickr.photos_search(api_key=self.api_key,"me")

        photos = self._extract_photos_from_xml(x)
        photo_filenames = self._sync_photos(photos, download_dir)
        return photo_filenames


def main():
    #logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    script = Flickr()
    #key,secret = script.read_keys()
    #script.set_keys(key,secret)
    #script.get_auth2()
    script.get_recent(10)


if __name__ == '__main__':
    main()


