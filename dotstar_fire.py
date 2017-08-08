import threading
import time
import random

DEBUG = False
COOLING_SPEED = 55

class FireThread(threading.Thread):
  def __init__(self, strip, ready):
    threading.Thread.__init__(self)
    print "init"
    # For every pixel, construct a heat vector with a magnitude and direction.
    self.heat = [{'magnitude': 0, 'direction': 0} for i in range(strip.numPixels())]
    self.strip = strip
    self.ready = ready
    self._stopEvent = threading.Event()

  def run(self):
    try:
      print "run"
      self.ready.set()
      while not self._stopEvent.isSet():
        self.propagate()
    except Exception as e:
      print "Exiting %s due to Error: %s"%(self.name,str(e))

  def join(self, timeout=None):
    self._stopEvent.set()
    threading.Thread.join(self, timeout)

  def ignite(self, center):
    # Ignite 2 'sparks' near the center going outward:
    leftSpark, rightSpark = center, center + 1
    # Round towards the center. That way, both pixels are always on-screen.
    if (center > self.strip.numPixels() / 2):
      leftSpark -= 1
      rightSpark -= 1

    self.heat[rightSpark]['magnitude'] = random.randint(175,255);
    self.heat[rightSpark]['direction'] = 1;
    self.heat[leftSpark]['magnitude'] = random.randint(175,255);
    self.heat[leftSpark]['direction'] = -1;
    print "Igniting right spark to %d and left to %d" % (self.heat[rightSpark]['magnitude'], self.heat[leftSpark]['magnitude'])

  def propagate(self):
    heat = self.heat
    # Step 1.  Cool down every cell a little
    for h in heat:
      cooldown = random.randint(0, ((COOLING_SPEED * 20) / self.strip.numPixels()) + 2);
      if cooldown > h['magnitude']:
        h['magnitude'] = 0;
      else:
        h['magnitude'] = h['magnitude'] - cooldown;

    # Step 2.  Heat from each cell drifts in the corresponding direction
    rights = []
    lefts = []
    for i in range(len(heat)):
      if heat[i]['direction'] == 1 and i < len(heat) - 1:
        heat[i + 1]['magnitude'] = min(heat[i + 1]['magnitude'] + heat[i]['magnitude'], 255)
        rights.append(i)
      elif heat[i]['direction'] == -1 and i > 0:
        heat[i - 1]['magnitude'] = min(heat[i - 1]['magnitude'] + heat[i]['magnitude'], 255)
        lefts.append(i)
      heat[i]['direction'] = 0

    for r in rights:
      if r < len(heat) - 1:
        heat[r + 1]['direction'] = 1

    for l in lefts:
      if l > 0:
        heat[l - 1]['direction'] -= 1

    # Step 4.  Convert heat to LED colors
    for i in range(len(heat)):
      self.setPixelHeatColor(i, heat[i]['magnitude']);

    self.strip.show()
    if DEBUG:
      print [h['magnitude'] for h in self.heat]
    time.sleep(1.0 / 50)             # Pause 20 milliseconds (~50 fps)

  def setPixelHeatColor(self, pixel, temperature):
    # Scale 'heat' down from 0-255 to 0-191
    t192 = int(round((temperature/255.0)*191))

    # calculate ramp up from
    heatramp = t192 & 0x3F # 0..63
    heatramp <<= 2 # scale up to 0..252

    # figure out which third of the spectrum we're in:
    if t192 > 0x80:                     # hottest
      self.strip.setPixelColor(pixel, self.strip.Color(255, 255, heatramp))
    elif t192 > 0x40:             # middle
      self.strip.setPixelColor(pixel, self.strip.Color(255, heatramp, 0))
    else:                               # coolest
      if pixel == 17:
        self.strip.setPixelColor(pixel, self.strip.Color(max(heatramp, 4), 4, 0))
      else:
        self.strip.setPixelColor(pixel, self.strip.Color(heatramp, 0, 0))
