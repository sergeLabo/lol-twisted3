#! /usr/bin/python3
# -*- coding: UTF-8 -*-

## display_land.py

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

'''
Tourne toutes les 3 frames
'''


from bge import logic as gl

# get the controller
controller = gl.getCurrentController()

# Get the owner
owner = controller.owner

# get current scene
scene = gl.getCurrentScene()

# get a list of the objects in the current scene
objList = scene.objects

color_table = gl.color_table

def display():
    '''Affichage initial, ne tourne qu'une seule fois.

    https://www.blender.org/api/blender_python_api_2_67_1/bge.types.KX_Scene.html
    addObject(object, other, time=0)
        Adds an object to the scene like the Add Object Actuator would.
        Parameters:
            object (KX_GameObject or string) – The object to add
            other (KX_GameObject or string) – The object’s center to use
                                                when addind the object
            time (integer) – The lifetime of the added object, in frames.
                             A time of 0 means the object will last forever.

        Returns:    The newly added object.

    '''

    # Parcours de gl.land pour le compléter avec les objets
    for point, val in gl.land.items():
        X = point[0]
        Y = point[1]
        Z = point[2]
        C = val[0]

        empty = objList["Empty-0000"]
        empty.worldPosition = (2*X, 2*Y, 2*Z)

        for color_num, color_object in list(color_table.items()):
            if int(color_num) == int(C):
                obj_added = scene.addObject(color_object, empty, 0)
                gl.land[X, Y, Z][1] = obj_added

display()
