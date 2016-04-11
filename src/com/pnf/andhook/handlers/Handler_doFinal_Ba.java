package com.pnf.andhook.handlers;

import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerEventData;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerThreadStackFrame;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerVariable;

/**
 * Hook for Cipher method: <code>byte[] doFinal(byte[] input)</code>.
 * 
 * @author Nicolas Falliere
 *
 */
public class Handler_doFinal_Ba extends AbstractHandler {

    @Override
    public String getAddress() {
        return "Ljavax/crypto/Cipher;->doFinal([B)[B";
    }

    @Override
    public void onEnter(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        IDebuggerThreadStackFrame f0 = dbg.getThreadById(tid).getFrame(0);
        IDebuggerVariable p1 = f0.getInternalParameter(1, "[B");
        byte[] in = readByteArray(p1.getTypedValue());
        tls.put(tid, "in", in);
    }

    @Override
    public void onExit(IDebuggerUnit dbg, IDebuggerEventData data) {
        long tid = data.getThreadId();

        if(data.getReturnValue() == null) {
            logger.error("Cannot get return value");
            return;
        }

        byte[] out = readByteArray(data.getReturnValue());
        byte[] in = tls.get(tid, "in", byte[].class);
        logData(in, out);

        tls.clean(tid);
    }
}
