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
 'kick',
 'cymbal',
 'snare',
 'low_tom',
 'high_tom',
 'hi_hat_closed',
 'clap',
 'cowbell',
 'vocal',
 'horn',
 'misc'
]

KEY_TO_FINGER = [
 (0, 3),
 (3, 4),
 (7, 4),
 (11, 4),
 (15, 3),
 (18, 3),
 (21, 4),
 (25, 4),
 (29, 4),
 (33, 3)
]

# DotStar setup
NUM_PIXELS = 36
strip = Adafruit_DotStar(NUM_PIXELS, 4000000, order='bgr')
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
    'name': Sound('/home/pi/musicboard/samples/' + kit_name + '.wav'),
    'kick': Sound(prefix + filenames[0] + '.wav'),
    'cymbal': Sound(prefix + filenames[1] + '.wav'),
    'snare': Sound(prefix + filenames[2] + '.wav'),
    'low_tom': Sound(prefix + filenames[3] + '.wav'),
    'high_tom': Sound(prefix + filenames[4] + '.wav'),
    'hi_hat_closed': Sound(prefix + filenames[5] + '.wav'),
    'clap': Sound(prefix + filenames[6] + '.wav'),
    'cowbell': Sound(prefix + filenames[7] + '.wav'),
    'vocal': Sound(prefix + filenames[8] + '.wav'),
    'horn': Sound(prefix + filenames[9] + '.wav'),
    'misc': Sound(prefix + filenames[10] + '.wav')
  }

def handle_key(key):
  global kit_index
  global fireThread
  if key == -1 or key == 10:
    if key == -1:
      kit_index = (kit_index + 1) % len(kits)
      fireThread.ignite(KEY_TO_FINGER[4][0], KEY_TO_FINGER[4][1])
    else :
      kit_index = (kit_index - 1) % len(kits)
      fireThread.ignite(KEY_TO_FINGER[5][0], KEY_TO_FINGER[5][1])
    log('new kit_index: {0}', kit_index)
    kits[kit_index]['name'].play()
    if mode == 1:
      sequencerThread.setKit(kits[kit_index])
  elif key <  len(KEY_TO_FINGER) - 2:
    log('pressed {0}', KEY_TO_SOUND[key])
    if mode == 1:
      sequencerThread.addClip(KEY_TO_SOUND[key])
    else:
      kits[kit_index][KEY_TO_SOUND[key]].play()
      # Make room for the thumbs because of my dumb soldering.
      if key > 3:
        key = key + 2
      fireThread.ignite(KEY_TO_FINGER[key][0], KEY_TO_FINGER[key][1])
  else:
    log('unknown key: {0}', key)

kits = [
  build_kit('F_Major', ['F2', 'G2', 'A3', 'A#3', 'C3', 'D3', 'E3', 'F3', 'G3', 'A4', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('G_Dorian', ['G2', 'A3', 'A#3', 'C3', 'D3', 'E3', 'F3', 'G3', 'A4', 'B4', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('A_Phrygian', ['A3', 'A#3', 'C3', 'D3', 'E3', 'F3', 'G3', 'A4', 'B4', 'C4', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('A_Sharp_Lydian', ['A#3', 'C3', 'D3', 'E3', 'F3', 'G3', 'A4', 'B4', 'C4', 'rimshot', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('C_Mixolydian', ['C3', 'D3', 'E3', 'F3', 'G3', 'A4', 'B4', 'C4', 'x', 'rimshot', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('D_Minor', ['D3', 'E3', 'F3', 'G3', 'A4', 'B4', 'C4', 'D4', 'x', 'rimshot', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
  build_kit('E_Lochrian', ['E3', 'F3', 'G3', 'A4', 'B4', 'C4', 'D4', 'E4', 'x', 'rimshot', 'elec_twang'], '/home/pi/musicboard/samples/keys/'),
]

kit_index = 0

def makeFireThread():
  global fireThread
  ready = threading.Event()
  fireThread = FireThread(strip, ready)
  fireThread.daemon = True
  fireThread.start()
  ready.wait()

def makeSequencerThread():
  global sequencerThread
  sequencerThread = SequencerThread(kits[kit_index], strip)
  sequencerThread.daemon = True
  sequencerThread.start()


GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)
# Mode 0 is clip triggering. Mode 1 is sequencer.
mode = 0
lastPressedModeButton = 0
if mode == 1:
  makeSequencerThread()
  kits[kit_index]['kick'].play()
else:
  makeFireThread()
  handle_key(2)

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')
last_touched = cap.touched()
while True:
  # Uncomment this and comment out the next line to enable mode switching.
  # if (GPIO.input(22) == False and (time.time() * 1000) - lastPressedModeButton > 500):
  if (False):
    lastPressedModeButton = time.time() * 1000
    mode = (mode + 1) % 2
    log("swapping modes. New Mode: {0}", 'sequencer' if mode == 1 else 'clips')
    if mode == 0:
      sequencerThread.join()
      makeFireThread()
    else:
      fireThread.join()
      makeSequencerThread()

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

