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

from enum import Enum
import re
from typing import Union

from resyst.libdeep import DanceDevice, DeepCmdError

from resyst.client.model_tree import Tree, System, Param, Signal
from resyst.client.acq import Acq


class ProgramLocation(Enum):
    """Enumeration for program location.
    
    Attributes:
        STORED (str): Program is store on the DAnCE server.
        LOADED (str): Program is loaded on the controlled SLRT
            device and ready to run.
    """
    STORED  = 'STORED'
    LOADED  = 'LOADED'

class Program:
    """Program object for monitoring, model exploration and acquisition
    management.
    
    Note: Class constructor is for inner use.
    """

    def __init__(self, name: str, location: ProgramLocation,
                 device: DanceDevice, is_running: bool=False):
        """Initialise a program object

        Args:
            name (str): Name of the program
            device (DanceDevice): DanceDevice object for communication
        """
        # Name of the program
        self._name = name
        
        # Location of the program
        self._location = location

        # Device for communication
        self._device = device

        # Tell if is running
        self._is_running = is_running

        # Cached tree object
        self._tree: Tree = None

    @property
    def name(self):
        """Name of the program, typically, name of the package file
        ``<prog_name>.mldatx``.
        """
        return self._name
    
    @property
    def location(self):
        """Location of the program either stored (on DAnCE server) or
        loaded (on Simulink RT device)
        """
        return self._location
    
    @property
    def is_running(self) -> bool:
        """Tell if this program is running.
        """
        return self._is_running
    
    @property
    def hash(self) -> bool:
        """Compute and return md5 hash of the file for comparison.
        """
        cmd = f'?SYSPACK {self._location.value} HASH {self._name}'
        return self._device.ackcommand(cmd)

    @property
    def tree(self) -> Tree:
        """Load this program model tree from DAnCE controller and
        generated adapted object.
        """

        if self._tree is None:
            self._tree = self._get_tree()

        return self._tree
    
    def _get_tree(self) -> Tree:
        """Effectively retrieve tree from DAnCE server

        Returns:
            Tree: Tree object
        """
        cmd = f'?*MODELTREE {self.location.value} {self.name}'
        _, tree_dict = self._device.ackcommand(cmd)
        
        flat_params: dict[str, Signal] = {}
        flat_signals: dict[str, Param] = {}

        device = self._device if self._is_running else None

        # Build system, parameter and signals path tree
        def recursively_get_system(system: dict[str, any]):
            """Recursively get model tree from dict.
            """
            
            subsystems: list[System] = []
            for subsystem in system['subsystems']:
                subsystems.append(recursively_get_system(subsystem))

            params: list[Param] = []
            for item in system['parameters']:
                param = Param(
                    path=item['path'], dtype=item['dtype'],
                    ctype=item['ctype'], shape=item['shape'],
                    variable_name=item['variable_name'],
                    description=item['long_id'], device=device)
                params.append(param)
                flat_params[param.path] = param
            
            signals: list[Signal] = []
            for item in system['signals']:
                signal = Signal(
                    path=item['path'], dtype=item['dtype'],
                    ctype=item['ctype'], shape=item['shape'],
                    variable_name=item['variable_name'],
                    description=item['long_id'], device=device)
                signals.append(signal)
                flat_signals[signal.path] = signal

            return System(
                system['path'],
                subsystems,
                params,
                signals
            )

        root_system = recursively_get_system(tree_dict)
        return Tree(root_system, flat_params, flat_signals)

    def add_acq(self, acq: Acq) -> Acq:
        """Add acquisition by creating and configuring it on DAnCE
        controller and return the updated object.

        Args:
            acq (Acq): Acquisition to add and configure

        Returns:
            Acq: Acquisition added and configured
        """
        
        # Acquisition name shall start with a letter
        if not re.match(r'^[a-zA-Z]{1}\w*$', acq.name):
            message = 'Acquisition name shall start with a letter'
            raise DeepCmdError(message)

        # Check that signals are present in model tree
        diff_signals = list(set(acq.signal_paths).difference(
            self.tree.signals.keys()))
        if len(diff_signals) != 0:
            diff_signals.sort()
            diff_signals_str = '", "'.join(diff_signals)
            message = f'Following signals have not been found:'
            message += f' "{diff_signals_str}"'
            raise DeepCmdError(message)

        cmd = f'DAQCTRL ADD {acq.name}'
        self._device.ackcommand(cmd)

        signals_str = ' '.join([f'"{x}"' for x in acq.signal_paths])

        cmd = f'?*DAQCONF {acq.name}'
        cmd += f' SRC {signals_str} NSAMPLES {acq.nbp}'
        cmd += f' SAMPLRATE {acq.decimation}'
        if acq.filter_path is not None:
            cmd += f' FILTER "{acq.filter_path}"'
        if acq.start_path is not None:
            cmd += f' START "{acq.start_path}" {acq.start_pre_samples}'
        
        try:
            self._device.ackcommand(cmd)
        except DeepCmdError as e:
            self.remove_acq(acq.name)
            raise e

        acq._device = self._device
        return acq

    @property
    def acqs(self) -> list[Acq]:
        """List of acquisitions currently loaded on DAnCE controller.
        """
        answer = self._device.ackcommand('?*DAQCONF')
        acqs_dict: dict[str, dict[any]] = answer[1]
        acqs: list[Acq] = []
        for name, acq_dict in acqs_dict.items():
            acqs.append(Acq(
                name=name,
                signal_paths=acq_dict['signal_paths'],
                nbp=acq_dict['count'],
                decimation=acq_dict['prescaler'],
                filter_path=acq_dict.get('filter_path', None),
                start_path=acq_dict.get('start_path', None),
                start_pre_samples=acq_dict.get('start_pre_samples', 0),
                device=self._device
            ))
        return acqs

    def start_acqs(self, acqs: Union[list[Acq], list[str]]) -> None:
        """Start given acquisitions by their objects or by their names.
        They shall start simultaneously on Speedgoat device

        Args:
            acqs (list[Acq]): Acquisitions to start
        """
        if isinstance(acqs[0], Acq):
            acqs = [x.name for x in acqs]
        acq_names_str = ' '.join(acqs)
        cmd = f'DAQCTRL START {acq_names_str}'
        self._device.ackcommand(cmd)
        
    def remove_acq(self, acq_name:str) -> None:
        """Remove acquisition from DAnCE controller.

        Args:
            acq_name (str): Name of acquisition to remove
        """
        cmd = f'DAQCTRL REMOVE {acq_name}'
        self._device.ackcommand(cmd)

    def remove_all_acqs(self) -> None:
        """Remove all acquisitions from DAnCE controller.
        """
        cmd = f'DAQCTRL REMOVE ALLDAQS'
        self._device.ackcommand(cmd)
