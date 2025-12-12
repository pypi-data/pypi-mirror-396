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

"""Handle communication with any DEEP based instruments"""

from __future__  import absolute_import, print_function

import sys
from itertools import cycle

from . import deepobject
from . import clibdeep

from .clibdeep import (DevPars, CmdInfo, EventFD)
from .clibdeep import (DeepError, DeepSysError, DeepDeviceError, DeepCommError, DeepCmdError)


if 'unicode' in __builtins__:
    #print('Python 2')
    exec('def _deeperror(ex): deeperror = ex.clean(); raise deeperror', locals())
else:
    #print('Python 3')
    exec('def _deeperror(ex): deeperror = ex.clean(); raise deeperror from None', locals())


def _badkeyword_exception(func, kwd):
    return TypeError('{}() got an unexpected keyword argument \'{}\''.format(func, kwd))


# Device generic commands
COMM_ALIVE_CMD    = "?APPNAME"
COMM_ALIVE_ICECMD = "?_SOCKPING"
DSTREAMS_QCMD     = "?DSTREAM"
DSTREAMS_CMD      = "DSTREAM"
DSTREAMS_ICEQCMD  = "?REPORT"
DSTREAMS_ICECMD   = "REPORT"



class DeepCommandInfo(object):
    _filedescr = None

    def __init__(self, useselect=False):
        self.cmdinfo = CmdInfo()
        if useselect:
            self._evfd = EventFD()
            self._evfd.add_evsource(self.cmdinfo)
        else:
            self._evfd = None

    def fileno(self):
        if self._evfd:
            return self._evfd.fileno()
        else:
            raise IOError

    def completeselect(self):
        evsource = self._evfd.get_evsource()
        if evsource != self.cmdinfo._evsrc_ptr:
            raise IOError

    @property
    def done(self):
        return self.cmdinfo.done


