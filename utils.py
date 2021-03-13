import socket
import tkinter as tk
import re
import queue
import os
import heapq
import random
import json

from tkinter import ttk
from thonny import get_workbench
from thonny.editors import Editor

ALL_REGEX = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")

MIN_FREE_ID = 0
FREE_IDS = []

def get_instr_direct(event, editor_id, user_id = -1, cursor_pos = "", in_insert = False, debug = False):
    if debug:
        print("direct")
    
    instr = dict()
    text = event.widget

    if ALL_REGEX.match(event.char):
        instr["type"] = "I"
        instr["num"] = random.randint(0, 100000)
        instr["pos"] = text.index(tk.INSERT)
        
        if user_id == -1:
            instr["doc"] = editor_id
            instr["text"] = event.char
    
    elif event.keysym == "BackSpace":
        pos = text.index(tk.INSERT)

        try:
            col = int(pos[pos.find('.') + 1 :])
            pos = pos[ : pos.find('.') + 1] + str(col - 1)
        except: 
            pass

        instr["type"] = "D"
        instr["num"] = random.randint(0, 100000)
        instr["start"] = pos

    else:
        return None

    if user_id != -1 and len(instr) != 0:
        instr["user"] = user_id
        instr["user_pos"] = cursor_pos
        instr["doc"] = editor_id
        instr["text"] = event.char
    
    if debug:
        print(instr)
    return instr

def get_instr_latent(event, editor_id, is_insert, user_id = -1, debug = False):
    print("latent")
    instr = dict()

    if is_insert:
        instr["type"] = "I"
        instr["num"] = random.randint(0, 100000)
        instr["pos"] = event.text_widget.index(event.index)


        if user_id != -1:
            instr["user"] = user_id
            instr["user_pos"] = event.cursor_after_change
            instr["doc"] = editor_id
            instr["text"] = event.text
    else:
        instr["type"] = "D"
        instr["num"] = random.randint(0, 100000)
        instr["start"] = event.text_widget.index(event.index1)

        if event.index2 != None:
            instr["end"] = event.text_widget.index(event.index2)
        
        if user_id != -1 and instr != None:
            instr["user"] = user_id
            instr["user_pos"] = event.cursor_after_change
            instr["doc"] = editor_id    
    return instr

def get_new_id():
    global MIN_FREE_ID
    global FREE_IDS

    if len(FREE_IDS) == 0:
        temp = MIN_FREE_ID
        MIN_FREE_ID += 1
        return temp
    
    else:
        return heapq.heappop(FREE_IDS)

def free_id(val):
    heapq.heappush(FREE_IDS, val)

def send_all(sock, lock, msg):
    sock.sendall(bytes(msg, encoding="utf-8"))

def receive_json(sock):
    while True:
        pass

def publish_delete(broadcast_widget, source, cursor_after_change, index1, index2 = None):
    broadcast_widget.event_generate("LocalDelete", 
                                    index1 = source.index(index1),
                                    index2 = source.index(index2) if index2 else None,
                                    text_widget = source,
                                    cursor_after_change = cursor_after_change)

def publish_insert(broadcast_widget, source, cursor_after_change, index, text):
    broadcast_widget.event_generate("LocalInsert", 
                                    index = source.index(index),
                                    text = text,
                                    text_widget = source,
                                    cursor_after_change = cursor_after_change)

def str_to_editor(title, body):
    wb = get_workbench()
    notebook = wb.get_editor_notebook()
    new_editor = Editor(notebook)

    wb.event_generate("NewFile", editor=new_editor)
    ttk.Notebook.add(notebook, new_editor, text = title)
    notebook.select(new_editor)

    notebook.update_editor_title(new_editor, title = title)

    new_editor.focus_set()
    tk.Text.insert(new_editor.get_text_widget(), "0.0", body)

    return new_editor

def intiialize_documents(doc_list):
    editors = dict()
    for i in doc_list:
        doc = doc_list[i]
        editor = str_to_editor(doc["title"], doc["content"])
        editors[editor] = i

    return editors