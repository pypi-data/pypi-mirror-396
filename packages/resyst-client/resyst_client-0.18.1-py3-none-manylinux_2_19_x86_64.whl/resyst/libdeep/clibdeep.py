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

from __future__ import absolute_import, print_function, division

import os
import numpy
import atexit

try:
    import weakref   # weakref.finalize() is not available in Python 2
except:
    weakref = None

from ctypes import (cdll, c_void_p, c_char_p, c_char, c_byte, c_int, c_size_t, c_float,
                    pointer, POINTER, cast, addressof, byref,
                    Structure, Union)

#from .device import log_print
from .deepobject import DEEPopt, numpybuffer_to_object, object_to_numpybuffer

_LIBDEEP_LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libdeep.so')

libdeeplib = cdll.LoadLibrary(_LIBDEEP_LIB)



_is_alive = True
_global_debug = False

def _del_logmessage(self):
    if _global_debug: print("Destroying", self.__class__.__name__)


@atexit.register
def clibdeep_cleanup():
    if _global_debug: print("Quitting: releasing all internal libdeep resources")
    # make sure that the library is flagged unusable (global flag)
    global _is_alive
    _is_alive = False
    # close all communication and free all the library resources
    deepdev_closeall()



class DeepError(Exception):
    _error_descr = None

    def clean(self):
        return self.__class__(self.args[0])

    def __str__(self):
        return "{} ({})".format(self.args[0], self._error_descr)

class DeepSysError(DeepError):    _str_id = 'SYSERR'
class DeepDeviceError(DeepError): _str_id = 'ERR'
class DeepCommError(DeepError):   _str_id = 'COMMERR'
class DeepCmdError(DeepError):    _str_id = 'ANSERR'

_deep_error_list = (DeepSysError,
                    DeepDeviceError,
                    DeepCommError,
                    DeepCmdError)


"""
 ctypes c_char_p ASCIIZ strings are returned either
 as None (NULL), str (Python2) or bytes (Python3)
 This function allows to treat all cases and return
 only None or str
"""
def ptr_to_string(val):
    return val if val is None or type(val) is str else val.decode()

"""
def _nparray_to_pointer(array, type):
    address = array.__array_interface__['data'][0]
    return pointer(type.from_address(address))


def _extract_string_list(name):
    ptr = pointer(c_char_p.in_dll(libdeeplib, name))
    n_strings = c_int.in_dll(libdeeplib, name + "_n").value
    strlist = []
    for i in range(n_strings):
        strlist.append(ptr[i].decode())
    return strlist
"""

def _extract_errorcode_list():
    n_errcodes = c_int.in_dll(libdeeplib, "deepdev_errcodes_n").value
    name_ptr = pointer(c_char_p.in_dll(libdeeplib, "deepdev_errcodes"))
    msg_ptr = pointer(c_char_p.in_dll(libdeeplib, "deepdev_errmsgs"))
    errdict = dict()
    for i in range(n_errcodes):
        name = ptr_to_string(name_ptr[i])  # for Python3 compatibility
        for ex in _deep_error_list:
            if ex._str_id == name:
                ex._error_descr = ptr_to_string(msg_ptr[i])
                errdict[i] = ex
                break
        else:
            errdict[i] = None
    return errdict


def _struct_union_repr(obj, prefix):
    out = "struct " if isinstance(obj, Structure) else "union "
    out += repr(obj.__class__) + " at " + hex(addressof(obj))
    prefix += "    "
    for field in obj._fields_:
        out += prefix + field[0]
        element = getattr(obj, field[0])
        if isinstance(element, (Structure, Union)):
            out += " " + _struct_union_repr(element, prefix)
        else:
            try:
                element._type_
                address = c_void_p.from_buffer(element).value
                out += ": " + (hex(address) if address else "NULL")
                out += " pointer to " + repr(element._type_)
            except AttributeError:
                out += ": " + element.__repr__()
    return out


class _Structure(Structure):
    def __repr__(self):
        return _struct_union_repr(self, '\n')

    def from_param(self):
        return byref(self)


class _Union(Union):
    def __repr__(self):
        return _struct_union_repr(self, '\n')

    def from_param(self):
        return byref(self)


class _DeepError():
    OK = 0
    NOTREADY = 1
    deep_errors = _extract_errorcode_list()


