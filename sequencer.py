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
      self.lastBeatTime = time.clock()
      while True:
        self.nextBeat()
        # Allows 16th notes:
        time.sleep(15.0 / BPM)
    except Exception as e:
      print "Exiting %s due to Error: %s"%(self.name,str(e))

  def setKit(self, kit):
    self.kit = kit

  def addClip(self, sound):
    if not sound in self.kit.keys():
      return
    self.beatLock.acquire()
    # Snap to nearest 16th
    if time.clock() - self.lastBeatTime > (7.5 / BPM):
      self.beats[self.currentBeat] ^= (1 << self.kit.keys().index(sound))
    else:
      self.beats[self.currentBeat - 1] ^= (1 << self.kit.keys().index(sound))
      self.kit[sound].play()
    print "New value for beat %d: %d" % (self.currentBeat, self.beats[self.currentBeat])
    self.beatLock.release()

  def nextBeat(self):
    print "Playing beat %d: %d" % (self.currentBeat, self.beats[self.currentBeat])
    sounds = self.kit.keys()
    self.beatLock.acquire()
    for i in range(len(sounds)):
      if (1 << i) & self.beats[self.currentBeat]:
        self.kit[sounds[i]].play()
    self.currentBeat = (self.currentBeat + 1) % (NUM_BARS * 16)
    self.lastBeatTime = time.clock()
    self.beatLock.release()
