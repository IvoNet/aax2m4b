#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 2021-03-10 20:59:56$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """
The Main Application Window
"""

import ast
import os
from configparser import ConfigParser

import wx
import wx.adv
from wx.lib.wordwrap import wordwrap

import ivonet
from ivonet.events import dbg
from ivonet.events.custom import EVT_PROCESS_CLEAN, ProcessCleanEvent, \
    EVT_PROCESS_CANCELLED, ProcessCancelledEvent
from ivonet.gui.AudiobookEntryPanel import AudiobookEntry
from ivonet.gui.MP3DropTarget import MP3DropTarget
from ivonet.gui.MenuBar import MenuBar, FILE_MENU_QUEUE
from ivonet.image.IvoNetArtProvider import IvoNetArtProvider
from ivonet.model.Project import Project

try:
    from ivonet.image.images import yoda, pixel
except ImportError:
    raise ImportError("The images file was not found. Did you forget to generate them?")


def handle_numeric_keypress(event):
    keycode = event.GetKeyCode()
    if keycode < 255 and chr(keycode).isnumeric():
        event.Skip()


class MainFrame(wx.Frame):
    """The main application Frame holding all the other panels"""

    def __init__(self, *args, **kw):
        """Initialize the gui here"""
        super().__init__(*args, **kw)

        #  Startup Settings
        self.activation_bytes = None
        self.active_queue = []
        self.genre_pristine = True
        self.project = Project()
        self.default_save_path = ivonet.DEFAULT_SAVE_PATH
        wx.ArtProvider.Push(IvoNetArtProvider())

        self.SetSize((1024, 768))
        self.SetMinSize((1024, 768))
        self.current_size = self.GetSize()

        self.__make_toolbar()
        self.SetMenuBar(MenuBar(self))

        self.CreateStatusBar()
        self.SetStatusText(ivonet.TXT_COPYRIGHT)

        self.status_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_clear_status, self.status_timer)

        vs_main = wx.BoxSizer(wx.VERTICAL)

        self.main_panel = wx.Panel(self, wx.ID_ANY)
        vs_main.Add(self.main_panel, 3, wx.EXPAND, 0)

        vs_main_panel = wx.BoxSizer(wx.VERTICAL)

        hs_main_panel = wx.BoxSizer(wx.HORIZONTAL)
        vs_main_panel.Add(hs_main_panel, 4, wx.EXPAND, 0)

        self.m4b_panel = wx.Panel(self.main_panel, wx.ID_ANY)
        hs_main_panel.Add(self.m4b_panel, 1, wx.EXPAND, 0)

        vs_m4b_panel = wx.BoxSizer(wx.VERTICAL)

        hs_m4b_panel = wx.BoxSizer(wx.HORIZONTAL)
        vs_m4b_panel.Add(hs_m4b_panel, 1, wx.EXPAND, 0)

        self.lc_audiofiles = wx.adv.EditableListBox(self, wx.ID_ANY, "Drag and Drop aax files below...",
                                                    style=wx.adv.EL_ALLOW_DELETE)
        self.lc_audiofiles.SetDropTarget(MP3DropTarget(self))
        self.lc_audiofiles.SetToolTip("Drag and Drop AAX files here")
        self.lc_audiofiles.del_button = self.lc_audiofiles.GetDelButton()
        self.lc_audiofiles.GetListCtrl().Bind(wx.EVT_LEFT_DCLICK, self.on_tracks_empty)

        hs_m4b_panel.Add(self.lc_audiofiles, 5, wx.ALL | wx.EXPAND, 0)

        self.log_panel = wx.Panel(self.main_panel, wx.ID_ANY)
        vs_main_panel.Add(self.log_panel, 1, wx.EXPAND, 0)

        log_sizer_v = wx.BoxSizer(wx.VERTICAL)

        log_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer_v.Add(log_sizer_h, 1, wx.EXPAND, 0)

        self.tc_log = wx.TextCtrl(self.log_panel, wx.ID_ANY, "",
                                  style=wx.TE_MULTILINE | wx.TE_LEFT | wx.TE_READONLY | wx.HSCROLL)
        self.tc_log.SetFont(
            wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Courier New"))
        wx.Log.SetActiveTarget(wx.LogTextCtrl(self.tc_log))
        log_sizer_h.Add(self.tc_log, 1, wx.EXPAND, 0)

        # Queue Part
        self.queue_window = wx.ScrolledWindow(self.main_panel, wx.ID_ANY,
                                              style=wx.BORDER_RAISED | wx.TAB_TRAVERSAL | wx.HT_WINDOW_VERT_SCROLLBAR)
        self.queue_window.SetScrollRate(10, 10)
        vs_main_panel.Add(self.queue_window, 1, wx.EXPAND, 0)

        self.queue_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.queue_window.SetSizer(self.queue_sizer_v)

        self.log_panel.SetSizer(log_sizer_v)

        self.m4b_panel.SetSizer(vs_m4b_panel)

        self.main_panel.SetSizer(vs_main_panel)

        self.SetSizer(vs_main)
        vs_main.SetSizeHints(self)

        self.load_settings()
        self.Layout()

        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_ui)
        self.update_timer.Start(750)

        self.Bind(wx.EVT_TEXT_MAXLEN, self.on_log_empty, self.tc_log)
        self.tc_log.Bind(wx.EVT_LEFT_DCLICK, self.on_log_empty)

        self.Bind(EVT_PROCESS_CLEAN, self.on_clean_queue_item)
        self.Bind(EVT_PROCESS_CANCELLED, self.on_process_cancelled)

        self.init()

    def init(self):
        # Remove old log file if still exists
        if os.path.isfile(ivonet.LOG_FILE):
            os.remove(ivonet.LOG_FILE)

        # Tell the world we started anew
        self.reset_metadata(self.project)

    def __make_toolbar(self):
        """Toolbar"""
        tool_bar_size = (256, 256)
        tool_bar = self.CreateToolBar((wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT))
        tool_bar.SetToolBitmapSize(tool_bar_size)

        tool_buttons = [
            (ivonet.TOOLBAR_ID_QUEUE, "queue", "Queue for processing", self.on_queue, False),
        ]
        for art_id, label, short_help, func, enabled in tool_buttons:
            if art_id <= 0:
                tool_bar.AddSeparator()
            else:
                bmp = wx.ArtProvider.GetBitmap("{prefix}{label}".format(
                    prefix=ivonet.ART_PREFIX,
                    label=label.upper()),
                    wx.ART_TOOLBAR, tool_bar_size)
                tool_bar.AddTool(art_id, label.capitalize(), bmp, short_help, wx.ITEM_NORMAL)
                self.Bind(wx.EVT_TOOL, func, id=art_id)
                tool_bar.EnableTool(art_id, enabled)

        tool_bar.Realize()

    def on_update_ui(self, event):
        """Handles the wx.UpdateUIEvent."""
        self.project.tracks = self.lc_audiofiles.GetStrings()
        enable_disable = self.project.verify()
        self.GetToolBar().EnableTool(ivonet.TOOLBAR_ID_QUEUE, enable_disable)
        self.GetMenuBar().Enable(FILE_MENU_QUEUE, enable_disable)
        self.queue_window.Refresh()
        self.main_panel.Layout()
        self.Refresh()
        event.Skip()

    def on_exit(self, event):
        """Close the frame, terminating the application."""
        if self.active_queue:
            with wx.MessageDialog(self, 'Conversions happening...',
                                  'Are you sure you want to exit?',
                                  wx.ICON_EXCLAMATION | wx.YES_NO) as dlg:
                if dlg.ShowModal() == wx.ID_NO:
                    return

        self.save_settings()
        self.Close(True)
        event.Skip()

    def on_about(self, event):
        """Display an About Dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName(ivonet.TXT_APP_NAME)
        info.SetVersion(ivonet.VERSION)
        info.SetCopyright(ivonet.TXT_COPYRIGHT)
        info.SetDescription(wordwrap(ivonet.TXT_ABOUT_DESCRIPTION, 350, wx.ClientDC(self)))
        info.SetWebSite(ivonet.TXT_URL_BLOG, ivonet.TXT_DESCRIPTION_BLOG)
        info.SetDevelopers(ivonet.DEVELOPERS)
        info.SetLicense(wordwrap(ivonet.TXT_LICENSE, 500, wx.ClientDC(self)))
        info.SetIcon(yoda.GetIcon())
        wx.adv.AboutBox(info, self)
        event.Skip()

    def on_queue(self, event):
        """Handles the queue event from either the toolbar or the File menu (shortcut)."""
        if not self.project.verify():
            dbg("You slipped between verifies :-) no no no processing allowed.")
            return
        self.status("Queueing audiobook...")

        for aax in self.project.tracks:
            self.queue_project(aax)

        self.on_clear(event)
        event.Skip()

    def queue_project(self, filename):
        """Queue a project.
        Wraps a project into an AudiobookEntry and puts it on the queue and start it.
        AudiobookEntry will take care of the rest.
        """
        book = AudiobookEntry(self, filename)
        self.queue_sizer_v.Prepend(book, 0, wx.ALL | wx.EXPAND, 0)
        self.active_queue.append(book)
        self.queue_window.Layout()
        self.Refresh()
        book.start()

    def on_clean_queue_item(self, event: ProcessCleanEvent):
        """Handles the cleaning of a queued item after it has been stopped and the button is pressed again."""
        event.obj.Destroy()
        self.remove_from_active_queue(event.obj)
        event.Skip()

    def on_process_cancelled(self, event: ProcessCancelledEvent):
        """Remove the process from the active queue when it is cancelled"""
        self.remove_from_active_queue(event.obj)

    def remove_from_active_queue(self, book):
        try:
            self.active_queue.remove(book)
        except ValueError as e:
            dbg(e)

    def reset_metadata(self, project):
        """Resets all the metadata fields to te provided project."""
        self.project = project
        self.lc_audiofiles.SetStrings(project.tracks)

    def on_clear(self, event):
        """Handles the new project event."""
        self.status("Starting new project")
        self.project = Project()
        self.reset_metadata(self.project)
        event.Skip()

    def status(self, msg):
        """Sets the statusbar text and triggers the reset timer"""
        self.SetStatusText(msg)
        if not self.status_timer.IsRunning():
            self.status_timer.Start(2000)

    def on_clear_status(self, event):
        """Handles the status bar timer event when triggered and resets it to the default message."""
        self.SetStatusText(ivonet.TXT_COPYRIGHT)
        if self.status_timer.IsRunning():
            self.status_timer.Stop()
        event.Skip()

    def on_tracks_empty(self, event):
        """Handles the double click event on the tracks panel and will empty the list"""
        dbg("on_tracks_empty")
        self.lc_audiofiles.SetStrings([])
        event.Skip()

    def append_track(self, line):
        """Add a line to the list."""
        lines = list(self.lc_audiofiles.GetStrings())
        lines.append(line)
        self.lc_audiofiles.SetStrings(lines)

    def save_settings(self):
        """save_settings() -> Saves default settings to the application settings location"""
        ini = ConfigParser()
        ini.add_section("Settings")
        ini.set('Settings', 'screen_size', str(self.GetSize()))
        ini.set('Settings', 'screen_pos', str(self.GetPosition()))
        with open(ivonet.SETTINGS_FILE, "w") as fp:
            ini.write(fp)

    def load_settings(self):
        """Load_ settings() -> Loads and activates the settings saved by save_settings()"""
        if os.path.isfile(ivonet.SETTINGS_FILE):
            ini = ConfigParser()
            ini.read(ivonet.SETTINGS_FILE)
            display_width, display_height = wx.DisplaySize()
            view_size = ast.literal_eval(ini.get('Settings', 'screen_size'))
            view_x, view_h = view_size
            if view_x > display_width or view_h > display_height:
                self.SetSize(self.GetBestSize())
            else:
                self.SetSize(view_size)
            position = ast.literal_eval(ini.get('Settings', 'screen_pos'))
            pos_w, pos_h = position
            if pos_w > display_width or pos_h > display_height:
                self.Center()
            else:
                self.SetPosition(position)
        else:
            self.Center()

    def on_log_empty(self, event):
        """Happends on double click and max_len"""
        self.tc_log.SetValue("")
        event.Skip()
