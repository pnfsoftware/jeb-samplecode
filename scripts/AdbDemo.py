#?description=Create and use adb (Android Debug Bridge) wrappers and adb utility objects
#?shortcut=
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android.adb import AdbWrapperFactory, AdbWrapperFactory, AndroidDeviceUtil
"""
Sample script for JEB Decompiler.
This script shows how to create and use Android Debug Bridge (adb) wrappers and adb utility objects.
Reference: AdbWrapperFactory, AdbWrapper, AndroidDeviceUtil
"""
class AdbDemo(IScript):
  def run(self, ctx):
    # factory object wraps adb, not tied to a specific device
    adbf = AdbWrapperFactory()  # see javadoc for a list of methods
    adbf.initialize()
    print('adb version: %s' %adbf.getVersion())

    for dev in adbf.listDevices():
      # an AdbWrapper object is tied to a debuggable device
      adb = adbf.createWrapper(dev.getSerial())
      break
    else:
      print 'no android device found'
      return
    print(adb) # see javadoc for a list of methods
    #adb.listPackages()
    #adb.listProcesses()
    #adb.readProperty("ro.build.version.release")
    #adb....    

    # higher-level wrappers: see AndroidDeviceUtil