deepdev_error = libdeeplib.deepdev_error
deepdev_error.argtypes = [POINTER(c_char_p)]
deepdev_error.restype = c_int

def _raise_exception():
    errmsg = c_char_p()
    errcode = deepdev_error(byref(errmsg))
    ex = _DeepError.deep_errors[errcode]
    raise ex(ptr_to_string(errmsg.value))


def _int_result_check(errcode):
    if errcode == _DeepError.OK :
        return True
    elif errcode == _DeepError.NOTREADY :
        return False
    else:
        _raise_exception()


def _deeppointer_result_check(deeppointer):
    if not deeppointer:
        _raise_exception()
    else:
        return deeppointer


def pointer_result_check(c_pointer, type=None):
    if not c_pointer:
        _raise_exception()
    elif type:
        return cast(c_pointer, POINTER(type)).contents
    else:
        return c_pointer


#   This does not work for unknown reason (bug in ctypes?):
#class deephandle_t(POINTER(Structure)): pass
#
#   This does not work for lack of storage size (empty structure):
#class devhandle_t(Structure): pass
#deephandle_t = POINTER(devhandle_t)
#
# use the following instead:
deephandle_t = c_void_p
deepcmd_t = c_void_p
deepdpars_t = c_void_p
deepobject_t = c_void_p
deepfd_t = c_void_p
deepevsrc_t = c_void_p
_deepobject_t = c_void_p
_deeppar_t = c_void_p


def dump_databuf(databuf, prompt='databuf:'):
    ptr = cast(databuf, POINTER(c_byte * 64))
    print(prompt, hex(databuf), [x for x in ptr.contents])


def build_python_buffer(bdata, cmdrelease=None):
    datasize = bdata.datasize
    dtype = 'uint{}'.format(8 * bdata.datatype)
    cbuffer = (c_byte * (bdata.datatype * datasize)).from_address(bdata.databuf)

    if not cmdrelease:
        # if memory ownership must remain external, just return a conventional ndarray buffer
        return numpy.ndarray(datasize, dtype=dtype, buffer=cbuffer)
        
    else:
        # if memory ownership has to be acquired by Python, request the external
        #   library to release the memory (not to manage it anymore)
        release_databuffer(cmdrelease._evsrc_ptr)

        # and implement a delayed free() mechanism
        if weakref:
            # register a weakref finaliser for cbuffer
            dataptr = c_void_p(bdata.databuf)
            args = (0, byref(dataptr))
            cbuffer._finalizer = weakref.finalize(cbuffer, deepdev_releasedata, *args)
            return numpy.ndarray(datasize, dtype=dtype, buffer=cbuffer)

        else:
            # if weakref is not available use __del__() in a ndarray subclass
            class LDndarray(numpy.ndarray):
                _basedataID = 0  # needed to check that it is the base array not a subarray

                def __del__(self):
                    if id(self) == self._basedataID:  # only if the original base array
                        if _global_debug: print("Destroying", self.__class__.__name__)
                        if _is_alive:
                            dataptr = c_void_p(self.ctypes.data)
                            deepdev_releasedata(0, byref(dataptr))

            npbuffer = LDndarray(datasize, dtype=dtype, buffer=cbuffer)
            npbuffer._basedataID = id(npbuffer)
            return npbuffer


class deepbindata_t(_Structure):
    _fields_ = [("databuf",  c_void_p),
                ("bufsize",  c_size_t),
                ("datatype", c_int),
                ("datasize", c_size_t),
                ("objtype",  c_char_p)]

    _dtypes = {1:"uint8", 2:"uint16", 4:"uint32", 8:"uint64"}

    def __init__(self):
        self.clear()

    def clear(self):
        self.databuf = 0
        self.bufsize = 0
        self.datatype = 1   # datatype cannot be 0
        self.datasize = 0
        self.objtype = 0
        return self

    @classmethod
    def from_python_object(cls, obj, deepopts):
        try:
            npbuffer, objinfo = object_to_numpybuffer(obj)
        except ValueError as ex:
            raise DeepCommError(ex.args[0])
        bdata = deepbindata_t()

        bdata.databuf = npbuffer.ctypes.data
        bdata.bufsize = npbuffer.nbytes
        if npbuffer.itemsize in [1, 2, 4, 8]:
            bdata.datatype = npbuffer.itemsize
            bdata.datasize = npbuffer.nbytes // npbuffer.itemsize
            if objinfo and not (deepopts & DEEPopt.OBJECTS):
                objinfo = None
        else:
            bdata.datatype = 1
            bdata.datasize = npbuffer.nbytes

        if objinfo:
            bdata.objtype = objinfo.encode()
        else:
            bdata.objtype = 0

        # a dirty way for keeping a python reference to the buffer
        #  to prevent memory reuse
        bdata._npbuffer = npbuffer
        return bdata

    def to_python_object(self, cmdrelease=None):
        if self.datasize == 0 or self.datatype == 0:
            return None

        objinfo = ptr_to_string(self.objtype) if self.objtype else None
        npbuffer = build_python_buffer(self, cmdrelease)
        try:
            obj = numpybuffer_to_object(npbuffer, objinfo)
            if isinstance(obj, numpy.ndarray) and not cmdrelease:
                return obj.copy()
            else:
                return obj

        except ValueError as ex:
            raise DeepCommError(ex.args[0])


