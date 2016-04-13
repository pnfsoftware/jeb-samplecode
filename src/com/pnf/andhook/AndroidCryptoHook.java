package com.pnf.andhook;

import com.pnf.andhook.handlers.Handler_doFinal_Ba;
import com.pnf.andhook.handlers.Handler_doFinal_BaI;
import com.pnf.andhook.handlers.Handler_update_BaIIBa;
import com.pnfsoftware.jeb.core.events.J;
import com.pnfsoftware.jeb.core.events.JebEvent;
import com.pnfsoftware.jeb.core.units.code.android.IDexUnit;
import com.pnfsoftware.jeb.core.units.code.debug.DebuggerEventType;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerEventData;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;
import com.pnfsoftware.jeb.util.events.IEvent;
import com.pnfsoftware.jeb.util.events.IEventListener;
import com.pnfsoftware.jeb.util.logging.GlobalLog;
import com.pnfsoftware.jeb.util.logging.ILogger;

/**
 * Hook set-up, tear-down and debugger listener.
 * 
 * @author Nicolas Falliere
 *
 */
public class AndroidCryptoHook {
    private static final ILogger logger = GlobalLog.getLogger(AndroidCryptoHook.class);

    IDexUnit dex;
    IDebuggerUnit dbg;
    IEventListener dbgListener;
    HandlerManager hm;

    AndroidCryptoHook(IDexUnit dex, IDebuggerUnit dbg) {
        this.dex = dex;
        this.dbg = dbg;
    }

    synchronized boolean stop() {
        if(dbgListener != null) {
            dbg.removeListener(dbgListener);
            dbgListener = null;
        }
        hm.unregisterAll();
        return true;
    }

    synchronized boolean start() {
        // our listener will be called first
        dbg.insertListener(0, dbgListener = new IEventListener() {
            @Override
            public void onEvent(IEvent e) {
                onDebuggerEvent(e);
            }
        });

        hm = new HandlerManager(dbg, dex);

        // sample hooks for 3 key encryption methods in the Cipher abstract class
        // TODO: more methods, other classes/libs, hook native libs via the native debugger
        hm.register(new Handler_doFinal_Ba());
        hm.register(new Handler_doFinal_BaI());
        hm.register(new Handler_update_BaIIBa());

        return true;
    }

    synchronized void onDebuggerEvent(IEvent e) {
        if(e.getSource() != dbg) {
            return;
        }

        if(!(e.getType() == J.DbgTargetEvent && e.getData() instanceof IDebuggerEventData)) {
            return;
        }

        IDebuggerEventData data = (IDebuggerEventData)e.getData();
        String address = data.getAddress();
        if(address == null) {
            return;
        }

        if(data.getType() == DebuggerEventType.BREAKPOINT) {
            logger.debug("METHOD ENTRY: %s", address);
            IHandler h = hm.getByAddress(address);
            if(h != null) {
                h.onEnter(dbg, data);
                dbg.run();
                ((JebEvent)e).setStopPropagation(true);
            }
        }
        else if(data.getType() == DebuggerEventType.BREAKPOINT_FUNCTION_EXIT) {
            logger.debug("METHOD EXIT: %s", address);
            IHandler h = hm.getByAddress(address);
            if(h != null) {
                h.onExit(dbg, data);
                dbg.run();
                ((JebEvent)e).setStopPropagation(true);
            }
        }
    }
}
