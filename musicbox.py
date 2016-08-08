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

kits = [
  {
    'kick': Sound("samples/bd_808.wav"),
    'cymbal': Sound("samples/drum_cymbal_hard.wav"),
    'snare': Sound("samples/drum_snare_hard.wav"),
    'low_tom': Sound("samples/bass_trance_c.wav"),
    'high_tom': Sound("samples/ambi_haunted_hum.wav"),
    'hi_hat_closed': Sound("samples/drum_cymbal_pedal.wav")
  },
  {
    'kick': Sound("samples/bd_tek.wav"),
    'cymbal': Sound("samples/drum_splash_soft.wav"),
    'snare': Sound("samples/sn_dub.wav"),
    'low_tom': Sound("samples/tabla_ghe6.wav"),
    'high_tom': Sound("samples/tabla_ghe8.wav"),
    'hi_hat_closed': Sound("samples/drum_cymbal_closed.wav")
  },
  {
    'kick': Sound("samples/Oneshotsample/kick.wav"),
    'cymbal': Sound("samples/Oneshotsample/horn.wav"),
    'snare': Sound("samples/Oneshotsample/snare.wav"),
    'low_tom': Sound("samples/Oneshotsample/femalevox.wav"),
    'high_tom': Sound("samples/Oneshotsample/pitchyvox.wav"),
    'hi_hat_closed': Sound("samples/Oneshotsample/hatz.wav")
  }
]

kit_index = 0

while True:
  for event in pygame.event.get(): # event handling loop
    if event.type == KEYDOWN:
      if (event.key == K_UP):
        print "pressed up"
        kits[kit_index]['cymbal'].play()
      elif (event.key == K_LEFT):
        print "pressed left"
        kits[kit_index]['snare'].play()
      elif (event.key == K_SPACE):
        print "pressed space"
        kits[kit_index]['kick'].play()
      elif (event.key == K_RIGHT):
        print "pressed right"
        kits[kit_index]['low_tom'].play()
      elif (event.key == K_DOWN):
        print "pressed down"
        kits[kit_index]['high_tom'].play()
      elif (event.key == K_v):
        print "pressed c"
        kits[kit_index]['hi_hat_closed'].play()
      elif (event.key == K_z):
        kit_index = (kit_index + 1) % len(kits)
        print("new kit_index: {0}".format(kit_index))