class DeepDevice(object):
    class _DeepOperMode(str): pass

    DANCEMODE    = _DeepOperMode("DANCE")
    PREDANCEMODE = _DeepOperMode("PREDANCE")
    ICEPAPMODE   = _DeepOperMode("ICEPAP")
    LEGACYMODE   = _DeepOperMode("LEGACY")

    _devfamily = DANCEMODE
    _devhandle = None
    _helpquery = "?HELP ALL"
    _debuglevel = 0
    _commands = None
    _commandinfo = None
    _deepoptions = 0

    _devparam_names = ['timeoutms', 'reconnect', 'tcpport', 'usechecksum', 'deepoptions']
    _libparam_names = ['debuglevel', 'debugtags', 'maxthreads', 'maxdevices'] + _devparam_names
    _devparam_names += ['servertype']


    def __init__(self, dev_id, mode=None, debuglevel=None, timeout=None, threaded=None, devneedslock=False, usegevent=None, **kwargs):
        """
        Object initialization
        """
        if mode:
            if not isinstance(mode, _DeepOperMode):
                raise ValueError("Bad DeepDevice operation mode in 'mode' keyword")
            self._devfamily = mode

        # update global level of debug if passed as keyword argument
        dbglevel = debuglevel if debuglevel is not None else self.libparam("debuglevel")
        self.libparam("debuglevel", dbglevel)

        # process timeout value if passed as keyword argument
        if timeout is not None and timeout > 0:
            kwargs['timeoutms'] = int(1000 * timeout)
        kwargs.setdefault('usechecksum', False)

        try:
            # initialise with empty command list
            self._select = None

            explicit_threaded = threaded is not None
            self._threaded = bool(threaded)

            lockfunct = None

            # decide whether or not to use gevent
            if usegevent is True or usegevent is None and 'gevent' in sys.modules:
                try:
                    import gevent
                    # check first RLock (before select) to deal with old versions
                    if devneedslock and not explicit_nothreaded:
                        lockfunct = gevent.lock.RLock
                    self._select = gevent.select.select
                    # once all went fine (no exceptions), force thread mode to True
                    #   if was not explicitely set
                    if not explicit_threaded:
                        self._threaded = True
                except:
                    if usegevent is True:
                        raise ImportError('gevent module is not available or not the right version')

            if self._select is None: # if the gevent mechanism was not adopted...
                import select
                self._select = select.select
                # this is to check if gevent monkey-patched select.select and to revert it
                if 'gevent' in self._select.__module__:
                    import gevent
                    self._select = gevent.select._original_select
                """
                class DummyLock(object):
                    def __enter__(self): pass
                    def __exit__(self, *exc):  pass
                lockfunct = DummyLock
                """
                if devneedslock:
                    import threading
                    lockfunct = threading.Lock

            # instantiate the lock object if needed
            self._commlock = lockfunct() if self._threaded and devneedslock else None


            # load the parameters in a dictionary to initialise the device/lib
            devparams = dict(DEVFAMILY = str(self._devfamily))
            for parname, value in kwargs.items():
                if parname in self._devparam_names:
                    devparams[parname] = value
                elif parname in self._libparam_names:
                    self.libparam(parname, value)
                else:
                    raise _badkeyword_exception(self.__class__.__name__, parname)

            pars = DevPars(**devparams)
            self._devhandle = clibdeep.deepdev_devinit(dev_id, pars._pars_ptr)

            self._commandinfo = self._newcommandinfo()
            # and update command list and deep options
            self.getcommandlist()
            self._deepoptions = self.devparam('deepoptions')

        except DeepError as ex:
            _deeperror(ex)


    def __del__(self):
        if clibdeep:
            if clibdeep._global_debug: print("Destroying", self.__class__.__name__)
            if clibdeep._is_alive and self._devhandle:
                if clibdeep._global_debug: print("Close and free device handle:", hex(self._devhandle))
                clibdeep.deepdev_close(self._devhandle)


    @staticmethod
    def show_libdeep_internals():
        # passing None (NULL) the function dumps its internal state
        clibdeep.deepdev_free(None)


    def name(self):
        return clibdeep.deepdev_getparam("devname", self._devhandle)


    @staticmethod
    def libparam(param=None, value=None, _handle=None):
        '''
        Manages (sets/returns) the common library parameters
        '''
        paramlist = DeepDevice._libparam_names if _handle is None else DeepDevice._devparam_names
        if param is None:
            return {param : clibdeep.deepdev_getparam(param, _handle) for param in paramlist}
        else:
            if param not in paramlist:
                raise ValueError("'{}' is not a valid libdeep parameter".format(param))

            if value is not None:
                clibdeep.deepdev_setparam(param, value, _handle)
            value = clibdeep.deepdev_getparam(param, _handle)

            if param == 'debuglevel':
                global _global_debug
                _global_debug = (value > 0)

            return value


    def devparam(self, param=None, value=None):
        '''
        Manages (sets/returns) the device parameters
        '''
        return self.libparam(param, value, _handle=self._devhandle)


    @staticmethod
    def debug(level=None, tags=None):
        dbglevel = level if level is not None else DeepDevice.libparam('debuglevel')

        if tags is None:
            dbgtags = DeepDevice.libparam('debugtags')
        else:
            if type(tags) is str:    # if tags is a string
                tags = {t for t in tags.split()}
            else:                    # if tags is a container of strings
                tags = {t for s in tags for t in s.split()}
            dbgtags = ' '.join(tags)

        dbglevel = DeepDevice.libparam('debuglevel', dbglevel)
        dbgtags = DeepDevice.libparam('debugtags', dbgtags)

        return dbglevel, dbgtags


    def timeout(self, timeout=None):
        timeout_ms = int(1000 * timeout) if timeout else None
        return self.devparam('timeoutms', timeout_ms) / 1000.


    def reconnect(self, reconnect=None):
        return bool(self.devparam('reconnect', reconnect))


    def getcommandlist(self, force=False):
        """
        Returns the list of commands supported by the instrument
        """
        if force or self._commands is None:
            answ = self.command(self._helpquery).splitlines()
            if self._devfamily is DeepDevice.ICEPAPMODE:
                self._commands = [s for line in answ for s in line.split()]
            else:
                self._commands = [s.split(":")[0].strip() for s in answ if s.rfind(":") >= 0]

        return self._commands


    def isvalidcommand(self, cmdstr):
        """
        Returns True if the given command/query keyword in cmdstr is supported by the instrument
        """
        curr_commands = self.getcommandlist()
        return cmdstr.split()[0].upper() in curr_commands


    def getinfo(self):
        """
        Returns a dictionary with information about the communication settings
        """
        info = {}
        info['name'] = self.name()
        info['devfamily'] = self._devfamily
        info['commandlock'] = bool(self._commlock)
        info['threaded'] = self._threaded
        info['usegevent'] = (self._select and 'gevent' in self._select.__module__)
        info['useselect'] = bool(self._select)
        info.update(self.libparam())
        info.update(self.devparam())
        return info


    def _newcommandinfo(self):
        """
        Returns a new DeepCommandInfo instance to be used by a DeepDevice object
        for subsequent issuing of commands
        """
        return DeepCommandInfo(self._select is not None)


    def check_cmd(self, comminfo, wait=False):
        """
        Checks the completion state of the command monitored by the DeepCommandInfo
        instance comminfo and updates and returns the 'done' attribute.
        """
        clibdeep.deepdev_checkcommand(comminfo.cmdinfo, wait)
        return comminfo.done


    def wait_cmd(self, comminfo):
        """
        Waits the completion of the command monitored by the DeepCommandInfo instance
        comminfo and returns True.
        """
        if comminfo.done: return True

        if self._select:  # actually, in the current version select is always used
            self._select([comminfo], [], [])
            comminfo.completeselect()

        return self.check_cmd(comminfo, wait=True)


    def _command_answer(self, comminfo):
        """
        Returns the answer of the command monitored by the DeepCommandInfo instance
        comminfo as a tuple (answer, deepobject) according to the type of query.
        """
        parsefns = comminfo.parsefns

        self.wait_cmd(comminfo)

        answ, retobj = comminfo.cmdinfo.fullanswer
        comminfo.cmdinfo.fullanswer = None  # to reduce references to data

        if answ and parsefns:
            try:
                answ = parsefns(answ)
            except TypeError:
                answ = self._parse_string(parsefns, answ)

        if comminfo.cmdinfo.isquery and comminfo.cmdinfo.isbinary:
            return answ, retobj
        else:
            return answ


    def _command_compose(self, comminfo, cmdstr, *args, **kwargs):
        """
        Initialises and sends a command or query to the instrument.
        Returns the DeepCommandInfo instance that must be used to
        monitor the progress and the result of the command with
        the 'done' attribute updated.
        """

        # minimum command check
        cmdline = cmdstr.strip()
        if cmdline.startswith(('?*', '#?*')) or ':?*' in cmdline:
            isquery, isbinary = True, True
        elif cmdline.startswith(('*', '#*')) or ':*' in cmdline:
            isquery, isbinary = False, True
        elif cmdline.startswith(('?', '#?')) or ':?' in cmdline:
            isquery, isbinary = True, False
        else:
            isquery, isbinary = False, False

        # check specifically bindata (this is tricky)
        bindatanotset = 'bindata' not in kwargs
        bindata  = kwargs.pop('bindata', None)
        # if a binary command, binary argument may be optionally passed as the last one
        if isbinary and not isquery and bindatanotset:
            try:
                # TODO: the following line should be replaced simply by:
                # args, bindata = args[:-1], args[-1]
                if type(args[-1]) is not str: args, bindata = args[:-1], args[-1]
            except:
                pass

        # extract other keyword arguments: addr, ack, parsefns
        parsefns = kwargs.pop('parsefns', None)
        ack      = bool(kwargs.pop('ack', False))
        addr     = kwargs.pop('addr', None)
        if addr:
            addr = str(addr)  # in case it is a numeric value

        if kwargs:
            raise _badkeyword_exception('command', next(iter(kwargs)))

        # join all args in a single string (excluding 'None')
        args_cmd = ' '.join([str(a).strip() for a in args if a is not None])
        if args_cmd:
            cmdline += ' ' + args_cmd

        if not comminfo:
            comminfo = self._newcommandinfo()

        comminfo.cmdinfo.isquery = isquery
        comminfo.cmdinfo.isbinary = isbinary
        comminfo.parsefns = parsefns

        #print('<{}> bindata={} addr={} ack={}'.format(cmdline, bindata, addr, ack))
        clibdeep.deepdev_startcommand(comminfo.cmdinfo, self, addr, cmdline, ack, bindata)

        return comminfo


    def command(self, cmdstr, *args, **kwargs):
        try:
            if self._commlock:
                with self._commlock:
                    self._command_compose(self._commandinfo, cmdstr, *args, **kwargs)
                    fullanswer = self._command_answer(self._commandinfo)
            else:
                if self._threaded:
                    comminfo = self._command_compose(None, cmdstr, *args, **kwargs)
                    fullanswer = self._command_answer(comminfo)
                else:
                    self._command_compose(self._commandinfo, cmdstr, *args, **kwargs)
                    fullanswer = self._command_answer(self._commandinfo)
            return fullanswer

        except DeepError as ex:
            _deeperror(ex)

        except KeyboardInterrupt:
            # if interrupted, reinstantiate commandifo to use a fresh one next time
            self._commandinfo = self._newcommandinfo()
            # and re-raise the KeyboardInterrupt
            raise KeyboardInterrupt


    def ackcommand(self, cmdstr, *args, **kwargs):
        """
        Send a command/query to the instrument with acknowledge request
        """
        kwargs['ack'] = True
        try:
            return self.command(cmdstr, *args, **kwargs)
        except DeepError as ex:
            _deeperror(ex)


    def commsequence(self, cmdseq, cmdstr, *args, **kwargs):
        try:
            if not cmdseq: cmdseq = []
            if cmdstr:
                cmdseq.append(self._command_compose(None, cmdstr, *args, **kwargs))
                return cmdseq
            else:
                answers = []
                for comminfo in cmdseq: answers.append(self._command_answer(comminfo))
                return answers

        except DeepError as ex:
            _deeperror(ex)


    def get_parser(self, fmtstring=None, **kwargs):
        try:
            proxy = self._parserproxy
        except:
            from .dparser import DParserProxy
            proxy = self._parserproxy = DParserProxy(**kwargs)

        return proxy.parser(fmtstring) if fmtstring else None


    def query(self, fmtstring, devquery, *args, **kwargs):
        parser = self.get_parser(fmtstring)
        try:
            return self.command(devquery, *args, parsefns=parser, **kwargs)
        except DeepError as ex:
            _deeperror(ex)


    def getanswer(self, parsefns, devquery, *args, **kwargs):
        try:
            return self.parsedquery(parsefns, devquery, *args, **kwargs)
        except DeepError as ex:
            _deeperror(ex)

    get_answer = getanswer  # for backwards compatibility...


    def parsedquery(self, parsefns, devquery, *args, **kwargs):
        """
        Returns the ASCII answer from the device to a given query converted
        into a tuple of values, each element of the tuple having been parsed
        accordingly to the argument parsefns. If the query also returns a binary
        block, the method returns in addition the DeepArray containing the
        binary data. In general, parsefns is either a function or a sequence of
        functions that is used to extract from the device ASCII answer the
        elements included in the returned tuple. If needed, the sequence of
        conversion or parsing functions in parsefns is repeated cyclically until
        all the elements in the device answer are extracted. The most frequently
        used are the conversion functions for the built-in types int, float
        and str, but the method accepts also any user provided parsing function
        as well as certain objects that select special conversions as described
        below. In general the built-in conversions parse and extract a string
        token separated by whitespaces in the answer string and converts them
        to the corresponding type. However, for string conversion, the method
        also manages single or double quoted strings in the device answer that
        are treated and returned as full strings regardless of whether or not
        they include whitespaces. The built-in integer conversion is also
        extended to accept C-format hexadecimal strings.

        User provided parsing functions must parse an input string and extract
        a single element at each call. The functions must return a two-value
        tuple consisting of the extracted element, that can be an object of any
        arbitrary type, and the remaining string still to be parsed. If the
        extracted element returned by the user function is None, the element
        is ignored and not included in the final sequence. This feature may be
        used to manipulate the ASCII string at a given point of the parsing
        sequence without generation of output values.

        Optionally the conversion functions may be replaced with predefined
        strings that select special built-in parsing operations. Currenly the
        following special parsing operations are implemented:

        - 'auto' - the method tries and converts automatically the next token
                   into one of the built-in types int, float or str.
        - 'tail' - the method treats and extracts as a single string all the
                   remaining characters pending to parse. This is always the
                   last element returned by the method.
        - 'skip' - the method discards the next token in the string to parse.

        :param  parsefns: the conversion/parsing function or the list or tuple
                         of conversion/parsing functions that is used by the
                         method. The strings 'auto', 'tail' and 'skip' may be
                         used instead of a function to indicate special parsing
                         operations.
        :param  devquery: The query string to be sent to the device followed by
                          any additional required arguments.
        :raises DeepDeviceError: If the query is not properly executed in the
                             device.
        :raises IOError: If there is any communication error.
        :raises ValueError: If devquery is not a query or if the answer from
                            the device is not compatible with the conversion
                            scheme described by parsefns.
        """
        return self.command(devquery, *args, parsefns=parsefns, **kwargs)


    @staticmethod
    def _string_extract(type_fn, str_value):
        if type_fn in (int, float, str):
            if not str_value:
               if type_fn == str:
                   return None, None
               else:
                   msg = "empty string cannot be converted to " + repr(type_fn)
                   raise ValueError(msg)

            elif type_fn == str and str_value[0] in "\"\'":
               idx = str_value[1:].find(str_value[0])
               if idx >= 0:
                   return str_value[1:1+idx], str_value[2+idx:].strip()
               else:
                   return str_value[1:].strip(), None

            else:
               strsplit = str_value.split(None, 1)
               str_token = strsplit[0]
               str_remain = strsplit[1] if len(strsplit) == 2 else None

               if type_fn == int and str_token[0:2].lower() == '0x':
                   # convert C-type hexadecimal values
                   return int(str_token, base=16), str_remain
               else:
                   return type_fn(str_token), str_remain

        elif type_fn:
            # used define parsing function
            return type_fn(str_value)

        else:
            # type_fn == None
            try:
                return self._string_extract(int, str_value)
            except ValueError:
                try:
                    return self._string_extract(float, str_value)
                except ValueError:
                    return self._string_extract(str, str_value)


    @staticmethod
    def _parse_string(parsefns, answ):
        """
        Parses an input string and extracts values by the same method used in
        parse_answer(). Returns the input string converted into a tuple of
        values, each element of the tuple having been parsed accordingly to
        the argument parsefns.

        :param  parsefns: the conversion/parsing function or the list or tuple
                          of conversion/parsing functions that is used by the
                          method. The strings 'auto', 'tail' and 'skip' may be
                          used instead of a function to indicate special parsing
                          operations.
        :param  answ: The string to be parsed.
        :raises ValueError: If the input string is not compatible with the
                            conversion scheme described by convfs.
        """
        str_remain = answ.strip()
        vtuple = ()

        if isinstance(parsefns, (list, tuple)):
            single = False
            fn_iterator = cycle(list(parsefns))
        else:
            single = True
            fn_iterator = cycle([parsefns])

        for type_fn in fn_iterator:
            if str_remain == None:
                break

            if (type(type_fn) is str):
                if type_fn == 'auto':
                    # None requests automatic parsing in _string_extract()
                    type_fn = None
                elif type_fn == 'tail':
                    vtuple += (str_remain,)
                    break
                elif type_fn == 'skip':
                    # No try block here: parsing strings should never
                    # raise exceptions...
                    value, str_remain = self._string_extract(str, str_remain)
                    continue
                else:
                    msg = "string '%s' is not a valid special " % type_fn
                    msg += "parsing selector"
                    raise ValueError(msg)
            try:
                value, str_remain = self._string_extract(type_fn, str_remain)
            except ValueError as ex:
                raise ValueError(str(ex) + " from string: '" + answ + "'")

            if value != None:
                vtuple += (value,)

        return vtuple if len(vtuple) > 1 or not single else vtuple[0]


    def _get_instrument_info(self):
        """
        Returns a dictionary of relevant info on instrument firmware
        """
        if self._devfamily is DeepDevice.ICEPAPMODE:
            # for IcePAP systems
            cmd_list = ["?_DRVVER", "?VER"]
        else:
            # for old and new DAnCE systems
            cmd_list = ["?APPNAME", "?VERSION"]

        return {cmd:self.command(cmd) for cmd in cmd_list}


    def isalive(self):
        """
        Checks if the instrument is reachable and returns True/false accordingly
        """

        # try a generic command
        if self._devfamily is DeepDevice.ICEPAPMODE:
            cmd = COMM_ALIVE_ICECMD
        else:
            cmd = COMM_ALIVE_CMD

        # requesting a command will force a try to reconnect to
        # the instrument if it was currently disconnected
        try:
            self.command(cmd)
        except:
            return False
        else:
            return True


    def datastream(self, stream_id, **kwargs):
        """
        Returns a DataStream object
        The stream id is in principle a string
        """
        return DataStream(self, stream_id, **kwargs)


    def datareceiver(self, stream, buffer, **kwargs):
        """
        Returns a DataReceiver object corresponding to the given stream.
        The stream can be either a stream id or a DataStream instance.
        """

        if not isinstance(stream, DataStream):
            ds = DataStream(self, stream)
        else:
            ds = stream

        return DataReceiver(ds, buffer, **kwargs)


    # for backwards compatibility only
    def close(self):
        pass



