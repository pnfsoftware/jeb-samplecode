# -*- coding: utf-8 -*-

"""
[Deobfuscate WhatsApp Strings, (c) B. Kerler 2016]
- Example JEB2 Plugin for >= V2.2.1 -
* Change key values from switch statements, run plugin using Scripts/Run scripts with Source Tab open (Bytecode won't work), then close and reopen Source Tab to see decrypted strings *
** Tested with Whatsapp Version 4.5.1077 **
"""

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass, IJavaArrayElt


class JEB2WhatsAppStringDecryptor(IScript):
  def run(self, ctx):
    self.keys = [12,18,85,49,116] #Change keys here (see switch statements), here it's for com.whatsapp-451077/util/a2
	
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return

    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    project = projects[0] # Get current project(IRuntimeProject)
    print('Decompiling code units of %s...' % project)
	
    self.dexunit = RuntimeProjectUtil.findUnitsByType(project, IDexUnit, False)[0] # Get dex context, needs >=V2.2.1
    self.currentunit = ctx.getFocusedView().getActiveFragment().getUnit() # Get current Source Tab in Focus
    javaclass = self.currentunit.getClassElement()  # needs >V2.1.4
    curaddr=ctx.getFocusedView().getActiveFragment().getActiveAddress()  # needs 2.1.4
    print('Current class: %s' % javaclass.getName())
    print('Current address: %s' % curaddr)
    self.cstbuilder = self.currentunit.getFactories().getConstantFactory() # we need a context to cstbuilder to replace strings
    self.processTargetClass(javaclass) #Call our main function

  def addstring(self,insn,pre): #This function gets Strings from dex instructions and decrypts them using given xor keys
   stringindex = insn.getParameters()[1].getValue() 
   s=self.dexunit.getString(stringindex).getValue()
   s2=self.decode_string(s)
   if (stringindex not in self.stringlist):
    self.stringlist[stringindex]=s2
   if (pre not in self.resultlist):
    self.resultlist[pre]=s2
   print ("Res["+hex(stringindex)+"] Idx["+hex(pre)+"]: "+s2)

  def processTargetClass(self, javaClass):
    selclass=self.dexunit.getClass(javaClass.getName())
    addr=selclass.getAddress()
    print("%s" % addr)
    code=self.getMethodName(selclass,'<clinit>') #We need <clinit> method, as encrypted strings are there being stored in an array
    self.stringlist = {}
    self.resultlist = {}
    lines=iter(code.getInstructions()) #get all instructions for <clinit>
    idx=0
    self.searchname=""

    for insn in lines: #Here we search for the array index for the encrypted strings, which is just before the strings as const field
     if (insn.getMnemonic()) in ('const/4','const/16'):
      pre=insn.getParameters()[1].getValue()
      insn=lines.next()
      if (insn.getMnemonic()) in ('const-string','const-string/jumbo'):
       idx=pre
       self.addstring(insn,idx)
       idx+=1
     elif (insn.getMnemonic()) in ('const-string','const-string/jumbo'):
      self.addstring(insn,idx)
      idx+=1

    for item in selclass.getFields(): #Here we locate the name of the string array we try to replace
     fsig = item.getSignature(1)
     if (fsig.endswith(':[LString;')):
      self.searchname=item.getName(1)
      break

    for methods in javaClass.getMethods(): #Get Methods from Source View and use AST to get elements
     block=methods.getBody()
     i=2
     while i < block.size():
      e = block.get(i)
      self.checkElement(block,e) #Check for our string array and replace with decrypted strings
      i+=1
    
    print('*********************** Finished ***********************')

  def checkElement(self, parent, e): #Here we search for our string array and replace with decrypted strings
    if isinstance(e, IJavaArrayElt):
     for sub in e.getSubElements():
      if isinstance(sub, IJavaStaticField): #Static field holds name for string array
        name=sub.getField().getName() #here name of string array
        if (name==self.searchname):
         index=e.getIndex().getInt()	#string array index
         print("Replacing "+name+"["+hex(index)+"]")
         parent.replaceSubElement(e, self.cstbuilder.createString(self.resultlist[index])) #do our magic replace

    for sub in e.getSubElements(): #We need to parse all subelements, as we search down the ast tree for all string arrays whereever they may occur
      if isinstance(sub, IJavaClass) or isinstance(sub, IJavaField) or isinstance(sub, IJavaMethod):
        continue
      self.checkElement(e, sub)
   
  def getMethodName(self, javaClass, methodname):
    for statConst in javaClass.getMethods():
      if statConst.getName(0) == methodname:
        return statConst

  def decode_string(self,encoded_str):
   decoded_str = ''
   for i in range(len(encoded_str)):
    decoded_str += chr(ord(encoded_str[i]) ^ self.keys[i % 5])
   return decoded_str