libdeeplib.deepdev_partblinit.argtypes = [deepdpars_t]
libdeeplib.deepdev_partblinit.restype = deepdpars_t
def _partblinit(*args): return _deeppointer_result_check(libdeeplib.deepdev_partblinit(*args))


class DevPars(object):
    DEFAULT_DEVPARAMS = deepobject_t(-1)
    CURRENT_DEVPARAMS = deepobject_t(-2)
    _pars_ptr = None

    def __init__(self, default=None, **kwargs):
        self.pars = {}
        if default is None:
            defptbl = DevPars.CURRENT_DEVPARAMS
        else:
            defptbl = default._pars_ptr
        self._pars_ptr = _partblinit(defptbl)
        for par in kwargs:
            self.setparam(par, kwargs[par])

    def __del__(self):
        if _global_debug: print("Destroying", self.__class__.__name__)
        if _is_alive and self._pars_ptr: deepdev_free(self._pars_ptr)

    def setparam(self, param_name, param_value):
        deepdev_setparam(param_name, param_value, obj=self._pars_ptr)
        self.pars[param_name] = param_value


libdeeplib.deepdev_cmdinit.argtypes = []
libdeeplib.deepdev_cmdinit.restype = deepcmd_t
def deepdev_cmdinit(*args): return pointer_result_check(libdeeplib.deepdev_cmdinit(*args))

libdeeplib.deepdev_free.argtypes = [_deepobject_t]
libdeeplib.deepdev_free.restype = None
deepdev_free = libdeeplib.deepdev_free


class EventSource(object):
    _evsrc_ptr = None
    done = False

    def __del__(self):
        if _global_debug: print("Destroying", self.__class__.__name__)
        if _is_alive and self._evsrc_ptr: deepdev_free(self._evsrc_ptr)


class CmdInfo(EventSource):
    def __init__(self):
        self._evsrc_ptr = deepdev_cmdinit()
        self.answ_p = c_char_p()
        self.def_bindata = deepbindata_t()
        self.isquery = False
        self.isbinary = False

    def initialise(self, binobj, deepopt):
        self.answ_p.value = 0
        if binobj is not None:
            self.bindata = deepbindata_t.from_python_object(binobj, deepopt)
            #dump_databuf(bindata.databuf, prompt='BEFORE:')
        else:
            self.bindata = self.def_bindata.clear()

    def update_answer(self):
        if not self.isquery:
            answer, retobj = (None, None)
        else:
            answer = ptr_to_string(self.answ_p.value)
            if not self.isbinary or not self.isquery or not self.bindata.databuf:
                retobj = None
            else:
                retobj = self.bindata.to_python_object(cmdrelease=self)

        self.fullanswer = (answer, retobj)

    def from_param(self):
        return byref(self)



libdeeplib.deepdev_fdinit.argtypes = [POINTER(c_int)]
libdeeplib.deepdev_fdinit.restype = deepfd_t
def deepdev_fdinit():
    fd = c_int()
    fdinfo = pointer_result_check(libdeeplib.deepdev_fdinit(byref(fd)))
    return fdinfo, fd.value


libdeeplib.deepdev_addevsource.argtypes = [deepfd_t, deepevsrc_t, c_int]
libdeeplib.deepdev_addevsource.restype = _int_result_check
def deepdev_addevsource(eventfd, event_source, flags):
    libdeeplib.deepdev_addevsource(eventfd, event_source, flags)


