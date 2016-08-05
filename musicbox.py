#!/usr/bin/env python

import time
import os
import pygame
import pygame.mixer
from pygame.locals import *
from pygame.mixer import Sound

os.putenv('SDL_VIDEODRIVER', 'fbcon')
pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.mixer.init()
pygame.display.init()
pygame.init()
pygame.display.set_mode((1,1))

cymbal = Sound("samples/drum_cymbal_hard.wav")
snare = Sound("samples/drum_snare_hard.wav")
bd_808 = Sound("samples/bd_808.wav")
bass_trance = Sound("samples/bass_trance_c.wav")
hum = Sound("samples/ambi_haunted_hum.wav")

while True:
  for event in pygame.event.get(): # event handling loop
    if event.type == KEYDOWN:
      if (event.key == K_UP):
        print "pressed up"
        cymbal.play()  
      elif (event.key == K_LEFT):
        print "pressed left"
	snare.play()
      elif (event.key == K_SPACE):
        print "pressed space"
	bd_808.play()
      elif (event.key == K_RIGHT):
        print "pressed right"
	bass_trance.play()
      elif (event.key == K_DOWN):
        print "pressed down"
	hum.play()

