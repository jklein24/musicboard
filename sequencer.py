import threading
import time

DEBUG = True
BPM = 120
NUM_BARS = 2

class SequencerThread(threading.Thread):
  def __init__(self, kit, strip):
    threading.Thread.__init__(self)
    self.beats = [1024, 0, 0, 0] * (NUM_BARS * 4)
    self.beatLock = threading.Lock()
    self.kit = kit
    self.strip = strip
    self.currentBeat = 0
    self._stopEvent = threading.Event()

  def run(self):
    try:
      self.lastBeatTime = time.time() * 1000
      while not self._stopEvent.isSet():
        self.nextBeat()
        # Allows 16th notes:
        time.sleep(15.0 / BPM)
    except Exception as e:
      print "Exiting %s due to Error: %s"%(self.name,str(e))

  def join(self, timeout=None):
    self._stopEvent.set()
    threading.Thread.join(self, timeout)

  def setKit(self, kit):
    self.kit = kit

  def log(self, msg):
    if DEBUG:
      print msg

  def addClip(self, sound):
    if not sound in self.kit.keys():
      return
    self.beatLock.acquire()
    # Snap to nearest 16th
    currentTime = time.time() * 1000
    self.log("currentTime: %d, lastTime: %d, diff: %d"%(currentTime, self.lastBeatTime, currentTime - self.lastBeatTime))
    if currentTime - self.lastBeatTime > (7.5 / BPM) * 1000:
      self.beats[self.currentBeat] ^= (1 << self.kit.keys().index(sound))
    else:
      self.beats[self.currentBeat - 1] ^= (1 << self.kit.keys().index(sound))
      self.kit[sound].play()
    self.log("New value for beat %d: %d" % (self.currentBeat, self.beats[self.currentBeat]))
    self.beatLock.release()

  def nextBeat(self):
    self.log("Playing beat %d: %d" % (self.currentBeat, self.beats[self.currentBeat]))
    self.moveBeatPixel()
    sounds = self.kit.keys()
    self.beatLock.acquire()
    for i in range(len(sounds)):
      if (1 << i) & self.beats[self.currentBeat]:
        self.kit[sounds[i]].play()
    self.currentBeat = (self.currentBeat + 1) % (NUM_BARS * 16)
    self.lastBeatTime = time.time() * 1000
    self.beatLock.release()

  def moveBeatPixel(self):
    for i in range(self.strip.numPixels() - 1):
      if i >= len(self.beats):
        self.strip.setPixelColor(i, self.strip.Color(0, 0, 0))
      elif i == self.currentBeat:
        self.strip.setPixelColor(i, self.strip.Color(0, 255, 150))
      else:
        self.strip.setPixelColor(i, self.colorForBeat(i))
    self.strip.show()

  def colorForBeat(self, beatNum):
    maxBeatValue = float(2 ** len(self.kit.keys()))
    # Project onto color space of 24 bits:
    beatInt = (self.beats[beatNum] * 20001899) & 0xFFFFFF
    red = (0xFF0000 & beatInt) >> 16
    green = (0x00FF00 & beatInt) >> 8
    blue = 0x0000FF & beatInt
    return self.strip.Color(red, green, blue)


