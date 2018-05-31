# -*- coding: utf-8 -*-
"""
Created on Fri May 25 20:34:16 2018

@author: User

what to improve:
AI behaviour - if winning position, emulate players previous move for pairs
different AI settings
"""

import pygame
from pygame.locals import *
import sys
import random

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

WHITE = (250,250,250)
BLACK = (0,0,0)
GREY = (231,231,231)
DARKGREY = (180,180,180)
RED = (255,0,0)
BLUE = (0,0,255)

stickassets = []
for i in range(9):
    row = []
    for j in range(i):
        row.append((340-i*20+j*40,20+i*50))
    stickassets.append(row)

def main():
    global DISPLAYSURF,buttonSound,swipeSound,whooshSound,winSound,multiplay
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    # Window settings
    pygame.display.set_caption('Nim')
    icon = pygame.image.load('nimpygame.png')
    pygame.display.set_icon(icon)
    # Sounds
    pygame.mixer.music.load('bgm.mp3')
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1,0.0)
    buttonSound = pygame.mixer.Sound('button.wav')
    buttonSound.set_volume(0.1)
    swipeSound = pygame.mixer.Sound('swipe.wav')
    swipeSound.set_volume(0.1)
    whooshSound = pygame.mixer.Sound('whoosh.wav')
    whooshSound.set_volume(0.1)
    winSound = pygame.mixer.Sound('win.wav')
    winSound.set_volume(0.1)
    # Main game loop
    while True:
        rows = None
        multiplay = False
        if showStartScreen():
            rows = showRowSelect()
            if rows and multiplay:
                runGame2(rows)
            elif rows:
                runGame(rows)
        else:
            showRules()
        

def runGame(rows):
    """Game logic"""
    lines = []
    sticks = []
    crossed = []
    for row in stickassets[:rows+1]:
        for pair in row:
            sticks.append(pygame.Rect(pair[0],pair[1],3,40))
    player1 = True
    error = False
    # Hacky way to get back button
    back = displayGame(sticks,crossed,lines,player1,error,True)
    pygame.display.update()
    drawing = False
    while sticks:
        checkQuit()
        if not player1:
            # Computer 'thinking'
            pygame.time.delay(800)
            player1 = not player1
            line = analyse(sticks)
            for stick in sticks:
                if stick.colliderect(line):
                    any_crossed += 1
                    crossed.append(stick)
            for stick in crossed:
                if stick in sticks:
                    sticks.remove(stick)       
            lines.append(line)
            # AI draw line animation
            x,y = line.topleft
            width = line.width
            for i in range(width):
                pygame.draw.line(DISPLAYSURF,RED,(x+i,y),(x+i,y+2))
                pygame.display.update()
                pygame.time.delay(2)
            displayGame(sticks,crossed,lines,player1,error,True)
            swipeSound.play()
            pygame.display.update()
            pygame.event.clear()
            
        else:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    drawing = False
                    if checkBack(back,event.pos):
                        buttonSound.play()
                        return
                    else:
                        any_crossed = 0
                        cross_crossed = 0
                        x1 = event.pos[0]
                        if x1 >= x:
                            line = pygame.Rect(x,y-1,x1-x+1,3)
                        else:
                            line = pygame.Rect(x1,y-1,x-x1+1,3)
                        # Check what sticks are crossed
                        for stick in crossed:
                            if stick.colliderect(line):
                                cross_crossed += 1
                        if not cross_crossed:
                            for stick in sticks:
                                if stick.colliderect(line):
                                    any_crossed += 1
                                    crossed.append(stick)
                            if any_crossed:
                                # Update sticks
                                for stick in crossed:
                                    if stick in sticks:
                                        sticks.remove(stick)
                                player1 = not player1
                                lines.append(line)
                                displayGame(sticks,crossed,lines,player1,error,True)
                                swipeSound.play()
                                pygame.display.update()
                            else:
                                error = True
                                whooshSound.play()
                                displayGame(sticks,crossed,lines,player1,error,True)
                                pygame.display.update()
                                error = False
                                
                        else:
                            error = True
                            whooshSound.play()
                            displayGame(sticks,crossed,lines,player1,error,True)
                            pygame.display.update()
                            error = False
                            
                elif event.type == MOUSEBUTTONDOWN:
                    x,y = event.pos
                    drawing = True
                elif event.type == MOUSEMOTION and drawing:
                    displayGame(sticks,crossed,lines,player1,error,True)
                    pygame.draw.line(DISPLAYSURF,RED,(x,y),
                                     (event.pos[0],y),3)
                    pygame.display.update()
    # Show who won
    if player1:
        makeText(20,'Player wins!',BLACK,GREY,240,0,160,30)
    else:
        makeText(20,'AI wins!',BLACK,GREY,240,0,160,30)
    winSound.play()
    pygame.display.update()
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if checkBack(back,event.pos):
                    buttonSound.play()
                    return
                
