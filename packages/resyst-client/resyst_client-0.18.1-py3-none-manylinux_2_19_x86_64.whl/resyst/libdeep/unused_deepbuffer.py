# -*- coding: utf-8 -*-
#
# this file is part of libdeep project
#


"""Enhanced data buffer"""

# Public objects of this module
__all__ = ['DeepBuffer']


# --------------------------------------------------------------------------
#
class DeepBuffer(object):
    """

    TODO: remove this: there is no DataFrame knowledge.
    The data is manipulated in DataFrame blocks, possible of variable sizes.
    The DeepBuffer is independent of DeepDevice.

    Object creation::

        db = DeepBuffer(10)
        db = DeepBuffer(10, circular=True)

        buffer = bytearray(100)
        db = DeepBuffer(buffer)

    Usage examples::

        print len(db)
        print db.len()
        print db.used()
        print db.free()

        data = bytearray(20)
        db.write(data)

        db.read()
        db.read(10)

        db.flush()
    """

    # -----------------------------------------------------------------------
    #
    def __init__(self, argin, **kwargs):

        # Get mandatory argins
        try:
            # a buffer can passed (ex: byterray)
            self._size = len(argin)
            self.buffer = argin
        except TypeError:
            # a size in bytes can be passed
            self._size = int(argin)
            self.buffer = bytearray(self._size)

        # Get optional argins
        # TODO: remove dframe reference??
        #self._maxdframes = kwargs.get("maxdframes", 0)
        #self._maxbytes   = kwargs.get("maxbytes",   0)
        self._circular = kwargs.pop("circular", False)
        self._overwrite = kwargs.pop("overwrite", False)
        if kwargs.keys():
            raise BufferError('invalid arguments')

        # Internal initialization
        self._beg = 0
        self._end = 0

        # not needed by class itself but useful for parser class
        self.conditions = []

    # -----------------------------------------------------------------------
    #
    def write(self, dframe):
        """
        Append a new DataFrame.
        """

        #
        # TODO: handle buffer size
        bytes = len(dframe)
        if bytes > self.free():
            raise BufferError('not enough free space')

        # Append object
        # TODO: avoid data copy here
        # TODO: handle overwriting
        beg = self._end
        end = beg + bytes
        if self._circular:
            # Handle circular buffer
            l = self.len()
            if end > l:
                end = l
            n = end - beg
            rem = bytes - n
            self.buffer[beg:end] = dframe[0:n]
            if rem != 0:
                self.buffer[0:rem] = dframe[n:]
                self._end = rem
            else:
                self._end = end
        else:
            # Handle linear buffer
            self.buffer[beg:end] = dframe
            self._end = end

    # -----------------------------------------------------------------------
    #
    def read(self, bytes=0):
        """
        Return a bytearray of data from buffer.
        The maximum number of bytes returned can be given.
        Otherwise the full buffer is returned.
        """

        # By default empty the buffer
        if (bytes == 0) or (bytes > self.used()):
            bytes = self.used()

        # TODO: avoid data copy here
        ret = bytearray(bytes)

        # Consume data
        beg = self._beg
        end = beg + bytes
        if self._circular:
            # Handle circular buffer
            l = self.len()
            if end > l:
                end = l
            n = end - beg
            rem = bytes - n
            ret[0:n] = self.buffer[beg:end]
            if rem != 0:
                ret[n:] = self.buffer[0:rem]
                self._beg = rem
            else:
                self._beg = end
        else:
            # Handle linear buffer
            ret[:] = self.buffer[beg:end]
            self._beg = end

        # If buffer is empty then rewind
        if self.used() == 0:
            self._beg = self._end = 0

        #
        return ret

    # -----------------------------------------------------------------------
    #
    def flush(self, bytes=0):
        """
        Flush some data.
        The maximum number of bytes to flush can be given.
        Otherwise the full buffer is flushed.
        Returns the number of bytes flushed.
        """

        return len(self.read(bytes))

    # -----------------------------------------------------------------------
    #
    def __len__(self):
        return self.len()

    def len(self):
        """
        Returns the current size in bytes of the DeepBuffer
        which is diffrent from the current contained data.
        """

        # should be the same than len(self.buffer)
        return self._size

    # -----------------------------------------------------------------------
    #
    def used(self):
        """
        Returns the number of bytes currently contained.
        """

        # Calculate in bytes
        bytes = self._end - self._beg
        if bytes < 0:
            # handle circular buffer
            bytes = self.len() + bytes

        return bytes

    # -----------------------------------------------------------------------
    #
    def free(self):
        """
        Returns the number of bytes that could be written.
        """

        # Calculate in bytes
        if self._overwrite:
            # Handle overwrited buffer
            bytes = float('inf')
        else:
            # Handle linear buffer
            bytes = self.len() - self.used()

        return bytes
