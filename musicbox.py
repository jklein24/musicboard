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

KEY_TO_SOUND = {
  K_UP: 'cymbal',
  K_LEFT: 'snare',
  K_RIGHT: 'low_tom',
  K_DOWN: 'high_tom',
  K_SPACE: 'kick',
  K_v: 'hi_hat_closed'
}

def log(message, *args):
  if __debug__:
    print(message.format(*args))

def build_kit(filenames, prefix=''):
  assert len(filenames) == 6
  return {
    'kick': Sound('samples/' + prefix + filenames[0] + '.wav'),
    'cymbal': Sound('samples/' + prefix + filenames[1] + '.wav'),
    'snare': Sound('samples/' + prefix + filenames[2] + '.wav'),
    'low_tom': Sound('samples/' + prefix + filenames[3] + '.wav'),
    'high_tom': Sound('samples/' + prefix + filenames[4] + '.wav'),
    'hi_hat_closed': Sound('samples/' + prefix + filenames[5] + '.wav')
  }

def handle_key(key):
  global kit_index
  if key in KEY_TO_SOUND.keys():
    log('pressed {0}', KEY_TO_SOUND[key])
    kits[kit_index][KEY_TO_SOUND[key]].play()
  elif key == K_z:
    kit_index = (kit_index + 1) % len(kits)
    log('new kit_index: {0}', kit_index)
  else:
    log('unknown key: {0}', key)

kits = [
  build_kit(['bd_808', 'drum_cymbal_hard', 'drum_snare_hard', 'bass_trance_c', 'ambi_haunted_hum', 'drum_cymbal_pedal']),
  build_kit(['bd_tek', 'drum_splash_soft', 'sn_dub', 'tabla_ghe6', 'table_ghe8', 'drum_cymbal_closed']),
  build_kit(['kick', 'horn', 'snare', 'femalevox', 'pitchyvox', 'hatz'], 'Oneshotsample/')
]

kit_index = 0

while True:
  for event in pygame.event.get(): # event handling loop
    if event.type == KEYDOWN:
      handle_key(event.key)

