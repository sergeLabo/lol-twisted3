#! /usr/bin/python3
# -*- coding: UTF-8 -*-

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
Ce script:
    - télécharge de fichier land.sqlite
    - sert de relay entre blender, le serveur UDP et le BOT IRC:
        - envoie à blender les cubes reçus sur IRC
        - reçoit les cubes ajoutés par blender
        - puis les envoie sur l'IRC
'''


import os, sys
from threading import Thread
from queue import Queue, Empty
from time import time, sleep
import asyncio
import os
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from jaraco.stream import buffer
import subprocess
import json
import urllib.request, urllib.error
from point_is_valid import point_is_valid

try:
    import signal
except ImportError:
    signal = None

# Variable globale
Q_TO_IRC = Queue(maxsize=60)
Q_FROM_IRC = Queue(maxsize=60)


class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):

        self.channel = channel
        self.message = ""

        self.t = Thread(target=self.infinite_loop)
        self.t.start()

        # le bot est "self."
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        irc.bot.SingleServerIRCBot.start(self)

    def infinite_loop(self):
        '''Récupération dans la pile Q_TO_IRC des cubes pour envoi sur l'IRC
        Boucle infinie qui tourne à 60 fps
        Un ajout ou suppr dans blender provoque l'envoi.
        '''

        global Q_TO_IRC

        while 1:
            try:
                # Récupération dans la pile
                data = Q_TO_IRC.get(block=False, timeout=0.01)
                #print("Récupération dans la pile de {} {}".format(data, type(data)))
            except:
                #print("Récup dans la pile Q_TO_IRC raté")
                data = None

            # envoi par IRC
            if data:
                print("Envoi sur IRC de {}".format(data))
                # self. est le bot !!
                self.send_msg(data)
            sleep(0.02)

    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse ", c, e)
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("Welcome")
        c.join(self.channel)
        self.connection.privmsg(self.channel, u"Test envoi sur l'IRC on Welcomme")

    def on_privmsg(self, c, e):
        print("on_privmsg", c, e, type(e))
        self.do_command(e, e.arguments[0])

    def send_msg(self, msg):
        # msg est soit bytes, soit unicode
        self.connection.privmsg(self.channel, msg)

    def on_pubmsg(self, c, e):
        # a est une liste
        a = e.arguments[0].split(":", 1)
        if len(a) > 0:
            msg = ""
            for n in range(len(a)):
                msg += str(a[n])
                self.message = msg
            print("Dans on_pubmsg, le message est: {} {}".format(msg, type(msg)))
            # 20,1,1,2 str

            # si le message est un cube, j'envoie à UDP
            is_valid, x, y, z , c = point_is_valid(msg)
            if is_valid:
                print("Ajout dans la pile UDP:", x, y, z , c)
                # ajout dans la queue Q_FROM_IRC
                Q_FROM_IRC.put((x, y, z , c), block=False, timeout=0.005)

        # Message système
        nick = self.connection.get_nickname()
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(nick):
            self.do_command(e, a[1].strip())

        return msg

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        '''Quel doit-être la forme du message ?'''

        print("Dans do_command: {}".format(cmd))
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "Not understood: " + cmd)


class MyServerUdpProtocol:
    '''Un seul protocol pour toutes les connexions.'''

    def __init__(self):
        self.tempo_1s = time()

    def connection_made(self, transport):
        print("Le serveur tourne ...")
        self.transport = transport

    def datagram_received(self, data, addr):
        '''lol reçoit de blender:
        - Nouvelle frame à chaque frame à 60 Hz
        - les cubes ajoutés
        '''

        if "Exit python script" in data.decode("utf-8"):
            print("Exit")
            os._exit(0)

        # Imp de toutes les réceptions, sauf Nouvelle frame
        if not "Nouvelle frame" in data.decode("utf-8"):
            print("Data reçu sur UDP: {}".format(data.decode("utf-8")))
        else:
            self.print_fps()

        # Traitement
        is_valid, x, y, z , c = self.data_is_cube(data)
        self.add_to_Q_TO_IRC(is_valid, x, y, z , c)
        list_from_IRC = self.IRC_to_blender()
        self.send_list_to_blender(list_from_IRC, addr)

    def data_is_cube(self, data):
        '''Retourne valeur du point si point, sinon none.'''

        try:
            is_valid, x, y, z , c = point_is_valid(data)
        except:
            is_valid, x, y, z , c = False, 0, 0, 0, 0

        return is_valid, x, y, z , c

    def add_to_Q_TO_IRC(self, is_valid, x, y, z , c):
        '''Ajout dans la pile des points valide.'''

        if is_valid:
            Q_TO_IRC.put((x, y, z , c), block=False, timeout=0.005)
            print("Ajout dans la pile Q_TO_IRC de {} ".format((x, y, z , c)))

    def IRC_to_blender(self):
        '''Lecture de la pile
        ajout dans une liste
        envoi de la liste à blender.
        '''

        global Q_FROM_IRC

        list_from_IRC = []
        while not Q_FROM_IRC.empty():
            last = Q_FROM_IRC.get(block=False, timeout=0.005)
            list_from_IRC.append(last)
        #print("Liste de IRC à envoyer à blender: {}".format(list_from_IRC))

        return list_from_IRC

    def send_list_to_blender(self, list_from_IRC, addr):
        '''Envoi de la liste reçu de IRC vers blender.'''

        # Envoi à blender
        if len(list_from_IRC) > 0:
            msg = json.dumps(list_from_IRC).encode("utf-8")
            self.transport.sendto(msg, addr)
            if len(msg) > 2:
                print("Envoi à blender:", msg)

    def print_fps(self):
        # bidouille pour affichage FPS chaque seconde
        if  time() - self.tempo_1s > 1:
            #print("Frame Rate", data.decode("utf-8")[15:])
            self.tempo_1s = time()


def create_irc_login():
    '''Retourne a IRC Login '''

    cmd="USER"
    # Get user as string
    user = os.getenv(cmd)
    # temps en entier comme str
    number = str(int(time()))
    number = number[5:]
    # Create unique IRC login
    nick = user + str(number)

    print("User IRC {}".format(nick))

    return nick

def start_server(loop, addr):
    # create_datagram_endpoint donc UDP
    # Pour serveur TCP, voir exemple de la doc

    t = asyncio.Task(loop.create_datagram_endpoint(MyServerUdpProtocol,
                                                       local_addr=addr))

    transport, server = loop.run_until_complete(t)

    return transport

def main_server():
    '''Lance le serveur UDP forever'''

    host, port = "127.0.0.1", 9999

    loop = asyncio.get_event_loop()

    if signal is not None:
        loop.add_signal_handler(signal.SIGINT, loop.stop)

    server = start_server(loop, (host, port))

    try:
        print("Le serveur UDP tourne IP =", host, "port =", port)
        loop.run_forever()
    finally:
        server.close()
        loop.close()

def irc_bot():

    print("Bot IRC lancé")
    server = 'jeuxlibres.org'
    port = 6667
    channel = "#jeuxlibres"
    nickname = create_irc_login()
    IrcBot(channel, nickname, server, port)

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

def run_blender(optimus):
    '''blender.'''

    # Get path to blend file in current directory
    cur_dir = os.getcwd()
    blend_file = cur_dir + '/LandOfLove.blend'

    if optimus:
        optirun = "primusrun "
        print("Lancement de Blenderplayer avec Optimus")
    else:
        optirun = ""
        print("Lancement de Blenderplayer sans Optimus")

    cmd = optirun + 'blenderplayer ' + blend_file

    print("Commande shell", cmd)

    p = subprocess.Popen([cmd], stdout = subprocess.PIPE,stdin=subprocess.PIPE,
                                stderr = subprocess.PIPE, shell=True)

def main_lol(optimus, u):

    optimus = int(optimus)

    if u == "l":
        url = "http://192.168.1.18:8080/land.sqlite"
    elif u == "p":
        url = "http://jeuxlibres.org:8080/land.sqlite"
    else:
        os._exit(0)

    download_file(url)

    run_blender(optimus)

    # IRC
    t = Thread(target=irc_bot)
    t.start()

    # UDP
    main_server()


if __name__ == "__main__":
    print("\n   Script local du jeu Land Of Love")
    print("   En python 3, serveur asyncio et bot IRC\n\n")

    print('''Il faut 2 arguments:
    - 0 sans optimus, 1 avec optimus
    - l en local chez moi, p avec ip publique
    ''')

    optimus = sys.argv[1]
    url = sys.argv[2]

    print("Argument", optimus, url)

    main_lol(optimus, url)
