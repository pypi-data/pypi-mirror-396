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

import pickle
import numpy
import sys



class DEEPopt(object):
    BINARY  = 0x0001
    CHUNKED = 0x0002
    ARRAY   = 0x0100
    PICKLE  = 0x0200

    OBJECTS = (ARRAY | PICKLE)



"""
Format:
     // array <shape> <dtype.name> [<dtype.descr>]
     // pickle [<protocol>]
"""

def numpybuffer_to_object(dbuffer, objinfo):
    if not objinfo:
        return dbuffer

    else:
        objdata = objinfo.split(None, 3)
        objtype = objdata[0].lower()

        if objtype == 'pickle':
            try:
                return pickle.loads(dbuffer)
            except:
                raise ValueError('Error converting pickled object {!r}'.format(objinfo))

        elif objtype == 'array':
            try:
                shape = eval(objdata[1])
                dtype = objdata[2].lower()
                if dtype.startswith('void'):
                    dtype = eval(objdata[3])

                return numpy.ndarray(shape, dtype=dtype, buffer=dbuffer)
            except:
                raise ValueError('Error converting array object {!r}'.format(objinfo))
        else:
            raise ValueError('DEEP object {!r} not recognised',format(objinfo))


# bytes is a string in Python 2 and not a valid byte array class
_byteclasses = bytearray if sys.version_info.major == 2 else (bytearray, bytes)

def object_to_numpybuffer(obj):
    if obj is None:
        return None, None

    if isinstance(obj, _byteclasses):
        dbuffer = numpy.ndarray(len(obj), dtype='uint8', buffer=obj)
        objinfo = None

    elif isinstance(obj, numpy.ndarray) and obj.flags['C_CONTIGUOUS'] == True:
        itemsize = obj.itemsize if obj.itemsize in [1, 2, 4, 8] else 1
        size = obj.nbytes // itemsize
        dbuffer = numpy.ndarray(size, dtype='uint{}'.format(8 * itemsize), buffer=obj)

        shape = str(obj.shape).replace(' ', '')
        dtype = obj.dtype.name
        if dtype.startswith('void'):
            descr = str(obj.dtype.descr)
            objinfo = 'ARRAY {} {} {}'.format(shape, dtype, descr)
        else:
            objinfo = 'ARRAY {} {}'.format(shape, dtype)

    else:  # otherwise a generic pickled object
        pkbytes = None
        for prot in [2,3,4,5]:
            try:
                pkbytes = pickle.dumps(obj, protocol=prot)
                break
            except:
                continue
        if not pkbytes:
            raise ValueError('Cannot pickle DEEP object')
        dbuffer = numpy.ndarray(len(pkbytes), dtype='uint8', buffer=pkbytes)
        objinfo = 'pickle {}'.format(prot)

    return dbuffer, objinfo



class DeepArray(numpy.ndarray):

    def __new__(cls, data, dtype=None):
        # First, a workaround to treat the anomalous case of a string or bytes used as data source
        if isinstance(data, str):
            return cls.fromstring(data, dtype)
        elif isinstance(data, bytes):
            return cls.frombytes(data, dtype)

        # if not, start by deciding which dtype to use if not specified
        if dtype is None:
            try:
                dtype = None
                dtype = data.dtype   # this works for DeepArray and NumPy instances
            except:
                itemsize = data.itemsize if hasattr(data, 'itemsize') else 1
                dtype = 'uint{}'.format(itemsize * 8)

        # Then create a numpy array with the provided data
        array = numpy.array(data, dtype=dtype)

        # Initialise the final numpy array using the first array as the base object
        self = super(DeepArray, cls).__new__(cls, array.shape, dtype=array.dtype, buffer=array)
        return self

    @classmethod
    def fromfile(cls, file_id, dtype=None, byteorder="little"):
        if isinstance(file_id, str):
            with open(file_id, "rb") as f:
                databytes = f.read()
        else:
            databytes = file_id.read()

        return cls.frombytes(bytearray(databytes), dtype=dtype, byteorder=byteorder)

    @classmethod
    def fromstring(cls, datastr, dtype=None, byteorder="little"):
        return cls.frombytes(datastr.encode(), dtype, byteorder)

    @classmethod
    def frombytes(cls, databytes, dtype=None, byteorder="little"):
        darr = cls(bytearray(databytes), dtype=dtype)
        if byteorder != sys.byteorder:
            darr.byteswap()
        return darr