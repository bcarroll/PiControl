#!/usr/bin/python
# coding=utf-8
import os
from pwd import getpwall
from grp import getgrgid, getgrall

from flask import jsonify

from lib._logging import logging

def get_users():
    users  = {}
    for user in getpwall():
        name     = user[0]    #Login name
        uid      = user[2]    #Numerical user ID
        gid      = user[3]    #Numerical group ID
        gecos    = user[4]    #User name or comment field
        home_dir = user[5]    #User home directory
        shell    = user[6]    #User command interpreter
        users[name] = {
            'uid': uid,
            'gid': gid,
            'group_name': getgrgid(gid)[0],
            'gecos': gecos.replace(',,,',''),
            'home_dir': home_dir,
            'shell': shell
        }
    return(jsonify(users))

def get_groups():
    groups = {}
    for group in getgrall():
        name    = group[0]    #the name of the group
        gid     = group[2]    #the numerical group ID
        members = group[3]    #all the group member’s user names
        groups[name] = {
            'gid': gid,
            'members': members
        }
    return(jsonify(groups))