libdeeplib.deepdev_evsource.argtypes = [deepfd_t]
libdeeplib.deepdev_evsource.restype = deepevsrc_t
def deepdev_evsource(fdinfo): return _deeppointer_result_check(libdeeplib.deepdev_evsource(fdinfo))


libdeeplib.deepdev_evinfo.argtypes = [deepevsrc_t, POINTER(deephandle_t),
                                      POINTER(deepcmd_t), POINTER(c_int)]
libdeeplib.deepdev_evinfo.restype = _int_result_check
def deepdev_evinfo(evsource):
    devhandle = deephandle_t()
    cmdinfo = deepcmd_t
    flags = c_int
    libdeeplib.deepdev_evinfo(evsource, byref(devhandle), byref(cmdinfo), byref(flags))
    return devhandle, cmdinfo, flags


class EventFD(object):
    _evfd_ptr = None

    def __init__(self):
        self._evfd_ptr, self.fd = deepdev_fdinit()

    def __del__(self):
        if _global_debug: print("Destroying", self.__class__.__name__)
        if _is_alive and self._evfd_ptr: deepdev_free(self._evfd_ptr)

    def fileno(self):
        return(self.fd)

    def add_evsource(self, evsource):
        deepdev_addevsource(self._evfd_ptr, evsource._evsrc_ptr, 0)

    def get_evsource(self):
        return deepdev_evsource(self._evfd_ptr)


libdeeplib.deepdev_devinit.argtypes = [c_char_p,_deeppar_t]
libdeeplib.deepdev_devinit.restype = deephandle_t
def deepdev_devinit(dev_id, dpartbl):
    dev_id = dev_id.encode()
    return _deeppointer_result_check(libdeeplib.deepdev_devinit(dev_id, dpartbl))


libdeeplib.deepdev_open.argtypes = [c_char_p]
libdeeplib.deepdev_open.restype = deephandle_t
def deepdev_open(dev_id):
    dev_id = dev_id.encode()
    return _deeppointer_result_check(libdeeplib.deepdev_open(dev_id))


libdeeplib.deepdev_close.argtypes = [deephandle_t]
libdeeplib.deepdev_close.restype = _int_result_check
deepdev_close = libdeeplib.deepdev_close


libdeeplib.deepdev_closeall.argtypes = []
libdeeplib.deepdev_closeall.restype = _int_result_check
deepdev_closeall = libdeeplib.deepdev_closeall


libdeeplib.deepdev_connect.argtypes = [deephandle_t]
libdeeplib.deepdev_connect.restype = _int_result_check
deepdev_connect = libdeeplib.deepdev_connect


libdeeplib.deepdev_disconnect.argtypes = [deephandle_t]
libdeeplib.deepdev_disconnect.restype = _int_result_check
deepdev_disconnect = libdeeplib.deepdev_disconnect



libdeeplib.deepdev_setparam.argtypes = [_deepobject_t, c_char_p, _deeppar_t]
libdeeplib.deepdev_setparam.restype = _int_result_check
def deepdev_setparam(param_name, param, obj=None):
    if obj is None: obj = DevPars.CURRENT_DEVPARAMS
    if param_name.upper() == "ERROROUTPUT":
        raise ValueError("Cannot set parameter " + param_name)
    try:
        param = byref(c_int(int(param)))
    except ValueError:
        param = c_char_p(param.encode())
    param_name = param_name.encode()
    libdeeplib.deepdev_setparam(obj, param_name, param)


libdeeplib.deepdev_getparam.argtypes = [_deepobject_t, c_char_p, POINTER(_deeppar_t)]
libdeeplib.deepdev_getparam.restype = _int_result_check
def deepdev_getparam(param_name, obj=None):
    if obj is None: obj = DevPars.CURRENT_DEVPARAMS
    param_name = param_name.upper()
    if param_name == "ERROROUTPUT":
        raise ValueError('Cannot access parameter "{}"'.format(param_name))
    param_ptr = _deeppar_t()
    libdeeplib.deepdev_getparam(obj, param_name.encode(), byref(param_ptr))
    if param_name in ("HOSTNAME", "DEVNAME", "DEBUGTAGS", "SERVERTYPE"):
        param = ptr_to_string(cast(param_ptr, c_char_p).value)
    else:
        param = cast(param_ptr, POINTER(c_int)).contents.value
    return param


