#!/usr/bin/python

# SR Apr25 - The Helpful Cube
# needs Python packages aioserial, asyncio, RubikTwoPhase, luma.led_matrix
# apt install libjpeg-dev
# pip install --break-system-packages aioserial asyncio RubikTwoPhase luma.led_matrix
# or rather (for much higher cube solving speed)
# apt install pypy3 pypy3-dev libjpeg-dev ; apt remove python3-spidev
# pip --python /usr/bin/pypy3 install --break-system-packages aioserial asyncio RubikTwoPhase luma.led_matrix spidev rpi.gpio
# activate SPI via raspi-config

import aioserial
import asyncio
#import kociemba
#import re
from twophase.solver import solve
from time import sleep,time
from showcube import *  # control WLED via UDP
from matrix import *    # text display
import RPi.GPIO as GPIO # PWM for spot
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
Dimmer = GPIO.PWM(18,100) # 100Hz
Dimmer.start(0)

# when the ESP32C3 resets while this code is running, it changes the port
from pathlib import Path
serial = '/dev/ttyACM0'
if not Path(serial).exists():
   serial = '/dev/ttyACM1'
   print("Trying "+serial)
if Path(serial).exists():
   print("Using "+serial)
else:
   print("Could not find the serial port.")
   exit()

solved='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
cubeString='K'*54
recommendation=''
goodBoy=False
previousMove=''
count=0  # identical moves -> battery display
lastMoveTime=time()
moves=[]

async def read_and_print(aioserial_instance: aioserial.AioSerial):
    global cubeString, lastMove, lastMoveTime, previousMove, count, moves, recommendation, goodBoy, battery
    while True:
        line=(await aioserial_instance.readline_async()).decode(errors='ignore')
        fields=line.split(' ')
        # print("== received: == "+line)
        
        if (len(fields)>9 and fields[9]=='batteryLevel'):
            battery=fields[10].strip()
            print('BatteryLevel = '+battery)

        # data on last move received: play animation, check if 'correct'
        #if (line[30:39]=='Last move'):
        if (len(fields)>8 and fields[7]=='move'):
            lastMove=['L3','L1','R3','R1','D3','D1','U3','U1','F3','F1','B3','B1'][int(fields[8][:2],16)-1] # 0c/B
            #if (lastMove[1]==','):
            #    lastMove=lastMove[0]+' '
            print("last move received: "+lastMove)
            lastMoveTime=time()
            if (lastMove==previousMove):
                count=count+1
                if (count>3):
                    showMessage('Battery '+battery+'%')
                    await asyncio.sleep(.5)
            else:
                count=0
            previousMove=lastMove
            if (recommendation!=''):  # recommended move?
                if (lastMove[0]==recommendation[0]):
                    #if ((lastMove[1]=='\'' and recommendation[1]=='1') or (lastMove[1]==' ' and recommendation[1]=='3')):
                    if ((lastMove[1]=='3' and recommendation[1]=='1') or (lastMove[1]=='1' and recommendation[1]=='3')):
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
        # if (line[:11]=='cubeString:'):
        if (fields[0]=='cubeString:'):
            #cubeString=line[12:66]
            cubeString=fields[1].strip() # trim trailing \n
            print("cubeString received: "+cubeString)
            show(cubeString)
            if (cubeString==solved):
                # print("Congratulations!")
                showMessage("You made it!")
                show("W"*54)  # flash the cube 
                await asyncio.sleep(.5)
                show(cubeString)
                recommendation=''
                moves=[]
                goodBoy=False
            else:
                if (goodBoy):
                    moves=moves[1:]
                    if (recommendation[1]=="2"):
                        print("Double move... recommend remaining part")
                        moves.insert(0,lastMove)  # same direction again!
                else:
                    print("Looking for a solution...")
                    newsolution=solve(cubeString,0,.5) # best solution found in 500ms, last element is # of moves
                    print("newsolution= "+newsolution)
                    newmoves=newsolution.split(' ')[:-1]
                    if (len(moves)>1 and lastMove!='' and len(newmoves)>len(moves)+1):
                        print("Solution too long, backtracking to old state!")
                        print("Inserting "+lastMove[0]+str((int(lastMove[1])+2)%4))
                        moves.insert(0,lastMove[0]+str((int(lastMove[1])+2)%4))
                        if (moves[0][0]==moves[1][0]):
                            turns=int(moves[0][1])+int(moves[1][1])
                            if (turns==4):
                                print("Moves cancel out!")
                                moves=moves[2:]
                            else:
                                combinedmove=moves[0][0]+str(turns%4)
                                print("Moves combined to "+combinedmove)
                                moves=moves[2:]
                                moves.insert(0,combinedmove)
                    else:
                        moves=newmoves
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
                Dimmer.ChangeDutyCycle(80)
                sleep(.2)  # no await asyncio! 
            elif (seconds==14):
                showMessage(" Yes, you!")
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(.1)

#def showMessage(message):
#    print("*** "+message+" ***")

async def spot():
    global lastMoveTime
    while True:
        if ( time()>=lastMoveTime+60 ):
            # Dimmer.ChangeDutyCycle(abs(int(time()*10%100-50))/2+20) # 20->45->20 in 10sec
            Dimmer.ChangeDutyCycle(10)
        else:
            Dimmer.ChangeDutyCycle(50)
        await asyncio.sleep(.1) # (.02)         

async def main():
    print("Helpful Cube started. Looking for Cube.")
    showMessage("  Welcome!")
    tasks=[asyncio.create_task(loop()), asyncio.create_task(read_and_print(aioserial.AioSerial(port=serial))), asyncio.create_task(spot())]
    # c.f. https://superfastpython.com/asyncio-cancel-all-tasks-if-task-fails/
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f'A task failed with: {e}, canceling all tasks')
        for task in tasks:
            task.cancel()
        # wait for all tasks to cancel
        for task in tasks:
            try:
                await task
            except Exception:
                pass
            except asyncio.CancelledError:
                pass
                
asyncio.run(main())

print("End reached. (should not happen)")

