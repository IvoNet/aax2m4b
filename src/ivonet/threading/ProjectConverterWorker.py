#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 2021-03-10 21:00:01$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """

"""

import _thread
import os
import re
import subprocess

import wx
import wx.lib.newevent

import ivonet
from ivonet.events import dbg, log
from ivonet.events.custom import ProcessDoneEvent, ProcessExceptionEvent
from ivonet.io import ffprobe


def time_seconds(seq) -> int:
    """ Calculates the time in seconds based on hours, minutes, seconds.
    The milliseconds are ignored. That kind of accuracy is not needed
    :param seq: (hours, minutes, seconds, [milliseconds])
    :return: int of seconds
    """
    return int(seq[0]) * 3600 + int(seq[1]) * 60 + int(seq[2])


class ProjectConverterWorker(object):
    DURATION = re.compile(".*Duration: ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{2}).*")
    TIME_ELAPSED = re.compile(".*size=.*time=([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{2}).*")

    def __init__(self, parent, project) -> None:
        self.parent = parent
        self.project = project
        self.base_dir, self.filename = os.path.split(self.project)
        self.audiobook_name = os.path.splitext(self.filename)[0]
        self.m4a = os.path.join(self.base_dir, self.audiobook_name + ".m4a")
        self.m4b = os.path.join(self.base_dir, self.audiobook_name + ".m4b")
        self.cover = os.path.join(self.base_dir, self.audiobook_name + ".jpg")
        self.keep_going = False
        self.running = False
        self.pid = None
        self.total_duration = 0
        self.progress = 0
        self.process = None

    def calc_percentage_done(self, seq):
        return int(time_seconds(seq) * 100 / self.total_duration)

    def start(self):
        self.keep_going = self.running = True
        _thread.start_new_thread(self.run, ())

    def stop(self):
        self.keep_going = False

    def is_running(self) -> bool:
        return self.running

    def run(self):
        self.running = True
        log(f"Creating: {self.m4b}")

        self.parent.stage = 1
        checksum = ffprobe.checksum(self.project)
        log(f"Checksum for [{self.project}] is [{checksum}]")
        if not checksum:
            wx.PostEvent(self.parent, ProcessExceptionEvent(msg="No checksum retrieved.", project=self.project))
            return

        self.parent.stage = 2
        activation_bytes = self.get_activation_bytes(checksum)
        log(f"Activation bytes for [{self.project}] are [{activation_bytes}]")
        if not activation_bytes:
            wx.PostEvent(self.parent, ProcessExceptionEvent(msg="No activation bites found.", project=self.project))
            return

        if not self.keep_going:
            self.running = False
            return

        self.parent.stage = 3
        metadata = ffprobe.metadata(self.project)

        if not self.keep_going:
            self.running = False
            return

        self.parent.stage = 4
        self.convert_2_m4a(activation_bytes)

        if not self.keep_going:
            self.running = False
            return

        self.parent.stage = 5
        self.add_metadata(metadata)

        if not self.keep_going:
            self.running = False
            return

        self.parent.stage = 7
        self.extract_cover()

        if not self.keep_going:
            self.running = False
            return

        self.parent.stage = 8
        self.add_cover_art()

        self.cleanup()

        if self.keep_going:
            self.parent.update(100)
            wx.PostEvent(self.parent, ProcessDoneEvent())
        self.running = False
        self.keep_going = False
        log(f"Created: {self.m4b}")

    def get_activation_bytes(self, checksum):
        ret = None
        for idx, rt_file in enumerate(ivonet.RAINBOW_FILES, 1):
            self.parent.update(idx * (100 / len(ivonet.RAINBOW_FILES)))
            ret = self.activation_bytes(rt_file, checksum)
            if ret:
                self.parent.update(100)
                return ret
        if not ret:
            self.keep_going = False
        return ret

    def activation_bytes(self, rt_file, checksum):
        cmd = [ivonet.APP_RCRACK, rt_file, "-h", checksum]
        dbg(cmd)

        self.subprocess(cmd)

        log(f"RainbowCrack: {self.project}")
        ret = None
        while self.keep_going:
            try:
                line = self.process.stdout.readline()
            except UnicodeDecodeError:
                continue
            dbg(line)
            if not line:
                dbg(f"Finished Merge for: {self.project}")
                break
            if "hex:" in line:
                ret = line.split("hex:")[1]
                if not ret or "notfound" in ret:
                    ret = None
        self.__check_process(cmd)
        self.parent.update(100)
        return ret.strip()

    def convert_2_m4a(self, activation_bytes):
        cmd = [ivonet.APP_FFMPEG,
               "-activation_bytes", activation_bytes,
               '-i',
               self.project,
               "-stats",
               "-y",
               "-vn",
               "-c:a", "copy",
               "-acodec", "aac",
               "-movflags", "use_metadata_tags",
               "-map_metadata", "0",
               "-map_metadata:s:a", "0:s:a",
               self.m4a,
               ]
        dbg(cmd)
        self.subprocess(cmd)

        log(f"Conversion has started for: {self.project}")
        while self.keep_going:
            try:
                line = self.process.stdout.readline()
            except UnicodeDecodeError:
                #  just skip a line
                continue
            if not line:
                dbg(f"Conversion finished for: {self.project}")
                break
            dbg(line)
            duration = self.DURATION.match(line)
            if duration:
                self.total_duration = time_seconds(duration.groups())
                continue
            elapsed = self.TIME_ELAPSED.match(line)
            if elapsed:
                self.progress = self.calc_percentage_done(elapsed.groups())
                self.parent.update(self.progress)
        self.__check_process(cmd)

    def add_metadata(self, metadata):
        """AtomicParsley "${AUDIOBOOK}.m4a" --title "${TITLE}"
        --grouping "${GROUPING}" --sortOrder album "${GROUPING}"
        --album "${ALBUM}" --artist "${AUTHOR}" --genre "${GENRE}"
        --tracknum "${TRACK}" --disk "${TRACK}" --comment "${COMMENT}"
        --year "${YEAR}" --stik Audiobook --overWrite"""
        tags = metadata["format"]["tags"]
        cmd = [
            ivonet.APP_ATOMIC_PARSLEY,
            self.m4a,
            "--title", f"{tags['title']}",
            "--album", f"{tags['album']}",
            "--artist", f"{tags['artist']}",
            "--genre", f"{tags['genre']}",
            "--comment", f"""{tags['comment']}""",
            "--year", f"{tags['date']}",
            "--encodingTool", f"{ivonet.TXT_APP_NAME} ({ivonet.TXT_APP_TINY_URL})",
            "--stik", "Audiobook",
            "--overWrite"
        ]
        dbg(cmd)
        self.subprocess(cmd)

        log(f"Adding metadata to: {self.project}")
        while self.keep_going:
            try:
                line = self.process.stdout.readline()
            except UnicodeDecodeError:
                #  just skip a line
                continue
            if not line:
                dbg(f"Finished Adding metadata to {self.project}")
                break
            dbg(line)
            if "Progress:" in line:
                ret = line.split("%")
                if len(ret) > 1:
                    try:
                        percentage = int(ret[0].split()[-1])
                        self.parent.update(percentage)
                        dbg(percentage)
                    except (IndexError, ValueError):
                        # Just ignore... probably bad line
                        pass
        self.parent.update(100)
        self.__check_process(cmd)

    def extract_cover(self):
        dbg("Extracting cover...")
        ret = subprocess.getstatusoutput(f'ffmpeg -i "{self.project}" -y -v quiet -an -vcodec copy "{self.cover}"')
        if ret[0] != 0:
            self.keep_going = False

    def add_cover_art(self):
        self.parent.update(10)
        cmd = [ivonet.APP_MP4_ART, "--add", self.cover, self.m4b]

        self.subprocess(cmd)

        log(f"Adding Cover Art to: {self.project}")
        while self.keep_going:
            try:
                line = self.process.stdout.readline()
            except UnicodeDecodeError:
                #  just skip a line.
                continue
            if not line:
                dbg(f"Finished Adding CoverArt to: {self.project}")
                break
            dbg(line)
            if "adding" in line:
                self.parent.update(50)
        self.__check_process(cmd)
        self.parent.update(100)

    def cleanup(self):
        try:
            os.remove(self.m4a)
        except IOError:
            pass

    def subprocess(self, cmd: list):
        """subprocess(command_list) -> perfors a system command.

        Runs a subprocess with the stderr piped to stdout.
        The input stream (stdin) is closed right after startup. The process does not need it.
        """
        if not self.keep_going:
            self.running = False
            return
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            universal_newlines=True,
        )
        # Close stdin as it is not used
        self.process.stdin.close()

    def __check_process(self, cmd):
        if self.process and not self.keep_going:
            self.process.terminate()
        self.process.stdout.close()
        self.process.wait()
        if self.process.returncode != 0 and self.keep_going:
            # Only throw an exception if the process terminated wrong
            # but we wanted to keep going
            self.keep_going = False
            dbg("Process exitcode: ", self.process.returncode)
            wx.PostEvent(self.parent, ProcessExceptionEvent(cmd=cmd, project=self.project, msg="Processing went wrong"))
