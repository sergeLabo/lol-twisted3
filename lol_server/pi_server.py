#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pi_server.py

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
Script du serveur du jeu LandOfLove sur mon serveur personnel.

Python3:
    pas de twisted

IRC:
    Ecoute l'IRC pour ajouter les cubes dans la db

HTTPServer:
    pour envoyer la base de données sans la compresser
"""


import sys
import gzip
import threading
from time import time, sleep
import datetime
import ast

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from jaraco.stream import buffer

import http.server
import socketserver

from my_db import MyDataBase
from point_is_valid import point_is_valid

class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.my_db = MyDataBase("./land.sqlite")

    def on_nicknameinuse(self, c, e):
        print("Nick name in use, ajout de _ ")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("Welcome")
        c.join(self.channel)

    def on_privmsg(self, c, e):
        print("on_privmsg réception d'un message privé ".format(c, e))
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        '''Evénement sur message public.'''

        self.message_sorting(e)

    def message_sorting(self, e):
        '''Les message système sont du type: test:die'''

        # Découpe le message au niveau des :
        a = e.arguments[0].split(":", 1)  # a est une liste

        msg = ""
        try:
            if len(a) > 0:
                for n in range(len(a)):
                    msg += str(a[n])
        except:
            print("Message IRC refusé")

        print("Dans on_pubmsg, le message est: {}".format(msg))
        # Enregistrement dans la db si c'est un cube
        self.add_cube(msg)

        # Message Système du Bot
        nick = self.connection.get_nickname()
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(nick):
            self.do_command(e, a[1].strip())

    def add_cube(self, cube):
        is_valid, x, y, z , c = point_is_valid(cube)

        if is_valid:
            # Si c > 0, ajout du cube
            if c != 0:
                self.my_db.record_in_db(x, y, z , c)
                print("Ajout du cube: {} {} {} {}".format(x, y, z, c))
            # Si c = 0, suppression du cube
            else:
                self.my_db.delete_in_db(x, y, z)
                print("Suppression du cube:{} {} {}".format(x, y, z))
        else:
            print("Le message reçu n'est pas un point")

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: {}".format(text))

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


def create_irc_login():
    '''Retourne un login IRC.'''

    # temps en entier comme str
    number = str(int(time()))
    number = number[5:]
    # Create unique IRC login
    nick = "Lol" + str(number)

    print("User IRC {}".format(nick))
    return nick

def run_httpserver(addr):
    '''host = ""
    port = 8080
    addr = host, port
    '''

    print("HTTP Serving at HOST {} port {}".format(addr[0], addr[1]))

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(addr, Handler)
    httpd.serve_forever()

def run_IRC_bot(irc_info):
    server = irc_info[0]
    port = int(irc_info[1])
    channel = irc_info[2]

    nickname = create_irc_login()
    bot = IrcBot(channel, nickname, server, port)
    print("IRC Bot ok")
    bot.start()

def print_strftime_thread():
    '''Pour que le nohup soit mis à jour.'''

    while 1:
        print("Je tourne: {0:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now()))
        sleep(120)  # 2 mn

def main(addr, irc_info):

    print("Server sur Raspberry Pi")

    # Print pour nohup.txt
    thread1 = threading.Thread(target=print_strftime_thread)
    thread1.start()

    # HTTP Server
    thread2 = threading.Thread(target=run_httpserver, args=(addr, ))
    thread2.start()
    print("HTTP Server ok")

    # IRC
    print("IRC OK")
    run_IRC_bot(irc_info)


if __name__ == '__main__':

    # Pour le serveur http
    host = ""
    port = 8080
    addr = host, port
    print("HTTP: {}".format(addr))

    # Pour l'IRC
    server = "jeuxlibres.org"
    port = 6667
    channel = "#jeuxlibres"
    irc_info = server, port, channel
    print("IRC: {} {} {}".format(server, port, channel))

    main(addr, irc_info)
