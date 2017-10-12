"""
A sample contribution plugin that provides translations when hovering over words in a text document.
Drop this file in your JEB's coreplugins/ folder. Make sure to have a Jython JAR package in that folder as well.
"""

import urllib2

from com.pnfsoftware.jeb.core import IUnitContribution, PluginInformation, Version
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.util.base import TypedContent


def translate(s):
  ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.8'
  headers = {
    'User-Agent': ua,
  }

  es = urllib2.quote(s.encode('utf8'))
  url = "http://www.google.com/search?safe=off&q=translate:" + es
  print('Query: %s' % url)

  request = urllib2.Request(url, None, headers)
  response = urllib2.urlopen(request)
  data = response.read()
  #print(data)

  m1 = '<cite>translate.google.com</cite>'
  pos = data.find(m1)
  if pos < 0:
    print('Cannot find marker1')
    return None
  #print(pos)

  m2 = '</span> - \xe2\x80\x8e<span class="nobr">' #utf-8 encoded
  pos = data.find(m2, pos + len(m1))
  if pos < 0:
    print('Cannot find marker2')
    return None
  #print(pos)

  m3 = '</span>'
  pos1 = data.find(m3, pos + len(m2))
  if pos1 < 0:
    print('Cannot find marker3')
    return None
  #print(pos1)

  r = data[pos + len(m2): pos1]
  return r


class TranslationContributionPlugin(IUnitContribution):

  def __init__(self):
    pass
  
  def getPluginInformation(self):
    return PluginInformation('Translation Contribution',
            'Hover over strings in text disassembly to see its English translation',
            'PNF Software', Version.create(1, 0, 0))

  def isTarget(self, unit):
    return isinstance(unit, ICodeUnit)

  def setPrimaryTarget(self, unit):
    self.target = unit

  def getPrimaryTarget(self):
    return self.target

  def getItemInformation(self, targetUnit, itemId, itemText):
    if not itemText:
      return None
    s = itemText.strip(' \'\"')
    if not s:
      return None
    try:
      ts = translate(s)
    except Exception as e:
      print 'ERROR:', e
      return None
    if not ts:
      print 'Cannot translate: "%s"' % s
      return None

    s = 'Translation of "%s": "%s"' % (s, ts)
    return TypedContent.text(s)

  def getLocationInformation(self, targetUnit, location):
    return None