def runGame2(rows):
    """Game logic"""
    lines = []
    sticks = []
    crossed = []
    for row in stickassets[:rows+1]:
        for pair in row:
            sticks.append(pygame.Rect(pair[0],pair[1],3,40))
    player1 = True
    error = False
    # Hacky way to get back button
    back = displayGame(sticks,crossed,lines,player1,error)
    pygame.display.update()
    drawing = False
    while sticks:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                drawing = False
                if checkBack(back,event.pos):
                    buttonSound.play()
                    return
                else:
                    any_crossed = 0
                    cross_crossed = 0
                    x1 = event.pos[0]
                    if x1 >= x:
                        line = pygame.Rect(x,y-1,x1-x+1,3)
                    else:
                        line = pygame.Rect(x1,y-1,x-x1+1,3)
                    # Check what sticks are crossed
                    for stick in crossed:
                        if stick.colliderect(line):
                            cross_crossed += 1
                    if not cross_crossed:
                        for stick in sticks:
                            if stick.colliderect(line):
                                any_crossed += 1
                                crossed.append(stick)
                        if any_crossed:
                            # Update sticks
                            for stick in crossed:
                                if stick in sticks:
                                    sticks.remove(stick)
                            player1 = not player1
                            lines.append(line)
                            displayGame(sticks,crossed,lines,player1,error)
                            swipeSound.play()
                            pygame.display.update()
                        else:
                            error = True
                            whooshSound.play()
                            displayGame(sticks,crossed,lines,player1,error)
                            pygame.display.update()
                            error = False
                            
                    else:
                        error = True
                        whooshSound.play()
                        displayGame(sticks,crossed,lines,player1,error)
                        pygame.display.update()
                        error = False
                        
            elif event.type == MOUSEBUTTONDOWN:
                x,y = event.pos
                drawing = True
            elif event.type == MOUSEMOTION and drawing:
                displayGame(sticks,crossed,lines,player1,error)
                pygame.draw.line(DISPLAYSURF,RED,(x,y),
                                 (event.pos[0],y),3)
                pygame.display.update()
    # Show who won
    if player1:
        makeText(20,'Player 1 wins!',BLACK,GREY,240,0,160,30)
    else:
        makeText(20,'Player 2 wins!',BLACK,GREY,240,0,160,30)
    winSound.play()
    pygame.display.update()
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if checkBack(back,event.pos):
                    buttonSound.play()
                    return

def displayGame(sticks,crossed,lines,player1,error,AI=False):
    """Helper function to update display during runGame"""
    DISPLAYSURF.fill(WHITE)
    # Draw back button
    back = makeBack()
    # Draw error message
    if error:
        makeText(20,'Invalid move!',BLACK,GREY,500,0,140,30)
    # Draw player message
    if player1 and AI:
        makeText(20,'Player to move',BLACK,GREY,240,0,160,30)
    elif player1:
        makeText(20,'Player 1 to move',BLACK,GREY,240,0,160,30)
    elif AI:
        makeText(20,'AI to move',BLACK,GREY,240,0,160,30)
    else:
        makeText(20,'Player 2 to move',BLACK,GREY,240,0,160,30)
    # Draw sticks
    for stick in sticks:
        pygame.draw.rect(DISPLAYSURF,BLACK,stick)
    # Draw crossed sticks
    for stick in crossed:
        pygame.draw.rect(DISPLAYSURF,DARKGREY,stick)
    # Draw lines
    for line in lines:
        pygame.draw.rect(DISPLAYSURF,DARKGREY,line)
    return back

