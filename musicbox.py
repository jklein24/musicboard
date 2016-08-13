#!/usr/bin/env python

import time
import os
import threading
import pygame
import pygame.mixer
from gpiozero import LED
from time import sleep
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

SOUND_TO_LED = {
  'cymbal': LED(17),
  'snare': LED(18),
  'low_tom': LED(27),
  'high_tom': LED(22),
  'kick': LED(23),
  'hi_hat_closed': LED(24)
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

class LedThread (threading.Thread):
  threadLock = threading.Lock()
  threads = []

  def __init__(self, led):
    threading.Thread.__init__(self)
    self.threadId = led.pin.number
    self.led = led

  def run(self):
    try:
      LedThread.threadLock.acquire()
      if self.threadId in LedThread.threads:
        LedThread.threadLock.release()
        return
      LedThread.threads.append(self.threadId)
      LedThread.threadLock.release()
      log("LED #{0} on", self.threadId)
      self.led.on()
      sleep(1)
      self.led.off()
      log("LED #{0} off", self.threadId)
      LedThread.threads.remove(self.threadId)
    except Exception as e:
      print "Exiting %s due to Error: %s"%(self.name,str(e))

def flash_led(led):
  thread = LedThread(led)
  thread.daemon = True
  thread.start()

def handle_key(key):
  global kit_index
  if key in KEY_TO_SOUND.keys():
    log('pressed {0}', KEY_TO_SOUND[key])
    kits[kit_index][KEY_TO_SOUND[key]].play()
    flash_led(SOUND_TO_LED[KEY_TO_SOUND[key]])
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

