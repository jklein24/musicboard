#!/usr/bin/env python

import pygame
import pygame.mixer
import threading
import time
from dotstar_fire import FireThread
from sequencer import SequencerThread
from pygame.mixer import Sound
from dotstar import Adafruit_DotStar
import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.mixer.init()
pygame.init()

KEY_TO_SOUND = [
 'misc',
 'horn',
 'vocal',
 'cowbell',
 'clap',
 'hi_hat_closed',
 'kick',
 'high_tom',
 'low_tom',
 'snare',
 'cymbal'
]

KEY_TO_CENTER_PIXEL = [2, 7, 11, 17, 21, 24, 34, 41, 47, 51, 57]

# DotStar setup
NUM_PIXELS = 60
strip = Adafruit_DotStar(NUM_PIXELS, order='bgr')
strip.begin()           # Initialize pins for output
strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle

# Create MPR121 instance.
cap = MPR121.MPR121()

# Initialize communication with MPR121 using default I2C bus of device, and
# default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
if not cap.begin():
    print('Error initializing MPR121.  Check your wiring!')
    sys.exit(1)

def log(message, *args):
  if __debug__:
    print(message.format(*args))

def build_kit(kit_name, filenames, prefix=''):
  assert len(filenames) == 11
  return {
    'name': Sound('samples/' + kit_name + '.wav'),
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
  if key == -1:
    kit_index = (kit_index + 1) % len(kits)
    log('new kit_index: {0}', kit_index)
    kits[kit_index]['name'].play()
    sequencerThread.setKit(kits[kit_index])
  elif key < len(KEY_TO_SOUND):
    log('pressed {0}', KEY_TO_SOUND[key])
    if mode == 1:
      sequencerThread.addClip(KEY_TO_SOUND[key])
    else:
      kits[kit_index][KEY_TO_SOUND[key]].play()
    fireThread.ignite(KEY_TO_CENTER_PIXEL[key])
  else:
    log('unknown key: {0}', key)

kits = [
  build_kit('Kit_one', ['kick', 'horn', 'snare', 'femalevox', 'pitchyvox', 'hatz', 'monstervox', 'malevox', 'rimshot', 'bd_zome', 'elec_twang'], 'Oneshotsample/'),
  build_kit('Kit_two', ['bd_808', 'drum_cymbal_hard', 'drum_snare_hard', 'bass_trance_c', 'ambi_haunted_hum', 'drum_cymbal_pedal', 'neverbe_clap', 'drum_cowbell', 'ambi_choir', 'misc_crow', 'vinyl_scratch']),
  build_kit('Kit_three', ['bd_tek', 'drum_splash_soft', 'sn_dub', 'tabla_ghe6', 'tabla_ghe8', 'drum_cymbal_closed', 'neverbe_clap', 'drum_cowbell', 'ambi_choir', 'misc_crow', 'vinyl_scratch'])
]

kit_index = 0

ready = threading.Event()
fireThread = FireThread(strip, ready)
fireThread.daemon = True
fireThread.start()
ready.wait()

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)
# Mode 0 is clip triggering. Mode 1 is sequencer.
mode = 1
lastPressedModeButton = 0
if mode == 1:
  sequencerThread = SequencerThread(kits[kit_index], strip)
  sequencerThread.daemon = True
  sequencerThread.start()
  fireThread.setEnabled(False)

if mode == 0:
  handle_key(6)
else:
  kits[kit_index]['kick'].play()
  fireThread.ignite(KEY_TO_CENTER_PIXEL[6])

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')
last_touched = cap.touched()
while True:
  if (GPIO.input(22) == True and (time.time() * 1000) - lastPressedModeButton > 500):
    lastPressedModeButton = time.time() * 1000
    mode = (mode + 1) % 2
    log("swapping modes. New Mode: {0}", mode)
    if mode == 0:
      sequencerThread.join()
      fireThread.setEnabled(True)
    else:
      sequencerThread = SequencerThread(kits[kit_index], strip)
      sequencerThread.daemon = True
      sequencerThread.start()
      fireThread.setEnabled(False)

  current_touched = cap.touched()
  # Check each pin's last and current state to see if it was pressed or released.
  for i in range(12):
    # Each pin is represented by a bit in the touched value.  A value of 1
    # means the pin is being touched, and 0 means it is not being touched.
    pin_bit = 1 << i
    # First check if transitioned from not touched to touched.
    if current_touched & pin_bit and not last_touched & pin_bit:
      print('{0} pressed!'.format(i))
      handle_key(i - 1)
    if not current_touched & pin_bit and last_touched & pin_bit:
      print('{0} released!'.format(i))

  last_touched = current_touched
  time.sleep(0.05)

