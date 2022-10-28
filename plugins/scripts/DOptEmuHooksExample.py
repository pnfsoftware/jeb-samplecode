from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDOptimizer, IDEmulatorHooks
'''
dexdec IR plugin showing how to set up an emulator hooks for internal dex methods.
The plugin below is an IR optimizer repeatedly invoked during the IR optimization phase of decompilation.
API reference: see IDEmulatorHooks
'''
class DOptEmuHooksExample(AbstractDOptimizer):
  def perform(self):
    # retrieve or create the current decompiler thread emulator
    emu = self.g.getEmulator()
    # create and register a hooks object (for internal dex methods)
    hooks_id = emu.registerEmulatorHooks(Hooks(emu))
    try:
      # do some work using the emulator
      # when/if the emulator emulates internal dex methods, the hooks routines will be called
      pass
    finally:
      assert emu.unregisterEmulatorHooks(hooks_id)

    # alternatively, you may want to set up global hooks to customize how other optimizers do their work
    # in this case, you want to make sure to not re-register the same hooks every time this optimizer is called
    # and also not unregister the hooks object when done
    '''
    emu = self.g.getEmulator()
    if not emu.getData('hooksSet'):
      emu.setData('hooksSet', True)
      emu.registerEmulatorHooks(Hooks(emu))
    '''
    return 0

class Hooks(IDEmulatorHooks):
  def __init__(self, emu):
    self.emu = emu

  def invokeMethod(self, reqid, msig, args):
    print('IR: invokeMethod: id=%d: %s(%s)' % (reqid, msig, args))
    # TODO: add custom code
    return None

  # note that this routine is called only if the emulation of the invocation succeeded
  def examineMethodResult(self, reqid, result):
    print('IR: examineMethodResult: id=%d: ret=%s' % (reqid, result))
    # TODO: add custom code
    return None
