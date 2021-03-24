#?description=How to use PyDev and pydevd to debug JEB Python scripts
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler..
"""
class SampleScriptDebugging(IScript):
  def run(self, ctx):

    # To be done once:
    # 1) Install Eclipse IDE and the PyDev plugin (PyCharm users: look into https://pypi.org/project/pydevd-pycharm/)
    # 2) Git-clone https://github.com/fabioz/PyDev.Debugger into your JEB folder

    # To be done to get ready to debug a script:
    # 3) Fire up the IDE, switch to the Debug perspective, then select Pydev menu, Start Debug Server...
    # 4) In the script to be debugged, import pydevd:
    import sys
    sys.path.append(ctx.getBaseDirectory() + '/PyDev.Debugger')
    import pydevd

    # 5) Wherever the breakpoint is to be placed, call settrace()
    pydevd.settrace()

    # 6) Now, run your script (e.g. within JEB GUI, press F2, then select or browse for your script, and execute it)
    # With settrace invoked just above, when the script is run, the debugger will be brought up when execution reaches
    # the statement that follows it, in the case of this example, that one:
    a = 1

    # 7) Switch to your IDE; your script should have been brought up in the editor, with the current on-breakpoint line
    # highlighted in green. Debug as expected (tracing, variable views/writes, etc.). Note that rendering of print() statements
    # will be delayed in JEB's logger; you can see them if JEB was started from a shell rendering stdout

    # some random code that can be stepped over...
    b = 100L
    c = 'strings and primitives can be viewed and changed when debugging'
    print('Hello, JEB script debugging: %d %d %s' % (a, b, c))
