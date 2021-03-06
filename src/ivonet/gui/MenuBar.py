#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 2021-03-04 22:53:16$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """
The Menubar
"""

import wx

# File Menu

FILE_MENU_QUEUE = wx.NewIdRef()
FILE_MENU_STOP_PROCESS = wx.NewIdRef()
FILE_MENU_TO_DIR = wx.NewIdRef()


class MenuBar(wx.MenuBar):
    """The Application menu."""

    def __init__(self, parent, style=0):
        super().__init__(style)
        self.parent = parent

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "New \tCTRL-N")
        file_menu.AppendSeparator()
        file_menu.Append(FILE_MENU_QUEUE, "Queue\tCTRL-R")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Quit\tCTRL-Q")

        self.Append(file_menu, "&File")

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT)

        self.Append(help_menu, "&Help")

        menu_handlers = [
            (FILE_MENU_QUEUE, self.parent.on_queue),
            (wx.ID_NEW, self.parent.on_clear),
            (wx.ID_EXIT, self.parent.on_exit),
            (wx.ID_ABOUT, self.parent.on_about),
        ]
        for menu_id, handler in menu_handlers:
            self.parent.Bind(wx.EVT_MENU, handler, id=menu_id)

