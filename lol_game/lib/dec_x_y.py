#! /usr/bin/python3
# -*- coding: UTF-8 -*-

## dec_x_y.py

#############################################################################
# Copyright (C) Labomedia June 2016
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franproplin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#############################################################################


from bge import logic as gl

'''dec_x_y.py run every frame
this script set cursor location and set gl.dec_x, gl.dec_y
'''


def main():
    # Get the owner.
    owner = gl.getCurrentController().owner

    # get current scene
    scene = gl.getCurrentScene()

    # get a list of the objects in the current scene
    objList = scene.objects

    # Get object Cursor (warning: cursor is sqlite in gl !)
    cursorCube = objList["Cursor"]

    # Get owner prop dec_x and dec_y
    dec_x = owner['dec_x']
    dec_y = owner['dec_y']
    dec_z = gl.dec_z

    gl.dec_x = dec_x
    gl.dec_y = dec_y

    # Set cursorCube position
    cursorCube.localPosition = (2*dec_x + 20, 2*dec_y + 20, dec_z)
