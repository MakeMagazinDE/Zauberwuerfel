# SR 6/2022-4/2025
# Show a rubik's cube defined by a cube string via RP pico and WLED json

# Two ways to display the data on a LED cube controlled by WLED:
# First method: Send json requests via http, problem: Can hang!
#response = requests.post(url, json={"on":True,"bri":255}) 
import requests
#urls=["http://192.168.2.54/json"] # kitchen
#urls=["http://192.168.2.117/json"] # cube
#urls=["http://10.42.0.196/json"]  # 8x8 Uni
urls=[]

# Second method: Send UDP packets, no problem if they get lost
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create UDP socket
#        small cube    large cube
udpIPs=["10.42.0.135","10.42.0.106"]    # "192.168.2.117"]  

# Some cubisms
# Order is URFDLB (white, red, green, yellow, orange, blue)
cube_solved='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

# On the facelet level, which faces are involved in the moves?
movedefs={ 'U': [20,19,18,38,37,36,47,46,45,11,10,9],
           'D': [24,25,26,15,16,17,51,52,53,42,43,44],
           'L': [0,3,6,18,21,24,27,30,33,53,50,47], # previously: 47,50,53],
           'R': [8,5,2,26,23,20,35,32,29,45,48,51], # previously: 55,52,49],
           'F': [6,7,8,9,12,15,29,28,27,44,41,38],
           'B': [2,1,0,36,39,42,33,34,35,17,14,11] }

def show(cubestring='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'):
    colours_full={ 'U': 'ffffff', # white
         'R': 'ff0000', # red
         'F': '00ff00', # green
         'D': 'ffff00', # yellow
         'L': 'aa3500', # orange
         'B': '0000ff'} # blue

    colours={ 'U': '7f7f7f', # white
         'R': '7f0000', # red
         'F': '007f00', # green
         'D': '7f7f00', # yellow
         'L': '7a2f00', # orange - '7a3f00' looks better on WLED
         'B': '00007f', # blue
         'K': '000000', # black
         'W': 'ffffff'} # brigxht white

    colours_dim={ 'U': '0f0f0f', # white
         'R': '0f0000', # red
         'F': '000f00', # green
         'D': '0f0f00', # yellow
         'L': '0a0300', # orange
         'B': '00000f', # blue
         'K': '000000', # black
         'W': '303030'} # bright white

    #print("cubestring=",cubestring)
    if ( cubestring == ''):
        cubestring = cube_solved
 
    # assemble output data from cube string
    data=[]
    for face in cubestring:
        data.append(colours[face])
    # print("debug: ", output, " - ",data)
 
    # send data via UDP
    for udpIP in udpIPs:
        # 0x02 is DRGB, F0 is hold for 240 seconds, see https://kno.wled.ge/interfaces/udp-realtime/
        for i in range(3):
           sock.sendto(bytes.fromhex("02F0"+"".join(data)), (udpIP, 21324))
           sleep(0.01)

    # send data via TCP json request
    for url in []:
        try:
           response = requests.post(url, json={"seg": [{"id": 0, "i": data }]}, timeout=5)
        except:
           print("Problem sending to ",url)
        
    # send coulour data over USB serial
    with open('/dev/ttyACM0', 'a') as f:
        for _ in data:
            f.write(_)
        f.write('\n')
 

from time import sleep
def flashmove(cube, move, repeat=1,delay=0.1):
    flash=['','']
    for i in range(54):
            if ( i in movedefs[move[0]] ):   # this element is involved in this move!
                flash[0]=flash[0]+"W"
                flash[1]=flash[1]+"K"
            else:
                flash[0]=flash[0]+cube[i]
                flash[1]=flash[1]+cube[i]
    for j in range(repeat):   # first, flash to attract attention
        show(flash[0])
        sleep(delay)
        show(flash[1])
        sleep(delay)
    show(cube)

def animove(cube, move,repeat=3,delay=0.15):
    anim=['','','']  # construct three frames of animations and flashing
    for i in range(54):
        for j in range(3):
            if ( i in movedefs[move[0]] ):   # this element is involved in this move!
                anim[j]=anim[j]+"WKK"[(movedefs[move[0]].index(i)-j)%3]  # white moves
            else:
                anim[j]=anim[j]+cube[i]

    if (move[1]=="3"):  # second char is 3: inverse move!
        for i in range(repeat):
            for j in range(3):
                show(anim[2-j])
                sleep(delay)
    else: # normal or double move
        for i in range(repeat):
            for j in range(3):
                show(anim[j])
                sleep(delay)
    show(cube)

def testcube():
    for i in range(55):
        testcube=''
        for j in range(54):
            if (i==j):
                testcube+='W'
            else:
                testcube+=cube_solved[j]
        show(testcube)
        sleep(1)
