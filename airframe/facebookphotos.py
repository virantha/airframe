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
import facebook
import urllib
import urlparse
from operator import itemgetter


SAFE_CHARS = '-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class Photo(object):
    def __init__(self, photo_element):
        """Construct a photo object out of the JSON response from Facebook"""
        attrs = { 'source': 'source', 'photoid':'photoid'}
        for fb_attr, py_attr in attrs.items():
            setattr(self, fb_attr, photo_element.get(fb_attr))

    def download_photo(self, dirname, cache=False, tgt_filename=None):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        tgt = os.path.join(dirname, "%s.jpg" % self.photoid)
        if cache:
            if os.path.isfile(tgt):
                return tgt
        urllib.urlretrieve(self.source, tgt)
        return tgt
        
class FacebookPhotos(object):

    def __init__(self):
        self.set_keys(*self.read_keys())
        #self.get_auth2()
#        self.refresh_token()

    def read_keys(self):
        """
            Read the Facebook API App ID and App Secret from a local file
        """
        with open("facebook_api.yaml") as f:
            api = yaml.load(f)
        return (api["app_id"], api["app_secret"], api["client_token"],  api["access_token"])

    def set_keys(self, app_id, app_secret, client_token, access_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.client_token = client_token
        self.access_token = access_token

    def write_keys(self):
        data = {'app_id': self.app_id, 'app_secret': self.app_secret, 'client_token': self.client_token, 'access_token': self.access_token}
        with open('facebook_api.yaml', 'w') as outfile:
            outfile.write(yaml.dump(data, default_flow_style=False))
            outfile.close()

#    def get_auth2(self):
#        self.token = facebook.get_app_access_token(self.app_id, self.app_secret)
#        print self.token
 
    def refresh_token(self):
        new_token = None
        """
            Gets a new long-lived token using the current long-lived token.
            See http://nodotcom.org/python-facebook-tutorial.html for reference.
        """
        url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=fb_exchange_token&fb_exchange_token=%s' % (self.app_id, self.app_secret, self.access_token)
        response = urllib.urlopen(url)
        oauth = response.read()
        try:
            new_token = urlparse.parse_qs(oauth)['access_token'][0]
            self.access_token = new_token
            self.write_keys()
        except:
            print 'Failed to retrieve and store a new long-lived token.'
        response.close()

    def _sync_photos(self, photos, download_dir="photos", clean_up=False):
        """
            Connect to Facebook, and for each photo in the list, download.
            Then, if deleted photos that are present locally that weren't present in the list of photos.

            :returns: List of filenames downloaded
        """
        photo_filenames = []
        photo_count = len(photos)
        for i,photo in enumerate(photos):
            print("[%d/%d] Downloading %s from Facebook" % (i+1, photo_count, photo.photoid))
            filename = photo.download_photo(download_dir, cache=True)
            photo_filenames.append(filename)

        # Now, go through and clean up directory if required
        
        if clean_up:
            photo_file_list = ["%s.jpg" % (x.photoid) for x in photos]
            for fn in os.listdir(download_dir):
                full_fn = os.path.join(download_dir, fn)
                if os.path.isfile(full_fn):
                    if not fn in photo_file_list:
                        print ("Facebook sync: Deleting file %s" % fn)
                        os.remove(full_fn)

        return photo_filenames

    def _extract_photos_from_json(self, dat):
        """Extract required data from a row"""
        err = []
        photos = []
        for d in dat:
            if 'id' not in d:
                err.append(d)
                continue
            photoid = d['id']
            
            if 'source' not in d:
                err.append(d)
                continue
            source = d['source']
            
            if 'images' not in d:
                err.append(d)
                continue
            images = d['images']
            images.sort(key=itemgetter('width'), reverse=True)
            photos.append(Photo({'source': images[0]['source'], 'photoid': photoid}))
        if err:
            print '%d errors.' % len(err)
            print err
        return photos

    def get_recent(self, count, download_dir="photos"):
        depth=10
        
        """Fetch the data using Facebook's Graph API"""
        photo_filenames = []
        graph = facebook.GraphAPI(self.access_token)
        url = 'me/photos/uploaded'
#        url = 'me/photos/'
        photos = []

        args = {'fields': ['source', 'photoid', 'images'], 'limit': count}
        res = graph.request(url, args)
        photos.extend(self._extract_photos_from_json(res['data']))
    
        # continue fetching till all photos are found
        for _ in xrange(depth):
            if 'paging' not in res:
                break
            try:
                url = res['paging']['next']
                res = json.loads(urllib.urlopen(url).read())
                photos.extend(self._extract_photos_from_json(res['data']))
            except:
                break
            
        photo_filenames = self._sync_photos(photos, download_dir)
        return photo_filenames

def main():
    #logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    script = FacebookPhotos()
    script.get_recent(10)


if __name__ == '__main__':
    main()
