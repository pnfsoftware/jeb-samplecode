#?description=Show how to "tag" elements of an AST tree, and later on retrieve those tags from the Java text document output (referred to as "marks").
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.units.code.java import IJavaConstant
"""
Sample script for JEB Decompiler.

This script shows how to "tag" elements of an AST tree, and later on retrieve
those tags from the Java text document output (referred to as "marks").

This code looks for Java units, and tags String contants containing the word
'html'. Output example:

  ...
  <Java code >
  ...
  => Marks:
  17:59 - htmlTag (Potential HTML code found)

Tags are persisted in JDB2 database files.

Note: tags are specific to Java units. However, marks are not (they are
specific to text documents). The Java plugin simply renders tags as text
marks. This example demonstrates usage of tags in that context.

Marks are not displayed by the desktop GUI client.
It is up to third-party code (clients, plugins, or scripts) to display them.

Revision note: Script updated on April 12 2022.
"""
class JavaASTTags(IScript):

  def run(self, ctx):
    prj = ctx.getMainProject()
    assert prj, 'Need a project'

    for unit in prj.findUnits(IJavaSourceUnit):
      self.processClassTree(unit.getClassElement())
      doc = unit.getSourceDocument()
      javaCode, formattedMarks = self.formatTextDocument(doc)
      #print(javaCode)
      if(formattedMarks):
        print('=> Marks:')
        print(formattedMarks)

  def processClassTree(self, e_class):
    for e in e_class.getMethods():
      self.processEltTree(e)

  def processEltTree(self, e):
    if e:
      self.analyzeNode(e)
      elts = e.getSubElements()
      for e in elts:
        self.processEltTree(e)

  # demo
  def analyzeNode(self, e):
    if isinstance(e, IJavaConstant):
      if e.isString():
        if e.getString().find('html') >= 0:
          print('TAGGING: %s' % e)
          e.addTag('htmlTag', 'Potential HTML code found')

  def formatTextDocument(self, doc):
    javaCode, formattedMarks = '', ''
    # retrieve the entire document -it's a source file,
    # no need to buffer individual parts. 10 MLoC is enough 
    alldoc = doc.getDocumentPart(0, 10000000)
    for lineIndex, line in enumerate(alldoc.getLines()):
      javaCode += line.getText().toString() + '\n'
      for mark in line.getMarks():
        # the mark name is the tag attribute's key 
        if mark.getName() == 'htmlTag':
          # 0-based line and column indexes
          # the mark object is the tag attribute's value 
          formattedMarks += '%d:%d %s\n' % (lineIndex, mark.getOffset(), mark.getObject())
    return javaCode, formattedMarks
