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
import sys, os, shutil
import logging
import requests

import hashlib
import time

class FlashAir(object):
    """
        Interface to the REST API of the Toshiba FlashAir card.  
        See the documentation to their API at:
            https://flashair-developers.com/en/
    """
    def __init__(self, hostname):
        """ 
            :param hostname: IP address or hostname of the FlashAir card
            :type hostname: string
        """
        self.hostname = hostname
        self.card_path = "/DCIM/100__TSB"

    def delete_file(self, filename):
        payload = {"op":100, "DIR":self.card_path}
        r = requests.get("http://%s/command.cgi" % self.hostname, params=payload)

    def get_file_list(self):
        """

            The SD card returns a list that looks like the following:

            WLANSD_FILELIST
            /DCIM/100__TSB,FA000001.JPG,128751,33,16602,18432
            /DCIM/100__TSB,FLASH3.JPG,370952,32,0,0
            /DCIM/100__TSB,FLASH5.JPG,287034,32,0,0
            /DCIM/100__TSB,FLASH6.JPG,387163,32,17295,31508
            /DCIM/100__TSB,FLASH7.JPG,533998,32,17295,31520

        """
        payload = {"op":100, "DIR":self.card_path}
        r = requests.get("http://%s/command.cgi" % self.hostname, params=payload)
        r.raise_for_status()
        print r.text
        # Divide the returned text by newline, and ignore the first line "WLANSD_FILELIST"
        lines = r.text.split('\n')
        assert lines[0].strip()=='WLANSD_FILELIST'

        filenames = []
        for line in lines[1:]:
            # Split each line by ',' and take the second column for the filename
            values = line.split(',')
            if len(values) > 2:
                filename = values[1].strip()
                filenames.append(filename)

        print filenames
        return filenames

    def _get_renamed_filename(self, filename):
        # First, separate out the path from the filename
        path = os.path.dirname(filename)
        fn = os.path.basename(filename)
        h = hashlib.sha1()
        h.update(fn)
        hash_filename = "%s.JPG" % (h.hexdigest()[:8].upper())

        hash_full_filename = os.path.join(path, hash_filename)
        logging.debug("Hashed file: %s" % (hash_full_filename))
        return hash_full_filename


    def copy_and_rename_file(self, filename):
        """
            :returns: hashed filename in 8.3 format with JPG extension
        """
        hash_full_filename = self._get_renamed_filename(filename)

        # First, separate out the path from the filename
        path = os.path.dirname(filename)
        fn = os.path.basename(filename)
        hash_filename = os.path.basename(hash_full_filename)

        # Rename the file to the hashed filename
        cwd = os.getcwd()
        os.chdir(path)
        if not os.path.exists(hash_filename):
            shutil.copy(fn, hash_filename)
            logging.debug("Copied %s to %s" % (fn, hash_filename))
        os.chdir(cwd)
        return hash_full_filename

    def delete_file(self, filename):
        # Change the upload directory on the card
        url = "http://%s/upload.cgi" % self.hostname

        payload = {'DEL': "%s/%s" % (self.card_path, filename)}
        r = requests.get(url, params=payload)
        r.raise_for_status()

    def _set_write_protect(self):
        # Change the upload directory on the card
        url = "http://%s/upload.cgi" % self.hostname

        payload = {'WRITEPROTECT': "ON"}
        r = requests.get(url, params=payload)
        r.raise_for_status()
        if not "SUCCESS" in r.content:
            print("Could not put card into host-write-protect mode")


    def set_timestamp(self, t):
        """
            :param t: The time stamp
            :type t: time.struct_time
        """
        fat32_time = ((t.tm_year-1980)<<25) | (t.tm_mon << 21) | (t.tm_mday << 16) | (t.tm_hour << 11) | (t.tm_min << 5) | (t.tm_sec >>1)

        #print("Setting timestamp to %d (0x%0.8X)" % (fat32_time, fat32_time))
        url = "http://%s/upload.cgi" % self.hostname
        payload = {'FTIME': "0x%0.8X" % fat32_time}
        r = requests.get(url, params=payload)
        r.raise_for_status()

    def upload_file(self, filename):
        # First, set the time of the photo to right now
        self.set_timestamp(time.localtime())
        # Change the upload directory on the card
        url = "http://%s/upload.cgi" % self.hostname

        payload = {'UPDIR':self.card_path}
        r = requests.get(url, params=payload)
        r.raise_for_status()

        # Now, upload the file
        hash_full_filename = self._get_renamed_filename(filename)
        hash_filename = os.path.basename(hash_full_filename)

        files = {'file':(hash_filename, open(filename,'rb'))}
        r = requests.post(url, files=files)
        r.raise_for_status()
        
    def sync_files_on_card_to_list(self, filename_list, force=False):
        """
            Delete any files on the SD card that are not present in the list.
            Upload any files not already present on the card (based on name).
            Ignore any files already present on the card.
        """

        self._set_write_protect()
        # First, get the file list on the card
        sd_file_list = self.get_file_list()
        
        hashed_local_list = [os.path.basename(self._get_renamed_filename(x)) for x in filename_list]

        # If force upload, we are going to delete all the files in this directory
        if force:
            files_to_delete_list = sd_file_list
        else:
            # Delete any file not present in the filename_list
            files_to_delete_list = [ fn for fn in sd_file_list if not fn in hashed_local_list]

        #for fn in sd_file_list:
            #if not fn in hashed_local_list:
        for fn in files_to_delete_list:
            print("Deleting file %s on FlashAir" % fn)
            self.delete_file(fn)

        # Now, for any file not already present in the SD card, upload it
        i = 0
        n = len(filename_list)
        for fn, hash_fn in zip(filename_list, hashed_local_list):

            i+=1
            if force or not hash_fn in sd_file_list:
                print("[%d/%d] Uploading file %s to %s on FlashAir" % (i,n,fn, hash_fn))
                self.upload_file(fn)

            else:
                print("[%d/%d] Uploading file %s to %s on FlashAir: SKIPPED(already present)" % (i,n,fn, hash_fn))

def main():
    #logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    script = FlashAir("192.168.9.70")
    file_list = script.get_file_list()
    #newfile = script.copy_and_rename_file("photos/11709952505.jpg")
    file_list =[ "photos/11692277333.jpg",
                "photos/11692418594.jpg",
                "photos/11692766176.jpg",
                "photos/11692787166.jpg",
                "photos/11699467984.jpg",
                "photos/11699860336.jpg",
                "photos/11709836005.jpg",
                "photos/11709952505.jpg",
                "photos/11710078243.jpg",
                "photos/11710080573.jpg",
                "photos/11710081763.jpg",]
    #script.upload_file("photos/11709836005.jpg")
    script.sync_files_on_card_to_list(file_list)
    

if __name__ == '__main__':
    main()


