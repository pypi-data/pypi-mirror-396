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

import json
import tkinter as tk
from tkinter.ttk import Treeview
from typing import Optional

import numpy as np

from resyst.client.model.gui_base import GuiBase
from resyst.client.model_tree import Tree as ModelTree, System

class Gui(GuiBase):
    def __init__(self, model_tree: ModelTree, title: str='SL Model view'):
        super().__init__(title)

        # Model tree for build GUI
        self._model_tree = model_tree
        
    def _populate_model_view(self, model_view: Treeview) -> tuple[str, str]:
        """Populate tree view and return root node id and name

        Returns:
            tuple[str, str]: Root node id and name
        """

        # Define function to create tree structure from SL one, this
        # function is called recursively and update a Tree object
        def add_system_to_tree(
            tree: Treeview, parent: str, system: System) -> str:
            text = system.path.split('/')[-1]
            values = [system.path]
            node = tree.insert(parent, tk.END, text=text, values=values)
            for subsystem in system.subsystems:
                add_system_to_tree(tree, node, subsystem)
            return node

        # Populate tree
        model_system = self._model_tree.root_system.subsystems[0]
        root_node = add_system_to_tree(model_view, '', model_system)

        # Add model workspace in model node
        root_system_path = self._model_tree.root_system.path

        return root_node, root_system_path

    def _populate_system_view(
        self, system_view: Treeview, system_path: str) -> None:
        """Populate with give system content."""

        system_view.delete(*system_view.get_children())

        def find_system(system: System, path:str) -> Optional[System]:
            """Recursively search for system with given path
            """
            for subsytem in system.subsystems:
                if subsytem.path == path: return subsytem
                subsytem = find_system(subsytem, path)
                if subsytem: return subsytem
            return None

        if system_path == '':
            system = self._model_tree.root_system
        else:
            system = find_system(
                self._model_tree.root_system, system_path)
        
        for item in system.params:
            shape = item.shape if len(item.shape) > 0 else 'Scalar'
            values = ['Parameter', item.dtype, shape, item.path]
            if '/' not in item.path:
                name = item.path
            else:
                name = '/'.join(item.path.split('/')[-2:])
            system_view.insert('', tk.END, text=name, values=values)
            
        for item in system.signals:
            shape = item.shape if len(item.shape) > 0 else 'Scalar'
            values = ['Signal', item.dtype, shape, item.path]
            name = item.path.split('/')[-1]
            system_view.insert('', tk.END, text=name, values=values)

    def _populate_element_view(self, element_view: tk.Text, type: str, path:str):
        """Populate with give system content."""
        
        if type == 'Signal':
            elements = self._model_tree.signals.values()
        elif type == 'Parameter':
            elements = self._model_tree.params.values()
        
        element = next(x for x in elements if x.path == path)

        ctype_str = None
        if element.ctype:
            ctype_str = element.ctype.__name__

        element_dict = {
            'path': element.path,
            'dtype': element.dtype,
            'ctype': ctype_str,
            'shape': element.shape if len(element.shape) > 0 else 'Scalar',
            'variable_name': element.variable_name,
            'description': element.description,
        }
        value = element.value
        if value is not None:
            element_dict['value'] = value

        def default(value) -> str:
            if isinstance(value, np.ndarray):
                return value.tolist()
            else:
                raise TypeError()

        text = json.dumps(element_dict, indent=4, default=default)

        element_view.configure(state='normal')
        element_view.delete('1.0', tk.END)
        element_view.insert(tk.END, text)
        element_view.configure(state='disabled')
