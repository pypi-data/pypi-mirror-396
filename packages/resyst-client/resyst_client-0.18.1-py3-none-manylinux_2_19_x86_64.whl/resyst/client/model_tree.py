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
from typing import Union

import numpy as np

from resyst.libdeep import DanceDevice


DataTypes = Union[int, float, str, bool, np.ndarray]

class Signal:
    """Signal object retrieved from model Tree object. It contains data
    information and access to its value if target application is
    currently the one running on the Simulink RT device.

    Note: Class constructor is for inner use.
    """

    def __init__(
            self, path: str, dtype: str, ctype: str, shape: tuple[int],
            variable_name: str, description:str, device: DanceDevice):
        # Path of the signal
        self._path = path

        # Data type read from generated C files
        self._dtype = dtype

        # Data type from ctypes Python module
        self._ctype = ctype

        # Shape of the signal value
        self._shape = shape

        # C code variable name
        self._variable_name = variable_name

        # Signal Documentation description
        self._description = description

        # Communication device
        self._device = device
    
    @property
    def path(self) -> str:
        """Path of the signal.
        """
        return self._path
    
    @property
    def dtype(self) -> str:
        """Data type read from generated C files.
        """
        return self._dtype
    
    @property
    def ctype(self) -> str:
        """Data type from ctypes Python module.
        """
        return self._ctype
    
    @property
    def shape(self) -> tuple[int]:
        """Shape of the signal value.
        """
        return self._shape
    
    @property
    def variable_name(self) -> str:
        """C code variable name."""
        return self._variable_name
    
    @property
    def description(self) -> str:
        """Signal Documentation description."""
        return self._description
    
    @property
    def value(self) -> Union[DataTypes, None]:
        """If generated from running application model tree, Get signal
        value by issuing a call to DAnCE controller else return None.
        """
        if not self._device: return None
        if self.ctype is None: return None

        cmd = f'?*MODELVAL SIGNAL "{self.path}"'
        _, value = self._device.ackcommand(cmd)
        return value

class Param(Signal):
    """Param object retrieved from model Tree object. It contains data
    information and access and update to its value if target application
    is currently the one running on the Simulink RT device.
    Param class inherits from Signal class and adds setter for
    value property for setting parameter value.

    Note: Class constructor is for inner use.
    """

    @property
    def value(self) -> Union[DataTypes, None]:
        """If generated from running application model tree, Get/Set
        parameter value by issuing a call to DAnCE controller else
        return None.
        """
        if not self._device: return None
        if self.ctype is None: return None

        cmd = f'?*MODELVAL PARAM "{self.path}"'
        _, value = self._device.ackcommand(cmd)
        return value

    @value.setter
    def value(self, value: DataTypes):
        if not self._device: return
        if self.ctype is None: return

        cmd = f'*MODELPAR "{self.path}"'
        self._device.ackcommand(cmd, bindata=value)

@dataclass(frozen=True)
class System:
    """Model Tree System object retrieved from model Tree object. It
    contains ist Simulink path, its own subsystems, params and
    signals.

    Note: Class constructor is for inner use.
    
    Attributes:
        path (str): Simulink model path to this system.
        subsystems (list[System]): List of subsystem of this system.
        params (list[Param]): List of params of this system.
        signals (list[Signal]): List of signals of this system.
    """

    # Path of the model subsystem
    path: str
    
    # Model subsystems of this subsystem
    subsystems: list['System']

    # Model subsystems parameters
    params: list[Param]
    
    # Model subsystems signals
    signals: list[Signal]

@dataclass(frozen=True)
class Tree:
    """Simulink model tree for exploring subsystems, signals and params.

    Note: Class constructor is for inner use.
    
    Attributes:
        root_system (System): Root system from which one can recursively
            explore subsystems, signals and params.
        params (list[Param]): Flat dictionary of all params indexed by
            their path.
        signals (list[Signal]): Flat dictionary of all signals indexed
            by their path.
    """
    # Model root system
    root_system: System

    # Flat list of model parameters
    params: dict[str, Param]
    
    # Flat list of model signals
    signals: dict[str, Signal]
