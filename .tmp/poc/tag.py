#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
__author__ = "Ivo Woltring"
__revised__ = "$revised: 14/03/2021 13:31$"
__copyright__ = "Copyright (c) 2021 Ivo Woltring"
__license__ = "Apache 2.0"
__doc__ = """

"""


from ivonet.io.ffprobe import checksum, metadata

if __name__ == '__main__':
    print(checksum("/Users/iwo16283/dev/ivonet-aax2m4b/BloodHeirKateDanielsWorldBook1_ep7.aax"))
    print(metadata("/Users/iwo16283/dev/ivonet-aax2m4b/BloodHeirKateDanielsWorldBook1_ep7.aax"))
