#!/usr/bin/env python

import time
import os
import threading
import pygame
import pygame.mixer
from dotstar_fire import FireThread
from pygame.locals import *
from pygame.mixer import Sound
from dotstar import Adafruit_DotStar
import Adafruit_MPR121.MPR121 as MPR121

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
  K_v: 'hi_hat_closed',
  K_w: 'clap',
  K_a: 'cowbell',
  K_s: 'vocal',
  K_d: 'horn',
  K_f: 'misc'
}

KEY_TO_CENTER_PIXEL = {
  K_UP: 5,
  K_LEFT: 10,
  K_RIGHT: 15,
  K_DOWN: 20,
  K_SPACE: 25,
  K_v: 30,
  K_w: 35,
  K_a: 40,
  K_s: 45,
  K_d: 50,
  K_f: 54
}

# DotStar setup
NUM_PIXELS = 60
strip = Adafruit_DotStar(NUM_PIXELS, order='bgr')
strip.begin()           # Initialize pins for output
strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle

def log(message, *args):
  if __debug__:
    print(message.format(*args))

def build_kit(filenames, prefix=''):
  assert len(filenames) == 11
  return {
    'kick': Sound('samples/' + prefix + filenames[0] + '.wav'),
    'cymbal': Sound('samples/' + prefix + filenames[1] + '.wav'),
    'snare': Sound('samples/' + prefix + filenames[2] + '.wav'),
    'low_tom': Sound('samples/' + prefix + filenames[3] + '.wav'),
    'high_tom': Sound('samples/' + prefix + filenames[4] + '.wav'),
    'hi_hat_closed': Sound('samples/' + prefix + filenames[5] + '.wav'),
    'clap': Sound('samples/' + prefix + filenames[6] + '.wav'),
    'cowbell': Sound('samples/' + prefix + filenames[7] + '.wav'),
    'vocal': Sound('samples/' + prefix + filenames[8] + '.wav'),
    'horn': Sound('samples/' + prefix + filenames[9] + '.wav'),
    'misc': Sound('samples/' + prefix + filenames[10] + '.wav')
  }

def handle_key(key):
  global kit_index
  global fireThread
  if key in KEY_TO_SOUND.keys():
    log('pressed {0}', KEY_TO_SOUND[key])
    kits[kit_index][KEY_TO_SOUND[key]].play()
    fireThread.ignite(KEY_TO_CENTER_PIXEL[key])
  elif key == K_z:
    kit_index = (kit_index + 1) % len(kits)
    log('new kit_index: {0}', kit_index)
  else:
    log('unknown key: {0}', key)

kits = [
  build_kit(['bd_808', 'drum_cymbal_hard', 'drum_snare_hard', 'bass_trance_c', 'ambi_haunted_hum', 'drum_cymbal_pedal', 'neverbe_clap', 'drum_cowbell', 'ambi_choir', 'misc_crow', 'vinyl_scratch']),
  build_kit(['bd_tek', 'drum_splash_soft', 'sn_dub', 'tabla_ghe6', 'table_ghe8', 'drum_cymbal_closed', 'neverbe_clap', 'drum_cowbell', 'ambi_choir', 'misc_crow', 'vinyl_scratch']),
  build_kit(['kick', 'horn', 'snare', 'femalevox', 'pitchyvox', 'hatz', 'monstervox', 'malevox', 'misc_burp', 'bd_zome', 'elec_twang'], 'Oneshotsample/')
]

kit_index = 0
fireThread = FireThread(strip)
fireThread.daemon = True
fireThread.start()

while True:
  for event in pygame.event.get(): # event handling loop
    if event.type == KEYDOWN:
      handle_key(event.key)

