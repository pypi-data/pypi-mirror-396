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

from typing import Union, Optional
from dataclasses import dataclass
from packaging.version import Version

from resyst.libdeep import DanceDevice, clibdeep, DeepDeviceError

from resyst.client import _version
from resyst.client.program import Program, ProgramLocation


@dataclass(frozen=True)
class SystemInfo:
    """System information

    Attributes:
        free_memory (int): Free memory in MB.
        serial_number (str): serial number of the Real-Time device.
    """

    free_memory: int
    serial_number: str

class System:
    """Class representing the Real-Time device DAnCE controller machine
    and operating system."""

    @staticmethod
    # pragma: no cover
    def create(addr:str, timeout: Union[None, int]=None) -> 'System':
        """Create a system by internally instantiating a DanceDevice
        object for communication

        Args:
            addr (str): DAnCE device IP address with port
            timeout (int, optional): Expiration time for DAnCE device
                response in seconds. Defaults to libdeep one, i.e., 3.
                This shall be increased to about 30 seconds for stop and
                run program operation as they can last long.

        Returns:
            System: Created system
        """
        dance_device = DanceDevice(addr, timeout=timeout)
        clibdeep._global_debug = False
        system = System(dance_device)

        server_version = system.server_version
        server_version = '.'.join(server_version.split('.')[:2])
        server_version = Version(server_version)

        client_version = _version.version
        client_version = '.'.join(client_version.split('.')[:2])
        client_version = Version(client_version)
        if client_version != server_version:
            message = f'Version mismatch: server is {server_version}' \
                f' and client is {client_version}'
            raise DeepDeviceError(message)

        return system

    def __init__(self, device: DanceDevice):
        """Create a System object whose communication will be done by a
        DanceDevice object

        Args:
            device (DanceDevice): libdeep DanceDevice for
                communication
        """
        
        # Device for communication
        self._device = device
        
    @property
    def timeout(self):
        """Get DAnCE device communication timeout in seconds."""
        return float(self._device.timeout())

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """Set DAnCE device communication timeout in seconds.

        Args:
            timeout (float): timeout in seconds
        """
        self._device.timeout(timeout)

    @property
    def version(self) -> str:
        """Get this module version."""
        return _version.version
    
    @property
    def server_version(self) -> str:
        """Get DAnCE server version."""
        answer = self._device.ackcommand('?HVERSION')
        return answer
    
    @property
    def info(self) -> SystemInfo:
        """Get system information."""
        answer = self._device.ackcommand('?*SYSINFO DICT')
        sys_info_dict: dict[str, dict[Union[str, float]]] = answer[1]
        sys_info = SystemInfo(**sys_info_dict)
        return sys_info
    
    @property
    def log(self) -> str:
        """Get system log."""
        sys_log = self._device.ackcommand('?SYSLOG')
        return sys_log
    
    def _get_programs(self, location: ProgramLocation) -> list[Program]:
        """Get program list according to given location

        Args:
            location (ProgramLocation): Store or loaded

        Returns:
            list[Program]: Stored or loaded program
        """
        cmd = f'?SYSPACK {location.value}'
        program_names: str = self._device.ackcommand(cmd)
        if program_names == 'None': return []
        
        program_names = program_names.split('\n')
        return [Program(x, location, self._device) \
            for x in program_names]

    @property
    def stored_programs(self) -> list[Program]:
        """Get the list of stored program on the DAnCE controller.

        Returns:
            list[Program]: List of stored program
        """
        return self._get_programs(ProgramLocation.STORED)

    @property
    def loaded_programs(self) -> list[Program]:
        """Get the list of loaded program on Simulink RT device.

        Returns:
            list[Program]: List of loaded program
        """
        return self._get_programs(ProgramLocation.LOADED)
        
    @property
    def running_program(self) -> Optional[Program]:
        """Get current running program in the DAnCE controller if any.

        Returns:
            Program: Running program or None if none is running
        """
        prog_name: str = self._device.ackcommand('?SYSPROG RUNNING')
        if prog_name == 'None': return None
        else: return Program(
            prog_name, ProgramLocation.LOADED, self._device, True)
        
    @property
    def autostart_program(self) -> Optional[Program]:
        """Set program to start when Speedgoat device is started

        Args:
            program (Program): Program to start at Speedgoad device
                startup
        """
        prog_name: str = self._device.ackcommand('?SYSPROG AUTOSTART')
        if prog_name == 'None': return None
        else: return Program(
            prog_name, ProgramLocation.LOADED, self._device)
    
    def set_autostart_program(self, prog_name: Optional[str]):
        """Set program to start when Speedgoat device is started

        Args:
            program (Program): Program to start at Speedgoad device
                startup
        """
        if prog_name: cmd = f'SYSPROG {prog_name} AUTOSTART'
        else: cmd = f'SYSPROG AUTOSTART'
        self._device.ackcommand(cmd)

    def program_load(
            self, name: str, data: bytes = None,
            overwrite: bool = False) -> None:
        """Load a program on DAnCE controller. If data argument is
        given, it shall contain binary of .mldatx package generated by
        Simulink using dedicated script. If data is not given, this
        package shall be stored into server dedicated directory.

        Args:
            name (str): Name of the program to load
            data (bytes, optional): Blob data read from .mldatx file in
                case of uploading package. Not mandatory if package is
                already stored. Defaults to None.
            overwrite (bool, optional): Overwrite program package on
                DAnCE controller and on SLRT device if already exists.
                Defaults to False.
        """
        cmd = f'*SYSPACK {name}'
        if data:
            cmd += ' STORE'
            if overwrite: cmd += ' OVERWRITE'
        cmd += ' LOAD'
        if overwrite: cmd += ' OVERWRITE'
        self._device.ackcommand(cmd, bindata=data)
    
    def program_run(self, prog_name: str, force=False) -> None:
        """Run program by giving its name, force action, if asked, by stopping
        current running program

        Args:
            force (bool, optional): Force potentially running program to stop. Defaults to False.
        """
        cmd = f'SYSPROG {prog_name} RUN'
        if force: cmd += ' FORCE'
        self._device.ackcommand(cmd)
        
    def program_stop(self) -> None:
        """Stop running program if any

        """
        cmd = f'SYSPROG STOP'
        self._device.ackcommand(cmd)
