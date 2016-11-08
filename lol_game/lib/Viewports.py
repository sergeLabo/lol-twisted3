#! /usr/bin/python3
# -*- coding: UTF-8 -*-

#Viewports.py

#########################################################################
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
#########################################################################


from bge import render
from bge import logic as gl

def get_prop():
    '''Retourne les prop utilisées dans ce script.'''

    # Get active scene list
    activeScenes = gl.getSceneList()

    # Get scene Level_x and Hud
    scene = activeScenes[0]

    # Get list of objects in scene and hud
    scene_ObjList = scene.objects
    dessus = scene_ObjList["Game_Motor"]["vue_dessus"]
    return dessus

# get game window height and width
height = render.getWindowHeight()
width = render.getWindowWidth()

############# Using 4 cameras

# get current scene
scene = gl.getCurrentScene()

# get list of objects in scene
objList = scene.objects

# use Camera for FPS
cam_A = objList["Camera"]

# use Camera.003 for map
cam_B = objList["Camera.003"]

# use Camera.004 for global cursor view
cam_C = objList["Camera.004"]

# use Camera.005 for global cursor view
cam_D = objList["Camera.005"]

############# Use the left for cam_A

left_A = 0
bottom_A = 0
right_A = width - int(width/5)
top_A = height

# set cam_A viewport
#cam_A.setViewport( left_A, bottom_A, right_A, top_A)
cam_A.setViewport( left_A, bottom_A, width, top_A)

############# Use top right for cam_B

left_B = width - int(width/5)
bottom_B = height -int(height/3)
right_B = width
top_B = height

# set cam_B viewport
cam_B.setViewport( left_B, bottom_B, right_B, top_B)

########### Use middle right for cam_C

##left_C = width - int(width/5)
##bottom_C = height -2*int(height/3)
##right_C = width
##top_C = height - int(height/3)

### set cam_C viewport
##cam_C.setViewport( left_C, bottom_C, right_C, top_C)

########### Use bottom right for cam_D

##left_D = width - int(width/5)
##bottom_D = 0
##right_D = width
##top_D = int(height/3)

### set cam_B viewport
##cam_D.setViewport( left_D, bottom_D, right_D, top_D)


##############

cam_A.useViewport = True

dessus = get_prop()

if dessus:
    cam_B.useViewport = True
else:
    cam_B.useViewport = False

#cam_C.useViewport = True
#cam_D.useViewport = True