libdeeplib.deepdev_parsecommand.argtypes = [POINTER(c_int), #  int   flags
                                            c_char_p,       #  char *addr
                                            c_char_p,       #  char *cmd
                                            c_int]          #  int   ack
libdeeplib.deepdev_parsecommand.restype = _int_result_check
def deepdev_parsecommand(cmd, addr=None, ack=False):
    flags = c_int()
    if addr: addr = addr.encode()
    cmd = cmd.encode()
    libdeeplib.deepdev_parsecommand(byref(flags), addr, cmd, ack)
    return int(flags)


libdeeplib.deepdev_command.argtypes = [deephandle_t,           #   deephandle_t dev
                                       c_char_p,               #   char        *addr
                                       c_char_p,               #   char        *cmd
                                       c_int,                  #   int          ack
                                       POINTER(c_char_p),      #   char       **answ
                                       POINTER(deepbindata_t)] # deepbindata_t *bobj
libdeeplib.deepdev_command.restype = _int_result_check
def deepdev_command(dev, addr, cmdstr, ack, bindat):
    if addr: addr = addr.encode()

    cmdstr = cmdstr.strip()
    binpar, outbin = None, None
    if cmdstr.startswith(('*', '#*')) or ':*' in cmdstr:
        inbin = deepbindata_t() if bindat is None else deepbindata_t.from_python_object(bindat, dev._deepoptions)
        binpar = byref(inbin)
    elif cmdstr.startswith(('?*', '#?*')) or ':?*' in cmdstr:
        outbin = deepbindata_t()
        binpar = byref(outbin)

    answ_p = c_char_p()

    libdeeplib.deepdev_command(dev._devhandle, addr, cmdstr.encode(), ack, byref(answ_p), binpar)

    answer = answ_p.value
    if answer is not None: answer = answer.decode()

    if outbin and outbin.databuf:
        bobj = outbin.to_python_object()
        return answer, bobj
    else:
        return answer


libdeeplib.deepdev_startcommand.argtypes = [deepcmd_t,     #   deepcmd_t    cmdinfo
                                            deephandle_t,  #   deephandle_t dev
                                            c_char_p,      #   char        *addr
                                            c_char_p,      #   char        *cmd
                                            c_int,         #   int          ack
                                            POINTER(c_char_p),      # char         **answ
                                            POINTER(deepbindata_t)] # deepbindata_t *bobj
libdeeplib.deepdev_startcommand.restype = _int_result_check
def deepdev_startcommand(cmdinfo, dev, addr, cmdstr, ack, bindat):
    if addr: addr = addr.encode()
    cmdstr = cmdstr.encode()
    if cmdinfo.isbinary:
        cmdinfo.initialise(bindat, dev._deepoptions)
        binpar = byref(cmdinfo.bindata)
    else:
        cmdinfo.initialise(None, None)
        binpar = None
    cmdinfo.done = libdeeplib.deepdev_startcommand(cmdinfo._evsrc_ptr,
                       dev._devhandle, addr, cmdstr, ack, byref(cmdinfo.answ_p), binpar)
    if cmdinfo.done:
        cmdinfo.update_answer()


libdeeplib.deepdev_checkcommand.argtypes = [deepcmd_t, c_int]
libdeeplib.deepdev_checkcommand.restype = _int_result_check
def deepdev_checkcommand(evsrc, wait=False):
    was_done = evsrc.done
    evsrc.done = libdeeplib.deepdev_checkcommand(evsrc._evsrc_ptr, wait)

    if evsrc.done and not was_done and isinstance(evsrc, CmdInfo):
        cmdinfo = evsrc
        cmdinfo.update_answer()

    return evsrc.done


libdeeplib.deepdev_releasedata.argtypes = [deepcmd_t, POINTER(c_void_p)]
libdeeplib.deepdev_releasedata.restype = _int_result_check
def deepdev_releasedata(cmdinfo, ptr_p):
    libdeeplib.deepdev_releasedata(cmdinfo, ptr_p)
    return


def release_databuffer(cmdinfo_ptr):
    ptr = c_void_p()
    deepdev_releasedata(cmdinfo_ptr, byref(ptr))
    return ptr
