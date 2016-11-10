#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## labircbot.py

'''
Bot IRC construit avec le module python

python3-irc

En terminal:
* sudo apt-get install python3-pip
ou
* sudo pip3 install irc

Compatible python 2 et 3

Cette version envoie des cubes sur IRC jeuxlibre
'''

import os
from time import time, sleep
import json

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

try:
    from bge import logic as gl
except:
    gl = None


class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        '''le bot est "self'''

        self.channel = channel
        self.message = ""

        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname,
                                            nickname)
        irc.bot.SingleServerIRCBot.start(self)

    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse ", c, e)
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("\nLe serveur IRC de jeuxlibres.org vous souhaite la bienvenue\n")
        c.join(self.channel)
        self.connection.privmsg(self.channel, u"Test on Welcome")

        self.simul_lot_cube()

    def on_privmsg(self, c, e):
        print("on_privmsg", c, e, type(e))
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        # a est une liste
        a = e.arguments[0].split(":", 1)
        if len(a) > 0:
            msg = ""
            for n in range(len(a)):
                msg += str(a[n])
                self.message = msg
                if gl:
                    gl.irc_text = msg
            print("Dans on_pubmsg, le message est: {}".format(msg))

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

    def send_msg(self, msg):
        '''msg est soit bytes, soit unicode'''

        self.connection.privmsg(self.channel, msg)

    def simul_lot_cube(self):
        '''Envoi d'un lot de cube sur jeuxlibres.
        Lancé dans on_welcome()
        '''

        for c in [6, 0]:
            for i in range(10):
                x = i + 50
                for j in range(10):
                    y = j + 50
                    for k in range(1):
                        for a  in [15,16,17,18,19]:
                            z = k + a
                            sleep(1)
                            msg = json.dumps((x, y, z, c))
                            try:
                                self.connection.privmsg(self.channel, msg)
                                print("Message à IRC", msg)
                            except:
                                print("Déconnecté !!")


def irc_bot():
    print("Bot IRC lancé")
    server = 'jeuxlibres.org'
    port = 6667
    channel = "#jeuxlibres"
    nickname = create_irc_login()
    IrcBot(channel, nickname, server, port)

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


if __name__ == '__main__':
    irc_bot()
