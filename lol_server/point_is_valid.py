#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import ast

'''
Message brut [22, 2, 2, 2] <class 'list'>
Message décodé 22 <class 'int'>
'''


def to_utf8(msg):
    '''msg est un message, soit en bytes soit en utf-8.
    Retourne le message en unicode, sinon None.
    '''

    #print("\nMessage brut", msg, type(msg))

    if isinstance(msg, bytes):
        msg_dec = msg.decode("utf-8")
        #print("Message décodé uft-8", msg_dec, type(msg_dec))

    elif isinstance(msg, str):
        msg_dec = msg

    elif isinstance(msg, list):
        msg_dec = msg

    else:
        #print("Message non décodé")
        msg_dec = None

    return msg_dec

def ast_eval(msg):
    if isinstance(msg, list):
        msg_eval = msg
    else:
        try:
            msg_eval = ast.literal_eval(msg)
            #print("Eval ok", msg_eval, type(msg_eval))
        except:
            #print("Message non conforme", msg, type(msg))
            msg_eval = None

    try:
        if msg_eval:
            x, y, z , c = msg_eval[0], msg_eval[1], msg_eval[2], msg_eval[3]
            return True, x, y, z , c
    except:
        return False, None, None, None, None

def only_integers(x, y, z, c):
    '''Retourne True si 4 entiers'''
    try:
        x = int(x)
        y = int(y)
        z = int(z)
        c = int(c)
        return True, x, y, z, c
    except:
        return False, None, None, None, None

def in_range(x, y, z, c):
    '''x de 0 à 99
    y de 0 à 99
    z de 0 à 99
    c de 0 à 8
    '''

    verif = True
    for n in [x, y, z]:
        if n < 0 or n > 99:
            verif = False
            break
        if c < 0 or c > 8:
            verif = False
            break
    return verif, x, y, z, c

def point_is_valid(msg):
    '''msg est un message reçu non décodé:
    '''
    #print("Message à valider", msg, type(msg))

    is_valid, x, y, z , c = False, None, None, None, None

    try:
        msg_dec = to_utf8(msg)
        is_valid, x, y, z, c = ast_eval(msg_dec)
        if is_valid:
            is_valid, x, y, z, c = only_integers(x, y, z, c)
            if is_valid:
                is_valid, x, y, z, c = in_range(x, y, z, c)
                print("Validation du point", is_valid, x, y, z, c)
                return is_valid, x, y, z, c
    except:
        return False, None, None, None, None



if __name__ == "__main__":
    # du msg brut
    # les listes ne sont pas reconnue dans json
    l = [   [15, 1, 1, 1],
            ("(3, 1, 1, 1)"),
            ("(4, 1, 1)"),
            ("(5, 1, 1, 1 ,1)"),
            ("(D, a, e, r)")]

    for msg in l:
        point_is_valid(msg)

    point_is_valid(["[1, 2, 3, 4]"])
