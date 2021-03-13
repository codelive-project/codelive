
import os
import types
import tkinter as tk

from tkinter.messagebox import showinfo
from tkinter import Message, Button
from tkinter.commondialog import Dialog

from thonny import get_workbench
from thonny.tktextext import EnhancedText, TweakableText
from thonny.codeview import SyntaxText

from thonny.plugins.codelive.client import Session

from thonny.plugins.codelive.views.create_session import CreateSessionDialog
from thonny.plugins.codelive.views.join_session import JoinSessionDialog
from thonny.plugins.codelive.views.toolbar_popup import ToolbarPopup 

import thonny.plugins.codelive.patched_callbacks as pc
import thonny.plugins.codelive.utils as utils

WORKBENCH = get_workbench()
MENU_NAME = "CodeLive"
session = None

DEBUG = True

def create_session_vanilla(data = None):
    global session
    data_session = data or {
        "name": "Host Doe",
        "topic": "test_topic_1234",
        "broker": "test.mosquitto.org",
        "shared_editors": WORKBENCH.get_editor_notebook().winfo_children()
    }

    session = Session.create_session(name = data_session["name"],
                                     topic = data_session["topic"],
                                     broker = data_session["broker"],
                                     shared_editors = data_session["shared_editors"])
    session.start_session()

def create_session():
    top = CreateSessionDialog(WORKBENCH)
    WORKBENCH.wait_window(top)

    # if top data is none, then the user chose to cancel the session
    if top.data == None:
        return

    create_session_vanilla(top.data)

def join_session_vanilla(data = None):
    global session
    data_sess = data or {
        "name": "Join Doe",
        "topic": "test_topic_1234",
        "broker": "test.mosquitto.org"
    }
    session = Session.join_session(name = data_sess["name"],
                                   topic = data_sess["topic"],
                                   broker = data_sess["broker"])
    
    session.start_session()

def join_session():
    top = JoinSessionDialog(WORKBENCH)
    WORKBENCH.wait_window(top)

    #  if top data is none, then the user chose to cancel the session
    if top.data == None:
        return

    join_session_vanilla(top.data)

def end_session():
    pass

def leave_session():
    pass

def session_status():
    pass

def live_session():
    global session
    return session != None

def toolbar_callback():
    menu = ToolbarPopup(WORKBENCH, get_commands())

    try: 
        menu.tk_popup(WORKBENCH.winfo_pointerx(),
                                 WORKBENCH.winfo_pointery())
    finally: 
        menu.grab_release()

def get_commands():
    global session
    global MENU_NAME

    commnads = None
    commands = {
        19: [
            {
                "command_id": "codelive",
                "menu_name": MENU_NAME,
                "command_label": "Start a Live Collaboration Session",
                "handler" : toolbar_callback,
                "position_in_group": "end",
                "tester": None,
                "image" : os.path.join(os.path.dirname(__file__), "res/people-yellow-small.png"),
                "caption" : "CodeLive: MQTT based collaboration plugin",
                "include_in_menu" : False,
                "include_in_toolbar" : True,
                "bell_when_denied" : True,
                "enable": lambda: False
            }
        ],

        20: [
            {
                "command_id": "codelive_host",
                "menu_name": MENU_NAME,
                "command_label": "Create a New Session",
                "handler" : create_session,
                "position_in_group": "end",
                "image" : None,
                "tester": lambda: not live_session(),
                "caption" : "Create new collaborative session",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": lambda: not live_session()
            },
            {
                "command_id": "codelive_join",
                "menu_name": MENU_NAME,
                "command_label": "Join an Existing Session",
                "handler" : join_session,
                "position_in_group": "end",
                "image" : None,
                "tester": lambda: not live_session(),
                "caption" : "Join an existing collaborative session",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": lambda: not live_session()
            },
            # For testing only
            {
                "command_id": "codelive_host_t",
                "menu_name": MENU_NAME,
                "command_label": "Create Test",
                "handler" : create_session_vanilla,
                "position_in_group": "end",
                "image" : None,
                "tester": lambda: not live_session(),
                "caption" : "Create Test",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": lambda: not live_session()
            },
            # For testing only
            {
                "command_id": "codelive_join_t",
                "menu_name": MENU_NAME,
                "command_label": "Join Test",
                "handler" : join_session_vanilla,
                "position_in_group": "end",
                "image" : None,
                "tester": lambda: not live_session(),
                "caption" : "Join Test",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": lambda: not live_session()
            },
        ],

        21 : [
            {
                "command_id": "codelive_end",
                "menu_name": MENU_NAME,
                "command_label": "End Session",
                "handler" : end_session,
                "position_in_group": "end",
                "image" : None,
                "tester": live_session,
                "caption" : "End current session (for Hosts only)",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": live_session
            },
            {
                "command_id": "codelive_leave",
                "menu_name": MENU_NAME,
                "command_label": "Leave Session",
                "handler" : leave_session,
                "position_in_group": "end",
                "image" : None,
                "tester": live_session,
                "caption" : "Leave current session (for Hosts only)",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": live_session
            }
        ],
        22 : [
            {
                "command_id": "codelive_show",
                "menu_name": MENU_NAME,
                "command_label": "Show Current Session",
                "handler" : session_status,
                "position_in_group": "end",
                "image" : None,
                "tester": live_session,
                "caption" : "Show the status of the current session",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": live_session
            }
        ],
        23 : [
            {
                "command_id": "codelive_help",
                "menu_name": MENU_NAME,
                "command_label": "Help",
                "handler" : session_status,
                "position_in_group": "end",
                "image" : None,
                "tester": None,
                "caption" : "Show Help for How to use Codelive",
                "include_in_menu" : True,
                "include_in_toolbar" : False,
                "bell_when_denied" : True,
                "enable": lambda: True
            }
        ]
    }
    
    return commands

def add_menu_items():
    groups = get_commands()
    
    for group in sorted(groups.keys()):
        for item in groups[group]:
            WORKBENCH.add_command(command_id = item["command_id"],
                                    menu_name = item["menu_name"],
                                    command_label = item["command_label"],
                                    handler = item["handler"],
                                    position_in_group= item["position_in_group"],
                                    image = item["image"],
                                    tester = item["tester"],
                                    group = group,
                                    caption = item["caption"],
                                    include_in_menu= item["include_in_menu"],
                                    include_in_toolbar = item["include_in_toolbar"],
                                    bell_when_denied = item["bell_when_denied"])

def load_plugin():
    add_menu_items()

    EnhancedText.insert = pc.patched_insert
    EnhancedText.delete = pc.patched_delete
