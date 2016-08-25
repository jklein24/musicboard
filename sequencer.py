import threading
import time

DEBUG = True
BPM = 120
NUM_BARS = 2

class SequencerThread(threading.Thread):
  def __init__(self, kit):
    threading.Thread.__init__(self)
    self.beats = [1024, 0, 0, 0] * (NUM_BARS * 4)
    self.beatLock = threading.Lock()
    self.kit = kit
    self.currentBeat = 0

  def run(self):
    try:
      self.lastBeatTime = time.time() * 1000
      while True:
        self.nextBeat()
        # Allows 16th notes:
        time.sleep(15.0 / BPM)
    except Exception as e:
      print "Exiting %s due to Error: %s"%(self.name,str(e))

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
    sounds = self.kit.keys()
    self.beatLock.acquire()
    for i in range(len(sounds)):
      if (1 << i) & self.beats[self.currentBeat]:
        self.kit[sounds[i]].play()
    self.currentBeat = (self.currentBeat + 1) % (NUM_BARS * 16)
    self.lastBeatTime = time.time() * 1000
    self.beatLock.release()
