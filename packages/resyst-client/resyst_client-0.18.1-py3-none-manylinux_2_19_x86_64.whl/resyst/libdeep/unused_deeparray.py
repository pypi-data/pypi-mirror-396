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


"""
Data type used for communication with any Deep or IcePAP device
"""

from __future__ import absolute_import, print_function

import sys
import numpy


#---------------------------------------------------------------------
# old stuff to be removed ...

import array
import struct

_inPython2 = 'unicode' in __builtins__

class OldDeepArray(array.array):
    """
    Data type definition
    """

    # class private attributes
    _stypes = [('b', 'int'), ('B', 'uint'),
               ('h', 'int'), ('H', 'uint'),
               ('i', 'int'), ('I', 'uint'),
               ('l', 'int'), ('L', 'uint'),
               ('q', 'int'), ('Q', 'uint'),
               ('f', 'float'),
               ('d', 'float')]
    _dtypes = None

    @staticmethod
    def _update_dtypes():
        # build dtype dictionary:
        # _dtypes[dtype] = (itemsize, ctype, stype, atype)
        DeepArray._dtypes = dict()
        for stype, cprefix in DeepArray._stypes:
            try:
                csize = array.array(stype).itemsize
                ctype = cprefix + str(csize * 8)
                DeepArray._dtypes[stype] = (csize, ctype, stype, stype)
                DeepArray._dtypes[ctype] = (csize, ctype, stype, stype)
            except:  # Python2: not implemented stype code ('q', 'Q'), skip
                continue
        #for i in DeepArray._dtypes: print(i, DeepArray._dtypes[i])

    @classmethod
    def _check_dtype(cls, dtype, data=None):
        if not cls._dtypes:
            cls._update_dtypes()

        if dtype is None or dtype == 'a':
            try:
                dtype = None
                dtype = data.dtype   # this works for DeepArray instances
                dtype = dtype.name   # this works for numpy arrays
            except:
                if dtype is None:
                    itemsize = data.itemsize if hasattr(data, 'itemsize') else 1
                    dtype = 'uint{}'.format(itemsize * 8)
                    if dtype not in cls._dtypes:
                        for dt, (csize, ctyte, stype, stype) in cls._dtypes.items():
                            if csize == itemsize:
                                dtype = dt
                                break

        if dtype not in cls._dtypes.keys():
            raise ValueError('invalid dtype \'' + dtype + '\'')
        return dtype

    def __new__(cls, data, dtype=None):
        """
        Returns an object of type DeepArray
          dtype identifies the type:
            format characters used by struct module ('b', 'B', ..., 'f', 'd')
            c-like identifiers ('int8','uint8','int16'...'float32','float64')
        """

        # determine the type of the new array
        dtype = cls._check_dtype(dtype, data)
        _, ctype, stype, atype = cls._dtypes[dtype]

        if _inPython2:
            try:
                # try to instanciate directly (may fail if bad data type)
                # only way of initialising from a bytearray with Python 2
                self = super(DeepArray, cls).__new__(cls, atype, data)
            except:
                # otherwise initialise the array as an empty instance
                self = super(DeepArray, cls).__new__(cls, atype)
                # and append the data bytes
                try:    # from a numpy array or a DeepArray
                    super(DeepArray, self).fromstring(data.tobytes())
                except AttributeError:
                    if hasattr(data, '_b_base_') or isinstance(data, str):
                        # from a str or a ctypes object (a char array)
                        super(DeepArray, self).fromstring(data)
                    else:
                        # or a last try
                        super(DeepArray, self).extend(data)

        else:  # in Python 3
            # Initialise the array as an empty instance
            self = super(DeepArray, cls).__new__(cls, atype)
            # and append the data in a second step
            try:    # from a numpy array or a DeepArray
                super(DeepArray, self).frombytes(data.tobytes())
            except AttributeError:
                if hasattr(data, '_b_base_') or isinstance(data, (bytes, bytearray)):
                    # from a bytes, bytearray or a ctypes object (a char array)
                    super(DeepArray, self).frombytes(data)
                else:
                    # in other cases (e.g. a list) try to extend the array
                    super(DeepArray, self).extend(data)

        self.dtype = ctype
        self.format = stype
        self._update_size()
        return self

    def __repr__(self):
        return super(DeepArray, self).__repr__().replace('array', 'DeepArray')

    def _update_size(self):
        self.nitems = len(self)
        self.ndim = 1
        self.shape = (self.nitems,)
        #self.itemsize is defined by the array.array class and is not writable!!
        self.size = self.nitems

    def tolist(self):
        return super(DeepArray, self).tolist()

    def tobytes(self):
        if _inPython2:
            return super(DeepArray, self).tostring()  # Python 2
        else:
            return super().tobytes()   # Python 3

    def tostring(self):
        return str(self.tobytes())

    def tofile(self, file_id):
        if isinstance(file_id, str):
            with open(file_id, "wb+") as f:
                f.write(self.tobytes())
        else:
            file_id.write(self.tobytes())

    @classmethod
    def fromfile(cls, file_id, dtype=None, byteorder="little"):
        if isinstance(file_id, str):
            with open(file_id, "rb") as f:
                databytes = f.read()
        else:
            databytes = file_id.read()

        return cls.frombytes(databytes, dtype=dtype, byteorder=byteorder)

    @classmethod
    def fromstring(cls, datastr, dtype=None, byteorder="little"):
        return cls.frombytes(datastr, dtype, byteorder)

    @classmethod
    def frombytes(cls, databytes, dtype=None, byteorder="little"):
        darr = cls(databytes, dtype=dtype)
        if byteorder != sys.byteorder:
            darr.byteswap()
        return darr

    def byteswap(self):
        array.array.byteswap(self)

    def sum(self, dtype=None):
        """
        Returns the data checksum

        By default, the calculation is done considering using the
        native data type

        Another type can be specified
        """

        # by default return a checksum over native data type
        if(dtype is None):
            return sum(self)

        # checksum over different data type
        dtype = self._check_dtype(dtype)
        itemsize, ctype, stype, atype = self._dtypes[dtype]
        nitems = self.size
        dfrm = '<' + str(nitems) + stype
        dlist = struct.unpack_from(dfrm, self)
        return sum(dlist)

    def astype(self, dtype):
        """Returns copy of the array cast to specified type"""

        # destination data type
        ddtype = self._check_dtype(dtype)
        dcsize, dctype, dstype, datype = self._dtypes[dtype]

        # source data type
        scsize, sctype, sstype, satype = self._dtypes[self.dtype]

        #TODO: better/faster method than iterator to copy data
        #TODO: implement all casts, with/without safe ones
        #TODO: how to handle difference between float32/float64

        # cast from unsigned ...
        if (self.dtype[0] == 'u'):
            # cast from unsigned to signed
            if (dctype[0] == 'i'):
                sigmsk = 1 << ((scsize * 8) - 1)
                return DeepArray([i | (-(i & sigmsk)) for i in self], ddtype)
            # cast from unsigned to unsigned
            elif (dctype[0] == 'u'):
                valmsk = (1 << (dcsize * 8)) - 1
                return DeepArray([i & valmsk for i in self], ddtype)
            # cast from unsigned to float
            elif (dctype[0] == 'f'):
                return DeepArray([float(i) for i in self], ddtype)
        # cast from signed ...
        elif (self.dtype[0] == 'i'):
            # cast from signed to unsigned
            if (dctype[0] == 'u'):
                sigval = (1 << (dcsize * 8))
                valmsk = (1 << (dcsize * 8)) - 1
                return DeepArray([(i + sigval) & valmsk for i in self], ddtype)
            # cast from signed to signed
            elif (dctype[0] == 'i'):
                sigmsk = 1 << ((scsize * 8) - 1)
                return DeepArray([i | (-(i & sigmsk)) for i in self], ddtype)
            # cast from signed to float
            elif (dctype[0] == 'f'):
                return DeepArray([float(i) for i in self], ddtype)
        # cast from float ...
        elif (self.dtype[0] == 'f'):
            # cast from float to unsigned
            if (dctype[0] == 'u'):
                sigval = (1 << (dcsize * 8))
                valmsk = (1 << (dcsize * 8)) - 1
                return DeepArray([(int(i) + sigval) & valmsk for i in self],
                                 ddtype)
            # cast from float to signed
            elif (dctype[0] == 'i'):
                return DeepArray([int(i) for i in self], ddtype)
            # cast from float to signed
            elif (dctype[0] == 'f'):
                return DeepArray([i for i in self], ddtype)

        raise ValueError('non supported type conversion: {} to {}'.format(
            self.dtype, ctype))
