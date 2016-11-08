#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# my_db.py

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


"""
class pour la gestion de la base de données
La db est dans le dossier de ce script
"""

import os
import shutil
import sqlite3


class MyDataBase(object):
    '''TODO: pouvoir définir la dim de la grille'''

    def __init__(self, db_file):
        '''Crée l'objet de gestion de la base.
        Si pas de db, elle est créée
        '''

        self.db_file = db_file
        if not os.path.isfile(self.db_file):
            self.create_db()

    def create_db(self):
        '''os.path.isfile("land.sqlite")'''

        print("Création de la base demandée", self.db_file)

        # Connection à db
        conn = sqlite3.connect(self.db_file)
        # Curseur
        cur = conn.cursor()
        # Crée la table
        a = '''CREATE TABLE grille(X INTEGER, Y INTEGER,
                                   Z INTEGER, C INTEGER)'''
        cur.execute(a)
        # Save
        conn.commit()
        # Ferme
        conn.close()
        print("Nouvell base créée", self.db_file, "\n")

    def record_in_db(self, x, y ,z ,c):
        '''Si le point existe, une nouvelle entrée est ajoutée à la base. '''

        #print("Insertion dans la base de", x, y ,z , c)
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            with conn:
                cur.execute("INSERT INTO grille(X, Y, Z, C) VALUES(?,?,?,?)",
                                                                (x, y, z, c))
        except sqlite3.IntegrityError:
            print("Erreur lors de l'ajout d'un cube")

    def delete_in_db(self, x, y ,z):
        '''Supprime tous les cubes du point.'''

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            with conn:
                cur.execute("DELETE FROM grille WHERE X=? and Y=? and Z=?",
                                                (x,y,z))
        except sqlite3.IntegrityError:
            print("Erreur lors de la supression d'un cube")

    def delete_duplicate(self):
        '''Crée une nouvelle base land.sqlite sans doublons.'''

        land = self.create_dict_with_db()
        self.recreate_sqlite_with_dict(land)

    def create_dict_with_db(self):
        '''Lit la db, écrit toutes les clés, couleurs dans un dictionnaire.
        Un dictionnaire n'a pas de doubons !!
        Le dernier point lu sera conservé.'''

        land = {}
        nombre = 0

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        # Lecture db et écriture dans dict
        try:
            with conn:
                color = [1, 2, 3, 4, 5, 6, 7, 8]
                for c in color:
                    cur.execute('SELECT X, Y, Z, C FROM grille WHERE C = ?', (c,))
                    for value in cur:
                        X = value[0]
                        Y = value[1]
                        Z = value[2]
                        color = value[3]
                        land[(X, Y, Z)] = color
                        nombre += 1
        except sqlite3.IntegrityError:
            print("Erreur lors de la supression d'un cube")

        # Vérif du dict
        print("Nombre d'entrèe dans la base", nombre)
        print("Longueur du dictionnaire = ", len(land), "\n")
        return land

    def recreate_sqlite_with_dict(self, land):
        '''Copie de self.db_file vers
                            self.db_file[avec .sqlite coupé] + "_old.sqlite"
        Création d'une nouvelle base self.db_file,
        écriture du dict dans cette base.
        '''

        old_db = self.db_file[:-7] + "_old.sqlite"
        print("L'ancienne base\n", self.db_file, "\ndevient\n",old_db, "\n")
        shutil.copy(self.db_file, old_db)

        # Destruction puis recréation de la base
        os.remove(self.db_file)
        self.create_db()

        # Ecriture dans la base avec les points de land
        for key, val in land.items():
            x = key[0]
            y = key[1]
            z = key[2]
            c = val
            # Ajout dans la nouvelle base
            self.record_in_db(x, y ,z , c)

        print("La base a été recrée sans doublons")

def record_test():
    '''Test d'ajout de points'''

    db_file = "./land.sqlite"
    my_db = MyDataBase(db_file)
    my_db.record_in_db(1,1,1,2)
    my_db.record_in_db(1,2,2,2)
    my_db.record_in_db(1,3,2,2)
    my_db.record_in_db(1,4,2,2)
    my_db.record_in_db(1,5,2,2)
    my_db.delete_in_db(1,5,2)

def new():
    '''crée une base vide si inexistante'''

    my_db = MyDataBase("land.sqlite")

def no_doubles():
    db_file = "land.sqlite"
    my_db = MyDataBase(db_file)
    my_db.delete_duplicate()

def delete_plage_out(db_file, plage):
    '''Supprime les points en dehors de la plage spécifiée'''
    pass


if __name__ == '__main__':
    ##record_test()
    ##new()
    no_doubles()
