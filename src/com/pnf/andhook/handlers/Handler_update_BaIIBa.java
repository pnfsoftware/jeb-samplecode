package com.pnf.andhook.handlers;

import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerEventData;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerThreadStackFrame;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerVariable;

/**
 * Hook for Cipher method:
 * <code>int update(byte[] input, int inputOffset, int inputLen, byte[] output)</code>.
 * 
 * @author Nicolas Falliere
 *
 */
public class Handler_update_BaIIBa extends AbstractHandler {

    @Override
    public String getAddress() {
        return "Ljavax/crypto/Cipher;->update([BII[B)I";
    }

    @Override
    public void onEnter(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        IDebuggerThreadStackFrame f0 = dbg.getThreadById(tid).getFrame(0);
        IDebuggerVariable p1 = f0.getInternalParameter(1, "[B");
        IDebuggerVariable p2 = f0.getInternalParameter(2, "I");
        IDebuggerVariable p3 = f0.getInternalParameter(3, "I");
        IDebuggerVariable p4 = f0.getInternalParameter(4, "[B");

        int _inputOffset = readInt(p2.getTypedValue());
        int _inputLen = readInt(p3.getTypedValue());
        byte[] in = readByteArray(p1.getTypedValue(), _inputOffset, _inputLen);
        tls.put(tid, "in", in);

        tls.put(tid, "p_out", p4);
    }

    @Override
    public void onExit(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        if(data.getReturnValue() == null) {
            logger.error("Cannot get return value");
            return;
        }
        int outLen = readInt(data.getReturnValue());

        IDebuggerVariable p4 = tls.get(tid, "p_out", IDebuggerVariable.class);
        byte[] out = readByteArray(p4.getTypedValue(), 0, outLen);

        byte[] in = tls.get(tid, "in", byte[].class);
        logData(in, out);

        tls.clean(tid);
    }
}
