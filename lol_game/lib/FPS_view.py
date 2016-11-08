#! /usr/bin/python3
# -*- coding: UTF-8 -*-


# FPS_view.py

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


import bge.render as Rasterizer
import mathutils
from bge import logic as gl

# get game window height and width
height = Rasterizer.getWindowHeight()
width = Rasterizer.getWindowWidth()

# get the controller
controller = gl.getCurrentController()

# Get the owner
owner = controller.owner

# get current scene
scene = gl.getCurrentScene()

# get a list of the objects in the current scene
objList = scene.objects

# Get object Cursor (warning: cursor is sqlite in gl !)
cursorCube = objList["Cursor"]
gamemotor = objList["Game_Motor"]

dec_x = gl.dec_x
dec_y = gl.dec_y

mouse = controller.sensors['Mouse']

# set only one time with prop showMouse in owner
if not owner['showMouse']:
    Rasterizer.showMouse(1)
    owner['showMouse'] = True

def main():
    # Gets the movement
    delta = DeltaMouse(int(width/2),int(height/2),True)

    # this run only one time to recenter the mouse
    recenter()

    # Generates a value to the Horizontal rotation (in degrees)
    Hrot = delta[0] * owner['sens'] / -1000

    # Generates a value to the Vertical rotation (in degrees)
    Vrot = delta[1] * owner['sens'] / -1000

    # applyRotation([a,b,c], True) True set Global, False set local
    # If the "x" prop is True,
    # it does the horizontal rotation (global z axis rotation)
    if owner['x']:
        owner.applyRotation([0,0,Hrot], False)

    # If the "y" prop is True,
    # it does the vertical rotation (local x axis rotation)
    if owner['y']:
        owner.applyRotation([Vrot,0,0], True)

    # Set cursor
    cursorCube_height()

def cursorCube_height():
    '''Set Cube Curor height with cam angle'''
    # Get orientation, it's a list 3,3
    cam_ori = owner.localOrientation

    # Tranform orientation list to matrix 3x3
    ori_to_matrix = cam_ori.to_3x3()

    # Transform matrix to euler
    cursorCubeZ = ori_to_matrix.to_euler()

    cursorCubeZ = 40*cursorCubeZ[0] - 50
    #print (cursorCubeZ)

    # limit location
    if cursorCubeZ < 0:
        cursorCubeZ = 0
    if cursorCubeZ >= 38.0:
        cursorCubeZ = 38.0

    # create notch
    cursorCubeZ = cursorCubeZ - cursorCubeZ%2
    cursorCubeZ = int(cursorCubeZ)

    # Set cursorCube position in gl.dec_z
    # cursorCube position is set in dec_x_y.py every frame
    gl.dec_z = cursorCubeZ

def DeltaMouse(Xcenter,Ycenter,lockToCenter=False,Xpos=mouse.position[0],
                                                    Ypos=mouse.position[1]):
    ''' This function calculates the ditance (in pixels)
    of the mouse from two given points '''
    #Calculates the x variation
    Dx = Xpos - Xcenter
    #the y variation
    Dy = Ypos - Ycenter
    #Put in a list
    delta = [Dx,Dy]

    #If the "lockToCenter" flag is true AND the mouse is NOT in the center
    if lockToCenter and Dx or Dy:
        #It centers the mouse
        Rasterizer.setMousePosition(Xcenter,Ycenter)

    #Returns a list with the values
    return delta

def recenter():
    '''Recenter the mouse before to begin this script. If the mouse isn't
    in the center, it would generate a strange movement/gap. If it's the
    first time that the mouse moves the movement is ignored'''
    if owner['firstTime']:
        delta = [0,0]
        # Sets the flag to False
        owner['firstTime'] = False

if gamemotor['fps']:
    main()
##main()
