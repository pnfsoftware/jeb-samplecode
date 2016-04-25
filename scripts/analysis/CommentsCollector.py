"""
This JEB2 script shows how to collect all the comments and notes from a project and automatically generate a table document to show them.
Author: Ruoxiao Wang

How to use the script:
(1) (Optional) Copy CommentsCollector.py to your jeb2 scripts folder
(2) Start the JEB2 application and open an Android app
(3) Double click the top level unit
(4) Select: File -> Scripts -> Run Script -> CommentsCollector.py and click open
(5) A table document contains all comments and notes will be created in the top-level unit.

Several Objects and APIs are used:
(1) IScript: Interface for client's scripts.
(2) IInteractiveUnit: Interactive units are units that offer clients the ability to execute actions on their contents.
(3) IUnitView: Basic definition of a view, visually representing a unit. A client may have 0, 1, or many views.
(4) getFormatter(): Retrieve a fresh formatter for that unit.
(5) StaticTableDocument: A simple table document. Such table document objects do not listen to unit changes events; in fact, they are unaware of the IUnit family of classes. They are ideal to distribute static, immutable contents.
(6) TableRow: A trivial implementation of a table row of cells.
(7) Cell: A simple implementation of an actionable visual cell item.
(8) UnitRepresentationAdapter: A simple unit representation, always returning the document set provided at construction time.
(9) openView(): open the specified unit.

* For detailed information, please refer to the PNF API document.
* Detailed comments are added to the script CommentsCollector.py
"""

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units import IUnit, IInteractiveUnit
from com.pnfsoftware.jeb.core.output.table.impl import StaticTableDocument, TableRow, Cell
from com.pnfsoftware.jeb.core.output import UnitRepresentationAdapter, IUnitDocumentPresentation
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.events import JebEvent, J
from java.util import ArrayList, Arrays

class CommentsCollector(IScript):
  def run(self, ctx):
    self.documentName = 'Comments Table'
    engctx = ctx.getEnginesContext()
    if not engctx:
      print('Back-end engines not initialized')
      return
    
    projects = engctx.getProjects()
    if not projects:
      print('There is no opened project')
      return

    prj = projects[0]
    print('Decompiling code units of %s...' % prj)

    units = RuntimeProjectUtil.findUnitsByType(prj, None, False)

    if not units:
      print('No unit exists')
      return

    targetUnit = units[0] # Get the top-level unit
    formatter = targetUnit.getFormatter() # Get the formatter of the unit
    
    # Set table column names
    columnLabels = Arrays.asList('Unit Name', 'Address', 'Comment')

    # Add comments to the arraylist rows
    self.rows = ArrayList()
    for unit in units:
      self.addCommentsToDoc(unit)
    
    # Create the table doc
    tableDoc = StaticTableDocument(columnLabels, self.rows)
    
    # Delete the old table doc and add the new table doc to presentations
    newId = 2 # Set the initial table doc Id (Do not use 1! 1 is default number used by "source")
    for i, document in enumerate(formatter.getPresentations()): # Find the old table doc
      if (self.documentName == document.getLabel()):
        newId = document.getId() + 1 # Adding 1 to the old table doc Id as the Id of the new doc (avoid the collision)
        formatter.removePresentation(i) # Delete the old table doc from presentations
        break
    adapter = UnitRepresentationAdapter(newId, self.documentName, False, tableDoc) # Get the new adapter
    formatter.addPresentation(adapter, True) # Add the new table doc to presentations

    # Jump to the table doc fragment in the top-level unit
    views = ctx.getViews(targetUnit) # Get all views of target unit(top-level unit)
    if not views:
      ctx.displayMessageBox('Warning', 'Please open the top-level unit', None, None) # Show the value directly
      return

    targetView = views.get(0)
    
    fragments = targetView.getFragments() # Get all fragments of target view
    if not fragments:
      ctx.displayMessageBox('Warning', 'No fragment exists', None, None)
      return

    targetFragment = targetView.getFragments().get(fragments.size() - 1) # Get the table doc just created
    # targetView.setActiveFragment(targetFragment)
    ctx.openView(targetUnit) # Open target Unit(top-level unit)
    targetUnit.notifyListeners(JebEvent(J.UnitChange))

  def addCommentsToDoc(self, unit):
    notes = unit.getNotes() # Get the notes of unit
    if isinstance(unit, IInteractiveUnit): # If the type of unit is IInteractiveUnit, which means it my has comments and we can use getComments()
      totalComments = unit.getComments() # Get all comments
      flag = True # If flag is true, we will add the unit name in the first column, and after that, it will be set to false, which means other rows of this unit will not be added the unit name.
                  # So only the first row of the unit have the unit name
      if totalComments:
        for address in totalComments:
          if (totalComments[address] != None and totalComments[address] != ''):
            if (flag):
              self.rows.add(TableRow(Arrays.asList(Cell(unit.getName()), Cell(address), Cell(totalComments[address]))))
              flag = False
            else:
              self.rows.add(TableRow(Arrays.asList(Cell(''), Cell(address), Cell(totalComments[address]))))
      if totalComments and notes:
        self.rows.add(TableRow(Arrays.asList(Cell(''), Cell('Notes:'), Cell(unit.getNotes()))))
        return
      if notes:
        self.rows.add(TableRow(Arrays.asList(Cell(unit.getName()), Cell('Notes:'), Cell(unit.getNotes()))))
        return
      return
    if notes:
      self.rows.add(TableRow(Arrays.asList(Cell(unit.getName()), Cell('Notes:'), Cell(unit.getNotes()))))