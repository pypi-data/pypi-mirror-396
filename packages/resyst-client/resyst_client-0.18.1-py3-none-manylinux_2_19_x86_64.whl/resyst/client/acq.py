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

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

from resyst.libdeep import DanceDevice


class AcqState(Enum):
    """Acquisition state.
    
    Attributes:
        CONFIGURED (int): Acquisition has been added and configured.
        RUNNING (int): Acquisition is currently running.
        STOP (int): Acquisition has been stopped because:
        
            - Expected number of sammples have been acquired or
            - User stopped it before completion.
        ERROR (int): An error occured during acquisition, error property
            of status shall give more information
    """
    CONFIGURED  = 0
    RUNNING     = 1
    STOP        = 2
    ERROR       = 3
    
    @classmethod
    def from_name(cls, name):
        return cls.__members__[name]

@dataclass(frozen=True)
class AcqStatus:
    """Acquisition status.
    
    Attributes:
        state (AcqState): Current state of the acquisition.
        potential_loss (bool): Tell if a potential loss has been
            detected.
        error (str): Information in case of ERROR state.
    """
    state: AcqState
    potential_loss: bool
    error: str

class Acq:
    """Acquisition object to configure, add, start, monitor, fetch data
    and stop acquisitions.

    - When a acquisition is added, a buffer is allocated for it
      before starting it and remains until it has been explicitely
      removed. There is no limit to number of samples and server shall
      return an error when trying to allocate too much memory.
      
    - ``filter_path`` and ``start_path`` are for filter sample and
      trigger keeping sample in buffer. They must be paths pointing to
      boolean signal.
      
    - When ``start_path`` option is used, buffer is filled with
      incomming data even if start has not been triggered. Once start
      is triggered, acquisition keep the given ``start_pre_samples``
      samples and keep following samples until buffer is full.

    - ``filter_path`` and ``start_path`` options can be used together.
      Notice that start can be triggered on a filter sample, this one
      won't be part of the recorded acquisition samples but following
      not filtered will.
    """

    def __init__(
        self, name: str, signal_paths: list[str], nbp: int=100000,
        decimation: int=1, filter_path: Optional[str]=None,
        start_path: Optional[str]=None, start_pre_samples: int=0,
        device: DanceDevice = None):
        # Name of the acquisition
        self._name = name

        # Signal paths from which to acquire values
        self._signal_paths = signal_paths

        # Number of samples to acquire
        self._nbp = nbp

        # Decimation of acquisition, 1 meaning get all sample
        self._decimation = decimation

        # Filter signal path for filtering samples
        self._filter_path = filter_path
        
        # Start signal path for starting keeping samples
        self._start_path = start_path
        
        # Number of already acquired sample to keep when start is
        # triggered
        self._start_pre_samples = start_pre_samples

        self._device = device

    @property
    def name(self) -> str:
        """Name of this acquisition.
        """
        return self._name
    
    @property
    def signal_paths(self) -> list[str]:
        """List of signal paths to acquire samples from.
        """
        return self._signal_paths
    
    @property
    def nbp(self) -> int:
        """Number of samples to acquire.
        """
        return self._nbp
    
    @property
    def decimation(self) -> int:
        """Acquire every X sample, X being decimation.
        """
        return self._decimation
    
    @property
    def filter_path(self) -> str:
        """Path of signal to use as a filter, True meaning keeping the
        sample, False meaning dropping it. This selection is done before
        filling the Acquisition buffer.
        """
        return self._filter_path
    
    @property
    def start_path(self) -> str:
        """Path of signal to use as a start trigger, server begins to
        keep samples when this signal is evaluated to True.
        """
        return self._start_path
    
    @property
    def start_pre_samples(self) -> int:
        """Number of already acquired sample to keep when start is
        triggered.
        """
        return self._start_pre_samples

    @property
    def status(self) -> AcqStatus:
        """Get acquisition status.
        """
        cmd = f'?*DAQSTATUS {self._name}'
        _, status_dict = self._device.ackcommand(cmd)

        status = AcqStatus(
            state=AcqState.from_name(status_dict['state']),
            potential_loss=status_dict['potential_loss'],
            error=status_dict['error']
        )

        return status
    
    @property
    def is_running(self) -> bool:
        """Helper function to check if acquisition state is RUNNING.
        """
        return self.status.state == AcqState.RUNNING

    @property
    def is_done(self) -> bool:
        """Tell if acquisition is done from the point of view of the
        DAnCE server.
        """
        cmd = f'?DAQNSAMPL {self._name} DONE'
        done_count = int(self._device.ackcommand(cmd))
        return done_count == self._nbp

    @property
    def nb_sample_to_read(self) -> int:
        """Number of sample left to read from the DAnCE server
        acquisition buffer.
        """
        cmd = f'?DAQNSAMPL {self._name} TOREAD'
        to_read_count = int(self._device.ackcommand(cmd))
        return to_read_count

    def stop(self) -> None:
        """Manually stop this acquisition.
        """
        cmd = f'DAQCTRL STOP {self._name}'
        self._device.ackcommand(cmd)

    def get_data(
        self, nsamples: Optional[int]=None,
        filter_path: Optional[str]=None) -> np.ndarray:
        """Get given ``nsamples`` samples from acquired data during this
        acquisition or all sample available if ``nsamples`` is not
        given. If available sample is lower than given one, returns
        ``None``. Result is return as a structured numpy array.
        If ``filter_path`` is given, data is filtered using filter
        signal value located by ``filter_path`` and returns filtered
        array without the data of the filter signal.

        Args:
            nsamples (int, optional): Number of sample to retrieve.
                Defaults to None meaning all samples.
            filter_path (str, optional): Signal path for filtering data
                before sending it from DAnCE server. Filtering fields is
                also removed from data.

        Returns:
            np.ndarray: structured numpy array or None of no data
                available
        """
        cmd = f'?*DAQDATA {self._name}'
        if nsamples is not None:
            cmd += f' {nsamples}'
        if filter_path is not None:
            cmd += f' FILTER "{filter_path}"'
        _, data = self._device.ackcommand(cmd)

        if data is None: return None

        # Retreived matrices are ordered in F but presented as C
        data: np.ndarray
        for field in data.dtype.fields:
            array = data[field]
            if type(array) != np.ndarray: continue
            shape = array.shape
            if len(shape[1:]) > 1:
                rshape = tuple(reversed(shape[1:]))
                array = array.reshape((shape[0], *rshape))
                axes = [0, *reversed(range(1, len(shape)))]
                array = np.transpose(array, axes)
                data[field] = array

        return data
