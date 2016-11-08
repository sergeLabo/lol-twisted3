#! /usr/bin/python3
# -*- coding: UTF-8 -*-

## create_cube.py

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
Ajoute où détruit un cube à la position du curseur, valable pour Blender 2.72


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


from bge import logic as gl

def get_prop():
    '''Retourne les prop utilisées dans ce script.'''

    ## Get prop in object Hud_game_motor
    # Get active scene list
    activeScenes = gl.getSceneList()

    # Get scene Level_x and Hud
    scene = activeScenes[0]
    hud = activeScenes[2]

    # Get list of objects in scene and hud
    scene_ObjList = scene.objects
    # Position du cube à ajouter ou ôter
    CURSOR = scene_ObjList["Cursor"]

    hud_ObjList = hud.objects
    hud_game_motor = hud_ObjList["Hud_game_motor"]
    SCROLL = hud_game_motor['scroll']

    LEFT_CLIC = hud_game_motor['left clic']
    RIGHT_CLIC = hud_game_motor['right clic']

    return CURSOR, SCROLL, LEFT_CLIC, RIGHT_CLIC, scene

def add_cube_at_cursor(CURSOR, scene, c, origin):
    '''Ajoute un cube à la position du curseur de couleur c.'''

    x = int(CURSOR.worldPosition[0]/2)
    y = int(CURSOR.worldPosition[1]/2)
    z = int(CURSOR.worldPosition[2]/2)

    print(x, y, z)
    # Object in invisible layer
    cube = gl.cube_table[c]

    obj_added = scene.addObject(cube, CURSOR, 0)
    #obj_added.worldPosition = x, y, z

    # Maj du dict
    gl.land[(x, y, z)] = (c, obj_added)

    # Maj des msg
    if origin == "clic":
        add_to_msg_list(x, y, z, c)

def add_cube_at_xyz(CURSOR, scene, x, y, z, c, origin):
    '''Ajoute un cube à la position du curseur de couleur c.'''

    # Object in invisible layer
    cube = gl.cube_table[c]
    obj_added = scene.addObject(cube, CURSOR, 0)
    # Position géométrique dans blender à *2
    obj_added.worldPosition = 2*x, 2*y , 2*z

    try:
        gl.land[(x, y, z)]
    except:
        gl.land[(x, y, z)] = (c, obj_added)
        # Maj des msg
        if origin == "clic":
            add_to_msg_list(x, y, z, c)

def delete_cube_at_cursor(x, y, z, origin):
    '''Détruit le cube dans le curseur.'''

    # Destruction du cube
    print("Demande de supression du cube", x, y, z)

    # Suppression dans gl.land de l'objet à x,y,z
    object_to_delete = gl.land[(x, y, z)][1]
    object_to_delete.endObject()
    print("Cube supprimé de l'affichage")

    del gl.land[(x, y, z)]
    print("Cube supprimé de gl.land")

    # Maj des msg pour envoi à lol.py
    if origin == "clic":
        add_to_msg_list(x, y, z, 0)

def delete_cube_at_xyz(x, y, z, origin):
    '''Détruit le cube à x, y, z.'''

    print("Demande de supression du cube", x, y, z)

    try:
        object_to_delete = gl.land[(x, y, z)][1]
        object_to_delete.endObject()
        print("Cube supprimé de l'affichage")

        del gl.land[(x, y, z)]
        print("Cube supprimé de gl.land")
    except:
        print("Pas de cube à", x, y, z)

    # Maj des msg pour envoi à lol.py
    if origin == "clic":
        add_to_msg_list(x, y, z, 0)

def delete_stack(x, y):
    '''Destruction d'une pile de cube à x, y
    Demande la suppression de tous les cubes de z=0 à z=19
    '''

    print("Demande de supression de la pile de cube", x, y)
    for z in range(20):
        # Suppression dans gl.land de x y z
        delete_cube_at_xyz(x, y, z, "clic")

def add_or_del_cube_from_irc(CURSOR, scene):
    '''Avec la liste gl.cube_from_irc.'''

    nb = len(gl.cube_from_irc)
    # Si cube dans la liste des cubes concernés
    while nb:
        nb -= 1
        cube = gl.cube_from_irc[0]
        print("Cube à mettre à jour", cube)

        x, y, z, c = cube[0], cube[1], cube[2], cube[3]

        if c > 0:
            add_cube_at_xyz(CURSOR, scene, x, y, z, c, "irc")
        else:
            delete_cube_at_xyz(x, y, z, "irc")

        gl.cube_from_irc.remove(cube)

def add_to_msg_list(x, y, z, c):
    ## Envoi au server
    # Ajout à la liste des msg à envoyer
    gl.cube_to_irc.append((x, y, z, c))

def main():
    CURSOR, SCROLL, LEFT_CLIC, RIGHT_CLIC, scene = get_prop()

    # Suivi de IRC
    add_or_del_cube_from_irc(CURSOR, scene)

    # Les cubes sont ajoutés à la même position que le Cursor: a = 10, b = 10
    x = int(gl.dec_x + 10)
    y = int(gl.dec_y + 10)
    z = int(gl.dec_z / 2)

    # Delete all Cube in stack if keyboard X
    if gl.getCurrentController().sensors['X'].positive:
        stack = 1
        c = 0
        delete_stack(x, y)
        stack = 0

    # with mouse
    # Create cube with left clic
    if LEFT_CLIC:
        # Cube is created
        c = SCROLL
        add_cube_at_cursor(CURSOR, scene, c, origin="clic")

    # Delete cube with right clic
    if RIGHT_CLIC:
        c = 0
        delete_cube_at_cursor(x, y, z, origin="clic")
