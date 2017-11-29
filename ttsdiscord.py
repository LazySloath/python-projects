# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:33:32 2017

@author: User

Automatic tts in Discord
"""

import win32api
import pywinauto
from win32gui import FindWindow
import pyperclip
import pyautogui

#connect to discord
chatName = input('Enter your chat name (e.g. #general - Discord): ')
hwnd = FindWindow(None, chatName)
print(hwnd)
app = pywinauto.Application()
app.connect(handle = hwnd)
dlg = app.top_window()

#dictionary for conversion of key to shift+key
conversiondict = {32:32, 222:(39,34), 188:(44,60), 189:(45,95), 190:(46,62), \
                  191:(47,63), 48:41, 49:33, 50:64, 51:35, 52:36, 53:37, \
                  54:94,55:38, 56:42,57:40, 186:(59,58), 187:(61,43), \
                  219:(91,123), 220:(92,124), 221:(93,125), 96:126}

def EnterPressed():
    enterState = win32api.GetAsyncKeyState(13)
    if enterState == -32767:
        return True
    return False

def BackspacePressed():
    backspaceState = win32api.GetAsyncKeyState(8)
    if backspaceState == -32767:
        return True
    return False

def ZeroPressed():
    zeroState = win32api.GetAsyncKeyState(48)
    if zeroState == -32767:
        return True
    return False

def ShiftHeld():
    shiftState = win32api.GetKeyState(16)
    if shiftState < 0:
        return True
    return False

def FormSentence():
    sentence = ''
    while True:
        #end of sentence
        if EnterPressed():
            return(sentence)
        #simulate backspace
        if BackspacePressed():
            sentence = sentence[:-1]
        #normal typing
        for i in range(32, 222):
            if win32api.GetAsyncKeyState(i) == -32767:
                #letters
                if i in range(65,91):
                    if ShiftHeld():
                        sentence += chr(i)
                    else:
                        sentence += chr(i + 32)
                #special keys
                elif i in range(186, 223):
                    if ShiftHeld():
                        sentence += chr(conversiondict[i][1])
                    else:
                        sentence += chr(conversiondict[i][0])
                #other keys
                else:
                    try:
                        if ShiftHeld():
                            sentence += chr(conversiondict[i])
                        else:
                            sentence += chr(i)
                    except KeyError:
                        pass

while True:
    #set '0' as pause button
    if ZeroPressed():
        print('pause')
        while True:
            #resume button
            if ZeroPressed():
                print('resume')
                break
    #start of sentence
    if EnterPressed():
        print('initialising sentence')
        sentence = '/tts ' + FormSentence()
        pyperclip.copy(sentence)
        #simulate ctrl+v in discord
        pyautogui.keyDown('ctrl')
        dlg.send_keystrokes('v')
        pyautogui.keyUp('ctrl')
        #send message
        dlg.send_keystrokes('{ENTER}')
        print(sentence)
        
'''
'''
