from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.client.mcp import JebMcpServerInstance
import time
"""
This script opens or creates a new JEB project, and start the MCP server.
Connect to the MCP server with the AI tool of your choice.

How to run, e.g. on Windows:
$ jeb_wincon.bat -c --script=HeadlessMCP.py -- INPUT_FILE_PATH

Note: you need to provide an input file, as the JEB MCP server expects an opened project.
As of jeb-mcp-server v1.1.0 (JEB 5.40), there is no tool to create or load projects.
"""
class HeadlessMCP:
  def run(self, ctx):
    if not ctx.getArguments():
      print('Provide an input file or JDB2 after --')
      return
    inputpath = ctx.getArguments()[0]
    ctx.open(inputpath)
    print('Starting the MCP server...')
    mcp = JebMcpServerInstance.start()  # https://pnfsoftware.com/jeb/apidoc/com/pnfsoftware/jeb/client/mcp/JebMcpServerInstance.html
    print('%s v%s is listening on %s:%d%s' % (
      mcp.getName(), mcp.getVersion(), mcp.getHostname(), mcp.getPort(), mcp.getEndpoint()))
    input('Press Enter to stop the MCP server...')
    JebMcpServerInstance.stop()
