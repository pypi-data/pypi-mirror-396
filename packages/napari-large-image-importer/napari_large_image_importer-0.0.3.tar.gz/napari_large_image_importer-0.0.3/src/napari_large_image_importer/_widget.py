"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import os
from typing import TYPE_CHECKING

import dask
import numpy as np
import tifffile
import zarr
from magicgui.widgets import FileEdit, Label, CheckBox, PushButton
from qtpy.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    pass


class NliiQWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self._viewer = napari_viewer
        self.setLayout(QVBoxLayout())
        self.Label1 = Label(value='select image file')
        self.layout().addWidget(self.Label1.native)
        self.target_file = FileEdit(mode='r')
        self.layout().addWidget(self.target_file.native)
        self.Label2 = Label(value='select colormap file')
        self.layout().addWidget(self.Label2.native)
        self.colormap_file = FileEdit(mode='r')
        self.layout().addWidget(self.colormap_file.native)
        self.checkbox = CheckBox(text='split channels')
        self.layout().addWidget(self.checkbox.native)
        self.load_button = PushButton(text='Load')
        self.load_button.clicked.connect(self.load_file)
        self.layout().addWidget(self.load_button.native)
        self.save_button = PushButton(text='save colormap')
        self.save_button.clicked.connect(self.save_colormap)
        self.layout().addWidget(self.save_button.native)

    def load_file(self):
        print('start')
        try:
            with open(self.colormap_file.value, "r") as f:
                channels = []
                for x in f:
                    channels.append(x.rstrip("\n"))
        except:
            channels = ['blue', 'green', 'red', 'magenta', 'cyan', 'yellow', 'bop purple', 'gray']
        store = tifffile.imread(self.target_file.value, aszarr=True)
        zobj = zarr.open(store, mode='r')
        print(zobj.attrs.keys())

        if 'multiscales' in zobj.attrs:
            data = [zobj[str(dataset['path'])] for dataset in zobj.attrs['multiscales'][0]['datasets']]
            print(data[-1])

            d = [dask.array.from_zarr(z) for z in data]
            if len(d[0].shape) == 2:
                self._viewer.add_image(d, blending='additive', contrast_limits=[0, 255])
            elif (len(d[0].shape) > 2) & self.checkbox.value:
                c = np.argmin(d[0].shape)
                print(c)
                self._viewer.add_image(d, rgb=False, contrast_limits=[0, 255], channel_axis=c,
                                       name=[f'ch{x}' for x in range(d[0].shape[c])],
                                       blending='additive',
                                       colormap=channels[:d[0].shape[c]])
            elif (len(d[0].shape) > 2) & (self.checkbox.value is False):
                c = np.argmin(d[0].shape)
                if d[0].shape[c] == 3:
                    for i in range(len(d)):
                        d[i] = np.moveaxis(d[i], c, -1)
                    self._viewer.add_image(d, rgb=True, contrast_limits=[0, 255])
                else:
                    self._viewer.add_image(d, rgb=False, contrast_limits=[0, 255], channel_axis=c,
                                           name=[f'ch{x}' for x in range(d[0].shape[c])],
                                           blending='additive',
                                           colormap=channels[:d[0].shape[c]])
            else:
                pass
        else:
            d = dask.array.from_zarr(zobj)
            c = np.argmin(d.shape)
            if len(d.shape) == 2:
                d_list = [d, d[::2, ::2], d[::4, ::4], d[::8, ::8], d[::16, ::16]]
                self._viewer.add_image(d_list, blending='additive', contrast_limits=[0, 255])
            elif (len(d.shape) > 2) & self.checkbox.value:
                d = np.moveaxis(d, c, -1)
                d_list = [d, d[::2, ::2, :], d[::4, ::4, :], d[::8, ::8, :], d[::16, ::16, :]]
                self._viewer.add_image(d_list, rgb=False, contrast_limits=[0, 255], channel_axis=c,
                                       name=[f'ch{x}' for x in range(d.shape[-1])],
                                       blending='additive',
                                       colormap=channels[:d.shape[-1]])
            elif (len(d.shape) > 2) & (self.checkbox.value is False):
                d = np.moveaxis(d, c, -1)
                d_list = [d, d[::2, ::2, :], d[::4, ::4, :], d[::8, ::8, :], d[::16, ::16, :]]
                if d.shape[-1] == 3:
                    self._viewer.add_image(d_list, rgb=True, contrast_limits=[0, 255])
                else:
                    self._viewer.add_image(d_list, rgb=False, contrast_limits=[0, 255], channel_axis=-1,
                                           name=[f'ch{x}' for x in range(d.shape[-1])],
                                           blending='additive',
                                           colormap=channels[:d.shape[-1]])

    def save_colormap(self):
        colors = []
        for layer in self._viewer.layers:
            colors.append(layer.colormap.name)
        with open(os.path.splitext(self.target_file.value)[0] + '.txt', mode='w') as f:
            for x in colors:
                f.write(str(x) + "\n")
