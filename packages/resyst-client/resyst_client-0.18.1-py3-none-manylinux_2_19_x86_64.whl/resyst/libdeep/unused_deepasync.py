# -*- coding: utf-8 -*-
#
# this file is part of libdeep project
#


"""Needed for asynchronous communication"""

# Standard modules
from datetime import datetime
import threading

# DEEP public modules
import libdeep

# DEEP private modules
from .conditions import *

# Public objects of this module
__all__ = ['DataStream', 'DataReceiver', 'DeepCondition', 'DeepEvent']


# --------------------------------------------------------------------------
#
class AsyncEvent(object):
    """
    Notes: This class is used for IcePAP async which should be ported
    to DataReceiver class

    Object creation::

        evt = AsyncEvent()

    Automatic timestamp at object creation (with usec resolution)::

        print evt.timestamp().date()
        print evt.timestamp().microsecond

    Free description::

        desc['source']  = 'icepap'
        desc['datalen'] = 123
        evt.set_desc(desc)
        pring evt.desc()
    """

    #
    #
    def __init__(self):
        self._timestamp = datetime.now()
        self._desc      = {}
        self._data      = None

    #
    #
    def timestamp(self):
        return self._timestamp

    #
    #
    def set_desc(self, desc):
        if not isinstance(desc, dict):
            raise ValueError("argin must be a dictionary")
        self._desc = desc

    #
    #
    def desc(self):
        return self._desc

    #
    #
    def set_data(self, data):
        # TODO: check on data type
        self._data = data

    #
    #
    def data(self):
        return self._data


# --------------------------------------------------------------------------
#
class DataStream(object):
    """
    Object creation::

        dd = DeepDevice(...)
        ds = DataStream(dd, stream_id)

        ds = dd.datastream(stream_id)

    Usage examples::

        ds.start()
        ds.stop()
        ds.active(False)
        print ds.active()
        print ds.active(True)
        print ds.is_statustype()
        print ds.is_datatype()
    """

    #
    #
    def __init__(self, ddevice, stream_id):

        # check stream id validity
        if stream_id not in ddevice.async_stream_ids():
            raise ValueError("invalid data stream id")

        # check instrument capabilities
        if ddevice.is_olddance():
            raise ValueError("old DAnCE instruments are not supported")

        # mandatory argins
        self.ddevice = ddevice
        self.id      = stream_id

        # TODO: status/data type not implemented in protocol
        self.stype   = None

    #
    # TODO: implement methods to retrieve protocol information on streams
    #
    def is_statustype():
        """Returns True if the stream is of type Status"""
        raise RuntimeError("not implemented yet")

    #
    #
    def is_datatype():
        """Returns True if the stream is of type Data"""
        raise RuntimeError("not implemented yet")

    #
    #
    def start(self):
        """Activate the stream"""
        self.active(True)

    #
    #
    def stop(self):
        """Stop the stream"""
        self.active(False)

    #
    #
    def active(self, action=None):
        """
        Returns True if stream is active.
        Optionaly activate or stop the stream.
        """

        # action on stream
        if action is not None:
            self.ddevice.async_stream_active(self.id, action)

        # always return the current state
        return self.ddevice.async_stream_state(self.id)


# --------------------------------------------------------------------------
#
class DataReceiver(object):
    """
    Object creation::

        ds = DataStream(...)
        db = DeepBuffer(...)
        dr = DataReceiver(ds, db)

        dd = DeepDevice(...)
        dr = dd.datareceiver(stream_id, db)

    Usage examples::

        dr.start()
        dr.stop()
        dr.active(False)
        print dr.active()
        print dr.active(True)

        ds = dr.datastream()
    """

    #
    #
    def __init__(self, stream, buffer, **kwargs):

        # minimum checks
        if not isinstance(stream, DataStream):
            raise ValueError("invalid data stream object")
        if not isinstance(buffer, libdeep.DeepBuffer):
            raise ValueError("invalid deepbuffer object")

        # mandatory argins
        self.stream = stream
        self.buffer = buffer

        # optional argins
        self._active = False
        self._autostart = kwargs.get("autostart", False)
        if self._autostart:
            self.start()

    #
    #
    def datastream(self):
        """Returns the DataStream object beeing used"""
        return self.stream

    #
    #
    def start(self):
        """Activate the data receiving"""
        self.active(True)

    #
    #
    def stop(self):
        """Stop the data receiving"""
        self.active(False)

    #
    #
    def active(self, action=None):
        """
        Returns True if data receiver is active.
        Optionaly activate or stop the receiving.
        """

        # action on receiver
        if action is True:
            # TODO: activate silently the underlying datastream or not??
            # self.stream.start()

            # inform parser thread that it has from now to fill buffer
            self.stream.ddevice.async_receiver_register(self)
            self._active = True

        elif action is False:
            # TODO: des-activate silently the underlying datastream or not??
            # self.stream.stop()

            # inform parser thread
            self.stream.ddevice.async_receiver_unregister(self)
            self._active = False

        # always return the current state
        # TODO: should consult the parser thread instead of trusting internals
        return self._active


# --------------------------------------------------------------------------
#
class ConditionDef(object):
    def __init__(self, name, desc, value=None):
        self.name  = name
        self.desc  = desc
        self.value = value

    def __str__(self):
        ret = "%s" % self.name
        if self.value:
            ret += "(%r)" % self.value
        return ret

    def __repr__(self):
        return "<Condition: %s %s>" % (self, self.desc)


