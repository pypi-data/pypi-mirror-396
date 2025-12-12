# -*- coding: utf-8 -*-

# Copyright (C) 2025 by European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the “Software”), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, print_function

"""Handle communication with any Deep based device"""

#from .dconfig import DConfig
from .device import (DeepDevice, IcepapDevice, DanceDevice, LegacyDevice,
                     DeepError, DeepSysError, DeepDeviceError, DeepCommError, DeepCmdError)

from .deepobject import DeepArray
#from .deepasync import DataStream, DataReceiver, DeepCondition, DeepEvent
#from .deepbuffer import DeepBuffer

debug = DeepDevice.debug
show_internals = DeepDevice.show_libdeep_internals

__url__ = "https://deg-svn.esrf.fr/svn/libdeep/dev/python/libdeep"
__version__ = "0.0.0"
__modname__ = "libdeep"
__author__ = ""
__author_email__ = ""
__description__ = "Library that implements the deep protocol to handle" + \
                  " communication with any DEEP based device (DAnCE, IcePAP, ...)"
