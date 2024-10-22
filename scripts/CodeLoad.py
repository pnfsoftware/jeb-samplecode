#?description=Reload and apply basic refactoring data on loaded code units
#?shortcut=
import json
import os
import time
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
"""
Sample script for JEB Decompiler.

    JEB script to load/deserialize and apply basic refactoring data onto loaded code units.
    - On each unit of the main project it'll
      rename classes, fields and methods and add comments by it's address
    - Input data file: [JEB]/bin/codedata.txt
    - It's complementary script is: CodeSave.py . It'll save/serialize such data onto disk.


"""

# Set this to true to undo renaming and restore old names.  
#opt_UndoRename = True
opt_UndoRename = False



class CodeLoad(IScript):
  
  
  def run(self, ctx):
      
    prj = ctx.getMainProject()
    assert prj, 'getMainProject() failed:' 'Need a project'

    dataFileName = os.path.join( ctx.getProgramDirectory(), 'codedata.txt' )

    def OpenDatFile (fileName, prjname ):
        """
        Opens jsonFile and returns JSON-node with project name
        """
        data = {}
        if os.path.exists(fileName):
          with open(fileName, 'r') as f:
            try:
              data = json.load(f)
            except:
              pass
        
        FilePreviewSize=0x200      
        print '\nCurrent data (showing only the first ' + str(FilePreviewSize) + ' chars): ', json.dumps( data, indent=2  ) [:FilePreviewSize] 

        print 'MainProjectName:', prjname

        return data.get(prjname, None)

    prjname = prj.getName()
    d = OpenDatFile( dataFileName,
                     prjname )
    assert d, ('\n\nThe json-node "' + prjname + '" is not present in the file. \n'
              'Maybe because the file is empty.\n'
              'If not edit "' + dataFileName + '" and alter it to match with the MainProjectName.') 

    # Get units from project
    units = RuntimeProjectUtil.findUnitsByType( prj, ICodeUnit, False )
    assert units, 'In the project there are no code unit available.'

    unit_name_last=""

    # For all units in the project...
    for unit in units:

        # skip unprocessed units
        if not unit.isProcessed():
            continue

        unit_Name = unit.getName()
        print "unit_Name: ", unit_Name

        # open unit in data file
        unit_data = d.get(unit_Name)
        if not unit_data:
            if unit_name_last:
                print (
                    "For the unit '" + unit_Name + "' there are no entries in the data file. \n"
                    "    Maybe that is because the option 'parsers/apk/merge muli Dex' was changed \n"
                    "Trying unit_Name: '" + unit_name_last + "' instead."
                )
                unit_data = d.get(unit_name_last)
            assert unit_data, "For the unit '" + unit_Name + "' there are no entries in the data file."
        else:
            unit_name_last=unit_Name

        def ProcessItems( items, item_func ):
            myIter= IForEachWithStats(
                                        unit_data[items],
                                        item_func,
                                        items.split("_")[1] 
                                      )
            for item, name in myIter:
                pass

            global isAllSucessful            
            isAllSucessful &=  myIter.isComplete


        # #Version for people who don't like iterators:
        # # Process classes
        #for item, name in unit_data['renamed_classes'].items():
        #   item = unit.getClass(item)
        #   if item:
        #       item.setName(name)

        global isAllSucessful 
        isAllSucessful = True
        
        # Process classes
        ProcessItems( 'renamed_classes', unit.getClass )

        # Process fields
        ProcessItems( 'renamed_fields', unit.getField )

        # Process methods
        ProcessItems( 'renamed_methods', unit.getMethod )

        # note: comments are applied last since `addr` can be a refactored one here
        for addr, comment in unit_data['comments'].items():
          unit.setPrimaryComment(addr, comment)

        print(
                '\n'   +
                '='*80 +
                '\n'

        )
    print 'Basic refactoring data was applied' + (" with errors." if not isAllSucessful else "" )








class IForEachWithStats:
    """
    An iterator class to process items and keep track of statistics.

    Attributes:
        items      (dict)   : A dictionary of items to process.
        item_func (function): A function to process each item.
        item_type (str)     : A string representing the type of items being processed.

    Methods:
        __iter__(): Initializes the iterator and resets statistics.
        __next__(): Processes the next item, updates statistics, and prints the status.
    """

    printIndent = '   '

    def __init__(self, items, item_func, item_type):
        self.items = items
        self.item_func = item_func
        self.item_type = item_type

        # Initialize statistics
        self.stat_total = len(self.items)   # The total number of items
        self.stat_done = 0                  # The number of successfully processed items


        self.next = self.__next__ # Quirk: to make Python2 happy

    def __iter__(self):
        self._iterator = iter(self.items.items())


        print  '_'*80
        print  self.item_type

        return self

    def __next__(self):
        try:
            sig, name = next(self._iterator)
        except StopIteration:
            
            ##debug: fake errors
            #self.stat_done |=1
            
            self.isComplete = (self.stat_total == self.stat_done) 
            print( 
                    '{}' ' {} restored.'.format( self.stat_done,                   self.item_type ) if self.isComplete else 
                    '{}/{} {} restored.'.format( self.stat_done, self.stat_total,  self.item_type )
                  )

            raise StopIteration

        item = self.item_func(sig)
        
        currentName = item.name
        
        if opt_UndoRename:
            name=""
        
        isAlreadyRenamed = currentName == name
        
        if not isAlreadyRenamed:
            print(  IForEachWithStats.printIndent +
                    currentName + " -> " + name
            )
            
            # Set new name and store result in item
            item = item.setName(name) if item else none
        else:
             print(  IForEachWithStats.printIndent +
                     name + "\t was already renamed." )
            
        if item:
            self.stat_done += 1
        else:
             print(  IForEachWithStats.printIndent +
                IForEachWithStats.printIndent + sig + "\t is missing." )
            
        return item, name

