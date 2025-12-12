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

"""Needed for asynchronoous communication"""

from __future__ import print_function
from __future__ import absolute_import

# Public objects of this module
__all__ = ['DataFrame']

# Standard modules
import sys
import array


# DEEP modules
from . import deeplog as log


class DataFrame(object):
    """
    Minimum unit of data for asynchronous streams.

    Large DataFrames can be splitted in several data chuncks
    that are transmitted as integral blocks of binary data.

    Object creation::

        tododoc

    Usage examples::

        tododoc
    """

    # -----------------------------------------------------------------------
    #
    def __init__(self, io_stream, dframes=None, buffer=None, **kwargs):

        # Get mandatory argins
        self.io_stream = io_stream

        # Get optional initialization
        self._checksum  = kwargs.pop("checksum",  None)
        self._sync      = kwargs.pop("sync",      True)  # False if async
        self._binary    = kwargs.pop("binary",    True)  # False if ASCII
        self._stream_id = kwargs.pop("stream_id", None)
        self._ice_frame = kwargs.pop("ice_frame", None)  # Async IcePAP only
        if kwargs.keys():
            raise BufferError('invalid arguments')

        # Internal initialization
        self.cache = None

        # The data storage destination is optional
        if buffer:
            self.buffer   = buffer
            self.frame_sz = len(buffer) * buffer.itemsize
            self.chunk_sz = self.frame_sz
            # TODO: memoryview() doesn't support arrays in Python2
            #self.mview = memoryview(buffer)
            self.mview    = buffer
        else:
            # TODO: implement a re-use of already allocated buffers for
            #       the same _stream_id
            pass

            """
            PF's code, blocking _stream_id usage, to be understood later

            if not self._stream_id in dframes:
                self.frame_sz = 0
                self.chunk_sz = 0
                buffer = DeepArray([])
                dframes[self._stream_id] = self
            else:
                pass
            self.mview = memoryview(buffer)
            """

        # number of bytes already read
        self.chunk_rd = 0

    # -----------------------------------------------------------------------
    #
    def read_chunk(self):

        # return immediately if nothing to read
        # NOTE: otherwise the readinto() on python2.7 will generate
        # a non documented TypeError exception
        nbytes2tk = len(self.io_stream.peek())
        if(nbytes2tk == 0):
            return False
        log.trace("nbytes to take : %r" % nbytes2tk)

        # TODO: select() returns immediately without reading more
        # data from socket until all buffered is consumed
        # (python2.7 bug???)
        if(nbytes2tk < self.mview.itemsize):
            self.cache = bytearray(nbytes2tk)
            nbytes = self.io_stream.readinto(self.cache)
            log.trace("got partial item size bytes: %d/%d" %
                      (nbytes, self.mview.itemsize))
            log.trace("consuming bytes: %d" % nbytes)
            return False
        if self.cache:
            nbytes2ca = len(self.cache)
        else:
            nbytes2ca = 0
        nbytes2tk += nbytes2ca

        # handle partial chunk received
        if ((self.chunk_rd == 0) and ((nbytes2tk % self.mview.itemsize) == 0)):
            # TODO: memoryview() doesn't support arrays in Python2
            #nbytes = self.io_stream.readinto(self.mview)
            nbytes = self.io_stream.readinto(self.mview)
            log.trace("consuming bytes: %d" % nbytes)
        else:
            # TODO: io.readinto() doesn't support subarrays
            # dirty workaround until decision on buffer refactoring
            nbytes2rd = self.chunk_sz - self.chunk_rd
            log.trace("nbytes needed  : %r" % nbytes2rd)
            if(nbytes2tk < nbytes2rd):
                nbytes2rd = nbytes2tk

            # must be a multiple of item size to avoid buffer corruption
            nbytes2rd -= nbytes2rd % self.mview.itemsize
            log.trace("nbytes to read : %r" % nbytes2rd)

            tmp_ba = bytearray(nbytes2rd - nbytes2ca)
            nbytes = self.io_stream.readinto(tmp_ba)
            log.trace("consuming bytes: %d" % nbytes)
            if self.cache:
                tmp_ba = self.cache + tmp_ba
                nbytes += nbytes2ca
                self.cache = None
            tmp_ar = array.array(self.buffer.typecode)
            array.array.fromstring(tmp_ar, bytes(tmp_ba))
            to_skip = self.chunk_rd / self.mview.itemsize
            self.buffer[to_skip:] = tmp_ar

        self.chunk_rd += nbytes
        if self.chunk_rd < self.chunk_sz:
            # TODO: once memoryview() is usable
            #to_skip = nbytes / self.mview.itemsize
            #self.mview = self.mview[to_skip:]
            log.trace("got partial chunk bytes: %d/%d" %
                      (self.chunk_rd, self.chunk_sz))
            return False

        # at this point a full chunk has been received
        log.trace("got one chunk of bytes: %d" % self.chunk_sz)
        self.frame_sz -= self.chunk_sz
        log.trace("remaining dframe bytes: %d" % self.frame_sz)

        # prepare next chunk reception
        self.chunk_sz = 0
        self.chunk_rd = 0
        self.mview    = None

        # check if a full dframe has been received
        if self.frame_sz == 0:
            """
            PF's code, blocking _stream_id usage, to be understood later
            if self._stream_id:
                del dframes[self._stream_id]
            else:
            """
            if True:
                # convert data into native order
                if (sys.byteorder == "big"):
                    self.buffer.byteswap()

                # checksum to 32 bits
                if self._checksum:
                    # TODO: shouldn't be cheksum calculated over data type?
                    calc_checksum = self.buffer.sum() & 0xffffffff
                    if calc_checksum != self._checksum:
                        # TODO: if within parser thread, this exception is lost
                        raise IOError("Bad binary checksum")

        return True

    # -----------------------------------------------------------------------
    #
    def iscomplete(self):
        return self.frame_sz == 0

    # -----------------------------------------------------------------------
    #
    def issync(self):
        return self._sync is True

    # -----------------------------------------------------------------------
    #
    def isasync(self):
        return self._sync is not True
