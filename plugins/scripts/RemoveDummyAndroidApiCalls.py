from com.pnfsoftware.jeb.core.units.code.java import JavaOperatorType
from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDOptimizer, IDVisitor

'''
This JEB's dexdec IR optimizer will attempt to resolve artificial Android library invocations
added by app protectors, designed to hamper the string auto-decryption process.

This Python plugin is executed during the decompilation pipeline of a method.
Needs JEB 4.4 or above.

Example:
 
  private static String a(String str, int key) {
    StringBuilder out = new StringBuilder();
    for(int i = 0; i < str.length(); i++) {
      char c = (char)(str.charAt(i) - key + 0xFF);
      out.append(c);
    }
    return out.toString();
  }

  public String get() {
    int key = 0x100 - android.graphics.Color.red(0);  // 0x100 - 0 = 0x100, the key value
    return a("ifmmp", key);                           // would return "hello""
  }

Problem: Here, JEB cannot auto-decrypt and inline a(), because of the Color.red(0) invocation.
Solution: This IR plugin finds such calls, evaluates them, and replaces the IR by a constant, thereby allowing
further optimizers in the decompilation pipeline to proceed and eventually auto-decrypt and decompile this method to:

  public String get() {
    return "hello";
  }

How to use:
- Drop this file in your JEB's coreplugins/python/ sub-directory
- Make sure to have the setting `.LoadPythonPlugins = true` in your JEB's bin/jeb-engines.cfg file

For additional information regarding dexdec IR optimizer plugins, refer to:
- the JEB Manual (www.pnfsoftware.com/jeb/manual)
- the API documentation: https://www.pnfsoftware.com/jeb/apidoc/reference/com/pnfsoftware/jeb/core/units/code/android/ir/package-summary.html
'''

class RemoveDummyAndroidApiCalls(AbstractDOptimizer):  # note that we extend AbstractDOptimizer for convenience, instead of implementing IDOptimizer from scratch
  def perform(self):
    # create our instruction visitor
    vis = AndroidUtilityVisitor(self.ctx)

    # visit all the instructions of the IR CFG
    for insn in self.cfg.instructions():
      insn.visitInstruction(vis)

    # Reset deobfuscators counters, generally updated by IR optimizers that rely on IR emulation.
    # Counters are used to track emulation successes and failures for methods. Some optimizers may
    # check the counters to avoid attempting to emulate methods for which too many failures were
    # reported. Calling this method resets such counters, allowing emulation to be re-attempted.
    # (requires JEB 4.4)
    if vis.cnt > 0:
      self.g.resetDeobfuscatorCounters()

    # return the count of replacements
    return vis.cnt