BUFFER_FILLED    = ConditionDef("BUFFER_FILLED",
                                "buffer filled")

BUFFER_START     = ConditionDef("BUFFER_START",
                                "buffer filling started")

BUFFER_NBYTES    = ConditionDef("BUFFER_NBYTES",
                                "buffer filled with nbytes")

BUFFER_WRITE     = ConditionDef("BUFFER_WRITE",
                                "some data written into the buffer")

DEV_DISCONNECTED = ConditionDef("DEV_DISCONNECTED",
                                "lost connection to instrument")

DEV_COMMERROR    = ConditionDef("DEV_COMMERROR",
                                "error on instrument communication")


class DeepCondition(object):
    """
    Object creation::

        dc = DeepCondition(BUFFER_WRITE)
        BUFFER_NBYTES.value = 1024
        dc = DeepCondition(BUFFER_NBYTES)

    Usage examples::

        dc.has(BUFFER_WRITE)
        BUFFER_WRITE in dc
    """

    #
    #
    """
    def __init__(self, **kwargs):

        # Get optional initialization
        self._buf_filled      = kwargs.get("buffer_filled",     False)
        self._buf_written     = kwargs.get("buffer_written",    False)
        self._buf_start       = kwargs.get("buffer_start",      False)
        self._buf_nbytes      = kwargs.get("buffer_nbytes",     None)
        self._dev_disconnect  = kwargs.get("device_disconnect", False)
    """
    def __init__(self, *conditions):
        self.triggered = False
        self.conditions = []
        for cond in conditions:
            if not isinstance(cond, ConditionDef):
                raise ValueError("invalid condition object")
            self.conditions.append(cond)

    #
    # NOTE: method can not be named is()!!
    def has(self, *conditions):
        """
        Returns True if the object matches all the conditions given.
        The conditions could be given as a list or a DeepCondition object.
        """
        for cond in conditions:
            if isinstance(cond, DeepCondition):
                if not self.has(*cond.conditions):
                    return False
            elif cond not in self.conditions:
                return False
        return True

    #
    #
    def __contains__(self, condition):
        """
        Overload "in" operator
        """
        return condition in self.conditions

    #
    #
    def is_triggered(self):
        """Returns True if the condition occurred"""
        return self.triggered

    #
    #
    def clear(self):
        """Set the condition as non occurred"""
        self.triggered = False

    #
    #
    def trigger(self):
        """Set the condition as occurred"""
        self.triggered = True

    #
    #
    def __str__(self):
        return '+'.join(["%s" % c for c in self.conditions])


# --------------------------------------------------------------------------
#
class DeepEvent(object):
    """
    Object creation::

        db = DeepBuffer()
        dr = deepdev.datareceiver(stream_id, db)
        ev = DeepEvent(dr, BUFFER_WRITE)

        dc = DeepCondition(BUFFER_WRITE, BUFFER_FILLED)
        ev = DeepEvent(dr, dc)

    Usage examples::

        ev.wait()
        ev.wait(timeout=3)

        ev.register(my_call_back_func)
        ev.unregister(my_call_back_func)
    """

    #
    #
    def __init__(self, receiver, condition):

        # define on what object the condition will be applied
        if isinstance(receiver, DataReceiver):
            self.receiver = receiver
        elif isinstance(receiver, libdeep.DeepDevice):
            # TODO: support conditions on disconnection for instance
            raise ValueError("not implemented yet")
        else:
            raise ValueError("invalid data receiver object")

        # define the conditions wanted
        if isinstance(condition, ConditionDef):
            self.condition = DeepCondition(condition)
        elif isinstance(condition, DeepCondition):
            self.condition = condition
        else:
            raise ValueError("invalid condition object")

        # use to communicate with Parser thread
        self.thread_event = threading.Event()
        self.callbacks = []

        # for data events, the underlying buffer object need to
        # have the conditions to be able to update them when data
        # is written/read
        if isinstance(self.receiver, DataReceiver):
            self.receiver.buffer.conditions.append(self.condition)

    #
    #
    def __del__(self):

        # cleanup buffer embedded conditions
        if isinstance(self.receiver, DataReceiver):
            idx = self.receiver.buffer.conditions.index(self.condition)
            del self.receiver.buffer.conditions[idx]

    #
    #
    def wait(self, timeout=None):
        """
        Blocking call until the event or the given timeout occur.
        """
        # TODO: do only once the register fo DeepEvent object
        # pass the threading event to Parser thread
        self.thread_event.clear()
        self.receiver.stream.ddevice.async_event_register(self)

        # blocking call
        self.thread_event.wait(timeout)
        self.receiver.stream.ddevice.async_event_unregister(self)

        # detect timeout
        if self.thread_event.is_set() is False:
            raise RuntimeError("timeout waiting for async event")

    #
    #
    def register_cb(self, cb):
        """
        Register a function that will call on each event occurance
        """
        # update the list of callbacks associated with current event
        if cb not in self.callbacks:
            self.callbacks.append(cb)

        # TODO: do only once the register fo DeepEvent object
        # inform the Parser thread
        self.receiver.stream.ddevice.async_event_register_cb(self)

    #
    #
    def unregister_cb(self, cb):
        """
        Un-register the given function from callbacks
        """
        # may be called without having been previously registered
        try:
            idx = self.callbacks.index(cb)
        except ValueError:
            return

        # update the list of callbacks associated with current event
        del self.callbacks[idx]

        # inform the Parser thread
        self.receiver.stream.ddevice.async_event_unregister_cb(self)
