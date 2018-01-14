# coding=utf8
import os
import re
import subprocess
from flask import jsonify
import xmltodict

def update_keyboard_config(XKBMODEL='pc105', XKBLAYOUT='us', XKBVARIANT='nodeadkeys', XKBOPTIONS='', BACKSPACE='guess'):
    '''
    edit keyboard configuration settings in /etc/default/keyboard

    Keyword Arguments:
        XKBMODEL {str} -- [Specifies the XKB keyboard model name.] (default: {'pc105'})
        XKBLAYOUT {str} -- [Specifies the XKB keyboard layout name.] (default: {'us'})
        XKBVARIANT {str} -- [Specifies the XKB keyboard variant components.] (default: {'nodeadkeys'})
        XKBOPTIONS {str} -- [Specifies the XKB keyboard option components.] (default: {''})
        BACKSPACE {str} -- [Determines the behavior of <BackSpace> and <Delete> keys on the console.] (default: {'guess'})
    '''
    # Modify /etc/default/keyboard
    #
    # Check /usr/share/doc/keyboard-configuration/README.Debian for
    # documentation on what to do after having modified this file.
    # The following variables describe your keyboard and can have the same
    # values as the XkbModel, XkbLayout, XkbVariant and XkbOptions options
    # in /etc/X11/xorg.conf.

    #XKBMODEL="pc105"
    #XKBLAYOUT="de"
    #XKBVARIANT="nodeadkeys"
    #XKBOPTIONS="terminate:ctrl_alt_bksp"
    #BACKSPACE="guess"

    # If you don’t want to use the XKB layout on the console, you can
    # specify an alternative keymap. Make sure it will be accessible
    # before /usr is mounted.
    # KMAP=/etc/console-setup/defkeymap.kmap.gz
    # Apply config to the console
    # setupcon
    # Apply config change to X-Windows
    # udevadm trigger –subsystem-match=input –action=change
    return()

def get_keyboard_config():
    '''
    Returns the current keyboard configuration from /etc/default/keyboard
    '''
    keyboard_config = {}
    config = os.popen('grep -v "#" /etc/default/keyboard').read().splitlines()
    for option in config:
        if option:
            name,value = option.split('=')
            value = value.replace('"','')
            keyboard_config[name] = value
    return (keyboard_config)

def get_keyboard_config_data():
    return jsonify( xml2dict('/usr/share/X11/xkb/rules/base.xml') )

def xml2dict(xml_file, xml_attribs=True):
    with open(xml_file, "rb") as f:
        d = xmltodict.parse(f, xml_attribs=xml_attribs)
        return d