class AndroidUtilityVisitor(IDVisitor):
  def __init__(self, ctx):
    self.ctx = ctx
    self.cnt = 0

  def process(self, e, parent, results):
    repl = None

    if not repl and e.isCallInfo():
      sig = e.getMethodSignature()

      # Color.red(integer_value)
      if not repl and sig == 'Landroid/graphics/Color;->red(I)I' and e.getArgument(0).isImm():
        color = e.getArgument(0).toLong()
        # extract the red value
        val = (color >> 16) & 0xFF
        # replace the IDCallInfo by an IDImm
        repl = self.ctx.getGlobalContext().createInt(val)

      if not repl and sig == 'Landroid/graphics/Color;->green(I)I' and e.getArgument(0).isImm():
        color = e.getArgument(0).toLong()
        val = (color >> 8) & 0xFF
        repl = self.ctx.getGlobalContext().createInt(val)

      if not repl and sig == 'Landroid/graphics/Color;->blue(I)I' and e.getArgument(0).isImm():
        color = e.getArgument(0).toLong()
        val = color & 0xFF
        repl = self.ctx.getGlobalContext().createInt(val)

      # TextUtils.getOffsetBefore("", 0) => 0
      if not repl and sig == 'Landroid/text/TextUtils;->getOffsetBefore(Ljava/lang/CharSequence;I)I' and e.getArgument(0).isImm() and e.getArgument(1).isImm():
        buf = e.getArgument(0).getStringValue(self.ctx.getGlobalContext())
        val = e.getArgument(1).toLong()
        if buf == '' and val == 0:
          repl = self.ctx.getGlobalContext().createInt(0)

      # TextUtils.indexOf("", 'x') => -1
      if not repl and sig == 'Landroid/text/TextUtils;->indexOf(Ljava/lang/CharSequence;C)I' and e.getArgument(0).isImm():
        buf = e.getArgument(0).getStringValue(self.ctx.getGlobalContext())
        if buf == '':
          repl = self.ctx.getGlobalContext().createInt(-1)

      # TextUtils.indexOf("", "", [start=0, [end]]) => start
      if not repl and sig == 'Landroid/text/TextUtils;->indexOf(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)I' and e.getArgument(1).isImm():
        needle = e.getArgument(1).getStringValue(self.ctx.getGlobalContext())
        if needle == '':
          start = 0
          repl = self.ctx.getGlobalContext().createInt(start)
      if not repl and sig == 'Landroid/text/TextUtils;->indexOf(Ljava/lang/CharSequence;Ljava/lang/CharSequence;I)I' and e.getArgument(1).isImm() and e.getArgument(2).isImm():
        needle = e.getArgument(1).getStringValue(self.ctx.getGlobalContext())
        if needle == '':
          start = e.getArgument(2).toLong()
          repl = self.ctx.getGlobalContext().createInt(start)
      if not repl and sig == 'Landroid/text/TextUtils;->indexOf(Ljava/lang/CharSequence;Ljava/lang/CharSequence;II)I' and e.getArgument(1).isImm() and e.getArgument(2).isImm():
        needle = e.getArgument(1).getStringValue(self.ctx.getGlobalContext())
        if needle == '':
          start = e.getArgument(2).toLong()
          repl = self.ctx.getGlobalContext().createInt(start)

      # Long.compare(xxx, 0)
      if not repl and sig == 'Ljava/lang/Long;->compare(JJ)I' and e.getArgument(1).isImm() and e.getArgument(1).toLong() <= 0:
        v0 = None
        v1 = e.getArgument(1).toLong()
        if e.getArgument(0).isCallInfo():
          sig2 = e.getArgument(0).getMethodSignature()
          if sig2 == 'Landroid/os/Process;->getElapsedCpuTime()J':
            # elapsed time always >0, value does not matter since we are comparing against 0
            v0 = 1
          elif sig2 == 'Landroid/os/SystemClock;->currentThreadTimeMillis()J':
            v0 = 1
        if v0 != None:
          r = 1 if v0 > v1 else (-1 if v0 < v1 else 0)
          repl = self.ctx.getGlobalContext().createInt(r)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getFadingEdgeLength()I':
        # always a small positive integer, normally set to FADING_EDGE_LENGTH (12)
        repl = self.ctx.getGlobalContext().createInt(12)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getZoomControlsTimeout()J':
        repl = self.ctx.getGlobalContext().createLong(3000)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getEdgeSlop()I':
        repl = self.ctx.getGlobalContext().createInt(12)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getJumpTapTimeout()I':
        repl = self.ctx.getGlobalContext().createInt(500)

      if not repl and sig == 'Landroid/media/AudioTrack;->getMinVolume()F':
        repl = self.ctx.getGlobalContext().createFloat(0)

      if not repl and sig == 'Landroid/util/TypedValue;->complexToFloat(I)F' and e.getArgument(0).isImm():
        val = e.getArgument(0).toLong()
        if val == 0:
          repl = self.ctx.getGlobalContext().createFloat(0)

      if not repl and sig == 'Ljava/lang/Long;->compare(JJ)I' and e.getArgument(0).isImm() and e.getArgument(1).isImm():
        v0 = e.getArgument(0).toLong()
        v1 = e.getArgument(1).toLong()
        r = 1 if v0 > v1 else (-1 if v0 < v1 else 0)
        repl = self.ctx.getGlobalContext().createInt(r)

      if not repl and sig == 'Ljava/lang/Float;->compare(FF)I' and e.getArgument(0).isImm() and e.getArgument(1).isImm():
        v0 = e.getArgument(0).toFloat()
        v1 = e.getArgument(1).toFloat()
        r = 1 if v0 > v1 else (-1 if v0 < v1 else 0)
        repl = self.ctx.getGlobalContext().createInt(r)

      if not repl and sig == 'Ljava/lang/Double;->compare(DD)I' and e.getArgument(0).isImm() and e.getArgument(1).isImm():
        v0 = e.getArgument(0).toDouble()
        v1 = e.getArgument(1).toDouble()
        r = 1 if v0 > v1 else (-1 if v0 < v1 else 0)
        repl = self.ctx.getGlobalContext().createDouble(r)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getGlobalActionKeyTimeout()J':
        repl = self.ctx.getGlobalContext().createLong(500L)

      if not repl and sig == 'Landroid/view/ViewConfiguration;->getMaximumDrawingCacheSize()I':
        repl = self.ctx.getGlobalContext().createInt(480 * 800 * 4)

      if not repl and sig == 'Landroid/os/Process;->getGidForName(Ljava/lang/String;)I' and e.getArgument(0).isImm():
        name = e.getArgument(0).getStringValue(self.ctx.getGlobalContext())
        if name == '':
          repl = self.ctx.getGlobalContext().createInt(-1)

    # (android.os.Process.getThreadPriority(?) + 20) >> 6  ==> should be 0 since priority is in [-19, 20]
    if not repl and e.isOperation() and e.getOperator().is(JavaOperatorType.SHR):
      if e.getLeft().isOperation() and e.getRight().isImm():
        if e.getRight().toLong() >= 6:
          l = e.getLeft()
          if l.getOperator().is(JavaOperatorType.ADD):
            if l.getLeft().isCallInfo() and l.getLeft().getMethodSignature() == 'Landroid/os/Process;->getThreadPriority(I)I':
              if l.getRight().isImm() and l.getRight().toLong() >= 20:
                repl = self.ctx.getGlobalContext().createInt(0)

    if repl != None and parent.replaceSubExpression(e, repl):
      #print('*** CUSTOM REPLACE *** %s -> %s' % (e, repl))
      # success (this visitor is pre-order, we need to report the replaced node)
      results.setReplacedNode(repl)
      self.cnt += 1
