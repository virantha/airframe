AirFrame
===============================

.. image:: https://badge.fury.io/py/airframe.png
    :target: http://badge.fury.io/py/airframe
    
.. image:: https://pypip.in/d/airframe/badge.png
        :target: https://crate.io/packages/airframe?version=latest

Download images from an authenticated Flickr account and push
them wirelessly to a Toshiba FlashAir Wifi SD card mounted
in a digital photo frame.

* Free software: ASL2 license
* Documentation: http://documentup.com/virantha/airframe
* Source: http://github.com/virantha/airframe
* API docs: http://virantha.github.com/airframe/html

Features
--------

* Authenticates to Flickr to get your private photos
* Only downloads photos with specified tags
* Caches and syncs the photos to the Wifi SD card


Installation
------------

.. code-block:: bash

   $ pip install airframe

Usage
-----

First, go to Flickr and get a private key at http://www.flickr.com/services/api/misc.api_keys.html

Then, create a directory from where you will start airframe, and create a file called flickr_api.yaml:

.. code-block:: yaml

    key: "YOUR_API_KEY"
    secret: "YOUR_API_SECRET"

Then, setup your FlashAir card as described in `this post's
<http://virantha.com/2014/01/09/hacking-together-a-wifi-photo-frame-with-a-toshiba-flashair-sd-card-wireless-photo-uploads>`__
"Enabling the FlashAir" section.  

Now, you're ready to sync some photos!  Just run:

.. code-block:: bash

   $ airframe -n 100 -t photoframe YOUR_AIRFRAME_IP

This will download and sync the 100 most recent photos tagged with "photoframe" to your
AirFrame. 

.. warning:: Any other image files in the FlashAir upload directory will be deleted, so make sure you backup anything you want to keep from your SD card.

The image files from Flickr will be cached in a sub-directory called
``.airframe`` in the location you invoked airframe from, so as long as you rerun
from the same directory, the script will only download new files from Flickr.  If you want to
redownload all the files from scratch, just ``rm .airframe`` these files.

The script will also only upload new images to the FlashAir card, and ignore any files that are
already present on the card.  If you want to force a clean upload, do the following:

.. code-block:: bash

    $ airframe -n 100 -t photoframe -f YOUR_AIRFRAME_IP

This will delete all images already on the card, and upload every image again.

