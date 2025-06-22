#!/usr/bin/python
import RPi.GPIO as GPIO	       # Achtung: Schreibweise beachten: kleines i
import time
GPIO.setmode(GPIO.BCM)           # Wir stellen den Modus auf BCM ein
LED=18                                              # Das Wort ???LED??? steht jetzt f??r die Zahl ???23???.
GPIO.setup(LED,GPIO.OUT)          # ???LED??? (Pin 23) ist ein Ausgang.
Dimmer = GPIO.PWM(LED,100)  # Wir legen die LED als PWM mit einer Frequenz von 100 fest
Dimmer.start(0)                               # Dimmer wird gestartet
# Hier beginnt die Schleife
try:
    while True:                                     #while-Schleife damit das Programm durchgehend l??uft
        for dc in range(0,51,1):          # Schleife des Tastgrads in 5er-Schritten.
            Dimmer.ChangeDutyCycle(dc) # ??ndern des Tastgrads des Dimmers.
            time.sleep(0.01)                        # Warte 0.1 Sekunde.
        for dc in range(50,-1,-1):      # Schleife des Tastgrads in -5er-Schritten.
            Dimmer.ChangeDutyCycle(dc) # ??ndern des Tastgrads des Dimmers.
            time.sleep(0.01)                       # Warte 0.1 Sekunde.
except KeyboardInterrupt:            # Mit STRG+C unterbrechen wir das Programm
    Dimmer.stop()                                 # Stop des Dimmers.
    GPIO.cleanup() 