def showStartScreen():
    """Screen for start"""
    global multiplay
    DISPLAYSURF.fill(WHITE)
    # Make title
    makeText(85,'Nim',BLACK,GREY,180,80,280,150)
    # Make start
    singleplayer = makeText(20,'1-Player',BLACK,GREY,220,280,200,30)
    # Make 2 player
    multiplayer = makeText(20,'2-Player',BLACK,GREY,220,320,200,30)
    # Make rules
    rules = makeText(20,'Rules',BLACK,GREY,220,360,200,30)
    pygame.display.update()
    
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if singleplayer.collidepoint(event.pos):
                    buttonSound.play()
                    return True
                elif multiplayer.collidepoint(event.pos):
                    multiplay = True
                    buttonSound.play()
                    return True
                elif rules.collidepoint(event.pos):
                    buttonSound.play()
                    return False    

def showRowSelect():
    """Screen for row select"""
    DISPLAYSURF.fill(WHITE)
    makeText(20,'Choose number of rows',BLACK,GREY,200,0,240,30)
    # Make numbers
    numberRects = []
    for i in range(3):
        numberRect = makeText(40,str(i+3),BLACK,GREY,110+i*160,120,100,100)
        numberRects.append(numberRect)
    for i in range(3):
        numberRect = makeText(40,str(i+6),BLACK,GREY,110+i*160,280,100,100)
        numberRects.append(numberRect)
    # Make back
    back = makeBack()
    pygame.display.update()
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if checkBack(back,event.pos):
                    buttonSound.play()
                    return
                for rect in numberRects:
                    if rect.collidepoint(event.pos):
                        buttonSound.play()
                        pygame.display.update()
                        return numberRects.index(rect) + 3

def showRules():
    """Screen for rules"""
    DISPLAYSURF.fill(WHITE)
    # Make back button
    back = makeBack()
    rules = ('1. The player who crosses out the last stick loses',
             '2. You must cross out at least one stick each turn',
             '3. You may only cross out sticks in a horizontal line',
             '4. You may not cross over sticks that have already been crossed')
    makeText(30,'Rules',BLACK,GREY,240,10,160,50)
    for i in range(4):
        makeText(20,rules[i],BLACK,GREY,40,110+i*50,560,30)
    pygame.display.update()
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if checkBack(back,event.pos):
                    buttonSound.play()
                    return
    
def makeText(fontsize,text,color,bgcolor,x,y,rwidth,rheight):
    """Helper function to make text boxes"""
    textSurf = pygame.font.SysFont('Calibri',fontsize).render(text,True,color)
    twidth, theight = textSurf.get_size()
    textRect = pygame.Rect(x,y,rwidth,rheight)
    pygame.draw.rect(DISPLAYSURF,bgcolor,textRect)
    #Draw border
    pygame.draw.rect(DISPLAYSURF,DARKGREY,(x,y,rwidth,rheight),2)
    a,b = textRect.center
    DISPLAYSURF.blit(textSurf,(a-twidth/2, b-theight/2))
    pygame.draw.rect(DISPLAYSURF,DARKGREY,(0,0,639,479),2)
    return textRect

def checkQuit():
    """Check if player quits"""
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()

def makeBack():
    """Helper function for back button"""
    return makeText(20,'Back',BLACK,GREY,0,0,100,30)

def checkBack(back,event):
    """Helper function for back button"""
    return back.collidepoint(event)
    
def analyse(sticks):
    """Computer analysis"""
    xy = []
    currentgroup = [sticks[0].topleft]
    for i in range(1, len(sticks)):
        stick = sticks[i]
        if stick.top == currentgroup[0][1] and stick.left == currentgroup[-1][0] + 40:
            currentgroup.append(stick.topleft)
        else:
            xy.append(currentgroup)
            currentgroup = [stick.topleft]
    xy.append(currentgroup)
    xy.sort(key=lambda x: len(x))
    lengths = [len(group) for group in xy]
    move = firstpass(lengths,xy)
    if move:
        return move
    return nextpass(lengths,xy)