class LegacyDevice(DeepDevice):
    _devfamily = DeepDevice.LEGACYMODE
    _helpquery = "?HELP"


class IcepapDevice(DeepDevice):
    _devfamily = DeepDevice.ICEPAPMODE
    _helpquery = "?HELP"


class OldDanceDevice(DeepDevice):
    _devfamily = DeepDevice.PREDANCEMODE
    _helpquery = "?HELP"


class DanceDevice(DeepDevice):
    _helpquery = "?HELP ALL"

    def dconfig(self):
        """
        Fetches the DAnCE configuration from the device by issuing a ?DCONFIG
        query and creates a associated DConfig object.

        :returns: a DConfig instance containing the current device
                  configuration.
        :raises DeepDeviceError: If the ?DCONFIG query is not properly implemented
                             in the DAnCE device.
        :raises ValueError: If the answer from the DAnCE device is badly
                            formatted.
        :raises IOError: If there is any communication error.
        """
        from .dconfig import DConfig

        return DConfig(self)


    def upload_dconfig(self, dconfig):
        """
        Uploads the configuration contained in a DConfig object into the
        DAnCE device.

        :param  dconfig: The DConfig instance containing the DAnCE configuration
        :raises IOError: If there is any communication error.
        :raises DeepDeviceError: If the DAnCE device does not accept the
                             configuration contained in dconfig.
        """
        dconfig.write(self)
