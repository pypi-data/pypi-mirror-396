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

import os
import sys
from abc import abstractmethod
import tkinter as tk
from tkinter.ttk import Frame, Treeview, PanedWindow, Scrollbar

class GuiBase:
    def __init__(self, title: str='SL Model view'):

        # Selected model row ID
        self._model_view_row_id = ''

        # Selected system row ID
        self._system_view_row_id = ''

        # GUI main title
        self._title = title
    
    @abstractmethod
    def _populate_model_view(self, model_view: Treeview) -> tuple[str, str]:
        """Populate tree view and return root node id and name

        Returns:
            tuple[str, str]: Root node id and name
        """

    @abstractmethod
    def _populate_system_view(
        self, system_view: Treeview, system_path: str) -> None:
        """Populate with give system content."""

    @abstractmethod
    def _populate_element_view(self, element_view: tk.Text, type: str, path:str):
        """Populate with give system content."""

    def create_gui(self) -> tk.Tk:
        
        # Create UI elements
        root = tk.Tk()
        root.title(self._title)
        root.geometry('1024x768')
        # root.config(bg="skyblue")
        
        # Create a paned windows for resizing feature
        paned_window = PanedWindow(root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a model view for global exploration
        model_frame = Frame(root)
        model_view = Treeview(model_frame, columns=['path'])
        model_view['displaycolumns'] = []
        model_view.heading('#0', text='Model Hierarchy')
        
        scrollbar = Scrollbar(model_frame, orient=tk.VERTICAL, command=model_view.yview)
        model_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar = Scrollbar(model_frame, orient=tk.HORIZONTAL, command=model_view.xview)
        model_view.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        model_view.pack(fill=tk.BOTH, expand=True)
        model_frame.pack()
                
        # Create a system view for displaying selected system content
        # and a detailed parameter/signal content
        right_paned_window = PanedWindow(orient=tk.VERTICAL)

        # Create a system view
        system_frame = Frame(right_paned_window)
        columns = ['type', 'data_type', 'data_shape', 'path']
        system_view = Treeview(system_frame, columns=columns)
        system_view.heading('#0', text='Name')
        system_view.heading('type', text='Type')
        system_view.heading('data_type', text='Data Type')
        system_view.heading('data_shape', text='Data Shape')
        system_view.heading('path', text='Path')
        system_view.column('#0',           anchor=tk.W,        width=200,  minwidth=100 )
        system_view.column('type',         anchor=tk.CENTER,   width=70,   minwidth=70  )
        system_view.column('data_type',    anchor=tk.CENTER,   width=70,   minwidth=70  )
        system_view.column('data_shape',   anchor=tk.CENTER,   width=70,   minwidth=70  )
        system_view.column('path',         anchor=tk.W,        width=200,  minwidth=100 )

        scrollbar = Scrollbar(system_frame, orient=tk.VERTICAL, command=system_view.yview)
        system_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar = Scrollbar(system_frame, orient=tk.HORIZONTAL, command=system_view.xview)
        system_view.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        system_view.pack(fill=tk.BOTH, expand=True)
        system_frame.pack()
        
        # Create parameter/signal view
        element_frame = Frame(right_paned_window)
        columns = ['property_value']
        element_view = tk.Text(element_frame, state='disabled')

        scrollbar = Scrollbar(element_frame, orient=tk.VERTICAL, command=element_view.yview)
        element_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        element_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        element_frame.pack()
        
        # Add them to right side
        right_paned_window.add(system_frame, weight=1)
        right_paned_window.add(element_frame, weight=1)
        right_paned_window.pack(fill=tk.BOTH, expand=True)

        # Add main widgets to main paned window
        paned_window.add(model_frame)
        paned_window.add(right_paned_window)

        root_node_id, root_node_name = self._populate_model_view(model_view)

        # Add model workspace in model node
        values = [root_node_name]
        model_view.insert(
            root_node_id, 0, text='Model Workspace',values=values)

        # Open root tree node
        model_view.item(root_node_id, open=True)

        # Add contextual menu to system view to copy selected item path
        # to clipboard
        def copy_path():
            global system_row_id
            item = system_view.item(system_row_id)
            path = item['values'][-1]
            root.clipboard_clear()
            root.clipboard_append(f"{path}")
            if sys.platform == 'linux':
                os.system(f'echo {path} | xclip')

        menu = tk.Menu(system_view, tearoff=0)
        menu.add_command(label='Copy Path', command=copy_path)

        def do_popup(event: tk.Event):
            global system_row_id
            try:
                system_row_id = system_view.identify_row(event.y)
                if system_row_id == '':
                    menu.grab_release()
                    return
                system_view.selection_set(system_row_id)
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        system_view.bind("<Button-3>", do_popup)

        def model_view_on_select(event: tk.Event):
            row_id = model_view.selection()

            if row_id == self._model_view_row_id:
                return
            
            self._model_view_row_id = row_id
            item = model_view.item(row_id)
            system_path = item['values'][-1]
            self._populate_system_view(system_view, system_path)
        model_view.bind('<<TreeviewSelect>>', model_view_on_select)
        
        def clear_element_view():
            element_view.configure(state='normal')
            element_view.delete('1.0', tk.END)
            element_view.configure(state='disabled')

        def system_view_on_select(event: tk.Event):
            row_id = system_view.selection()

            if len(row_id) == 0:
                clear_element_view()
                return
            elif row_id == self._system_view_row_id:
                return
            
            self._system_view_row_id = row_id
            item = system_view.item(row_id)
            element_type = item['values'][0]
            element_path = item['values'][-1]
            self._populate_element_view(
                element_view, element_type, element_path)
        system_view.bind('<<TreeviewSelect>>', system_view_on_select)

        return root