def makemove(x,x1,y):
    """Helper function for analyse"""
    move = pygame.Rect(x,y,x1-x,3)
    return move

def firstpass(lengths,xy):
    """AI Logic for first look at problem"""
    length = len(lengths)
    if length == 1:
        y = xy[0][0][1] + 20
        x = xy[0][0][0] - 10
        # If only 1 stick left, cancel it and lose
        if lengths[0] == 1:
            x1 = x + 23
            return makemove(x,x1,y)
        # Else, cancel all but 1 for the win
        else:
            x1 = xy[0][-2][0] + 13
            return makemove(x,x1,y)
    
    elif length == 2:
        # If 1 is 1, cancel other
        if lengths[0] == 1:
            y = xy[1][0][1] + 20
            x = xy[1][0][0] - 10
            x1 = xy[1][-1][0] + 13
            return makemove(x,x1,y)
        # If is pair, just cancel 1 from one
        elif lengths[0] == lengths[1]:
            n = random.randrange(lengths[0])
            y = xy[0][n][1] + 20
            x = xy[0][n][0] - 10
            x1 = x + 23
            return makemove(x,x1,y)
        # Else, make pair
        else:
            cancellations = lengths[1] - lengths[0]
            y = xy[1][0][1] + 20
            x = xy[1][0][0] - 10
            x1 = x + (cancellations-1)*40 + 23
            return makemove(x,x1,y)
    # If all (possibly except last row) are 1s
    elif lengths[-2] == 1:
        # odd 1s: cancel all in last row
        if length%2 == 0:
            y = xy[-1][0][1] + 20
            x = xy[-1][0][0] - 10
            x1 = xy[-1][-1][0] + 13
            return makemove(x,x1,y)
        # even 1s
        else:
            # if last row is also 1, game is lost, just cancel 1
            if lengths[-1] == 1:
                y = xy[0][0][1] + 20
                x = xy[0][0][0] - 10
                x1 = x + 23
                return makemove(x,x1,y)
            # if not, cancel all but 1 on last row
            else:
                y = xy[-1][0][1] + 20
                x = xy[-1][0][0] - 10
                x1 = xy[-1][-2][0] + 13
                return makemove(x,x1,y)
            

def nextpass(lengths,xy):
    """AI Logic after first pass"""
    # Remove all instances of 1/2/3
    while 1 in lengths and 2 in lengths and 3 in lengths and len(lengths) > 3:
        for i in range(1,4):
            lengths.remove(i)
            for group in xy:
                if len(group) == i:
                    xy.remove(group)
                    break
    # Remove all instances of pairs
    for i in range(8):
        while lengths.count(i) >= 2 and len(lengths) > 2:
            for j in range(2):
                lengths.remove(i)
                for group in xy:
                    if len(group) == i:
                        xy.remove(group)
                        break
    # If 1 row left, cancel whole row
    if len(lengths) == 1:
        y = xy[0][0][1] + 20
        x = xy[0][0][0] - 10
        x1 = xy[0][-1][0] + 10
        return makemove(x,x1,y)
    # If 2 rows left
    elif len(lengths) == 2:
        # If pair
        if lengths[0] == lengths[1]:
            n = random.randrange(lengths[0])
            y = xy[0][n][1] + 20
            x = xy[0][n][0] - 10
            x1 = x + 23
            return makemove(x,x1,y)
        # If not pair:
        else:
            cancellations = lengths[1] - lengths[0]
            y = xy[1][0][1] + 20
            x = xy[1][0][0] - 10
            x1 = x + (cancellations-1)*40 + 23
            return makemove(x,x1,y)
    # Else just cancel random amount from random row
    else:
        row = random.choice(xy)
        lrow = len(row)
        cancellations = random.randint(1, lrow)
        if cancellations < lrow:
            n = random.randrange(lrow - cancellations)
            y = row[n][1] + 20
            x = row[n][0] - 10
            x1 = x + (cancellations-1)*40 + 23
            return makemove(x,x1,y)
        else:
            y = row[0][1] + 20
            x = row[0][0] - 10
            x1 = row[-1][0] + 10
            return makemove(x,x1,y)

if __name__ == '__main__':
    main()