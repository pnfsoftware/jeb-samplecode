#?description=Jump to or display an Android target resource (string, XML, etc.) referenced by an active resource ID item (interactive number)
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IUnitView
from com.pnfsoftware.jeb.core.units import IUnit, IXmlUnit
from com.pnfsoftware.jeb.core import RuntimeProjectUtil, IUnitFilter
import org.w3c.dom.Document
"""
Sample script for JEB Decompiler.

This JEB script jumps to or displays an Android target resource (string, XML, etc.)
referenced by an active resource ID item (interactive number).

Open an APK; in a Dalvik or Java view, set the caret on a resource id; execute the script.
"""
class DexJumpToResource(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    self.activeItemValue = self.getActiveItem(ctx)
    if self.activeItemValue:
      self.name = None
      self.typeC = None

      doc = self.getTargetDoc(prj, 'public.xml')
      if not doc:
        print("*** Target XML does not exist ***")
        return

      self.getValue(doc, 'public.xml', ctx)

      if self.name and self.typeC:
        if self.typeC == "string" or self.typeC == "id":
          self.value = None
          doc = self.getTargetDoc(prj, self.typeC + 's.xml')
          self.getValue(doc, self.typeC + 's.xml', ctx)
          ctx.displayText("Id: " + self.activeItemValue, "Value: " + self.value, False)
        else:
          self.jumpToTargetFile(prj, ctx) # Open the target file

      # TODO: dispose docs


  def getActiveItem(self, ctx):
    curItem = ctx.getFocusedView().getActiveFragment().getActiveItem()
    if curItem == None:
      print("*** Cannot get the value ***")
      return None
    # hack: only work for 32-bit numbers, may be disabled in the future
    activeItemVal = str(hex(curItem.getItemId() & 0xFFFFFFFF))[:-1]
    return activeItemVal.lower()


  def getTargetDoc(self, prj, targetXML):
    units = RuntimeProjectUtil.findUnitsByType(prj, IXmlUnit, False)
    for unit in units:
      if not unit.isProcessed():
        unit.process()
      if unit.getName() == targetXML:
        doc = unit.getDocument()
        return doc
    return None


  def getValue(self, doc, targetXML, ctx):
    #print(targetXML)
    if (targetXML == 'public.xml'):
      xmlLists = doc.getElementsByTagName("public");
      for i in range(xmlLists.getLength()):
        node = xmlLists.item(i)
        if(self.activeItemValue == str(node.getAttribute("id"))):
          self.name = node.getAttribute("name")
          self.typeC = node.getAttribute("type")
          return
      print("*** It does not belong to public.xml ***")
    if (targetXML == 'ids.xml'):
      xmlLists = doc.getElementsByTagName("item");
      for i in range(xmlLists.getLength()):
        node = xmlLists.item(i)
        if(self.name == str(node.getAttribute("name"))):
          self.value = node.getTextContent()
          return
      print("*** It does not belong to ids.xml ***")
    if (targetXML == 'strings.xml'):
      xmlLists = doc.getElementsByTagName("string");
      for i in range(xmlLists.getLength()):
        node = xmlLists.item(i)
        if(self.name == str(node.getAttribute("name"))):
          self.value = node.getTextContent()
          return
      print("*** It does not belong to strings.xml ***")
    print('*** Cannot find target XML file ***')


  def jumpToTargetFile(self, prj, ctx):
    unitFilter = UnitFilterByName(self.name + '.xml')
    unit = RuntimeProjectUtil.filterUnits(prj, unitFilter).get(0)
    if unit:
      ctx.openView(unit)
      return
    print("*** Cannot find target file ***")


class UnitFilterByName(IUnitFilter):
  def __init__(self, name):
    self.name = name
  def check(self, unit):
    return unit.getName() == self.name
