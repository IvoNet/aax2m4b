#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 08/03/2021 19:57$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """

"""

import wx

import ivonet
from ivonet.events import log, dbg


class MP3DropTarget(wx.FileDropTarget):
    """Handler for the Drag and Drop events of MP3 files"""

    def __init__(self, target):
        super().__init__()
        self.target = target
        self.genre_logged = False
        self.disc_correction_logged = False

    def OnDropFiles(self, x, y, filenames):
        dbg("MP3 Files dropped", filenames)

        for name in filenames:
            if name.lower().endswith(ivonet.FILE_EXTENSION):
                log("Recognized project file. Opening...")
                self.target.project_open(name)
                return True
            if name.lower().endswith(".aax") and name not in self.target.lc_audiofiles.GetStrings():
                self.target.append_track(name)
            else:
                log(f"Dropped file '{name}' is not an mp3 file or not unique in the list.")
                return False
        self.genre_logged = False
        self.disc_correction_logged = False
        return True
