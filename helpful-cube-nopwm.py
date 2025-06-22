#!/usr/bin/python

import aioserial
import asyncio
#import kociemba
#import re
from twophase.solver import solve
from time import sleep,time
from showcube import *
from matrix import *

solved='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
cubeString=solved
recommendation=''
goodBoy=False
lastMoveTime=time()
moves=[]

async def read_and_print(aioserial_instance: aioserial.AioSerial):
    global cubeString, lastMove, lastMoveTime, moves, recommendation, goodBoy
    while True:
        line=(await aioserial_instance.readline_async()).decode(errors='ignore')
        #print("== received: == "+line)
        
        # data on last move received: play animation, check if 'correct'
        if (line[30:39]=='Last move'):
            lastMove=line[43:45]
            if (lastMove[1]==','):
                lastMove=lastMove[0]+' '
            print("last move received: "+lastMove)
            lastMoveTime=time()
            if (recommendation!=''):  # recommended move?
                if (lastMove[0]==recommendation[0]):
                    if ((lastMove[1]=='\'' and recommendation[1]=='1') or (lastMove[1]==' ' and recommendation[1]=='3')):
                        goodBoy=False
                        print("-- Wrong direction! --")
                    else:
                        goodBoy=True
                        print("++ Well done! ++")
                else:
                    goodBoy=False
                    print("-- That was not the recommended face! --")
            flashmove(cubeString,lastMove)
                
        # cubeString received: display cube, show hint
        if (line[:11]=='cubeString:'):
            cubeString=line[12:66]
            print("cubeString received: "+cubeString)
            show(cubeString)
            if (cubeString==solved):
                print("Congratulations!")
                showMessage("You made it!")
                show("W"*54)
                await asyncio.sleep(.5)
                show(cubeString)
                recommendation=''
                goodBoy=False
            else:
                #if (goodBoy):
                #    moves=moves[1:]
                #else:
                    ## The kociemba module does not work very well (and it is not by Herbert Kociemba!
                    ## Sometimes the solution length exploded, therefore this complicated stuff
                    ## Not necessary anymore with Herbert Kociemba's twophase module
                    # newsolution=re.sub('(\w)2', '\\1 \\1', kociemba.solve(cubeString))
                    # print("newsolution= "+newsolution+" len="+str(len(newsolution.split(' '))))
                    # if (len(moves)>8 and lastMove!='' and len(newsolution.split(' '))>len(moves)+2):
                    #     print("Solution too long, backtracking to old state!")
                    #     moves.insert(0,invertMove(lastMove))
                    # else:
                    #    moves=newsolution.split(' ')
                    
                moves=solve(cubeString,0,.2).split(' ')[:-1] # best solution found in 200ms, last element is # of moves
                recommendation=moves[0]
                print("Kociemba says best move is "+recommendation+" ("+str(len(moves))+" moves total: "+' '.join(moves)+")")
                if (len(moves)>1):
                    # showMessage("Solution: "+str(len(moves)))            
#                   # showMessage((recommendation+" ")[:1]+" todo: "+str(len(moves)))            
                    #if (moves[0]==moves[1]):
                    #    srecommendation=recommendation[0]+chr(253) # squared, no '
                    #else:
                    #    srecommendation=recommendation
                    if (recommendation[1]=='1'):
                        showMessage("nxt "+recommendation[0]+" tot "+str(len(moves)))            
                    elif (recommendation[1]=='2'):
                        showMessage("nxt "+recommendation[0]+chr(253)+"tot "+str(len(moves)))
                    elif (recommendation[1]=='3'):
                        showMessage("nxt "+recommendation[0]+"'tot "+str(len(moves)))
                    else:
                        print("Cannot interpret move "+recommendation+"!")
                else:
                    showMessage("Almost there")
            lastMove='' # if we missed the move message, we might get into trouble with backtracking!

async def loop():
    global cubeString, lastMove, lastMoveTime, moves, recommendation, goodBoy
    while True:
        # print("Loop running.")
        if ((( time()>=lastMoveTime+5  and time()<lastMoveTime+11 ) or
             ( time()>=lastMoveTime+15 and time()<lastMoveTime+21 ) or
             ( time()>=lastMoveTime+1  and time()<lastMoveTime+7 and goodBoy ))
              and recommendation!='' and len(moves)>1 ):
            print("Suggesting move "+recommendation+" to player...")
            animove(cubeString,recommendation)
            await asyncio.sleep(2)
        elif ( time()>=lastMoveTime+60 ):
            seconds=int(time())%20  # idle messages
            if (seconds==0):
                showMessage("Helpful Cube")
            elif (seconds==16):
                showMessage("Use the cube")
            elif (seconds==18):
                showMessage("Play with me")
            seconds=int(time())%120  # every two min
            if (seconds==12):
                showMessage(" Hey, you!")
            elif (seconds==14):
                showMessage(" Yes, you!")
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(.1)

def invertMove(move):
    if (move[-1]=="'"):
        return move[0]
    else:
        return move+"'"
            
#def showMessage(message):
#    print("*** "+message+" ***")

async def main():
    print("Helpful Cube started.")
    showMessage("  Welcome!")
    maintask = asyncio.create_task(loop())
    iotask   = asyncio.create_task(read_and_print(aioserial.AioSerial(port='/dev/ttyACM0')))
    await maintask
    await iotask
    
asyncio.run(main())
    
#asyncio.run(read_and_print(aioserial.AioSerial(port='/dev/ttyACM0')))

print("End reached. (should not happen)")

