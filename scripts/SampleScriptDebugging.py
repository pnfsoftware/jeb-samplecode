#?description=How to use pydevd to debug JEB Python scripts inside Eclipse IDE or PyCharm
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
"""
Sample script for JEB Decompiler..
"""
class SampleScriptDebugging(IScript):
  def run(self, ctx):

    # To debug inside Eclipse IDE:
    #   1) Install Eclipse IDE and the PyDev plugin to make it a full-fledged Python IDE
    #   2) Git-clone https://github.com/fabioz/PyDev.Debugger into your JEB folder
    # To debug inside PyCharm:
    #   1) Install JetBrains PyCharm
    #   2) Download pydevd-pycharm from https://pypi.org/project/pydevd-pycharm/#files and
    #      unpack the pydevd-pycharm-xxx directory buried in the tarball to a newly
    #      created `pydevd-pycharm` folder into your JEB folder

    # Now get ready to debug a script:
    # 1) Fire up the IDE, switch to the Debug perspective/layout and start the PyDev Debug Server.
    # 2) In the script to be debugged, import the appropriate pydevd module:

    # ... with Eclipse:
    import sys
    sys.path.append(ctx.getBaseDirectory() + '/PyDev.Debugger')
    import pydevd
    # ... or with PyCharm: (uncomment below and comment above)
    #sys.path.append(ctx.getBaseDirectory() + '/pydevd-pycharm')
    #import pydevd_pycharm

    # 3) Wherever the breakpoint is to be placed, call settrace()
    # note: additional parameters may be specified, such as the debugger server hostname/port, etc.
    # refer to pydevd documentation for details
    pydevd.settrace(stdoutToServer=True, stderrToServer=True)

    # 4) Now, run your script (e.g. within JEB GUI, press F2, then select or browse for your script, and execute it)
    # With settrace invoked just above, when the script is run, the debugger will be brought up when execution reaches
    # the statement that follows it, in the case of this example, that one:
    a = 1

    # 5) Switch to your IDE; your script should have been brought up in the editor, with the current on-breakpoint line
    # highlighted in green. Debug as expected (tracing, variable views/writes, etc.). Note that rendering of print() statements
    # will be delayed in JEB's logger; you can see them if JEB was started from a shell rendering stdout

    # some random code that can be stepped over...
    b = 100L
    c = 'strings and primitives can be viewed and changed when debugging'
    print('Hello, JEB script debugging: %d %d %s' % (a, b, c))
