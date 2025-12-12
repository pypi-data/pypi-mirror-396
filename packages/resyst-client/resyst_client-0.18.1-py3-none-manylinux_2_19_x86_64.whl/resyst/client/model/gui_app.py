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

import argparse
import sys

from resyst.client.system import System
from resyst.client.program import ProgramLocation
from resyst.client.model.gui import Gui


def main():
    parser=argparse.ArgumentParser(
        description='GUI application to display SLRT model tree from'
        ' DAnCE server controlling a Simulink RT device',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('ip_address', type=str,
                        help='IP address of DAnCE server controlling'
                        ' Simulink RT device')

    parser.add_argument('-p', '--prog-name', type=str, default='',
                        help='Name of the program from which display'
                        ' model tree, empty meaning running program')

    parser.add_argument('-l', '--location', type=str,
                        choices=['STORED', 'LOADED'], default='LOADED',
                        help='Location of program')

    parser.add_argument('--port', type=int, default=5000,
                        help='Port of DAnCE server')
                        
    args = parser.parse_args()

    ip_address: str = args.ip_address
    prog_name: str = args.prog_name
    location: ProgramLocation = args.location
    port: int = args.port

    system = System.create(f'{ip_address}:{port}')

    if prog_name == '':
        program = system.running_program
        if program is None:
            sys.exit('No running program, specify one with -p option.')
        title = f'SL Model view (RUNNING {program.hash})'
    else:
        if location == ProgramLocation.STORED.value:
            programs = system.stored_programs
        elif location == ProgramLocation.LOADED.value:
            programs = system.loaded_programs
        program = next(
            (x for x in programs if x.name == prog_name), None)
        title = f'SL Model view ({program.location.value} {program.hash})'

    # Create GUI from model tree and start it
    gui = Gui(program.tree, title)
    app = gui.create_gui()
    app.mainloop()

if __name__ == '__main__':
    main()