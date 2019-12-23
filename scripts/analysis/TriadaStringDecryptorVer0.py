# -*- coding: utf-8 -*-

"""
This JEB script is a string decryptor for the obfuscated Triada malware. Decrypted strings will be added as field comments in your Java classes.
Author: Ruoxiao Wang

The script can be tested on Triada Application MD5 592fa585b64412e31b3da77b1e825208
- The target class path: com/zmpk/a/a (contains all encrypted byte arrays and two decryptors)
- The main decryptor is in: com/zmpk/a/c

*** CUSTOMIZE the attributes TARGET_CLASS_NAME, DECRYPTOR_1_NAME_KEY, DECRYPTOR_2_NAME_KEY and DECRYPTOR_MAIN_KEY to decrypt strings located in other classes ***

How to run the script:
(1) (Optional) Copy TriadaStringDecryptorVer0.py to your jeb2 scripts folder
(2) Start the JEB application and open the Triada file
(3) Open the target class (path: com/zmpk/a/a)
(4) Press Q to decompile the class
(5) Select: File -> Scripts -> Run Script -> TriadaStringDecryptorVer0.py and click open
(6) Decrypted strings will be added to the target class as comments

Several Objects and APIs are used:
(1) IScript: Interface for client's scripts.
(2) IRuntimeProject: A runtime project represents a loaded instance of a JEB project.
(3) ICodeUnit: Base interface for units handling binary code, such as bytecode, opcodes, object files, executable files.
(4) IJavaSourceUnit: Definition of a source unit representing a Java class in the form of an Abstract Syntax Tree.
(5) IJavaClass: Java AST interface to represent a Java class. Class elements contain other classes (inner classes), fields, and methods.
(6) IJavaConstantFactory: Builder for Java AST constants.
(7) RuntimeProjectUtil: A collection of utility methods to navigate and act on JEB projects.
(8) ICodeField: A filed object.
(9) IJavaMethod: Java AST interface to represent Java methods.
(10) IJavaBlock: Java AST interface to represent a sequence of statements.
(11) IJavaAssignment: Java AST interface to represent assignments.
* For detailed information, please refer to the PNF API document.
* Detailed comments are added to the script TriadaStringDecryptorVer0.py
"""

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData
from com.pnfsoftware.jeb.core.events import JebEvent, J
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass


class TriadaStringDecryptorVer0(IScript):

  # NOTE: USERS MUST CUSTOMIZE THESE FIELDS in order to decrypt strings located in other classes
  TARGET_CLASS_NAME = "Lcom/zmpk/a/a;" # Specify the name of target class
  DECRYPTOR_1_NAME_KEY = ("a", 44) # Specify the name and key of decryptor 1
  DECRYPTOR_2_NAME_KEY = ("b", 43) # Specify the name and key of decryptor 2
  DECRYPTOR_MAIN_KEY = -1 # Specify the key of main decryptor

  def run(self, ctx):

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

    self.codeUnit = RuntimeProjectUtil.findUnitsByType(project, ICodeUnit, False)[0] # Get the current codeUnit(ICodeUnit)
    # RuntimeProjectUtil: A collection of utility methods to navigate and act on JEB projects.
    # findUnitsByType: Find all units of a project that are of the specified type
    # ICodeUnit: Code units are inherently interactive, in order to provide facility for code refactoring, modification...

    # enumerate the decompiled classes, find and process the target class
    units = RuntimeProjectUtil.findUnitsByType(project, IJavaSourceUnit, False)
    # IJavaSourceUnit: Definition of a source unit representing a Java class in the form of an Abstract Syntax Tree

    for unit in units:
      javaClass = unit.getClassElement() # Get a reference to the Java class defined in this unit
      # IJavaClass: Java AST interface to represent a Java class. Class elements contain other classes (inner classes), fields, and methods

      if javaClass.getName() == self.TARGET_CLASS_NAME: # If the current class is the target class
        self.cstbuilder = unit.getFactories().getConstantFactory()
        # getFactories: A collection of Java AST element factories
        # IJavaFactories: A collection of Java AST element factories(methods)
        # IJavaConstantFactory(self.cstbuilder): Builder for Java AST constants

        self.processClass(javaClass) # Process the target class
        break

  def processClass(self, javaClass):

    wanted_flags = ICodeItem.FLAG_PRIVATE|ICodeItem.FLAG_STATIC|ICodeItem.FLAG_FINAL # Set the flag: "private" && "static" && "final"

    # Get the static constructor
    statArea = "";
    for statArea in javaClass.getMethods():
      if statArea.getName() == '<clinit>':
        break

    for i in range(javaClass.getFields().size()):
      fsig = javaClass.getFields().get(i).getSignature()

      if fsig.endswith(':[B'):
        f = self.codeUnit.getField(fsig) # Get the field of the ith static final variable
        s0 = statArea.getBody().get(i) # Get the ith assignment in static constructor
        encbytes = [] # Used to store the elements of the current byte array

        if isinstance(s0.getLeft(), IJavaStaticField) and s0.getLeft().getField().getSignature() == f.getSignature(True):
          array = s0.getRight()

          if isinstance(array, IJavaNewArray):
            for v in array.getInitialValues(): # Get the list of initial values of the byte array
              optElement = 0 # Used to store the element decrypted by the decryptor

              if isinstance(v, IJavaCall): # Determine if the element is an instance of an IJavaCall
                mname = v.getMethod().getName() # Get the name of the method(call method, decryptor)
                arrayArguments = [] # Used to store the arguments of the method

                # Get decryptor name and store the arguments
                if mname == "byteValue":
                  # If the decryptor name is "byteValue", which means the method is like "a.b(74).byteValue()", we need to get the first part: "a.b(74)", 
                  # then extract the real method name "b"
                  mname = v.getArguments().get(0).getMethod().getName();
                  # Get the arguments of the method
                  for arg in v.getArguments().get(0).getArguments():
                    if isinstance(arg, IJavaConstant):
                      arrayArguments.append(arg.getInt())
                else:
                  # Get the arguments of the method
                  for arg in v.getArguments():
                    if isinstance(arg, IJavaConstant):
                      arrayArguments.append(arg.getInt())

                # Get the correspond decryptor and decrypt the element
                if mname == self.DECRYPTOR_1_NAME_KEY[0]:
                  if len(arrayArguments) == 1:
                    optElement = self.decryptor1(arrayArguments[0])
                if mname == self.DECRYPTOR_2_NAME_KEY[0]:
                  if len(arrayArguments) == 1:
                    optElement = self.decryptor2(arrayArguments[0])
                encbytes.append(optElement)
              else:
                encbytes.append(v.getByte())

        decrypted_string = self.decryptorMain(encbytes) # Descrpt the byte array into string
        self.addComments(self.codeUnit, f.getItemId(), decrypted_string) # Call the addComments method to add comment to the java class
    #print('*********************** Finished ***********************')

  def addComments(self, unit, itemId, comment):
    data = ActionCommentData() # Create a new instance of ActionCommentData
    data.setNewComment(comment) # Add the decrypted string as comment to data
    address = unit.getAddressOfItem(itemId)
    # Set the comment
    ctx = ActionContext(unit, Actions.COMMENT, itemId, address)
    if unit.prepareExecution(ctx, data):
      r = unit.executeAction(ctx, data)
      if not r:
        print('Cannot set comment at address %s' % address)

  def decryptor1(self, eachByte):
    eachByte += self.DECRYPTOR_1_NAME_KEY[1]
    return eachByte

  def decryptor2(self, eachByte):
    eachByte += self.DECRYPTOR_2_NAME_KEY[1]
    return eachByte

  def decryptorMain(self, encbytes):
    r = ''
    for i in encbytes:
      temp = i + self.DECRYPTOR_MAIN_KEY
      r += chr(temp & 0xFF)
    return r