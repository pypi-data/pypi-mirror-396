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
This module manages reading and writing of DANCE device configuration data.
The configuration data can be written either to a device or to disk.

The DConfig class parses the configuration file and delegates reading and
writing to one if its FormatHandlers. A FormatHandler takes care of reading and
writing data for a specific format

The available format handlers are:

    - DConfigTxtHandler - One ASCII file containing the configuration data
    - DConfigDirHandler - A directory with a set of files containing the
                          configuration data
    - DConfigZipHandler - A ZIP compressed version of the directory based format
    - DConfigDevHandler - For reading and writing the configuration data to a
                          DANCE Device
"""

from __future__ import absolute_import, print_function

import os
import errno

from zipfile import ZipFile, ZIP_DEFLATED


MAIN_CONFIG = 'dance.dcfg'


class DConfigEntry(object):
    """
    Represents one line containing a command
    """
    def __init__(self, cfg_line):
        super(DConfigEntry, self).__init__()
        self._cfg_line = cfg_line

    def cfgline(self):
        return self._cfg_line


class DConfigCommentEntry(DConfigEntry):
    """
    Represents a comment- or a blank line
    """
    def __init__(self, cfg_line, text, key, value):
        super(DConfigCommentEntry, self).__init__(cfg_line)
        self._text = text
        self._key = key
        self._value = value

    def info(self):
        return (self._key, self._value)

class DConfigBinEntry(DConfigEntry):
    """
    Represents a command that have binary data as arguments
    """
    def __init__(self, cfg_line, cmd, sname, data):
        """
        :param cmd_str str: The full command line
        :param cmd str: The dance command
        :param sname str: Symbolic name of binary data
        :param data bytearray: Binary data
        """
        super(DConfigBinEntry, self).__init__(cfg_line)
        self._cmd = cmd
        self._sname = sname
        self._data = data

    def data(self):
        return (self._cmd, self._sname, self._data)


class DConfigFormatHandler(object):
    """
    Format handler base class, used to implement reading and writing certain
    format.
    """
    def __init__(self):
        super(DConfigFormatHandler, self).__init__()

    def _add_extension(self, path):
        if isinstance(path, str):
            root, ext = os.path.splitext(path)

            if not ext:
                ext = self._ext()

            path = root + ext

        return path

    def _ext(self):
        return DConfig.TXT_EXTENSION

    # Abstract
    def read(source):
        """
        Reads configuration from source, where source typically is a path,
        but could also be a device, network resource or other.
        """
        pass

    # Abstract
    def read_bin(config_path, fname, retcmd):
        """
        Reads an argument that contains a binary data
        :returns: The binary data as a DeepArray or a bytearray object
        """
        pass

    def write(self, dest, entry_list):
        """
        Writes the entries in entry_list to dest, where dest typically is
        a location on disk but could also be a device, network resource
        or other. The entries in entry list are DConfigEntry classes or
        subclasses.
        """
        dest = self._add_extension(dest)
        self._write(dest, entry_list)

        for entry in entry_list:
            if isinstance(entry, DConfigBinEntry):
                cmd, fname, data = entry.data()
                self.write_bin(dest, fname, data)

    # Abstract
    def _write(self, fname, entry_list):
        """
        Used for light weight implementations compatible with the the write
        method. Complete re-implementation of write may be needed if the
        default procedure for writing in write is not suitable.
        """
        pass

    # Abstract
    def write_bin(arg):
        """
        Handles the writing of binary arguments.
        """
        pass


class DConfigDirHandler(DConfigFormatHandler):
    def __init__(self):
        super(DConfigDirHandler, self).__init__()

    def _ext(self):
        return DConfig.FMT_EXTENSIONS[DConfig.DIR]

    def create_dirs(slef, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def read(self, root_path, config = MAIN_CONFIG):
        fname = os.path.join(root_path, config)
        cmd_list = []

        with open(fname) as f:
            for line in f:
                cmd_list.append(line.strip('\n'))

        return cmd_list

    def read_bin(self, root_path, fname, retcmd, config = MAIN_CONFIG):
        cpath = os.path.join(root_path, config)

        config_root_path = os.path.dirname(cpath)
        fname = os.path.join(config_root_path, fname)
        data = bytearray()

        with open(fname, "rb") as f:
            byte = f.read(1)

            while byte:
                data.append(byte)
                byte = f.read(1)

        return data

    def _write(self, config_root_path, entry_list, config = MAIN_CONFIG):
        if config_root_path:
            self.create_dirs(config_root_path)
            fname = os.path.join(config_root_path, config)
        else:
            fname = config

        cmd_list = map(lambda e: e.cfgline(), entry_list)

        with open(fname, "w+") as f:
            buf = "\n".join(cmd_list)
            f.writelines(buf)

    def write_bin(self, config_root_path, fname, data, config = MAIN_CONFIG):
        cpath = os.path.join(config_root_path, config)
        config_root_path = os.path.dirname(cpath)
        fname = os.path.join(config_root_path, fname)

        with open(fname, "w+b") as f:
            f.write(data)


class DConfigTxtHandler(DConfigDirHandler):
    def __init__(self):
        super(DConfigTxtHandler, self).__init__()

    def _ext(self):
        return DConfig.FMT_EXTENSIONS[DConfig.TXT]

    def read(self, fname):
        dirname, fname = os.path.split(fname)
        cmd_list = super(DConfigTxtHandler, self).read(dirname, config = fname)
        return cmd_list

    def read_bin(self, config_path, fname, retcmd):
        self._bin_error()

    def _write(self, fname, entry_list):
        # Check if the configuration file contains binary data, we currently
        # do not support binary data in TXT based configuration files
        for entry in entry_list:
            if type(entry) is DConfigBinEntry:
                msg = "Writing binary data to TXT configuration" +\
                      "files is not supported"
                raise IOError(msg)

        dirname, fname = os.path.split(fname)
        sclass = super(DConfigTxtHandler, self)
        sclass._write(dirname, entry_list, config = fname)


class DConfigZipHandler(DConfigFormatHandler):
    def __init__(self):
        super(DConfigZipHandler, self).__init__()

    def _ext(self):
        return DConfig.FMT_EXTENSIONS[DConfig.ZIP]

    def read(self, archive_fname, fname = MAIN_CONFIG):
        cmd_list = []

        with ZipFile(archive_fname, 'r') as zf:
            # zf.read() returns either str (Python2) or bytes (Python3). This handles both.
            cmd_list = zf.read(fname).decode('utf-8').split('\n')

        return cmd_list

    def read_bin(self, archive_fname, fname, retcmd):
        data = None

        with ZipFile(archive_fname, 'r') as zf:
            data = zf.read(fname)

        return bytearray(data)

    def _write(self, archive_path, entry_list, fname = MAIN_CONFIG):
        cmd_list = map(lambda e: e.cfgline(), entry_list)

        with ZipFile(archive_path, 'w', ZIP_DEFLATED) as zf:
            buf = "\n".join(cmd_list)
            zf.writestr(fname, buf)

    def write_bin(self, archive_path, fname, data):
        with ZipFile(archive_path, 'a', ZIP_DEFLATED) as zf:
                zf.writestr(fname, data)


class DConfigDevHandler(DConfigFormatHandler):
    def __init__(self):
        super(DConfigDevHandler, self).__init__()

    def read(self, device):
        return device.ackcommand('?DCONFIG').split('\n')

    def read_bin(self, device, fname, retcmd):
        answ, data = device.ackcommand(retcmd)
        return data

    def write(self, device, entry_list):
        for entry in entry_list:
            cmd, sname, data = entry.data()
            if data:
                device.ackcommand(cmd, data)
            else:
                device.ackcommand(cmd)


class DConfig(object):
    """
    Reads the configuration at <source> getting the format from the
    extension provided it's valid. Uses the format <format> if no extension
    or an invalid extension is used. <format> is used as default format for
    the current instance and is set to:

    * DConfig.TXT if a device that have no binary data is passed as source
    * DConfig.ZIP if a device that have binary data is passed
    * Format associated to the extension of the file if source is a path

    :param source: str path or DanceDevice object to read from
    :param format int: The format for read and default format for this
                       instance on if: DConfig.ZIP, DConfig.TXT, DConfig.DIR
                       DConfig.DEV.

    :returns: None
    :raises ValueError: If the format is invalid or mismatching with the
                        extension of source.
    :raises IOError: If a binary file cant be read during parsing.
    """
    ZIP = 1
    TXT = 2
    DIR = 3
    DEV = 4

    COMMENT = '#'
    BINARY = '*'
    OVERWRITE = 'w+'

    FMT_HANDLERS = {ZIP: DConfigZipHandler(), TXT: DConfigTxtHandler(),
                    DIR: DConfigDirHandler(), DEV: DConfigDevHandler()}

    FMT_EXTENSIONS = {ZIP: '.dcfz', TXT: '.dcf', DIR: '.dcfd'}

    _DEFAULT_FMT = ZIP

    def __init__(self, source, format = None):
        self._entries = []
        self._binary_data = {}
        self._meta_data = {}
        self._read(source)

        if isinstance(source, str) and not format:
            self._format = self._format_from_ext(source)
        elif hasattr(source, 'ackcommand'):
            if self._binary_data:
                self._format = DConfig.ZIP
            else:
                self._format = DConfig.TXT
        else:
            self._format = format


    def _parse(self, path, fmt_handler):
        """
        Parses the config at path <path> using the format handler <fmt_handler>

        :param path str: The path to the configuration
        :param fmt_handler FormatHandler: A format handler
        :returns: A list with DConfigEntry objects
        :raises IOError: If a binary data file can't be read
        """
        cfg_lines = fmt_handler.read(path)
        entry_list = []

        for cfg_line in cfg_lines:
            cfg_line.strip()
            if not (cfg_line == '' or cfg_line.startswith(DConfig.COMMENT)):
                if cfg_line.startswith(DConfig.BINARY):
                    cmd, fname, retcmd = self._parse_binary(cfg_line)

                    try:
                        data = fmt_handler.read_bin(path, fname, retcmd)
                    except IOError:
                        # File does not exist
                        raise IOError("Can't read file '%s'" % fname)
                    else:
                        entry = DConfigBinEntry(cfg_line, cmd, fname, data)
                        entry_list.append(entry)
                else:
                    entry_list.append(DConfigEntry(cfg_line))
            else:
                # To handle comments and empty lines
                text, key, value = self._parse_comment(cfg_line)
                entry = DConfigCommentEntry(cfg_line, text, key, value)
                entry_list.append(entry)

        return entry_list

    def _parse_binary(self, cfg_line):
        """
        Parses a line containing binary data arguments

        :param cfg_line str: The, full config command, line to parse
        :returns: A tuple on the format (cmd, symbolic name, retcmd)
        """
        cmd, binargs = cfg_line.split('//')
        cmd = cmd.strip(' ')
        sname_sidx = binargs.find('<')
        sname_eidx = binargs.find('>')
        sname = binargs[sname_sidx+1:sname_eidx]
        retcmd = binargs[sname_eidx+1:]
        retcmd = retcmd.strip(' ')

        return cmd, sname, retcmd

    def _parse_comment(self, cfg_line):
        """
        Parses a comment line for meta data

        :returns: The tuple (comment text, key, value)
        """
        if '%' in cfg_line:
            text, key, value = cfg_line.split('%')
        else:
            text, key, value = cfg_line, None, None

        return text, key, value

    def _format_from_ext(self, source):
        """
        Get the format to use from the file extension or the type of source
        (str or device)
        """
        if hasattr(source, 'ackcommand'):
            return DConfig.DEV
        elif source.endswith(DConfig.FMT_EXTENSIONS[DConfig.ZIP]):
            return DConfig.ZIP
        elif source.endswith(DConfig.FMT_EXTENSIONS[DConfig.DIR]):
            return DConfig.DIR
        elif source.endswith(DConfig.FMT_EXTENSIONS[DConfig.TXT]):
            return DConfig.TXT

    def _ext_valid(self, source):
        """
        Checks if the extension of source is valid or if a 'valid' device object
        is passed (checks for ackcommand method)

        :returns: True if valid otherwise False
        """
        if isinstance(source, str):
            ext =  os.path.splitext(source)[1]

            if ext in DConfig.FMT_EXTENSIONS.values():
                return True

        elif hasattr(source, 'ackcommand'):
            return True

        return False

    def _read(self, path):
        """
        Reads the configuration at <path> as format <format>
        """
        if not self._ext_valid(path):
            msg = 'No format specified and the extension provided is not' +\
                  ' one of: %s' % str(DConfig.FMT_EXTENSIONS.values())
            raise ValueError(msg)

        fmt = self._format_from_ext(path)
        fmt_handler = DConfig.FMT_HANDLERS[fmt]
        self._entries = self._parse(path, fmt_handler)

        for entry in self._entries:
            if type(entry) is DConfigBinEntry:
                cmd, sname, data = entry.data()
                self._binary_data[sname] = data
            if type(entry) is DConfigCommentEntry:
                key, value = entry.info()
                if key:
                    self._meta_data[key] = value.strip()

    def write(self, path, fmt = None, overwrite = True, checkonly = False):
        """
        Write configuration to <path> with format <format> (if passed). Uses
        the format associated with the extension of the target path provided its
        a valid extension (one of: '.dcfz', '.dcf', '.dcfd'). Appends the
        correct format to the target file if an invalid extension is used and a
        (correct) format is provided. Uses the default format passed to
        __init__ if neither the extension nor the <fmt> is valid.

        :param path str: Target path

        :param fmt int: Format to use : Dconfig.ZIP, Dconfig.TXT, DConfig.DIR
                        DConfig.DEV.

        :param overwrite bool: Allow files to be overwritten (overwrite = True),
                               otherwise False.

        :param checkonly bool: Do not write or send data to disk/device, only
                               check validity of path, format and write access.

        :returns: The path, or None if writing into a DanceDevice.

        :raises ValueError: When both extension and a format is valid, but
                            mismatching.

        :raises OSError: If overwrite is False and the path already exists.
        """
            
        if fmt and self._ext_valid(path) and fmt != self._format_from_ext(path):
            # A valid extension is used but does not match the given format
            msg = 'The format given and the extension of the output file' +\
                  ' does not match'
            raise ValueError(msg)
        elif not self._ext_valid(path) and fmt:
            # The extension is not valid but a format was given, append
            # the correct format to the file name
            path += DConfig.FMT_EXTENSIONS[fmt]
        elif not self._ext_valid(path) and not fmt:
            # The extension is not valid and there was no format given,
            # Use the default format
            path += self.extension()

        fmt = self._format_from_ext(path)

        # Write if checkonly = False
        if not checkonly:
            handler = DConfig.FMT_HANDLERS[fmt]

            if not overwrite and os.path.exists(path):
                raise OSError('The file %s already exists' %path)

            handler.write(path, self._entries)

        if not isinstance(path, str):
            path = None

        return path

    def extension(self, fmt = None):
        """
        Returns the extension associated with the format <fmt> (if its not None).
        Otherwise (if nothing is passed to fmt) the default extension used by
        this  DConfig instance; one of: '.dcfz','.dcf', '.dcfd'. The default
        extension can be passed as the format keyword argument of __init__().
        The value of static variable _DEFAULT_FMT is used if nothing is passed
        to __init__()

        :param fmt int: One of DConfig.ZIP, DConfig.DIR, DConfig.TXT or None

        :returns: one of '.dcfz','.dcf', '.dcfd'
        """
        if not fmt:
            fmt = self._format
        
        return DConfig.FMT_EXTENSIONS[fmt]

    def commands(self):
        """
        :returns: All the commands and the symbolic name of any binary data
                  (if any). A list with pairs on the format (cmd, symbolic name)
        """
        result = []

        for entry in self._entries:
            if type(entry) is DConfigBinEntry:
                cmd, sname, data = entry.data()
                result.append((cmd, sname))
            elif type(entry) is DConfigEntry:
                result.append((entry.cfgline(), None))

        return result

    def cfglines(self):
        """
        :returns: A list containing all the lines of the configuration file
        """
        return map(lambda e: e.cfgline(), self._entries)

    def binary(self, sname = None):
        """
        :returns: The binary data associated with the symbolic name <sname> or
                  a list of all symbolic names if no symbolic name is passed.
        """
        if sname:
            if sname in self._binary_data:
                return self._binary_data[sname]
            else:
                msg = "The symbolic name '%s' does not exist in the " % sname +\
                      "current configuration"
                raise KeyError(msg)
        else:
            return self._binary_data.keys()

    def info(self, key = None):
        """
        :returns: The meta data for the key <key> as a str or all meta data as
                  a dict if no key is passed.
        """
        if key:
            return self._meta_data[key]
        else:
            return self._meta_data

#
# Convenience functions for reading and writing a configuration
#
def read_config(source, format = DConfig.ZIP):
    config = DConfig(source, format)
    return config.entries()


def write_config(source, dest, format = DConfig.ZIP):
    config = DConfig(source, format)
    config.write(dest, format = DConfig.ZIP)
