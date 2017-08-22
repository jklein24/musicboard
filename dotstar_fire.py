import threading
import time
import random

DEBUG = False
COOLING_SPEED = 55

class FireThread(threading.Thread):
  def __init__(self, strip, ready):
    threading.Thread.__init__(self)
    print "init"
    # For every pixel, construct a heat vector with a magnitude and a ttl representing steps left.
    self.heat = [{'magnitude': 0, 'ttl': 0} for i in range(strip.numPixels())]
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

  def ignite(self, start, pixelCount):
    self.heat[start]['magnitude'] = random.randint(175,255);
    self.heat[start]['ttl'] = pixelCount - 1;
    print "Igniting right spark to %d and left to %d" % (self.heat[start]['magnitude'], self.heat[start]['ttl'])

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
    for i in reversed(range(len(heat))):
      if heat[i]['ttl'] > 0 and i < len(heat) - 1:
        heat[i + 1]['magnitude'] = min(heat[i + 1]['magnitude'] + heat[i]['magnitude'], 255)
        heat[i + 1]['ttl'] = heat[i]['ttl'] - 1
        heat[i]['ttl'] = 0

    # Step 3.  Convert heat to LED colors
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
      self.strip.setPixelColor(pixel, self.strip.Color(heatramp, 0, 0))
