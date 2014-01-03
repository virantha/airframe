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

class MyOpener(urllib.FancyURLopener):
     version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Geck|  o/20071127 Firefox/3.5.0.11'    

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
                return
        urllib.urlretrieve(self._construct_flickr_url(), tgt)
        
class Flickr(object):

    def __init__(self):
        self.myopener = MyOpener()        
        pass

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
        self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
        (token,frob) = self.flickr.get_token_part_one(perms='read')
        if not token: raw_input("Press ENTER after you authorized this program")
        self.flickr.get_token_part_two((token,frob))


    def get_recent(self,count):
        """ Get the most recent photos
        """
        x = self.flickr.people_getPhotos(api_key = self.api_key, user_id="me",per_page=15)
        #x = self.flickr.photos_search(api_key=self.api_key,"me")
        photos = []
        for i in x.iter():
            if i.tag == 'rsp':
                # The response header.  stat member should be 'ok'
                if i.get('stat') == 'ok':
                    continue
                else:
                    # Error, so just break
                    break
            if i.tag == 'photo':
                photos.append(Photo(i))
        for photo in photos:
            print (photo._construct_flickr_url())
            photo.download_photo("photos", cache=True)


def main():
    script = Flickr()
    key,secret = script.read_keys()
    script.set_keys(key,secret)
    script.get_auth2()
    script.get_recent(10)


if __name__ == '__main__':
    main()


