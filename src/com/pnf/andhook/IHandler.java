package com.pnf.andhook;

import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerEventData;
import com.pnfsoftware.jeb.core.units.code.debug.IDebuggerUnit;

/**
 * Definition of a hook object.
 * 
 * @author Nicolas Falliere
 *
 */
public interface IHandler {

    /**
     * Get the hookd method address.
     * 
     * @return
     */
    String getAddress();

    /**
     * Hook routine called on method enter.
     * 
     * @param dbg
     * @param data
     */
    void onEnter(IDebuggerUnit dbg, IDebuggerEventData data);

    /**
     * Hook routine called on method exit.
     * 
     * @param dbg
     * @param data
     */
    void onExit(IDebuggerUnit dbg, IDebuggerEventData data);
}
