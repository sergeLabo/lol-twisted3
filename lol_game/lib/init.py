#! /usr/bin/python3
# -*- coding: UTF-8 -*-

## init.py

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
Télécharge la db
Charge la db dans un dict

Lance un bot irc dans un thread
    Le bot irc écoute l'irc, demande ajout cube
    Envoie cube sur irc si ajout local
'''


import os, sys
from time import time, sleep
import threading
import sqlite3
import urllib.request, urllib.error

from bge import logic as gl

import twisted.words
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

from lib.labtools.point_is_valid_old import point_is_valid


def create_nick():
    '''Retourne nick '''

    cmd = "USER"
    # Get user as string
    user = os.getenv(cmd)
    # temps en entier comme str
    number = str(int(time()))
    number = number[5:]
    # Create unique nickname
    nick = user + str(number)

    print("IRC nickname {}".format(nick))

    return nick


class IrcTwisted(irc.IRCClient):
    '''An IRC bot.'''

    nickname = create_nick()

    def connectionMade(self):

        irc.IRCClient.connectionMade(self)
        print("Connection Made")
        # Boucle infinie pour envoi
        self.send_thread()

    def connectionLost(self, reason):

        irc.IRCClient.connectionLost(self, reason)
        print("Connection Lost {}".format(reason))

    # callbacks for events
    def signedOn(self):
        '''Called when bot has succesfully signed on to server.'''

        self.join(self.factory.channel)

    def joined(self, channel):
        '''This will get called when the bot joins the channel.'''

        print("Le bot a rejoint le channel {}".format(channel))

    def privmsg(self, user, channel, msg):
        '''Réception d'un message public ou privé.'''

        print("IRC: {}".format(msg))

        # si le message est un cube, ajout à gl
        is_valid, x, y, z , c = point_is_valid(msg)

        if is_valid:
            X, Y, Z, color = int(x), int(y), int(z), int(c)

            # Il faut créer le cube ou le détruire dans create_cube.py
            # par mise à jour d'une liste
            print ("Cube reçu de IRC:", X, Y, Z, color)
            gl.cube_from_irc.append((X, Y, Z, color))

    def send(self, message):
        channel = "#jeuxlibres"
        self.say(channel, message)
        print("Message envoyé:", message)

    def action(self, user, channel, msg):
        '''This will get called when the bot sees someone do an action.'''

        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks
    def irc_NICK(self, prefix, params):
        '''Called when an IRC user changes their nickname.'''

        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

    # Boucle infinie pour envoi
    def infinite_loop(self):
        while 1:
            nb = len(gl.cube_to_irc)

            # Si msg dans la liste
            for i in range(nb):
                data = gl.cube_to_irc[0]
                self.send(str(data))
                gl.cube_to_irc.remove(data)

    def send_thread(self):
        self.t = threading.Thread(target=self.infinite_loop)
        self.t.start()


class IrcTwistedFactory(protocol.ClientFactory):
    '''A factory for IrcTwisteds.
    A new protocol instance will be created each time we connect to the server.
    '''

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        p = IrcTwisted()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        '''If we get disconnected, reconnect to server.'''

        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason)
        reactor.stop()


def main():
    set_variable()

    # l local p public
    u = "l"
    if u == "l":
        url = "http://192.168.1.18:8080/land.sqlite"
    elif u == "p":
        url = "http://jeuxlibres.org:8080/land.sqlite"
    else:
        os._exit(0)

    # Data base
    download_file(url)
    db_sqlite = get_db_file()
    read_db_sqlite(db_sqlite)

    # Bot IRC
    irc_thread()

def set_variable():
    '''Initialisation de variables attibuts du bge.logic'''

    # Create color table as dictionnary and save in gl
    gl.color_table =   {    '1' : 'White',
                            '2' : 'Black',
                            '3' : 'Red',
                            '4' : 'Blue',
                            '5' : 'Green',
                            '6' : 'Yellow',
                            '7' : 'Magenta',
                            '8' : 'Cyan'
                            }

    gl.cube_table = {   1 : 'White',
                        2 : 'Black',
                        3 : 'Red',
                        4 : 'Blue',
                        5 : 'Green',
                        6 : 'Yellow',
                        7 : 'Magenta',
                        8 : 'Cyan'}

    # Set init dec
    gl.dec_x = 0
    gl.dec_y = 0
    gl.dec_z = 0

    # Liste des cubes reçus et envoyés
    gl.cube_to_irc = []
    gl.cube_from_irc = []

    # Set gamma for mouse
    gl.gamma = 0.0

def download_file(url):
    try:
        print("Downloading .... from: {}".format(url))

        # Open the url
        req = urllib.request.Request(url)
        f = urllib.request.urlopen(req)

        # Get current directory
        cur_dir = os.getcwd()
        sqlite = cur_dir + '/land.sqlite'
        print("Le fichier enregistré à {}".format(sqlite))

        # Open our local file for writing
        local_file = open(sqlite, "wb")

        # Write to our local file
        local_file.write(f.read())
        local_file.close()

    # Handle errors
    except urllib.error.HTTPError as e:
        print("HTTP Error:",e.code , url)
    except urllib.error.URLError as e:
        print("URL Error:",e.reason , url)
    except:
        print("Download raté")

def get_db_file():
    '''Retourne le chemin absolu de la db
    Le fichier land.sqlite est dans /home/pierre/projets/lol2.72/lol_game
    '''
    cur = gl.expandPath("//")
    print("Current directory", cur)

    db_sqlite = cur + "land.sqlite"

    print("Vérif de land.sqlite:", db_sqlite)

    # Open our local file for reading
    local_file = open(db_sqlite, 'r')

    # close
    local_file.close()

    return db_sqlite

def read_db_sqlite(db_sqlite):
    '''Create dict with sqlite data'''

    # Connect to database
    db_connect = sqlite3.connect(db_sqlite)

    # Connect to database
    cursor = db_connect.cursor()

    # Create a local dictionnary with existing cube in db
    # Put existing cube in dictionnary land
    #gl.land = {(1, 1, 1): (5, objet_blender), ................}
    #            X  Y  Z    C, objet ajouté par display_land, 0 en provisoire
    gl.land = {}
    for color_num, color_object in list(gl.color_table.items()):
        cursor.execute('SELECT X, Y, Z, C FROM grille WHERE C = ?', color_num)
        # Put in land dict
        for value in cursor:
            X = value[0]
            Y = value[1]
            Z = value[2]
            color = value[3]
            gl.land[(X, Y, Z)] = [color, 0]
    print("Lenght of land dictionnary = ", len(gl.land))

def run_irc_bot():

    server = 'jeuxlibres.org'
    channel = "#jeuxlibres"
    port = 6667

    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = IrcTwistedFactory(channel)

    # connect factory to this host and port
    reactor.connectTCP(server, port, f)

    # run bot
    reactor.run(installSignalHandlers=False)

def irc_thread():

    irc_thread = threading.Thread(target=run_irc_bot)
    irc_thread.start()


main()
