#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 2021-03-10 14:03:34$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """
Global defines
"""

import os

from ivonet.sys.application import data_directory

TXT_APP_NAME = "Aax2m4b"
TXT_APP_TINY_URL = "http://ivo2u.nl/TODO"  # TODO Fix me
HERE = os.path.abspath(os.path.dirname(__file__))
RESOURCE = os.path.abspath(HERE + '/../resources/')
ICON_APP = f"{RESOURCE}/yoda.png"

APP_RCRACK = f'{RESOURCE}/rcrack'
APP_MP3_BINDER = f'{RESOURCE}/mp3binder'
APP_FFMPEG = f'{RESOURCE}/ffmpeg'
APP_FFPROBE = f'{RESOURCE}/ffprobe'
APP_ATOMIC_PARSLEY = f"{RESOURCE}/AtomicParsley"
APP_MP4_CHAPS = f'{RESOURCE}/mp4chaps'
APP_MP4_ART = f"{RESOURCE}/mp4art"
if not os.path.isfile(APP_RCRACK):
    raise IOError("rcrack not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_MP3_BINDER):
    raise IOError("mp3binder not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_FFMPEG):
    raise IOError("ffmpeg not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_FFPROBE):
    raise IOError("ffprobe not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_ATOMIC_PARSLEY):
    raise IOError("AtomicParsley not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_MP4_CHAPS):
    raise IOError("mp4chaps not found. Are you sure you copied it to the resource folder? See the README.md")
if not os.path.isfile(APP_MP4_ART):
    raise IOError("mp4art not found. Are you sure you copied it to the resource folder? See the README.md")

RAINBOW_FILES = [os.path.join(RESOURCE, x) for x in os.listdir(RESOURCE) if x.lower().endswith(".rt")]

SETTINGS_DIRECTORY = data_directory(TXT_APP_NAME)
if not os.path.isdir(SETTINGS_DIRECTORY):
    os.mkdir(SETTINGS_DIRECTORY)

DEFAULT_SAVE_PATH = os.path.join(os.environ["HOME"], "Music")
if not os.path.isdir(DEFAULT_SAVE_PATH):
    DEFAULT_SAVE_PATH = os.path.join(os.environ["HOME"], "Documents")
if not os.path.isdir(DEFAULT_SAVE_PATH):
    DEFAULT_SAVE_PATH = os.path.join(os.environ["HOME"], "Downloads")
if not os.path.isdir(DEFAULT_SAVE_PATH):
    DEFAULT_SAVE_PATH = os.environ["HOME"]
if not os.path.isdir(DEFAULT_SAVE_PATH):
    DEFAULT_SAVE_PATH = "/"

SETTINGS_FILE = os.path.join(SETTINGS_DIRECTORY, f"{TXT_APP_NAME}.ini")
LOG_FILE = os.path.join(SETTINGS_DIRECTORY, f"{TXT_APP_NAME}.log")

try:
    VERSION = open(os.path.join(RESOURCE, "VERSION"), "r").read().strip()
except IOError as e:
    VERSION = "0.0.0"

DEVELOPERS = [
    "Ivo Woltring"
]

# Art
ART_PREFIX = "inART_"

# texts
TXT_DESCRIPTION_BLOG = "Ivo's blog"
TXT_URL_BLOG = "https://www.ivonet.nl"
TXT_COPYRIGHT = "Aax2m4b (c) 2021 Ivo Woltring"
TXT_ABOUT_DESCRIPTION = """Converts mp3 files to m4b with metadata and chapter information"""
TXT_LICENSE = """Copyright 2021 Ivo Woltring
        
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

FILE_EXTENSION = ".m4baker"
FILE_WILDCARD_PROJECT = "Aax2m4b (*.m4baker)|*.m4baker"
FILE_WILDCARD_M4B = "Audiobook (*.m4b)|*.m4b"

# Toolbar IDs
TOOLBAR_ID_OPEN_PROJECT = 1
TOOLBAR_ID_SAVE_PROJECT = 2
TOOLBAR_ID_QUEUE = 3
TOOLBAR_ID_SEPARATOR = 0
