# -*- coding: utf-8 -*-

"""
[Deobfuscate WhatsApp Strings V2, (c) B. Kerler 2016]
- Example JEB Plugin for >= V2.2.1 -
* Change key values from switch statements, run plugin using Scripts/Run scripts with Source Tab open, clicking into it (Bytecode Window won't work)*
** Tested with Whatsapp Version 4.5.1077 and 2.16.20 **
"""

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass, IJavaArrayElt
from com.pnfsoftware.jeb.core.events import JebEvent, J

class WhatsAppStringDecryptor(IScript):
  def run(self, ctx):
    self.keys = {}
	
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
    self.currentunit.notifyListeners(JebEvent(J.UnitChange))

  def addstring(self,insn,pre): #This function gets Strings from dex instructions and decrypts them using given xor keys
   stringindex = insn.getParameters()[1].getValue() 
   s=self.dexunit.getString(stringindex).getValue()
   s2=self.decrypt_string(s)
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
    self.constlist = {}

    lines=iter(code.getInstructions()) #get all instructions for <clinit>, search for constants
    for insn in lines:
      #print (insn.getMnemonic())
      if (insn.getMnemonic()) in ('new-array'):
        break
      if (insn.getMnemonic()) in ('const/4','const/16'):
        self.constlist[insn.getParameters()[0].getValue()]=insn.getParameters()[1].getValue()

    print ("Extracted constants")
    print (self.constlist)

    #Start searching and extracting key values for encryption, which are stored either as const or as variable in a switch.	
    for insn in lines:
     if (insn.getMnemonic()) in ('rem-int/lit8'): #Find and extract default value from first switch context
      #print ("rem-int/lit8")
      if (len(insn.getParameters())<2):
        insn=lines.next()
        continue
      count=insn.getParameters()[2].getValue()
      if (count!=5):
        insn=lines.next()
        continue
      #print ("We got 5")
      insn=lines.next()
      if (insn.getMnemonic()) in ('packed-switch'):
       #print ("We got packed-switch")
       insn=lines.next()
       found=False
       if (insn.getMnemonic()) in ('const/16'):
        self.keys[4]=insn.getParameters()[1].getValue()
        found=True
       elif (insn.getMnemonic()) in ('move'):
        value=insn.getParameters()[1].getValue()
        #print("We got const: v%02X=%02X" % (value,self.constlist[value]))
        self.keys[4]=self.constlist[value]
        found=True
		
       if found==True: 
         keycount=0
         insn=lines.next()
         
         while (insn): #Skip to switch, first goto line
          if (insn.getMnemonic()) in ('goto/16'):
            break
          insn=lines.next()
		  
         while (insn):
          if (insn.getMnemonic()) in ('const/16'):
           #print("Key[%d]=%02X" % (keycount, insn.getParameters()[1].getValue()))
           self.keys[keycount]=insn.getParameters()[1].getValue()
           keycount=keycount+1
           if (keycount==4):
             break
          elif (insn.getMnemonic()) in ('move'):
           value=insn.getParameters()[1].getValue()
           #print("Key[%d]=v%02X=>%02X" % (keycount,value,self.constlist[value]))
           self.keys[keycount]=self.constlist[value]
           keycount=keycount+1
           if (keycount==4):
             break
          insn=lines.next()
       else:
         break

    print('**** Keys detected: %02X %02X %02X %02X %02X ****' % (self.keys[0],self.keys[1],self.keys[2],self.keys[3],self.keys[4]))

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
    
    for methods in javaClass.getMethods(): #Get Methods from Source View and use AST to get elements
     #print("["+methods.getName()+"]:")
     block=methods.getBody()
     i=2
     while i < block.size():
      e = block.get(i)
      self.checkElement(block,e) #Check for our string array and replace with decrypted strings
      i+=1
    
    print('*********************** Finished ***********************')

  def checkElement(self, parent, e): #Here we search for our string array and replace with decrypted strings
    if isinstance(e, IJavaArrayElt):
     #print(e)
     for sub in e.getSubElements():
      if isinstance(sub, IJavaStaticField): #Static field holds name for string array
        name=sub.getField().getName() #here name of string array
        #print("Got name "+name)
        if (name==self.searchname):
         try:
          index=e.getIndex().getInt() #string array index
          print("Replacing "+name+"["+hex(index)+"]")
          parent.replaceSubElement(e, self.cstbuilder.createString(self.resultlist[index])) #do our magic replace
         except:
          print("Err:")
          print(e.getIndex())

    for sub in e.getSubElements(): #We need to parse all subelements, as we search down the ast tree for all string arrays whereever they may occur
      #print("Sub:")
      #print(sub)
      if isinstance(sub, IJavaClass) or isinstance(sub, IJavaField) or isinstance(sub, IJavaMethod):
        continue
      self.checkElement(e, sub)
   
  def getMethodName(self, javaClass, methodname):
    for statConst in javaClass.getMethods():
      if statConst.getName(0) == methodname:
        return statConst

  def decrypt_string(self,encoded_str):
   decrypted_str = ''
   for i in range(len(encoded_str)):
    decrypted_str += chr(ord(encoded_str[i]) ^ self.keys[i % 5])
   return decrypted_str